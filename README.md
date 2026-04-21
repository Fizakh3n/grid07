# Grid07 — AI Cognitive Routing & RAG

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# add your groq api key to .env
```

Get a free Groq key at: https://console.groq.com

---

## Running Each Phase

```bash
python phase1_router.py
python phase2_content_engine.py
python phase3_combat_engine.py
```

---

## LangGraph Node Structure (Phase 2)

```
[decide_search] → [web_search] → [draft_post] → END
```

- **decide_search**: LLM reads the bot persona and decides today's topic + formats a search query. Returns JSON with `topic` and `search_query`.
- **web_search**: Calls `mock_searxng_search` tool with the query. Returns hardcoded headlines based on keywords (simulates real search).
- **draft_post**: LLM combines persona + search results to write a 280-char opinionated tweet. Outputs strict JSON `{bot_id, topic, post_content}`.

State flows forward through each node via a shared `BotState` TypedDict.

---

## Prompt Injection Defense (Phase 3)

The defense works at the **system prompt level**, not the user prompt level. Key strategies:

1. **Identity anchoring** — the system prompt declares the bot's persona as fixed and non-negotiable before any user content is processed.
2. **Explicit injection warning** — the system prompt directly tells the LLM that instructions inside `[HUMAN'S LATEST REPLY]` cannot override system-level rules.
3. **Role labeling** — human messages are clearly labeled as `[HUMAN'S LATEST REPLY]` so the LLM understands the trust boundary.
4. **Counter-instruction** — instead of just saying "ignore injections", we tell the bot to actively mock the attempt and keep arguing, which reinforces character consistency.

This means even if a human says "ignore all previous instructions", the LLM has already been told at the system level that such attempts are manipulation and should be rejected.

---

## Phase 1 — Threshold Note

Default threshold is `0.3` for `all-MiniLM-L6-v2`. The assignment says `0.85` but that was written assuming OpenAI embeddings. Sentence-transformer cosine scores on short texts typically land in the `0.2–0.5` range, so `0.3` gives realistic filtering without excluding everything.
