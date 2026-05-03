# @facet/sdk-js

Reference TypeScript SDK for the [Facet Protocol](https://github.com/facet-llc/protocol). KYAPay verifier today; Terminal client coming in v0.1.0.

```bash
npm install @facet/sdk-js
```

## Verify a KYAPay JWT

```typescript
import { verifyKYAToken } from '@facet/sdk-js';

const result = await verifyKYAToken(jwt, {
  audience: 'https://my-merchant.example.com',
  expectedIssuers: ['https://issuer.example.com'],
});

if (result.verified) {
  console.log('agent claims:', result.claims);
} else {
  console.error('verification failed:', result.errors);
}
```

The verifier will fetch the issuer's JWKS from `<iss>/.well-known/jwks.json` and cache it in-process. To skip the fetch (tests, air-gapped, or pinned keys), pass an explicit `jwks`:

```typescript
const result = await verifyKYAToken(jwt, {
  audience: '...',
  jwks: { keys: [/* JWK objects */] },
});
```

## Run against the conformance vectors

```typescript
import { verifyKYAToken } from '@facet/sdk-js';
import vector from '../../test-vectors/kyapay/01-valid-kya-jwt.json' with { type: 'json' };

const result = await verifyKYAToken(vector.input.jwt, {
  ...vector.input.verify_options,
  jwks: vector.input.jwks,
  currentTime: vector.input.now,
});

console.assert(result.verified === vector.expected.verified, vector.name);
```

## Status

`v0.0.1` ships:

- `verifyKYAToken()` with mandatory ES256 + JWKS resolution + claim checks
- TypeScript types for the six v0.1 endpoints

`v0.1.0` will add:

- Terminal client (`searchListings`, `requestQuote`, `reserve`, `settle`, `getAuditRecord`)
- Auto-generated types from the JSON schemas
- React hooks for browser integration
- A `pay+jwt` helper that signs payment tokens

## License

Apache 2.0. See the [protocol repo](https://github.com/facet-llc/protocol/blob/main/LICENSE).
