![Academic Automation Skill — literature search and download](assets/readme-banner.png)

# <img src="assets/logo.png" alt="" width="48" height="48" align="center"> Academic Automation Skill

**English** | [简体中文](README.zh-CN.md)

> **IMPORTANT, ACCESSIBILITY PERMISSIONS AND SAFETY: On macOS, this Skill makes your Agent/Harness request system Accessibility permission and automation access to Chrome and System Events, which it uses for UI automation and native PDF saving. Accessibility permission lets an application control the whole system UI, beyond any single webpage. If you have any security concerns, DO NOT USE THIS SKILL and do not grant these permissions.**
>
> **This notice ships in both the Windows and macOS packages. On Windows the Skill currently drives webpages through the Playwright extension and leaves system Save dialogs to you. If your Agent/Harness asks for any other system-control permission, assess it carefully.**

Install this Skill in an AI agent and you can ask the agent for papers in plain language. It searches PubMed and CNKI, and can also use Web of Science or Google Scholar. It writes a bibliography with a link for every entry, and downloads full texts into your library folder when you already have access to them. It stops and asks you when it hits a login page or a CAPTCHA, or needs a decision from you.

Everything runs in your own logged-in Chrome with your own account or institutional access. The project provides no database accounts and cannot get you paid papers for free.

The current version is **2.0.0 RC3** (release candidate). See the [release notes](RELEASE_NOTES.md) for changes and the [verification record](VERIFICATION.md) for what has been tested.

## What you can ask for

| Task | Example request |
| --- | --- |
| Search a topic and list the results | "Find Chinese journal papers on project-based learning in CNKI, bibliography only" |
| Search and download what is available | "Search PubMed for Mendelian randomization and download what you can" |
| Download from a list | "Download these titles from CNKI one by one; first authors are in column 2" |
| Use PMC only, no browser | "Get these PMIDs from PMC only and keep the rest as bibliography entries" |
| Download by DOI | "Download the full text of this DOI into papers/english" |

### Supported sources

| Source | Search and bibliography | Full-text download | Status |
| --- | --- | --- | --- |
| PubMed | Official API, no browser needed | Public PMC PDFs; others through the publisher | Preview |
| CNKI Chinese library | Basic and expert search | Yes; the first author is required | Supported |
| CNKI foreign library (WWJD) | Yes | No CNKI download button; goes to the publisher with the full DOI | Supported |
| Web of Science | Yes | Through the publisher by DOI | Supported |
| Google Scholar | Yes | Through the publisher by DOI | Supported |

Every bibliography entry links to its publication page, and entries without a link are listed separately as incomplete. Downloaded files are checked for completeness before archiving. With the optional `pypdf` package installed, the Skill also compares the title and authors on the first page, so a supplement or a different paper is not counted as the article. Files go into your existing folder structure and never overwrite a file with the same name. Interrupted searches and batch downloads can be resumed.

Some automation may stop working for a while after a database changes its pages or login flow.

## Platforms and requirements

| Platform | How the browser is controlled | Status |
| --- | --- | --- |
| macOS | Apple Events drive your everyday Chrome; native Save dialogs are handled through System Events. Playwright is not used | Main development and testing platform |
| Windows 10/11 | Playwright CLI with the official Chrome extension; an extension Token is required before the first connection | Preview. Testers have reported PubMed search, bibliography and two PMC downloads working; the RC3 extension and publisher flows still need Windows acceptance testing |
| Linux | None | Offline processing only |

All platforms need Python 3.9 or later; 3.11+ is recommended for new installs. Browser workflows on Windows also need Node.js 22+. PubMed API tasks and PMC-only downloads need only Python and a network connection, with no Chrome, Node.js or extension.

Google Chrome is the only supported browser.

## Installation

1. Download the package for your platform (`-windows.zip` or `-macos.zip`) from the [RC3 Release](https://github.com/spectrum527/academic-automation-skill/releases/tag/v2.0.0-rc.3). Packages do not include Python, Node.js or Chrome.
2. Put the whole Skill folder in your agent's skills directory. The current source and newly built packages use `academic-automation` for both the folder and Skill name; previously published packages retain the name in their bundled `SKILL.md`. For Codex, you can copy the current source checkout as follows.

   ```bash
   cp -R . ~/.agents/skills/academic-automation
   ```

   When upgrading an existing installation, replace the old active Skill instead of keeping both names loaded. Preserve task records and downloaded papers.

3. Set up the browser for your platform.
   - macOS: in Chrome, turn on View → Developer → Allow JavaScript from Apple Events. For automatic PDF saving, also grant Accessibility permission to the app that runs your agent in System Settings → Privacy & Security → Accessibility. See the [macOS guide](references/install-macos.md).
   - Windows: install Microsoft's official Playwright Chrome extension, run `npm.cmd ci --ignore-scripts` in the unzipped folder, and give the extension Token to the agent's process environment. See the [Windows guide](references/install-windows.md).
4. Optional: run `python3 -m pip install -r requirements-pdf.txt` in the Skill folder (`py -3` on Windows) to enable automatic article verification. Without it, files are still archived and the agent reports them as not automatically verified.

macOS users can also choose [Legacy Version 1](LEGACY.md), the old 1.6.0 release without PubMed or Windows support. It retains its frozen Skill name; keep only one version active when switching.

Earlier macOS versions were tested in OpenCode and Qoder, as well as Cursor and OpenAI Codex. The new cross-platform version still needs to be re-tested in them. Agents differ in how they load Skills and call tools, so behavior may not be identical everywhere.

The agent's operating rules are in `SKILL.md`. Command-line usage is in the [CLI reference](references/cli.md) (Chinese).

## When the agent stops to ask you

In the cases below the agent pauses the current paper, tells you what it needs, and waits for your reply. No reply, or a timeout, is never treated as permission to skip.

- **Subscription scope.** Before searching PubMed, the CNKI foreign library, WoS or Scholar, it asks whether to include paid or subscription papers if you have not said so. If you decline, it asks whether to drop those papers or keep them as bibliography entries. Saying yes only lets it try your existing institutional access; it never buys anything.
- **CAPTCHA, login or human verification.** It does not bypass these. You complete them in the browser and the task continues.
- **A PDF that cannot be saved automatically.** If automatic saving fails and no file turns up in the download folder, it asks whether you want bibliography entries only, or want each paper's tab kept open so you can download them by hand at the end. Files you save by hand are still verified before archiving.
- **A possible title mismatch.** If the title extracted from the PDF does not match the expected one, which can be a character-recognition glitch, it shows you both titles with the authors and DOI, and archives the file only after you confirm.
- **Unclear free access.** If the publisher page has no evidence that this particular article is free, the paper stays pending for you to decide. It is not dropped automatically.

If you tell it to stop everything, it cancels the whole batch and records that, so a later re-run will not restart it on its own.

## Accounts, access and responsible use

- The project provides no accounts, subscriptions or institutional access for CNKI, Google Scholar, Web of Science or any other database. It contains none of the developer's credentials or login sessions.
- All access goes through your own browser, account and existing permissions. The agent does not export cookies or copy your browser profile.
- The project does not circumvent authentication, paywalls, CAPTCHAs or other access controls. It does not host, sell or redistribute full texts from any database.
- Please keep the scale and frequency of automation reasonable and follow the rules of the databases and your institution. You are responsible for making sure your use complies with platform terms, institutional license agreements and applicable law.
- This is an independent personal project. It is not affiliated with, sponsored by or endorsed by CNKI, Google Scholar, Web of Science or their operators. All product names and trademarks belong to their owners.
- Third-party sites may change their terms, technical measures and access policies at any time. The maintainer cannot guarantee that they will keep allowing or supporting automated access.

## Development

This is a personal project built mostly through Vibe Coding. The maintainer decides requirements and feature direction, and handles testing and releases. Generative AI, mainly Cursor and OpenAI's ChatGPT, was used heavily for coding and debugging, and also for refactoring, documentation and design discussions. AI-assisted development is a deliberate part of how this project is made, so it is stated here.

The offline tests do not touch any website or account.

```bash
python3 -B -X utf8 -m unittest discover -s tests -v
```

`python3 scripts/build_release.py` builds the release packages into `dist/`. Acceptance testing is described in [references/acceptance.md](references/acceptance.md) and [VERIFICATION.md](VERIFICATION.md).

Current work focuses on more reliable searches across databases, better filtering and organization, keeping up with site changes, compatibility with more agents, and Windows support together with testers. If something breaks after a database updates its site, please open an issue. Test results and compatibility reports are welcome too.

## Changelog

- **2.0.0 RC3**: unified Skill and package-root naming as `academic-automation`, with upgrade guidance and Python 3.9 / 3.13 offline CI. Legacy snapshots retain their original name and contents.
- **2.0.0 RC2**: repository migration, refreshed documentation and branding, and bundled README images. See the [release notes](RELEASE_NOTES.md).
- **2.0.0 RC1**: PubMed and Windows workflow fixes; retained as a historical release.
- **1.6.0** (2026-09-12) Lower initial context use and resumable workflows.
  - Load workflow and troubleshooting references only when needed; reduce `SKILL.md` from 13,696 to 3,108 characters (77.3%).
  - Wait for stable page content and completed downloads; preserve WoS records recycled by virtual scrolling and detect download-time paywalls or CAPTCHA prompts.
  - Resume search pages and metadata collection, deduplicate batch entries by document identity, and reuse a 24-hour professional-search index with live detail verification.
  - Require the first author before starting Chinese downloads; use shared single-tab navigation for unknown publishers.
  - Add 16 regression tests and [verification results](VERIFICATION.md) covering live CNKI, WoS, Scholar, and OA download workflows.
- **1.5.1** (2026-08-26) Chinese library matching and file handling fixes. Title search now goes through `korder=TI`; exact matches take priority (several substring matches no longer resolve to the first row); a short title without an author exits with code 64; `--affiliation` carries `TI=`/`AU=` as well; the detail, paywall, and verification pages are polled before and after the download click; files are archived by mtime; after a CAPTCHA the downloaded file is checked first; single-tab navigation now covers WoS, Scholar, and the foreign library; status tables accept two header layouts; bibliographic entries without a URL are no longer written into the list.
- **1.5.0** (2026-08-26) Download stability for the Chinese library.
  - `cnki_dl.sh`: author check on the result row (titles of 6 characters or fewer require an author); `--expert` professional search (`SU='A' AND SU='B'`, which works around the advanced search button that ignores injected clicks); `--affiliation` institution filter; `《》〈〉""——` are stripped from the search URL automatically; NOMATCH scans up to 3 result pages (`--pages`); single-tab `set URL` with `window.stop()` before navigating; exit code 5 recognizes the paywall page at `bar.cnki.net/bar/fee`.
  - Added `scripts/cnki_batch.py`: `i/N` progress, an idempotent status table located by row number, pause and resume on CAPTCHA, and cleanup of surplus tabs in the front window every 10 papers.
  - Added `scripts/cnki_next.js` and `scripts/cnki_url.js`.
  - `SKILL.md`: scan the workspace before starting, how to use professional search, and "known pitfalls" (zsh `IFS`, cross-device `shutil.move`, JS return values, and how long `bar.cnki.net` order pages take).
- **1.4.1** CNKI foreign library (WWJD), quoted phrase search, DOI completion, publisher OA routing (`oa_dl.sh`), and the Web of Science / Google Scholar workflows.

## License

[MIT License](LICENSE)
