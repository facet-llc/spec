import { describe, it, expect } from 'vitest';
import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import type { JWK } from 'jose';
import { verifyAuditRecord } from '../src/audit.js';
import type { AuditRecord } from '../src/types.js';

interface AuditVector {
  name: string;
  description: string;
  spec_section: string;
  input: {
    record: AuditRecord;
    jwks: { keys: JWK[] };
  };
  expected: {
    verified: boolean;
    errors: string[];
  };
}

const VECTORS_DIR = join(__dirname, '..', '..', '..', 'test-vectors', 'audit');

function loadVectors(): AuditVector[] {
  const files = readdirSync(VECTORS_DIR).filter((f) => f.endsWith('.json')).sort();
  return files.map((f) => JSON.parse(readFileSync(join(VECTORS_DIR, f), 'utf8')));
}

describe('Ed25519 audit-record verifier conformance', () => {
  for (const v of loadVectors()) {
    it(`${v.name}: ${v.description}`, async () => {
      const result = await verifyAuditRecord(v.input.record, { jwks: v.input.jwks });

      expect(result.verified).toBe(v.expected.verified);

      if (!v.expected.verified && v.expected.errors.length > 0) {
        for (const expectedToken of v.expected.errors) {
          const matched = result.errors.some((e) =>
            e.toLowerCase().includes(expectedToken.toLowerCase())
          );
          expect(matched, `vector ${v.name}: expected error containing "${expectedToken}", got ${JSON.stringify(result.errors)}`).toBe(true);
        }
      }
    });
  }
});
