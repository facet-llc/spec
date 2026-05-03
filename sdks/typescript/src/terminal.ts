import type {
  SearchResponse,
  QuoteRequest,
  QuoteResponse,
  ReserveRequest,
  ReserveResponse,
  SettleRequest,
  SettleResponse,
  AuditRecord,
} from './types.js';

export interface TerminalConfig {
  /** Base URL of the Facet hosted Terminal. Defaults to https://facet.llc. */
  baseUrl?: string;
  /**
   * Returns a KYAPay JWT for the agent. Called per request so callers can
   * refresh tokens, swap scopes, or rotate issuers without rebuilding the
   * client.
   */
  getKYAToken: () => Promise<string> | string;
  /** Override fetch (Node 18+ has it native; pass a mock for tests). */
  fetch?: typeof globalThis.fetch;
}

export interface SearchOptions {
  q: string;
  k?: number;
  naics?: string;
  geo?: string;
}

export class FacetError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly body: unknown,
  ) {
    super(message);
    this.name = 'FacetError';
  }
}

/** Raised by the SDK when a /v1/reserve hits an x402 payment-required wall. */
export class PaymentRequiredError extends FacetError {
  constructor(
    public readonly required: {
      amount: string;
      currency: 'USDC';
      chain: 'base' | 'base-sepolia';
      to: string;
    },
    body: unknown,
  ) {
    super('payment required: x402', 402, body);
    this.name = 'PaymentRequiredError';
  }
}

/**
 * Client for the hosted Facet Terminal. Wraps the six v0.1 endpoints
 * (capabilities, search, quote, reserve, settle, audit) with KYAPay
 * authorization and typed responses.
 *
 * @example
 *   const facet = new FacetTerminal({ getKYAToken: () => process.env.KYA_TOKEN! });
 *   const { results } = await facet.searchListings({ q: 'dallas plumbing' });
 *   const quote = await facet.requestQuote({ listing_id: results[0].id });
 *   const reservation = await facet.reserve({ quote_id: quote.quote_id });
 *   const receipt = await facet.settle({
 *     reservation_id: reservation.reservation_id,
 *     x402_payment: { tx_hash: '0x...', chain: 'base' },
 *   });
 *   const audit = await facet.getAuditRecord(receipt.txn_id);
 */
export class FacetTerminal {
  private readonly baseUrl: string;
  private readonly fetchImpl: typeof globalThis.fetch;
  private readonly getKYAToken: TerminalConfig['getKYAToken'];

  constructor(config: TerminalConfig) {
    this.baseUrl = (config.baseUrl ?? 'https://facet.llc').replace(/\/$/, '');
    this.fetchImpl = config.fetch ?? globalThis.fetch;
    this.getKYAToken = config.getKYAToken;
  }

  async getCapabilities(): Promise<unknown> {
    return this.send<unknown>('GET', '/v1/capabilities');
  }

  async searchListings(opts: SearchOptions): Promise<SearchResponse> {
    const params = new URLSearchParams();
    params.set('q', opts.q);
    if (opts.k !== undefined) params.set('k', String(opts.k));
    if (opts.naics !== undefined) params.set('naics', opts.naics);
    if (opts.geo !== undefined) params.set('geo', opts.geo);
    return this.send<SearchResponse>('GET', `/v1/search?${params.toString()}`);
  }

  async requestQuote(req: QuoteRequest): Promise<QuoteResponse> {
    return this.send<QuoteResponse>('POST', '/v1/quote', req);
  }

  async reserve(req: ReserveRequest): Promise<ReserveResponse> {
    return this.send<ReserveResponse>('POST', '/v1/reserve', req);
  }

  async settle(req: SettleRequest): Promise<SettleResponse> {
    return this.send<SettleResponse>('POST', '/v1/settle', req);
  }

  async getAuditRecord(txnId: string): Promise<AuditRecord> {
    if (!txnId || typeof txnId !== 'string') {
      throw new Error('txnId must be a non-empty string');
    }
    return this.send<AuditRecord>('GET', `/v1/audit/${encodeURIComponent(txnId)}`);
  }

  private async send<T>(method: string, path: string, body?: unknown): Promise<T> {
    const token = await this.getKYAToken();
    const url = `${this.baseUrl}${path}`;
    const headers: Record<string, string> = {
      Authorization: `Bearer ${token}`,
      Accept: 'application/json',
    };
    if (body !== undefined) {
      headers['Content-Type'] = 'application/json';
    }

    const res = await this.fetchImpl(url, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });

    const contentType = res.headers.get('content-type') ?? '';
    const payload = contentType.includes('application/json')
      ? await res.json().catch(() => null)
      : await res.text().catch(() => '');

    if (res.status === 402) {
      const required = (payload as { x402_required?: PaymentRequiredError['required'] })
        ?.x402_required;
      if (required) {
        throw new PaymentRequiredError(required, payload);
      }
      throw new FacetError('payment required (no x402 instructions in body)', 402, payload);
    }

    if (!res.ok) {
      const message =
        (payload as { error?: { message?: string } })?.error?.message ??
        `${method} ${path} failed: ${res.status}`;
      throw new FacetError(message, res.status, payload);
    }

    return payload as T;
  }
}
