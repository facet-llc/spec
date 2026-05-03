/**
 * TypeScript types matching the v0.1 JSON Schemas in /schemas.
 *
 * These are hand-maintained for v0.0.1; v0.1.0 will derive them automatically
 * from the schemas via json-schema-to-typescript.
 */

export interface Listing {
  id: string;
  name: string;
  naics?: string;
  score: number;
  geo?: {
    city?: string;
    state?: string;
    zip?: string;
  };
  endpoints: {
    capabilities?: string;
    quote: string;
  };
}

export interface SearchResponse {
  query: string;
  results: Listing[];
  audit?: AuditRecord;
}

export interface QuoteRequest {
  listing_id: string;
  params?: Record<string, unknown>;
}

export interface QuoteResponse {
  quote_id: string;
  amount: string;
  currency: 'USDC';
  chain?: 'base' | 'base-sepolia';
  expires_at: number;
  reserve_endpoint: string;
}

export interface ReserveRequest {
  quote_id: string;
}

export interface ReserveResponse {
  reservation_id: string;
  expires_at: number;
  settle_endpoint: string;
  x402_required?: {
    amount: string;
    currency: 'USDC';
    chain: 'base' | 'base-sepolia';
    to: string;
  };
}

export interface SettleRequest {
  reservation_id: string;
  x402_payment: {
    tx_hash: string;
    chain: 'base' | 'base-sepolia';
    amount?: string;
  };
}

export interface SettleResponse {
  txn_id: string;
  audit_endpoint: string;
  fulfillment?: Record<string, unknown>;
}

export interface AuditRecord {
  txn_id: string;
  iat: number;
  merchant: string;
  agent: string;
  amount?: string;
  currency?: 'USDC';
  tx_hash?: string;
  sig: string;
  kid: string;
}
