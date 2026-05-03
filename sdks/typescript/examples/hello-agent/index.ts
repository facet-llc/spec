/**
 * hello-agent: an end-to-end Facet client. Hits facet.llc, picks a listing,
 * walks the quote -> reserve -> settle -> audit flow.
 *
 * Run:
 *   KYA_TOKEN=eyJ... pnpm tsx examples/hello-agent/index.ts "dallas plumbing"
 *
 * Without a real KYAPay token + funded wallet, the settle step will fail with
 * a payment-required error. That's the expected behavior when you haven't
 * actually paid yet; the example shows you what the wire-level flow looks like.
 */
import { FacetTerminal, PaymentRequiredError, FacetError } from '../../src/index.js';

const token = process.env.KYA_TOKEN;
const query = process.argv[2] ?? 'dallas plumbing';

if (!token) {
  console.error('set KYA_TOKEN env var (any KYAPay JWT for the agent)');
  process.exit(1);
}

const facet = new FacetTerminal({
  baseUrl: process.env.FACET_BASE_URL ?? 'https://facet.llc',
  getKYAToken: () => token,
});

async function main() {
  console.log(`> searching for "${query}"`);
  const search = await facet.searchListings({ q: query, k: 3 });
  console.log(`  ${search.results.length} results`);
  for (const listing of search.results) {
    console.log(`  - ${listing.name} (naics=${listing.naics ?? 'n/a'}, score=${listing.score.toFixed(2)})`);
  }
  if (search.results.length === 0) {
    console.error('no results; nothing to quote');
    process.exit(2);
  }
  const pick = search.results[0]!;
  console.log(`\n> picked: ${pick.name}`);

  console.log(`> requesting quote`);
  const quote = await facet.requestQuote({ listing_id: pick.id });
  console.log(`  quote ${quote.quote_id}: ${quote.amount} ${quote.currency}, expires at ${new Date(quote.expires_at * 1000).toISOString()}`);

  console.log(`> reserving`);
  const reservation = await facet.reserve({ quote_id: quote.quote_id });
  console.log(`  reservation ${reservation.reservation_id}, settle at ${reservation.settle_endpoint}`);

  console.log(`> settling (stub x402 payment)`);
  try {
    const receipt = await facet.settle({
      reservation_id: reservation.reservation_id,
      x402_payment: {
        tx_hash: '0x' + '00'.repeat(32),
        chain: 'base',
      },
    });
    console.log(`  txn ${receipt.txn_id}`);

    console.log(`> fetching audit record`);
    const audit = await facet.getAuditRecord(receipt.txn_id);
    console.log(`  signed by merchant=${audit.merchant} kid=${audit.kid}`);
    console.log(`  sig: ${audit.sig.slice(0, 32)}...`);
  } catch (err) {
    if (err instanceof PaymentRequiredError) {
      console.log(`  402 Payment Required (expected with stub tx_hash):`);
      console.log(`    pay ${err.required.amount} ${err.required.currency} on ${err.required.chain} to ${err.required.to}`);
    } else if (err instanceof FacetError) {
      console.log(`  ${err.status}: ${err.message}`);
    } else {
      throw err;
    }
  }
}

main().catch((err) => {
  console.error('fatal:', err instanceof Error ? err.message : String(err));
  process.exit(1);
});
