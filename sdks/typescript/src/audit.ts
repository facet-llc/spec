import { importJWK, errors as joseErrors, type JWK } from 'jose';
import type { AuditRecord } from './types.js';

export interface AuditVerifierOptions {
  /** Merchant JWKS containing the Ed25519 public key. */
  jwks: { keys: JWK[] };
}

export interface AuditVerifyResult {
  verified: boolean;
  errors: string[];
}

const REQUIRED_FIELDS = ['txn_id', 'iat', 'merchant', 'agent', 'sig', 'kid'] as const;

/** Canonicalize per AUDIT.md: sort keys, drop sig+kid, JSON serialize without whitespace. */
function canonicalize(record: Record<string, unknown>): string {
  const filtered: Record<string, unknown> = {};
  for (const key of Object.keys(record).sort()) {
    if (key === 'sig' || key === 'kid') continue;
    filtered[key] = record[key];
  }
  return JSON.stringify(filtered);
}

function base64urlDecode(s: string): Uint8Array {
  const pad = s.length % 4 === 0 ? '' : '='.repeat(4 - (s.length % 4));
  return new Uint8Array(Buffer.from(s + pad, 'base64'));
}

/**
 * Verify an Ed25519-signed audit record per AUDIT.md.
 *
 * Mandatory checks:
 *   - all required fields present
 *   - kid in record matches a JWK in options.jwks
 *   - JWK is kty=OKP, crv=Ed25519, alg=EdDSA
 *   - signature verifies over canonical(record without sig+kid)
 */
export async function verifyAuditRecord(
  record: AuditRecord,
  options: AuditVerifierOptions
): Promise<AuditVerifyResult> {
  for (const field of REQUIRED_FIELDS) {
    if (record[field as keyof AuditRecord] === undefined) {
      return { verified: false, errors: [`missing required field: ${field}`] };
    }
  }

  const matchingKey = options.jwks.keys.find((k) => k.kid === record.kid);
  if (!matchingKey) {
    return { verified: false, errors: [`no key in JWKS matching kid=${record.kid}`] };
  }
  if (matchingKey.kty !== 'OKP' || matchingKey.crv !== 'Ed25519') {
    return {
      verified: false,
      errors: [`audit signing key must be Ed25519 OKP; got kty=${matchingKey.kty}, crv=${matchingKey.crv}`],
    };
  }

  let publicKey: CryptoKey | Uint8Array;
  try {
    publicKey = await importJWK(matchingKey, 'EdDSA');
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return { verified: false, errors: [`failed to import key: ${message}`] };
  }

  const canonical = canonicalize(record as unknown as Record<string, unknown>);
  const message = new TextEncoder().encode(canonical);

  let signatureBytes: Uint8Array;
  try {
    signatureBytes = base64urlDecode(record.sig);
  } catch {
    return { verified: false, errors: ['malformed sig (not base64url)'] };
  }
  if (signatureBytes.length !== 64) {
    return { verified: false, errors: [`sig length must be 64 bytes, got ${signatureBytes.length}`] };
  }

  try {
    const cryptoKey = publicKey instanceof Uint8Array
      ? await crypto.subtle.importKey('raw', publicKey as BufferSource, { name: 'Ed25519' }, false, ['verify'])
      : publicKey;
    const ok = await crypto.subtle.verify(
      { name: 'Ed25519' },
      cryptoKey,
      signatureBytes as BufferSource,
      message as BufferSource
    );
    return ok
      ? { verified: true, errors: [] }
      : { verified: false, errors: ['signature verification failed'] };
  } catch (err) {
    if (err instanceof joseErrors.JOSEError) {
      return { verified: false, errors: [err.message] };
    }
    const message = err instanceof Error ? err.message : String(err);
    return { verified: false, errors: [message] };
  }
}
