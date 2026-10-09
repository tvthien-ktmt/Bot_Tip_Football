# KèoLab – Data Sources & Entity Mapping Architecture

KèoLab consumes data through a multi-source adapter pattern with strict rate limiting, point-in-time storage, and graceful degradation.

---

## 1. Supported Data Providers

| Source | Role | Rate Limit | Cache Strategy | Fallback Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **football-data.co.uk** | Free historical CSVs (FT/HT, shots, corners, cards, B365/PS odds, closing odds) | Unlimited / Static | Permanent local disk cache | Primary training source |
| **The Odds API** | Current live odds & line movements across global bookmakers | 500 req/month (Free tier) | In-memory 30m TTL + DB Snapshots | Fallback to opening lines |
| **football-data.org** | Real-time fixtures and league standings | 10 req/min | 60m TTL | Local schedule cache |
| **ClubElo API** | Team baseline Elo ratings | 10 req/min | 24h TTL | Internal calculated Elo |
| **Seed / Mock Layer** | Complete offline testing suite for all 5 top European leagues | N/A | Embedded SQLite | Immediate out-of-the-box demo |

---

## 2. Team Entity Normalization
Different bookmakers and APIs use varying nomenclature for the same football club (e.g., "Man United", "Manchester Utd", "Man Utd").
KèoLab resolves this via:
1. **Manual Dictionary Overrides** (`MANUAL_ALIASES` in `backend/app/data/team_mapper.py`) for common abbreviations.
2. **Fuzzy Token Matching** via `rapidfuzz.process.extractOne` with `token_sort_ratio >= 85` against canonical club registries.
3. **Database Aliases Table** (`team_aliases`) tracking every known external spelling with `(team_id, alias, source)`.

---

## 3. Data Integrity & Point-in-Time Guarantees
- Every match record preserves strict timestamps `date` and `status`.
- Features for match $M_t$ are computed using exclusively matches where $\text{date} < M_t$ and $\text{status} = \text{'FINISHED'}$.
- Tested against data leakage via automated regression suite (`backend/tests/test_no_leakage.py`).
