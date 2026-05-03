import { jwtVerify, createRemoteJWKSet, importJWK, JWK, JWTPayload } from 'jose';

export interface KYAClaims extends JWTPayload {
  agent_id?: string;
  scope?: string;
}

export interface VerifierOptions {
  /** Your merchant URL or DID. The token's `aud` must match. */
  audience: string;
  /** Optional issuer allowlist. If set, the token's `iss` must be in this list. */
  expectedIssuers?: string[];
  /**
   * Override "now" for verification (Unix epoch seconds). Useful for replaying
   * test vectors against a frozen timestamp. Defaults to wall clock.
   */
  currentTime?: number;
  /**
   * Bring-your-own JWKS (instead of fetching by issuer URL). Useful for tests
   * and air-gapped deployments.
   */
  jwks?: { keys: JWK[] };
}

export interface VerifyResult {
  verified: boolean;
  claims?: KYAClaims;
  errors: string[];
}

const remoteJwksCache = new Map<string, ReturnType<typeof createRemoteJWKSet>>();

function decodeUnverifiedHeader(jwt: string): Record<string, unknown> | null {
  const parts = jwt.split('.');
  if (parts.length !== 3) return null;
  try {
    const json = Buffer.from(parts[0]!, 'base64url').toString();
    return JSON.parse(json);
  } catch {
    return null;
  }
}

function decodeUnverifiedPayload(jwt: string): Record<string, unknown> | null {
  const parts = jwt.split('.');
  if (parts.length !== 3) return null;
  try {
    const json = Buffer.from(parts[1]!, 'base64url').toString();
    return JSON.parse(json);
  } catch {
    return null;
  }
}

/**
 * Verify a KYAPay JWT (kya+jwt, pay+jwt, or kya-pay+jwt) per Facet spec section 3.
 *
 * Mandatory checks:
 *   - alg MUST be ES256
 *   - signature verifies against issuer JWKS
 *   - aud matches options.audience
 *   - iss is in options.expectedIssuers (if set)
 *   - iat, nbf, exp are valid relative to currentTime
 */
export async function verifyKYAToken(
  jwt: string,
  options: VerifierOptions
): Promise<VerifyResult> {
  const errors: string[] = [];

  const header = decodeUnverifiedHeader(jwt);
  if (!header) return { verified: false, errors: ['malformed jwt'] };

  if (header.alg !== 'ES256') {
    return {
      verified: false,
      errors: [`unsupported algorithm: expected ES256, got ${String(header.alg)}`],
    };
  }

  const payload = decodeUnverifiedPayload(jwt);
  if (!payload) return { verified: false, errors: ['malformed jwt payload'] };

  const iss = payload.iss;
  if (typeof iss !== 'string') {
    return { verified: false, errors: ['missing iss claim'] };
  }

  if (options.expectedIssuers && !options.expectedIssuers.includes(iss)) {
    return { verified: false, errors: [`unexpected issuer: ${iss}`] };
  }

  // Resolve JWKS: prefer explicit options.jwks; otherwise fetch from issuer.
  let getKey: Parameters<typeof jwtVerify>[1];
  if (options.jwks) {
    const kid = (header as { kid?: string }).kid;
    const matchingKey = options.jwks.keys.find((k) => k.kid === kid) ?? options.jwks.keys[0];
    if (!matchingKey) return { verified: false, errors: ['no matching key in JWKS'] };
    getKey = await importJWK(matchingKey, 'ES256');
  } else {
    const jwksUrl = new URL('/.well-known/jwks.json', iss);
    let remote = remoteJwksCache.get(jwksUrl.toString());
    if (!remote) {
      remote = createRemoteJWKSet(jwksUrl);
      remoteJwksCache.set(jwksUrl.toString(), remote);
    }
    getKey = remote;
  }

  try {
    const { payload: verifiedPayload } = await jwtVerify(jwt, getKey, {
      audience: options.audience,
      algorithms: ['ES256'],
      currentDate: options.currentTime ? new Date(options.currentTime * 1000) : undefined,
    });
    return { verified: true, claims: verifiedPayload as KYAClaims, errors: [] };
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    // Normalize jose's error messages into the spec's error vocabulary.
    if (message.includes('exp')) errors.push('expired');
    else if (message.includes('aud')) errors.push('audience mismatch');
    else if (message.includes('signature')) errors.push('signature verification failed');
    else errors.push(message);
    return { verified: false, errors };
  }
}
