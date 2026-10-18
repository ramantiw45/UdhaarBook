# Deploying Udhaar Book

Two steps, about ten minutes, no card anywhere:

1. get a free open-weight key from Google AI Studio;
2. deploy this repo to Render, where `render.yaml` already describes everything.

The result is a public URL that runs the whole flow: photograph the sample page,
confirm the lines, open the asking screen, copy a WhatsApp message.

Nothing here is required to run the app locally — with no key at all it still
works end to end on the built-in parser.

---

## 1. Get the free AI Studio key (2 minutes, no card)

1. Open <https://aistudio.google.com/apikey> and sign in with any Google account.
2. Click **Create API key**. If it asks for a project, let it create one.
3. Copy the key. It starts with `AIza…` and is shown only once.
4. Check it before deploying:

   ```powershell
   $env:AI_STUDIO_API_KEY = "AIza...paste-here"

   $body = '{"model":"gemma-3-27b-it","messages":[{"role":"user","content":"Reply with the word ok."}]}'
   Invoke-RestMethod -Method Post `
     -Uri "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions" `
     -Headers @{ Authorization = "Bearer $env:AI_STUDIO_API_KEY" } `
     -ContentType "application/json" -Body $body |
     Select-Object -ExpandProperty choices |
     Select-Object -ExpandProperty message
   ```

   A reply containing `ok` means the key and the model name are both good.

   <details>
   <summary>macOS / Linux / Git Bash</summary>

   ```bash
   curl -s https://generativelanguage.googleapis.com/v1beta/openai/chat/completions \
     -H "Authorization: Bearer $AI_STUDIO_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"gemma-3-27b-it","messages":[{"role":"user","content":"Reply with the word ok."}]}'
   ```

   </details>

   | Response | Meaning |
   |---|---|
   | `200` with a reply | key and model name are good |
   | `400` / `404` | usually the model name — `AI_STUDIO_MODEL` must be `gemma-3-27b-it` |
   | `403` | the key is wrong, or the API is not enabled for that project |
   | `429` | free-tier rate limit — the app falls back, try again later |

The key is free and rate-limited, not metered: there is no billing account
attached, so it cannot produce a surprise charge. If a read hits the limit the
lane chain moves on — Groq if a key is set, then the parser.

Keep the key out of git. `.env` is already ignored, and the deployed copy lives
only in Render's environment.

---

## 2. Deploy on Render (5–7 minutes)

`render.yaml` in the repo root is the whole configuration: Python runtime, free
plan, Singapore region, `pip install -r requirements.txt`, uvicorn on `$PORT`,
health check at `/healthz`, SQLite at `data/udhaar.db`. No database service is
needed.

1. Sign in at <https://dashboard.render.com> **with GitHub**.
2. **New +** → **Blueprint**.
3. Choose the repo `ramantiw45/UdhaarBook` and branch `main`.
   Render reads `render.yaml` and shows one service, `udhaar-book`.
4. It asks for the values marked "set in the dashboard":
   - `AI_STUDIO_API_KEY` — paste the key from step 1.
   - `GROQ_API_KEY` — leave **blank**. It is an optional failover lane.
5. Click **Apply** / **Deploy Blueprint**. The first build takes two to four
   minutes.
6. When the service says **Live**, copy its URL — either
   `https://udhaar-book.onrender.com` or `https://udhaar-book-xxxx.onrender.com`.

---

## 3. Check which reader is actually live

```powershell
curl.exe -s https://YOUR-SERVICE.onrender.com/healthz
```

A healthy deploy with a working key answers:

```json
{
  "status": "ok",
  "ocr_backends": [],
  "lanes": ["ai-studio", "deterministic"],
  "db": "data/udhaar.db"
}
```

- `"lanes": ["ai-studio", "deterministic"]` — the Gemma lane is live, with the
  parser as the floor.
- `"lanes": ["deterministic"]` only — the key did not land. Open **Environment**
  in Render, check `AI_STUDIO_API_KEY`, then **Save** (the service restarts).
- `"ocr_backends": []` is expected on Render. The on-device OCR layer is optional
  and is not installed in the cloud build; there the model reads the image.

Then walk the demo once, in this order:
**Read** → tick **use the sample page** → **Read the page** → check the confirm
table → **Write these lines** → **Ask** → copy the WhatsApp message.

The line under the scanned text names what structured it, so the page itself
tells you whether the model or the parser did the work.

---

## What the free tier means

- **It sleeps.** After 15 minutes with no traffic the instance stops. The next
  request takes 30–60 seconds; the health check is not exempt, so a sleeping
  service can look down until it wakes.
- **The disk is ephemeral.** Every deploy or restart starts with an empty
  ledger. That is fine for a demo — the sample flow is the first stop, and
  `/ledger` and `/ask` have honest empty states that point back to it.
- **One file, no database service.** The ledger is a single SQLite file.
- **Surviving deploys** would need a paid Render disk mounted somewhere, with
  `UDHAAR_DB` pointed at it. Not needed to show the idea.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Build fails immediately | the requested Python patch is not offered | set `PYTHON_VERSION` to `3.12.11` or `3.13.7` in the dashboard and redeploy |
| Live, but every read says "built-in parser" | key missing, invalid, or model name retired | check `/healthz`, then the Render logs |
| `429` in the logs | free-tier request limit | expected; the chain falls back, retry later |
| First visit times out | free instance asleep | wait, then reload |
| Deploy is Live but `/healthz` 502s | the app crashed on boot | Render logs — the usual cause is a bad env value |

---

## What leaves the machine

- **No key:** nothing. The page is read by the local OCR layer if installed,
  otherwise by the parser.
- **With a key:** the page image (or its text) goes to Google AI Studio to be
  read, and nothing else — no names leave in any other request.
- No accounts, no cookies, no analytics, no payment links.

---

## Local equivalent

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
copy .env.example .env          # optional: one free key, or none
.\.venv\Scripts\python -m uvicorn app:app --reload
```

Open <http://127.0.0.1:8000>. Tick **use the sample page** to run without any
key at all.
