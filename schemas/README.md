# Schemas

JSON Schema (draft 2020-12) for the six v0.1 Facet endpoints.

| File | Endpoint |
|---|---|
| `v1.capabilities.json` | `GET /v1/capabilities` |
| `v1.search.json` | `GET /v1/search?q=<query>` |
| `v1.quote.json` | `POST /v1/quote` |
| `v1.reserve.json` | `POST /v1/reserve` |
| `v1.settle.json` | `POST /v1/settle` |
| `v1.audit.json` | `GET /v1/audit/<txn-id>` |

Each file defines `Request` and `Response` under `$defs`. Some endpoints (`v1.capabilities`, `v1.audit`) have responses only.

## Validate against a schema

```bash
# Using ajv (npm i -g ajv-cli)
ajv validate -s schemas/v1.search.json#/$defs/Response -d sample-response.json

# Or in TypeScript
import { Ajv } from 'ajv';
import addFormats from 'ajv-formats';
import schema from './schemas/v1.search.json';

const ajv = new Ajv({ strict: false });
addFormats(ajv);
const validate = ajv.compile(schema.$defs.Response);
if (!validate(payload)) console.error(validate.errors);
```

## Stability

These schemas are versioned with the spec. v0.1 schemas are frozen. Breaking changes will live in `v2.*.json` siblings.
