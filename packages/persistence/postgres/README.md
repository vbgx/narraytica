# Postgres Persistence Foundation

Rules:

- packages/persistence = IO adapters only
- No FastAPI / HTTPException imports
- No domain logic

Patterns:

- repo methods return domain models
- SQL rows are mapped via mappers
- transactions MUST use tx.transaction()

Forbidden:

- hidden commits
- implicit transactions
- direct driver usage outside this package
