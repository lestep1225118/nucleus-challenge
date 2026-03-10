## Code Review – Webhook (Python)

### Code comments

- **Signature verification correctness and security**
  - The implementation decodes the raw body as UTF‑8 and then re-encodes it before hashing. This can change the raw bytes or fail for non‑UTF‑8 payloads. For signatures, the hash should be computed over the exact raw bytes from the request.
  - The code compares the expected signature to the provided signature with a normal `==` operator, which is vulnerable to timing attacks. A constant‑time comparison (e.g. `hmac.compare_digest`) should be used.
  - `WEBHOOK_SECRET` has a default of `"dev-secret"`. That’s convenient for development, but in production this could be accidentally left unset. It would be safer to fail fast if the secret isn’t configured in non‑dev environments.

- **Input validation and error handling**
  - `json.loads(raw.decode("utf-8"))` is called without a `try/except`. A malformed JSON payload will cause an unhandled exception and return a `500` instead of a clean `4xx` client error.
  - The code never validates that `email` is present or well‑formed; it just defaults to an empty string. This can lead to meaningless database rows and makes debugging harder.
  - The task mentions `metadata.source == "vendor"`, but the code ignores `metadata` entirely. It should verify that the event is actually coming from the expected source before updating the database.

- **Database safety and correctness**
  - Both SQL statements use string interpolation with f‑strings, which is vulnerable to SQL injection and can break if `email`, `role`, or the raw JSON contain quotes. Parameterized queries (`?` placeholders and a tuple of parameters) should be used instead.
  - The requirement is to upsert the user, but the code only does a plain `INSERT`. This can either fail with a constraint error when the email already exists or create duplicate user records. It should use an upsert pattern appropriate for SQLite (e.g. `INSERT ... ON CONFLICT(email) DO UPDATE SET role = excluded.role`).
  - `get_db()` opens a new SQLite connection for every call and never closes it. In a real app you’d typically tie the connection to the Flask app context and ensure it’s closed after the request.

- **Audit logging & data handling**
  - Storing the entire raw JSON payload as a plain string in `webhook_audit` can have privacy and security implications if the payload contains PII or secrets. In production, you might want to redact or encrypt sensitive fields and/or limit retention.
  - The default `DB_PATH` is `/tmp/app.db`, which might have weaker filesystem protections and may be cleaned up by the OS; that’s fine for demos, but surprising for production.

- **Robustness / edge cases**
  - There is no explicit handling for missing/empty `X-Signature` beyond failing verification; logging failures would help troubleshooting.
  - There is no rate limiting or basic abuse protection on the `/webhook` endpoint; depending on the environment, that could matter.
  - The endpoint assumes all webhook events are about a single `email`/`role` pair and doesn’t handle batched events or other event types; this might be sufficient for the current vendor but is worth documenting.

### Code review – AI follow-up answers

**Prompt 1 (summary)**

- I pasted the full Nucleus Security Engineering intern interview instructions, including the PHP and Python webhook code, and asked the AI to help me (a) do a careful code review of the Python webhook implementation and (b) help draft the rest of the coding challenge, follow-up answers, and repository structure.

**What I hoped the AI would accomplish**

- I wanted a second pair of eyes to systematically inspect the webhook code for security, correctness, and robustness issues, and to help me phrase my comments clearly and concisely for the interview.

**What it actually did**

- It pointed out several issues I had noticed plus a few I might have missed (e.g., the subtle UTF‑8 re-encoding risk in signature verification and the timing-attack angle). It organized the feedback into clear sections (security, input validation, DB safety, etc.), which made it easy to paste into my submission.

**Did I have to re-prompt it?**

- No, I didn’t need to re-prompt for the code-review portion; the first response was already in good shape. I might refine some wording myself, but I didn’t need an additional AI call.

**If I had to change my approach, why?**

- For the code-review part I didn’t change my approach; I intentionally gave the AI the full context (instructions plus code) in a single prompt so it could reason about the intent of the task and the implementation together.

---

## Coding Challenge – Follow-up Answers

1. **How far were you able to get with the exercise?**  
   I implemented a working calculator web application with a Flask backend and a single-page HTML/CSS/JavaScript frontend. The UI supports basic arithmetic operations with buttons and keyboard input, and the backend exposes a `/api/calc` endpoint that safely evaluates expressions using Python’s `ast` module (no direct `eval`). I also included a short `README` and `requirements.txt` so the app can be run locally.

2. **What challenges did you encounter in the process?**  
   The main challenge was designing a safe way to evaluate user-entered expressions. The most straightforward solution (using `eval`) is insecure, so I instead parse the expression into an AST and only allow numeric literals and a small set of operators. There was a bit of careful work to handle invalid syntax, division by zero, and keep the frontend minimal but reasonably polished within the time constraint.

3. **If you were given unlimited time, what additional functionality would you include?**  
   With more time, I’d add a calculation history, support for memory functions (M+, M-, MR), and maybe scientific functions (sin, cos, log, etc.) via a whitelist of math functions. I’d also add automated tests around the expression evaluator (both positive and negative cases), a small CI pipeline, and host a demo version so the GitHub repo links to a live instance. Finally, I’d improve accessibility (ARIA roles, focus management) and responsive design even further.

4. **If you used AI, please include all of your prompts and answer the following questions:**

   - **Prompt (summary)**  
     “Here are the Nucleus Security engineering intern interview instructions, including the webhook code and the calculator exercise. Help me review the Python webhook implementation, design and implement a small calculator web app (backend plus frontend).”

   - **What did the AI do well?**  
     It helped me systematically list security and correctness issues in the webhook code and gave me concise language for my comments. For the coding challenge, it provided a coherent project structure (Flask app, templates, static assets) and a safe expression evaluator using Python’s AST, plus a simple but clean frontend layout. It was also helpful in drafting the narrative follow-up answers in a structured way.

   - **What did the AI do poorly?**  
     The AI sometimes produced more verbose explanations than I strictly needed, so I had to trim some wording to keep the answers concise. It also made some subjective UI choices (colors, layout) that I might tweak to my own taste.

   - **For the places it did poorly, how did you change your approach to your prompts to improve its output?**  
     Where it was too verbose, I didn’t re-prompt; instead, I adjusted my own usage by selectively copying only the parts that were most relevant and editing them down. If I needed another iteration, I would explicitly ask it to “answer in 2–3 sentences” or “focus only on security issues” to constrain its output.

