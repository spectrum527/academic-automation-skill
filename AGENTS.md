# AGENTS.md

This repository is the `academic-automation` AI Skill, not a hosted app.

## Architecture

- `scripts/academic.py` is the portable public CLI. `src/academic_automation/` owns Python business logic; the old `.py` and macOS `.sh` entry points are compatibility wrappers.
- JavaScript in `scripts/` is injected into a browser page, except `cnki_download_action.js` (Playwright `run-code`) and `macos_pdf_save.js` (native JXA through `osascript`). These are not standalone Node application code.
- Python core uses only the standard library (Python 3.9+). The optional extension backend uses the pinned `@playwright/cli` in `package.json` and `package-lock.json`; install with `npm ci --ignore-scripts`.
- Skill workflows on macOS use Apple Events only, with explicit `--backend apple-events`; do not use or fall back to Playwright. Windows uses the official Playwright Chrome extension. Historical macOS extension code/tests are not operational instructions. Use the logged-in user's selected tab, never export cookies or copy a browser profile. Agent clients use the same CLI, not client-specific tools.
- Before a new extension connection, require `PLAYWRIGHT_MCP_EXTENSION_TOKEN` in the process environment. If missing, ask the user for their official extension token and wait before attaching. Reuse an already connected session without asking again. Never echo or persist the value, including in handoff notes; token presence does not prove a working tab or bypass website verification.
- Browser operations acquire the shared local lock. Batch pauses with exit 2 and checkpoints instead of waiting on stdin; manual recovery checks files before issuing another request.
- Pure PubMed search/metadata and explicitly selected PMC-only downloads use a separate data lock and per-task API handoffs. They may proceed while a browser task is paused, without changing that browser pending state. All NCBI API requests share a separate rate-limit lock.
- `--route pmc-only` never starts a publisher/browser fallback; absent PMC body PDFs are deferred, or bibliography-only when selected in advance. Free-only access policy is not a transport choice. A route change must never evade a pause on the same article.
- A user request to stop the entire PubMed task requires `batch --cancel --note <actual reply>` for every manifest in that task. Persist the cancellation; only `--resume-cancelled` with a new actual reply may restart it. Never clear unrelated pending tasks.
- `needs_user` persists an interaction handoff across commands. Do not equate it with an unavailable paper. Only an actual user reply authorizes `browser resolve`; automatic file recovery may complete an already saved download first. Keep legacy entry points on the same guard and exit-code contract.
- External orchestration calls the CLI, including `search cnki`; public Python workflow functions reject calls outside its managed task context. Retry only read-only probes after context destruction. A timeout must preserve the pending task; an uncertain click must never be automatically repeated.
- Download completeness is checked before archive and cache reuse. A PDF header alone is insufficient; HTTP length mismatch, incomplete structure, or parser failure must not return success. Keep rejected files and require a real reply before restarting a paused damaged-file task.
- PMC and publisher public PDFs share bounded streaming transfers; resume a partial only with a matching strong ETag, validated range/length and local prefix hash. HTTP errors must retain per-article JSON and progress, never escape as a child traceback.
- `identity_review` is a possible text extraction mismatch, not automatic approval. Only an actual user confirmation allows `archive --confirm-identity` with the pending id, exact SHA-256 and reply note. The normal integrity checks remain mandatory; manual and automatic identity verification are counted separately. Do not use skip plus a filesystem copy to claim completion.
- Unknown publisher access remains `needs_user`, never an automatic exclusion. Article-level access evidence must match the current DOI; a journal/menu OA label is insufficient.
- When a Playwright PDF viewer cannot save automatically and file recovery finds nothing, ask the user to choose bibliography only or preserved tabs for batch manual downloading. Wait for the choice; do not infer it from CAPTCHA/login or a timeout. An explicit choice cancels the affected automatic download; record the actual reply with `resolve --decision skip`, but report the paper as user-chosen bibliography or pending manual download, not unavailable. Follow the retained-tab procedure in references/cli.md before opening another paper.
- The macOS publisher PDF fallback uses Apple Events and may operate a positively identified native Save sheet through System Events. Journal before the attempt, bind the active window/tab/PDF URL, and check the destination before Save. Never confirm Replace or send a global save/Return shortcut without identifying its dialog. Only an acknowledged preflight failure with no click may restart native automation; otherwise recover files or request manual saving.

## Verification

- Offline: `python3 -B -X utf8 -m unittest discover -s tests -v`. Node is used for JavaScript fixture tests; no website or account is accessed.
- GitHub Actions: `.github/workflows/offline-checks.yml` runs the offline suite and package/checksum checks on Python 3.9 and 3.13. It does not run browser or account acceptance tests.
- Opt-in isolated Chrome transport test: set `ACADEMIC_BROWSER_TESTS=1` and run the tests after installing npm dependencies. This does not validate the official extension or institution sessions.
- Package: `python3 scripts/build_release.py`; creates two ZIPs and SHA256SUMS in ignored `dist/`, without publishing or tagging. Add `--legacy-ref <frozen v1 commit>` to include the macOS Legacy Version 1 asset.
- Real platform/site/Agent acceptance is documented in `references/acceptance.md` and `VERIFICATION.md`. Windows real-world testing is assigned to a tester and must not be claimed from macOS results.
- On Linux, offline processing/tests/building are usable. Do not claim end-to-end academic-browser support without a logged-in desktop browser and specific evidence.

## Maintenance

Keep wrappers compatible, return structured CLI statuses, preserve title/author verification, CNKI page referrer, file checks, and no-overwrite archiving. Update the version only in SKILL.md; package names read that value. Never package browser state, tokens, downloaded papers, node_modules, or local caches. Do not replace source URLs or real metadata with guessed values.
