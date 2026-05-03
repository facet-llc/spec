# hello-agent

End-to-end Facet client. Walks the search → quote → reserve → settle → audit flow against a live Facet Terminal.

## Run it

```bash
KYA_TOKEN=eyJhbGciOiJFUzI1NiIs... \
pnpm tsx examples/hello-agent/index.ts "dallas plumbing"
```

Optional:

- `FACET_BASE_URL` (default `https://facet.llc`) point at a different Terminal
- second argv is the search query (default `dallas plumbing`)

## What you'll see

```
> searching for "dallas plumbing"
  3 results
  - Mr. Rooter Plumbing (naics=238220, score=0.52)
  - Dallas Plumbing Co. (naics=238220, score=0.48)
  - Benjamin Franklin Plumbing (naics=238220, score=0.47)

> picked: Mr. Rooter Plumbing
> requesting quote
  quote q_abc123: 250.00 USDC, expires at 2026-05-03T17:30:00.000Z
> reserving
  reservation r_xyz789, settle at https://facet.llc/v1/settle
> settling (stub x402 payment)
  402 Payment Required (expected with stub tx_hash):
    pay 250.00 USDC on base to 0xabc...
```

The settle step expects a real x402 payment receipt (a real `tx_hash` from a USDC transfer on Base). With the stub `0x000...`, the Terminal returns 402 with payment instructions. That's the SDK's `PaymentRequiredError` showing you exactly what you need to pay.

## What this example proves

- The Facet Terminal client SDK works against a live deployment
- The protocol composes (KYAPay identity → ranked search → quote/reserve/settle → signed audit)
- Errors are typed (`PaymentRequiredError`, `FacetError`)
- The whole flow is < 50 lines of TypeScript on the agent side

## When you have a real wallet

Replace the stub `tx_hash` with the actual transaction hash from your USDC transfer to the address in the 402 response, and the settle call returns a `txn_id` you can pass to `getAuditRecord` for the signed receipt.
