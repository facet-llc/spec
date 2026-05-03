import { describe, it, expect } from 'vitest';
import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { verifyKYAToken } from '../src/verifier.js';

interface Vector {
  name: string;
  description: string;
  spec_section: string;
  input: {
    jwt: string;
    jwks?: { keys: unknown[] };
    verify_options: {
      audience: string;
      expected_issuers?: string[];
    };
    now: number;
  };
  expected: {
    verified: boolean;
    claims?: Record<string, unknown>;
    errors: string[];
  };
}

const VECTORS_DIR = join(__dirname, '..', '..', '..', 'test-vectors', 'kyapay');

function loadVectors(): Vector[] {
  const files = readdirSync(VECTORS_DIR).filter((f) => f.endsWith('.json')).sort();
  return files.map((f) => JSON.parse(readFileSync(join(VECTORS_DIR, f), 'utf8')));
}

describe('KYAPay verifier conformance', () => {
  for (const v of loadVectors()) {
    it(`${v.name}: ${v.description}`, async () => {
      const result = await verifyKYAToken(v.input.jwt, {
        audience: v.input.verify_options.audience,
        expectedIssuers: v.input.verify_options.expected_issuers,
        jwks: v.input.jwks as { keys: never[] } | undefined,
        currentTime: v.input.now,
      });

      expect(result.verified).toBe(v.expected.verified);

      // For failure cases, ensure at least one error contains an expected token.
      if (!v.expected.verified && v.expected.errors.length > 0) {
        for (const expectedToken of v.expected.errors) {
          const matched = result.errors.some((e) =>
            e.toLowerCase().includes(expectedToken.toLowerCase())
          );
          expect(matched, `vector ${v.name}: expected error containing "${expectedToken}", got ${JSON.stringify(result.errors)}`).toBe(true);
        }
      }

      // For success cases, sanity-check returned claims.
      if (v.expected.verified && v.expected.claims) {
        expect(result.claims).toMatchObject(v.expected.claims);
      }
    });
  }
});
