# ADR-002: Estratégia de Containerização

## Status
**Aprovado** — 2026-07-03

## Contexto
A NAP deve rodar 100% em containers Docker para garantir reproducibilidade do ambiente de desenvolvimento e produção. O comando de inicialização universal é `docker compose up -d`.

## Decisão

### Estrutura de Serviços
1. **postgres** — PostgreSQL 16 Alpine, volume persistente
2. **redis** — Redis 7 Alpine, volume persistente
3. **qdrant** — Qdrant latest, volume persistente, healthcheck HTTP
4. **backend** — FastAPI com hot-reload via volume bind mount
5. **frontend** — Next.js dev server com hot-reload

### Volumes Persistentes
- `postgres_data`: dados do banco
- `redis_data`: cache do Redis
- `qdrant_data`: dados vetoriais

### Healthchecks
- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`
- Qdrant: `curl /healthz`
- Backend depende de todos os 3 healthchecks

### Variáveis de Ambiente
- Gerenciadas via `.env` (não versionado)
- `OPENROUTER_API_KEY` é obrigatória para funcionalidades de IA

## Consequências
- Ambiente totalmente reproduzível com um comando
- Volumes separados permitem reset seletivo
- Hot-reload para desenvolvimento ágil
- Backend só inicia após todos os serviços estarem saudáveis