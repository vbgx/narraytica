import type { SearchQueryDTO, SearchResultDTO } from "../dtos/search_dto";

export type SearchPort = {
  search(query: SearchQueryDTO): Promise<SearchResultDTO>;
};
