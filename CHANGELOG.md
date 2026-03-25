# Changelog

## [v6.4.3] — 2026-03-25

### Changed
- **`skip_upcoming` hardwired to `True`** — upcoming/unreleased content is always filtered; the toggle has been removed from the UI and DEFAULT_CONFIG; both Sonarr (by `airDateUtc`) and Radarr (by `digitalRelease` / `physicalRelease` / `inCinemas`) filter unreleased items before every run; skipped count logged at INFO level

### Added
- **Configurable log rotation** — new settings in General tab:
  - **Max file size (MB)**: 1–100 MB (default 5 MB)
  - **Backup count**: 0–10 files (default 2, giving 3 files total: current + 2 backups)
  - `_setup_file_logging()` accepts `max_mb` / `backups` from CONFIG; safe to call multiple times (reconfigures in-place without restart)
  - `_reconfigure_file_logging()` applies updated CONFIG values to running handler after `/api/config` save
  - `POST /api/log/rotate` — manually triggers `doRollover()` and returns file sizes of current + all backups
  - `GET /api/log/status` — returns all log files with sizes, max_bytes, backups_count, log_dir path
  - "🔄 Rotate now" and "📋 Status" buttons in General settings with inline result display
  - New i18n keys: `lbl_log_rotation`, `hint_log_rotation`, `lbl_log_max_mb`, `hint_log_max_mb`, `lbl_log_backups`, `hint_log_backups`, `btn_log_rotate`, `btn_log_status` (DE + EN)
- **Unit tests**: 15 assertions covering `_ep_is_released`, `_movie_is_released` (yesterday/tomorrow/ISO-Z/no-date edge cases) and `RotatingFileHandler` (initial setup, rollover, reconfigure, clamp-min, clamp-max) — all pass

## [v6.4.3] — 2026-03-25

### Fixed
- **Bug #22 — Stats tabs ignore theme**: `<button>` elements inherited browser-default background/border; added `background:none;border:none;cursor:pointer` inline styles so `.tab-btn` CSS variables apply correctly in all themes
- **Bug #21 — Console shows 0 entries**: `_feedConsole` was patching `updateUI` with a param that was never passed (function reads `appState` globally); fixed to call `_feedConsole(appState)` directly after `_origFetchState()` resolves; also fixed log entry field mapping (`ts`/`service`/`action`/`item` vs incorrect `ts`/`source`/`message`)
- **Bug #24 — Settings page not full width**: added `#page-settings.content { grid-template-columns: 1fr; }` so the settings card fills the full content area instead of half the grid
- **Bug #23 — Homepage hero version stuck on v6.3.8**: badge already fixed in v6.4.2 to `v6.4.2`; now shows `v6.4.3` as hardcoded fallback and fetches latest GitHub Release on load

### Added
- **Bug #20 — Config migration**: new `_migrate_config()` runs on every startup; non-destructively adds any keys from `DEFAULT_CONFIG` that are missing in the saved config (top-level and nested `discord.*`); adds instance defaults (`enabled`, `daily_limit`, `type`) without touching existing values; logs every added key at INFO level
- **Feature #25 — Skip upcoming/unreleased content**: new `skip_upcoming` toggle (default **On**) in General settings; filters Sonarr episodes where `airDateUtc` is in the future and Radarr movies where all known release dates (`digitalRelease`, `physicalRelease`, `inCinemas`) are future-dated; skipped count logged at DEBUG level
- **Persistent rotating log file**: `_setup_file_logging()` called at startup; writes to `/data/logs/mediastarr.log`; 5 MB max size with 2 backups (`mediastarr.log.1`, `.log.2`); `RotatingFileHandler` from stdlib — no new dependencies
- **More logging**: DEBUG-level log for every upstream filter decision (IMDb threshold, skip_upcoming count, target resolution skip, upgrade quality skip)
- **Roadmap updated**: Per-instance limits, config export/import, read-only API, skip-upcoming all marked done; new pending items added

## [v6.4.2] — 2026-03-25

### Fixed
- **Bug #19 — History title truncated** (`.hist-title` CSS): removed `max-width: 280px` — the `1fr` grid column now controls the width, titles are no longer clipped with `…`
- **Bug #17 — Discord embed missing title**: `ev_title` was always `"🔍 Fehlend gesucht"` — the actual content title (`title` param) was never shown in the embed heading. Now prepended: `"Breaking Bad S01E03 — 🔍 Fehlend gesucht"`

### Added
- **Statistics — Sonarr / Radarr tabs**: two new filter tabs (📺 Sonarr, 🎬 Radarr) next to the existing "All" tab on the Statistics page; all KPI cards, instance bars, donut, type bars and timeline filter to only the selected service type
- **Live Log Console** (`🖥 Console` in sidebar): new full-page live console fed directly from the server activity log; features level filter (INFO+ / WARN+ / ERROR), text search, auto-scroll toggle, red error badge on nav item, clear button; entries are colour-coded by level (INFO green / WARN yellow / ERROR red)
- **Homepage version badge**: hero badge now shows the current hardcoded version (`v6.4.2`) and silently fetches the latest GitHub Release tag on load — always shows the real latest release


## [v6.4.1] — 2026-03-24

### Added
- **Per-instance daily limit** — each Sonarr/Radarr instance can have its own `daily_limit` (0 = unlimited); shown as a live mini progress bar in the instance card; backend checks global limit first, then per-instance limit
- **Config backup: Export / Import** — `GET /api/config/export` downloads a timestamped `mediastarr_config_YYYYMMDD_HHMMSS.json`; `POST /api/config/import` uploads and hot-reloads config with full validation (type whitelist, name validation, 512 KB cap); page auto-reloads after successful import
- **Read-only public `/api/state`** — `public_api_state` toggle in General settings; when enabled, `/api/state` is accessible without login (API keys always stripped); saves immediately on toggle
- **Bright new icon** — redesigned SVG radar: white-hot centre, orange glow rings, crosshair ticks, radial gradient background, sweep sector; renders crisply at all sizes
- **`favicon.ico` (32×32)** — dedicated 32-pixel ICO for browser tabs; added to all templates (`index.html`, `login.html`, `setup.html`) and homepage
- **Discord icon fixed** — footer icon URL changed from raw.githubusercontent (404 until pushed) to `https://mediastarr.de/static/icon.png` (always live)
- **GitHub ISSUE_TEMPLATE** — `.github/ISSUE_TEMPLATE/config.yml`, `feature_request.yml`, `bug_report.yml` added; blank issues disabled

### Fixed
- **Duplicate `dcToggleUrl()` function** — second declaration was actually the body of `toggleDc()` with the wrong name; now correctly defined as `function toggleDc(key)`
- **Missing `togglePublicApi()` function** — HTML toggle wired to function that was never defined → fixed
- **Missing `importConfig()` function** — file input wired to function that was never defined → fixed
- **Missing i18n keys** — `lbl_backup`, `hint_backup`, `lbl_public_api`, `hint_public_api`, `btn_export`, `btn_import` added to T dict (DE + EN)
- **`public_api_state` not synced in `updateUI()`** — toggle state now correctly restored from server on every poll
- **`saveInst()` missing `daily_limit`** — field read from `#ilimit-{id}` and sent in PATCH body
- **Sidebar version** — updated to v6.4.1

### Removed
- Ntfy / Gotify / Apprise from roadmap (not planned for near future)

### Security
- All 50 audit checks pass (5 flagged were confirmed false-positives: f-string in `get_history` only interpolates whitelist-built `WHERE` clause, not user input; `api_key` in `api_state` is the strip filter not an exposure)
- Import endpoint: validates type against `ALLOWED_TYPES` whitelist, runs `validate_name()` on all instance names, enforces 512 KB file cap, merges over DEFAULT_CONFIG (no raw overwrite)

## [v6.4.0] — 2026-03-24

### Added
- **MSLog console logger** — structured browser console output with TRACE / DEBUG / INFO / WARN / ERROR levels, colour-coded and timestamped; level adjustable at runtime via `MSLog.setLevel('DEBUG')` in DevTools
- **Settings split into 4 tabs**: General, 📺 Sonarr, 🎬 Radarr, Discord — each type now has its own instance list, add-form, and type-specific filter settings
- `addInstByType(type)` — replaces the old shared `addInstFromSettings()`, works per service type
- **Brute-force login protection** — IP-based attempt counter; 10 failed logins trigger a 5-minute lockout; constant-time 0.3 s delay on every wrong password
- **CSRF validation in `_api_auth_required`** — all POST / PATCH / DELETE API calls now validated server-side (was only on form login before)
- **Discord tab — complete redesign**:
  - Collapsible step-by-step webhook setup guide (4 steps, DE/EN)
  - 6 event cards with live Discord message preview (colour bar + field rows)
  - Show/hide toggle (👁) for webhook URL field
  - Cleaner header strip with configured-badge and master toggle
  - Save button styled in Discord brand blue
- **Homepage flipchart / screenshot carousel** — 6 real UI screenshots (Dashboard, Settings, Sonarr tab, History, Discord, Console Logger) with tab nav, prev/next, dot indicator, keyboard navigation, 5 s auto-advance; pauses on hover; captions translate with DE/EN switcher
- Screenshots nav link added to homepage header
- `screen_discord.png` added (1280×800 px)
- **Discord notification embeds — full redesign**:
  - `avatar_url` + `username` set on every webhook payload (Mediastarr logo as bot avatar)
  - Author line now shows service name (Sonarr/Radarr) with the app's own icon
  - Poster (thumbnail) + fanart/backdrop (large `image` field) from Sonarr/Radarr APIs — pulls TMDB CDN URL directly
  - External links rendered as inline clickable buttons: **⭐ IMDb · 📺 TVDB · 🎬 TMDB** (whichever are available)
  - Richer fields: Type, Year, Runtime, multi-source Ratings (IMDb+TMDB+RT with vote count), Genres (up to 4), Network/Studio, Status (🟢/🔴), Current quality (upgrades)
  - `_year_str()`, `_runtime_str()`, `_status_str()` helpers added
  - `_sonarr_fanart()` + `_radarr_fanart()` helpers for backdrop image
  - Stats embed: ASCII progress bar (`████░░`) for daily limit, per-instance table with search+upgrade counts
  - Cooldown embed: formatted with ✅/⏱/📅 fields and context sentence
  - Daily-limit embed: full progress bar (`██████████`) + reset time info
  - Offline embed: backtick-formatted error + URL, service icon in author field
  - `screen_notify_missing.png` + `screen_notify_system.png` added (1280×800 px)
  - Both notification screenshots added to homepage flipchart (now 8 slides total)

### Fixed
- **History layout (Issue #12)** — root cause was CSS selector `#page-history .content` (child search) instead of `#page-history.content` (same element); page was rendered as 2-column grid instead of full-width
- **History: full date + time** — timestamps now show `DD.MM.YY HH:MM` instead of just `HH:MM`; sticky header row with correct 7-column alignment
- **Duplicate `setInterval`** — stats page refresh interval was registered twice; now exactly once
- `deleteInst()` — uses `showActionConfirm()` non-blocking banner instead of `window.confirm()`
- `toggleInst()` — re-renders the correct type tab (sonarr/radarr) instead of a single shared list
- `fetchState()` — now re-renders the active type tab (sonarr/radarr) when either is open
- Favicon (Issue #11) — confirmed present in dashboard template and homepage (was added in v6.3.8, issues closed)

### Security
- Login brute-force protection (IP-based, 10 attempts / 5 min lockout, constant-time delay)
- CSRF token now validated on all mutating API endpoints (`_api_auth_required` decorator)
- `X-Content-Type-Options: nosniff` and `Referrer-Policy: strict-origin-when-cross-origin` headers added (v6.3.8 backport confirmed)

### Fixed (mobile & refinements pass)
- **Dashboard — tabs-row overflow** on narrow screens: `overflow-x: auto` + hide scrollbar so tabs don't clip on 320 px phones
- **Dashboard — history header columns** on mobile: 480 px breakpoint hides Type/Year columns, adjusts hist-row grid to 5 columns
- **Dashboard — 480 px breakpoint** added: tighter padding, smaller stat values, hist-row column collapse
- **Dashboard — settings card scroll** on mobile: `overflow-x: hidden` prevents layout bleed
- **Dashboard — controls-bar gap** reduced on mobile, form-actions wrap properly
- **Homepage — mobile hamburger nav**: `toggleMobileNav()` + animated drawer (`fadeDown`), ☰/✕ toggle button
- **Homepage — fc-tabs horizontal scroll**: 8 tab buttons now scroll horizontally on phones instead of wrapping
- **Homepage — comparison table overflow-x**: wrapped in `overflow-x:auto` container for mobile
- **Homepage — fc-tab flex-shrink:0**: prevents tabs from being squashed in scroll container

### Fixed (bug-hunt pass)
- **Duplicate `upgrade_target_resolution` key** in JS `saveConfig()` — key was set twice, second value silently overwrote the first; first occurrence removed
- **`save_config()` thread-safety** — file was written without a lock; concurrent API request + hunt thread could corrupt `config.json`; added `_cfg_lock = threading.Lock()` and wrapped all file I/O in `with _cfg_lock:`
- **6 bare `except:` clauses** — caught `KeyboardInterrupt`/`SystemExit`; changed to `except Exception:` throughout
- **`float(last)` crash risk** — stats loop could raise `TypeError` on `None` or corrupt config value; changed to `float(last or 0)`
- **Screenshot posters missing** — notification screenshots had invisible poster placeholders; rebuilt with film-grain texture, title overlay, star rating and letterboxed fanart strips

### Improved
- Settings General tab: cleaner layout, toggles for Upgrades and Dry Run moved into the main form grid
- Sonarr/Radarr instance cards: rendered in type-specific containers, no mixing
- Homepage: screenshots section with full flipchart widget inserted between Features and Install

## [6.3.8] — 2026-03-22

### Added
- Action banner: non-blocking confirm/message bar replaces `window.confirm()` dialogs for delete, clear history, reset setup
- `escHtml()` helper in frontend — XSS protection in all dynamic HTML rendering (instance names, titles, log entries)
- `defaultArrUrl()` + `syncNewInstUrlHint()` — new instance URL field auto-fills with the correct host:port based on the browser URL
- Settings → Instances tab: auto-refreshes instance list on tab switch

### Improved
- Instance cards: offline instances show the specific error reason instead of just "offline" (e.g. "Host not found", "Timed out", "Authentication failed")
- Page navigation: `fetchState()` called on every page/tab switch to keep data fresh
- `renderHistory()`, `renderInstanceCards()`: all user-data passed through `escHtml()`

### Fixed
- `get_history()` in db.py: `cutoff` value now passed as SQL parameter instead of f-string interpolation (SQL injection hardening)
- `_detect_local_tz()`: 4-fallback OS timezone detection (TZ env → `ZoneInfo("localtime")` → `/etc/timezone` → `/etc/localtime` symlink) — improves timezone auto-detection in Docker containers
- `ArrClient.ping()` returns structured error detail via `summarize_ping_error()` — all ping callers updated

## [6.3.8] — 2026-03-22

### Fixed
- Upgrade search toggle (Issue #9): toggling "Search upgrades" off did not persist — the setting reverted to On after the next state refresh because no Save was triggered. Toggle now saves immediately on click, same behaviour as the Dry Run toggle.
- Upgrade toggle now shows a hint "Change is saved immediately" (DE + EN)
- Timezone UI (Issue #10): after saving a timezone change, the visible search input showed "UTC" again on next settings open — the hidden `cfg-timezone` field was synced from `fetchState` but the visible text input was not, making it look like the save had no effect (config.json was actually correct). Both fields are now synced together on every state refresh.

## [6.3.7] — 2026-03-22

### Changed
- Page switching now uses class-based visibility (`content-page` / `page-visible`) instead of inline `style.display` writes — cleaner layout state, fixes edge cases where `display:grid` was not restored correctly on some mobile browsers
- Stats page refresh check updated to match class-based visibility

### Added
- `theme-template.css` added to repo as developer documentation for adding custom themes

## [6.3.6] — 2026-03-22

### Fixed
- Mobile sidebar closes immediately after tap — four root causes fixed:
  1. `showPage()` was resetting `className` on nav-items, stripping all `addEventListener` bindings — navigation now uses `navClick()` with `onclick` attribute which survives className resets
  2. `.layout` had `z-index: 1` creating a stacking context that capped the sidebar's effective z-index — removed
  3. Sidebar `z-index` raised to 9999, overlay to 9998 — no longer cut off by other stacking contexts
  4. `backdrop-filter: blur()` on the overlay was causing the darkening effect — removed; overlay now uses plain `rgba(0,0,0,.55)`
- Sidebar navigation: `data-page` attribute used to set active state instead of index-based array lookup
- `openSidebar()` / `closeSidebar()` split into separate functions for clarity; sidebar click stops propagation to prevent accidental close

## [6.3.5] — 2026-03-22

### Fixed
- Language mixup (Issue #8): new filter labels (Sonarr/Radarr IMDb, resolution, timezone) showed in German even when English was selected — `applyLang()` now runs a bulk `data-i18n` translator on every language switch
- Placeholders ("Wie global" / "Same as global") now correctly translate on language switch
- `hint_timezone` T-dict key added to both DE and EN
- Mobile sidebar: hamburger now passes `event` to `toggleSidebar()` for proper `stopPropagation()`, prevents instant-close on some mobile browsers
- Mobile sidebar: nav-item close uses `setTimeout(150ms)` to avoid race with page navigation

## [6.3.4] — 2026-03-22

### Fixed
- Mobile sidebar closes immediately after opening — rewritten with explicit state variable, prevents event race condition
- Mobile sidebar now has slide-in animation and hamburger morphs to ✕ when open
- Activity log: timestamps now show HH:MM only instead of HH:MM:SS (cleaner on small screens)

## [6.3.3] — 2026-03-22

### Added
- Timezone: `TZ` environment variable now respected on startup — applied automatically when config is still at default UTC (fixes Issue #7)
- Timezone: settings dropdown now loads all 498 IANA timezones dynamically instead of 8 hardcoded options
- Timezone: searchable text input replaces static select — type to filter (e.g. `chicago`, `berlin`)
- Buy Me a Coffee link added to app sidebar and homepage (nav, hero, footer)

### Fixed
- CHANGELOG v6.3.2: removed incorrect line about ALLOWED_THEMES


## [6.3.2]

### Changed
- Version bump: all references updated to v6.3.2
- Code audit: 19/19 functional tests passed — all features verified

### Fixed (Issue #7)
- Timezone: `TZ` environment variable now respected on startup — if `TZ` is set and config is still at default UTC, the env var is applied automatically
- Timezone: settings dropdown now loads all available IANA timezones from the server dynamically (previously showed only 8 hardcoded options)
- Timezone: searchable input field — type any part of the timezone name (e.g. `chicago`, `america`) to filter the full list

### Verified
- Per-app IMDb and resolution filters (Sonarr/Radarr independent)
- Mobile sidebar with hamburger menu and overlay
- Version check against GitHub Releases API with Discord notification
- Discord stats enriched with missing/upgrade/cycle counts
- All 18+ API routes auth-protected
- DB WAL mode, CYCLE_LOCK, interval minutes conversion all intact

## [6.3.1]

### Added
- Settings → Filter: Separate IMDb minimum rating and upgrade target resolution for Sonarr and Radarr independently
- Mobile sidebar: hamburger menu button opens/closes sidebar on small screens with overlay
- Version check: Mediastarr queries GitHub Releases API hourly and notifies via Discord when an update is available
- Discord notifications enriched: stats report and test message now include missing/upgrade/cycle counts and online instance ratio
- Update badge in sidebar: green indicator when a new version is available on GitHub

### Security
- `_CURRENT_VERSION` constant — used for version comparison and Discord notifications

### Fixed
- Apostrophe syntax error in homepage JS (unescaped `'` in single-quoted strings)
- Old `_cmpT` translation map replaced with correct `_why` map matching actual HTML IDs

## [6.3.0]

### Added
- Settings → Filter: IMDb minimum rating — only search content with IMDb ≥ threshold (0 = off, applies to Sonarr series and Radarr movies)
- Settings → Filter: Target resolution for upgrades — skip upgrade search if current quality already meets or exceeds target (WEB-DL 720p … Bluray 2160p)
- `_parse_release_dt()` / `_is_released()` — unreleased episodes and movies are now skipped automatically
- `MEDIASTARR_PUBLIC_URL` / `MEDIASTARR_PUBLIC_PORT` env vars — startup log shows the actual externally reachable setup URL
- `MEDIASTARR_SESSION_SECURE` env var — enables Secure flag on session cookie for HTTPS deployments
- Default-password warning bar in dashboard — shown when `MEDIASTARR_PASSWORD=change-me` is still set
- Mobile history view — horizontal scroll for narrow screens

### Changed
- Search intervals changed from seconds to minutes in the UI (stored as seconds internally for backward compatibility)
- Default missing interval: 15 min → 30 min
- Default upgrade interval: 30 min → 60 min
- Minimum interval remains 15 minutes
- Dashboard overview now shows interval in minutes
- Dry Run toggle now saves immediately without requiring manual Save
- Homepage (mediastarr.de) fully rewritten with DE/EN language switcher

### Security
- Session cookies now set `HttpOnly`, `SameSite=Lax`, and optionally `Secure`
- Setup connection test validates that Sonarr/Radarr URLs resolve to private/internal hosts only (SSRF protection)
- `config.json` file permissions set to 0600 after every save
- All 18 API routes verified to have auth protection when `MEDIASTARR_PASSWORD` is set
- Setup log message uses dynamic URL instead of hardcoded `localhost:7979`

### Improved
- `db.py`: `_get_conn()` helper + `Optional` type annotations
- History clear log messages now respect UI language (DE/EN)
- README: added "Why not Huntarr or its forks" comparison section (DE + EN)
- Homepage: new "Why Mediastarr" section with security incident summary and feature comparison table


## [6.2.0]

### Added
- Settings → Filter: IMDb minimum rating — only search content with IMDb ≥ threshold (0 = off, applies to Sonarr series and Radarr movies)
- Settings → Filter: Target resolution for upgrades — skip upgrade search if current quality already meets or exceeds target (WEB-DL 720p … Bluray 2160p)
- `_parse_release_dt()` / `_is_released()` — unreleased episodes and movies are now skipped automatically
- `MEDIASTARR_PUBLIC_URL` / `MEDIASTARR_PUBLIC_PORT` env vars — startup log shows the actual externally reachable setup URL
- `MEDIASTARR_SESSION_SECURE` env var — enables Secure flag on session cookie for HTTPS deployments

### Changed
- Search intervals changed from seconds to minutes in the UI (stored as seconds internally for backward compatibility)
- Default missing interval: 15 min → 30 min
- Default upgrade interval: 30 min → 60 min
- Minimum interval: 15 minutes (unchanged)
- Dashboard overview now shows interval in minutes

### Security
- Session cookies now set `HttpOnly`, `SameSite=Lax`, and optionally `Secure`
- Setup connection test now validates that Sonarr/Radarr URLs resolve to private/internal hosts only (SSRF protection)
- `config.json` file permissions set to 0600 after every save
- Setup log message uses dynamic URL instead of hardcoded `localhost:7979`

### Improved
- Project homepage fully rewritten with DE/EN language switcher
- `db.py`: `_get_conn()` helper + `Optional` type annotations
- History clear log messages now respect UI language (DE/EN)
- All API routes verified to have auth protection when `MEDIASTARR_PASSWORD` is set
## [6.1.2]

### Fixed
- Settings → Instances tab: `ReferenceError: isDE4 is not defined` caused silent crash — list never rendered
- `isDE4` was defined in `renderInstanceCards()` (dashboard) but missing in `renderSettingsInstances()` (settings)
- Previous fix in v6.1.1 moved the re-render call outside the `fetchState` function body (dead code) — corrected

## [6.1.1]

### Fixed
- **Critical (Unraid):** Container started but hunt loop never ran under gunicorn — startup code was inside `if __name__ == "__main__"` block which gunicorn never executes. Moved to `@app.before_request` hook with thread-safe lock so it runs correctly on first request regardless of how the server is started
- Settings → Instances tab: list showed "Lade..." permanently — `isDE4` variable used in `renderSettingsInstances()` was not defined in that function scope (defined in `renderInstanceCards()` instead), causing a silent `ReferenceError`
- Settings → Instances tab: re-render hook was placed outside `fetchState()` function body (dead code)
- `showPage('settings')` never triggered instance list render — only `switchTab('instances')` did
- `switchTab('instances')` now retries render if `appState` not yet populated

## [6.1.0]

### Added
- Optional password protection via `MEDIASTARR_PASSWORD` environment variable
- Login page (`/login`) with session-based authentication
- CSRF protection for all write requests — browser fetch interceptor injects `X-CSRF-Token` header automatically
- gunicorn as production server (replaces `python app/main.py`) — multi-threaded, more stable under load
- `requirements.txt` with all dependencies (flask, requests, gunicorn)
- `MEDIASTARR_PASSWORD` variable added to Unraid template and docker-compose files

### Notes
- Password protection is fully optional — if `MEDIASTARR_PASSWORD` is not set, Mediastarr behaves identically to v6.0.x
- When password is set: dashboard, setup wizard, and all API endpoints require authentication
- CSRF protection activates automatically when password is set

## [6.0.3]

### Improved (from community fork review)
- `db.py`: `threading.Lock()` → `threading.RLock()` (prevents deadlock on recursive calls)
- `db.py`: `_require_init()` guard on all public functions (clear error instead of silent crash)
- `db.py`: SQL injection fix in `get_history` — cutoff value now passed as query parameter
- `main.py`: `CYCLE_LOCK` prevents two cycles running simultaneously (e.g. rapid Run Now clicks)
- `main.py`: `_bootstrap_host()` auto-detects container IP for Sonarr/Radarr fallback URLs
- `main.py`: Discord enabled_parts now language-aware (DE/EN) and uses filter() instead of string concat
- `main.py`: `clamp_int()` used consistently for Discord rate-limit and stats-interval validation
- `main.py`: Run Now when stopped now starts a single cycle instead of full hunt loop
- `index.html` + `setup.html`: `escHtml()` prevents XSS in instance name/URL fields
- `index.html` + `setup.html`: `defaultArrUrl()` uses browser hostname for URL suggestions
- `index.html` + `setup.html`: All UI messages (save, delete, ping, errors) fully translated DE/EN
- `setup.html`: Changing instance type auto-updates URL placeholder
- `setup.html`: Step counter corrected to "Step 1 of 4"
- `README.md`: Instance URL examples use `[IP]` instead of Docker hostnames

## [6.0.2]

### Fixed
- Setup wizard: validation error "#2 () Name: Name fehlt" when clicking Finish Setup on Discord step — client-side validation now runs before server call and shows errors directly in the visible pane
- New instances added via "+ Add instance" now default to name "Sonarr" or "Radarr" (type-dependent) instead of empty string, reducing chance of missing name
- Backend validation error messages now respect selected language (DE/EN)

## [6.0.1]

### Fixed
- Setup wizard: "Finish Setup" button stuck when skipping Discord step — error element was in wrong pane (Pane 2) causing button to stay disabled and page to not advance
- Error messages in setup wizard now display correctly in Pane 3 (Discord step)
- Button text reset now language-aware (was hardcoded German)
- Catch block now shows user-facing error message in both DE and EN

## [6.0.0]

### Added
- Multi-instance: any combination of Sonarr/Radarr, fully optional
- Custom instance names (Sonarr HD, Sonarr 4K, Anime, …) — editable in settings
- Instance management directly in settings (add/rename/delete/toggle/ping)
- Discord: 6 configurable events + periodic statistics report
- Discord: Rate-limit protection (configurable cooldown per event type)
- Discord: Discord 429 detection + logging
- Discord: Full DE/EN translations for all labels and messages
- Episode title format: `Series – Episode Title – S01E01` (TBA/TBD suppressed)
- Full i18n for all log messages (DE/EN)
- Configurable timezone — all timestamps in local time
- Sonarr search granularity: episode / season / full series
- Upgrade search global toggle
- Jitter with enforced minimum 15-minute interval
- Statistics dashboard: bar charts, 24h timeline, per-instance breakdowns
- Unraid Community Apps XML template
- `/api/discord/stats` endpoint for manual stats report trigger
- `_ep_title()` helper with graceful fallback for missing series data

### Fixed
- `? S2026E3648` log entries (missing series title from Sonarr API)
- Log messages always in configured language (DE/EN)
- Language switcher now updates sidebar, nav labels, and instance cards
- Server time displayed in configured timezone (not UTC)
- Settings instances tab no longer redirects to setup wizard

### Changed
- `docker-compose.yml` reduced to minimum (port + volume only)
- Version badge in sidebar is now colour-highlighted with GitHub link

## [5.0.0]

- Multi-instance architecture replacing fixed sonarr/radarr config slots
- Setup wizard supports unlimited instances of any type

## [4.0.0]

- SQLite replaces JSON for search history
- Cooldown in days (default 7), configurable 1–365
- Release year stored in DB
- 3 themes: Dark / Light / OLED Black
- Migration path for existing databases
