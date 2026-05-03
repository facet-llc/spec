import {
  jwtVerify,
  createRemoteJWKSet,
  importJWK,
  errors as joseErrors,
  type JWK,
  type JWTPayload,
} from 'jose';

export interface KYAClaims extends JWTPayload {
  agent_id?: string;
  scope?: string;
}

export interface VerifierOptions {
  /** Your merchant URL or DID. The token's `aud` must match. */
  audience: string;
  /**
   * Issuer allowlist. Required when `jwks` is not provided. The token's `iss`
   * must be in this list, and only HTTPS issuer URLs are accepted.
   *
   * Without this, the verifier would fetch a JWKS from any issuer URL the JWT
   * claims, accepting tokens from any internet-reachable host that publishes
   * a valid JWKS. That is a trust bypass; we refuse the unsafe default.
   */
  expectedIssuers?: string[];
  /**
   * Override "now" (Unix epoch seconds). Useful for replaying conformance
   * vectors against a frozen timestamp.
   */
  currentTime?: number;
  /**
   * Bring-your-own JWKS. When set, the verifier skips the issuer-driven JWKS
   * fetch entirely. Useful for tests, air-gapped deploys, and pinned-key
   * rotation.
   */
  jwks?: { keys: JWK[] };
  /** Clock skew tolerance for iat/nbf/exp checks. Defaults to '30s'. */
  clockTolerance?: string | number;
  /** JWKS fetch timeout (ms). Defaults to 5000. */
  jwksTimeoutMs?: number;
}

export interface VerifyResult {
  verified: boolean;
  claims?: KYAClaims;
  errors: string[];
}

const MAX_JWKS_CACHE = 64;
const remoteJwksCache = new Map<string, ReturnType<typeof createRemoteJWKSet>>();

function rememberJwks(url: string, set: ReturnType<typeof createRemoteJWKSet>) {
  if (remoteJwksCache.size >= MAX_JWKS_CACHE) {
    const oldest = remoteJwksCache.keys().next().value;
    if (oldest !== undefined) remoteJwksCache.delete(oldest);
  }
  remoteJwksCache.set(url, set);
}

function decodeUnverifiedHeader(jwt: string): Record<string, unknown> | null {
  const parts = jwt.split('.');
  if (parts.length !== 3) return null;
  try {
    return JSON.parse(Buffer.from(parts[0]!, 'base64url').toString());
  } catch {
    return null;
  }
}

function decodeUnverifiedPayload(jwt: string): Record<string, unknown> | null {
  const parts = jwt.split('.');
  if (parts.length !== 3) return null;
  try {
    return JSON.parse(Buffer.from(parts[1]!, 'base64url').toString());
  } catch {
    return null;
  }
}

function validateCustomClaims(p: JWTPayload): { ok: true; claims: KYAClaims } | { ok: false; reason: string } {
  if (p.agent_id !== undefined && typeof p.agent_id !== 'string') {
    return { ok: false, reason: 'agent_id must be a string' };
  }
  if (p.scope !== undefined && typeof p.scope !== 'string') {
    return { ok: false, reason: 'scope must be a string' };
  }
  return { ok: true, claims: p as KYAClaims };
}

function mapJoseError(err: unknown): string {
  if (err instanceof joseErrors.JWTExpired) return 'expired';
  if (err instanceof joseErrors.JWTClaimValidationFailed) {
    return err.claim === 'aud' ? 'audience mismatch' : `claim validation failed: ${err.claim}`;
  }
  if (err instanceof joseErrors.JWSSignatureVerificationFailed) return 'signature verification failed';
  if (err instanceof joseErrors.JOSEError) return err.message;
  return err instanceof Error ? err.message : String(err);
}

/**
 * Verify a KYAPay JWT (kya+jwt, pay+jwt, or kya-pay+jwt) per Facet spec section 3.
 *
 * Mandatory checks:
 *   - alg MUST be ES256
 *   - signature verifies against issuer JWKS
 *   - aud matches options.audience
 *   - iss is in options.expectedIssuers (required unless options.jwks is set)
 *   - iss URL uses https when fetching JWKS remotely
 *   - kid header is present and matches a key in the JWKS
 *   - iat, nbf, exp are valid relative to currentTime (with clockTolerance)
 *   - custom claims (agent_id, scope) match their declared types
 */
export async function verifyKYAToken(
  jwt: string,
  options: VerifierOptions
): Promise<VerifyResult> {
  const header = decodeUnverifiedHeader(jwt);
  if (!header) return { verified: false, errors: ['malformed jwt'] };

  if (header.alg !== 'ES256') {
    return {
      verified: false,
      errors: [`unsupported algorithm: expected ES256, got ${String(header.alg)}`],
    };
  }

  const kid = (header as { kid?: string }).kid;
  if (typeof kid !== 'string' || kid.length === 0) {
    return { verified: false, errors: ['jwt header missing kid'] };
  }

  const payload = decodeUnverifiedPayload(jwt);
  if (!payload) return { verified: false, errors: ['malformed jwt payload'] };

  const iss = payload.iss;
  if (typeof iss !== 'string') {
    return { verified: false, errors: ['missing iss claim'] };
  }

  // Trust gate: require explicit issuer allowlist OR explicit jwks.
  // Without one of those, the verifier would accept any issuer that hosts a
  // valid JWKS, which is a trust bypass. Refuse the unsafe default.
  const hasAllowlist = Array.isArray(options.expectedIssuers) && options.expectedIssuers.length > 0;
  if (!options.jwks && !hasAllowlist) {
    return {
      verified: false,
      errors: [
        'expectedIssuers is required when jwks is not provided. ' +
          'Pass an allowlist of trusted issuer URLs to prevent JWKS-trust bypass.',
      ],
    };
  }

  if (hasAllowlist && !options.expectedIssuers!.includes(iss)) {
    return { verified: false, errors: [`unexpected issuer: ${iss}`] };
  }

  const verifyOpts = {
    audience: options.audience,
    algorithms: ['ES256'],
    clockTolerance: options.clockTolerance ?? '30s',
    currentDate: options.currentTime ? new Date(options.currentTime * 1000) : undefined,
  };

  try {
    let verifiedPayload: JWTPayload;

    if (options.jwks) {
      const matchingKey = options.jwks.keys.find((k) => k.kid === kid);
      if (!matchingKey) {
        return { verified: false, errors: [`no key in JWKS matching kid=${kid}`] };
      }
      const key = await importJWK(matchingKey, 'ES256');
      ({ payload: verifiedPayload } = await jwtVerify(jwt, key, verifyOpts));
    } else {
      if (!iss.startsWith('https://')) {
        return { verified: false, errors: ['issuer must use https for remote JWKS resolution'] };
      }
      const jwksUrl = new URL('/.well-known/jwks.json', iss);
      const cacheKey = jwksUrl.toString();
      let remote = remoteJwksCache.get(cacheKey);
      if (!remote) {
        remote = createRemoteJWKSet(jwksUrl, {
          timeoutDuration: options.jwksTimeoutMs ?? 5000,
          cooldownDuration: 30_000,
        });
        rememberJwks(cacheKey, remote);
      }
      ({ payload: verifiedPayload } = await jwtVerify(jwt, remote, verifyOpts));
    }

    const validated = validateCustomClaims(verifiedPayload);
    if (!validated.ok) {
      return { verified: false, errors: [validated.reason] };
    }
    return { verified: true, claims: validated.claims, errors: [] };
  } catch (err: unknown) {
    return { verified: false, errors: [mapJoseError(err)] };
  }
}
