export type PageDTO = {
  limit: number;
  offset: number;
};

export type SearchQueryDTO = {
  q: string;
  page: PageDTO;

  // v0: filtres optionnels, à aligner avec contracts ensuite
  filters?: Record<string, unknown>;

  // v0: options de scoring/ranking si nécessaire
  options?: Record<string, unknown>;
};

export type SearchItemScoreDTO = {
  combined: number;
  // v0: breakdown optionnel
  lexical?: number;
  semantic?: number;
};

export type SearchItemDTO = {
  id: string;
  type: string;
  score: SearchItemScoreDTO;
  payload: Record<string, unknown>;
};

export type SearchResultDTO = {
  page: PageDTO;
  total?: number;
  items: SearchItemDTO[];
};
