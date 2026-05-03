/**
 * Verify a KYAPay JWT against an issuer's JWKS.
 *
 * Usage:
 *   KYA_TOKEN=eyJ... AUDIENCE=https://my-merchant.com pnpm tsx examples/verify.ts
 */
import { verifyKYAToken } from '../src/index.js';

const jwt = process.env.KYA_TOKEN;
const audience = process.env.AUDIENCE;

if (!jwt || !audience) {
  console.error('set KYA_TOKEN and AUDIENCE env vars');
  process.exit(1);
}

const result = await verifyKYAToken(jwt, { audience });

console.log(JSON.stringify(result, null, 2));
process.exit(result.verified ? 0 : 1);
