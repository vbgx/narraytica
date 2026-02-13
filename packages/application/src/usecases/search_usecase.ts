import type { SearchPort } from "../ports/search_port";
import type { SearchQueryDTO, SearchResultDTO } from "../dtos/search_dto";
import { AppError } from "../errors/app_error";

export type SearchUseCaseDeps = {
  searchPort: SearchPort;
};

export async function searchUseCase(
  deps: SearchUseCaseDeps,
  query: SearchQueryDTO
): Promise<SearchResultDTO> {
  if (!query.q || query.q.trim().length === 0) {
    throw new AppError("VALIDATION_ERROR", "q is required");
  }
  if (!query.page || typeof query.page.limit !== "number" || typeof query.page.offset !== "number") {
    throw new AppError("VALIDATION_ERROR", "page.limit and page.offset are required");
  }
  if (query.page.limit <= 0 || query.page.limit > 200) {
    throw new AppError("VALIDATION_ERROR", "page.limit out of range");
  }
  if (query.page.offset < 0) {
    throw new AppError("VALIDATION_ERROR", "page.offset out of range");
  }

  return deps.searchPort.search(query);
}
