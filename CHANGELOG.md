# Changelog

## [v7.0.3] — 2026-03-26

### Fixed
- **Bug #33 — Upgrade search not working even when globally enabled** — `hunt_sonarr_instance()` and `hunt_radarr_instance()` read only `inst.get("search_upgrades", False)` — the per-instance toggle. The global `CONFIG["search_upgrades"]` toggle was saved but never consulted by the hunt functions. Per-instance default is `False`, so upgrades never ran even with the global switch enabled. Fix: `do_upgrades = CONFIG.get("search_upgrades", True) and inst.get("search_upgrades", False)` — global is master switch, per-instance is fine-grained control
- **Bug #34 — Per-instance Search Upgrades toggle not saved** — `PATCH /api/instances/<id>` had no `search_upgrades` branch. `toggleInstUpgrades()` sent the PATCH correctly but the backend silently ignored the field. Fix: added `if "search_upgrades" in d: inst["search_upgrades"] = bool(d["search_upgrades"])` to the PATCH handler
- **Bug #35 — Discord notifications toggle reverting on save** — clicking Save in any settings tab called `saveConfig()` → `fetchState()` → `updateUI()` re-synced `dcStates` from the server, overwriting local discord toggle changes that hadn't been saved yet via the Discord tab. Fix: `saveConfig()` now always includes current `dcStates` in the request body so discord state is persisted atomically with any settings save
- **Settings reverting on 4-second poll** — `fetchState()` runs every 4 seconds and `updateUI()` overwrote all config input fields on every poll tick. Any field the user edited but hadn't yet saved was overwritten seconds later. Fix: added `_configDirty` flag — set `true` on any `input`/`change` event inside `#page-settings`, cleared to `false` after a successful `saveConfig()`. While dirty, `updateUI()` skips the config sync block entirely
- **`dcStates.stats` was undefined** — `dcStates` was initialized without the `stats` key. Every `saveConfig()` sent `notify_stats: undefined` → backend received `null` → `bool(null) = False` → Discord stats notifications silently disabled on every general save. Fix: `dcStates` now initialized with `stats: false`
- **10 settings fields not synced back to DOM** — `updateUI()` never wrote these fields back after `fetchState()`: `jitter_max`, `request_timeout`, `imdb_min_rating`, `upgrade_target_resolution`, `sonarr_imdb_min_rating`, `sonarr_search_mode`, `sonarr_upgrade_target_resolution`, `radarr_imdb_min_rating`, `radarr_upgrade_target_resolution`, `timezone`. All now synced via additional `syncField()` calls in `updateUI()`
- **Log settings excluded from general save** — `log_min_level`, `log_max_mb`, `log_backups` were only saved via their own dedicated buttons; now included in every `saveConfig()` call so all settings save atomically from any tab
- **Sonarr/Radarr IMDb override `null` not cleared** — when IMDb override was unset (`null` = use global), the input field was left showing the last value instead of clearing to empty. Fix: always sync, `null` → `''`
- **Season/Series mode duplicate searches** — in `season` or `series` mode, `wanted/missing` returns individual episodes. Previously each episode triggered its own `SeasonSearch` or `SeriesSearch` — identical commands fired multiple times for the same target. Fix: dedup sets `_searched_seasons` and `_searched_series` track already-triggered targets per cycle and skip redundant commands
- **Upgrades ignored search mode** — the upgrade loop always used `EpisodeSearch` regardless of the configured Sonarr search mode. Fix: upgrade loop now applies the same `season`/`series`/`episode` logic as the missing search loop

### Changed
- **API page size increased from 500 → 2000** — `wanted/missing` and `wanted/cutoff` now request up to 2000 records per call so large libraries are fully covered

## [v7.0.2] — 2026-03-26

### Fixed
- **Skip items don't consume search slots** — Root cause found and fixed: `should_search()` returned reason `"daily_limit"` but the stats dict key is `"skipped_daily"`. This caused a `KeyError` on every daily-limit hit, which was silently swallowed by the `except` block — making the `return` (stop-instance) unreachable and stats tracking broken.
  - `should_search` now returns reason `"daily"` to match the `skipped_daily` stats key
  - `stats[f"skipped_{reason}"] += 1` now correctly increments `skipped_cooldown` or `skipped_daily`
  - Cooldown skips have always used `continue` (correct — next item tried) — no change
  - Daily-limit hits correctly stop the instance loop via `return` (limit is genuinely reached)

## [v7.0.1] — 2026-03-26

### Fixed
- **Missing EN translations** — Sonarr/Radarr behavior section headers, instance headings, "Same as global" option, all previously untranslated
- **Log level dropdown** — all 4 options now translated DE/EN via i18n keys
- **Jitter** — changed from seconds to minutes in UI (min 0, max 60); stored as seconds internally; backend converts on save; hint text updated

### Added
- **Per-type global daily limit** — Sonarr and Radarr each get their own global searches/day cap (0 = unlimited); configured in Settings → Sonarr/Radarr tabs; applies across ALL instances of that type; per-instance limits apply additionally
- **Upgrade toggle hint** — instance card now shows "(global limit ignored)" note next to the per-instance upgrade toggle to clarify that when enabled, only the instance-level daily limit applies (not the global daily limit)

## [v7.0.0] — 2026-03-26

### Added
- **Structured Logging System** — replaces ad-hoc `logger.*` calls with a unified `ms_log()` architecture:
  - Central `ms_log(level, service, action, item)` function — writes to Docker console, rotating log file, AND the UI activity log simultaneously
  - Convenience helpers: `ms_debug()`, `ms_info()`, `ms_warn()`, `ms_error()`
  - Four levels: `DEBUG` | `INFO` | `WARN` | `ERROR` (replaces the previous implicit INFO-only behaviour)
  - `log_min_level` config key — persisted to `config.json`, applied via `_apply_log_level()` at startup and on every config save
  - Docker/Unraid console output format: `2026-03-26 14:32:10,123 [INFO] [Sonarr] Missing searched: Breaking Bad S01E03`
  - Settings → General → Log Level dropdown — four options, saves to backend and syncs frontend immediately
- **MSLog v2 (frontend)** — complete rewrite of the browser console logger:
  - Timestamp format: `[2026-03-26 14:32:10] [INFO] message`
  - `MSLog.log(level, ...args)` central function
  - Helpers: `MSLog.debug()`, `MSLog.info()`, `MSLog.warn()`, `MSLog.error()`
  - `MSLog.setLevel('WARN')` — suppress below threshold; persisted via `sessionStorage`
  - `MSLog.getLevel()` — returns current level string
  - `trace()` kept as backwards-compatible alias for `debug()`
  - Level synced from server config on every `fetchState()` poll


## [v6.4.6] — 2026-03-26

### Fixed
- **Bug #29** — Startup log showed `Mediastarr v6.3.8 started` instead of current version; now uses `_CURRENT_VERSION` dynamically in both DE and EN messages, and in the Discord stats embed version field
- **Bug #21 / #28** — Console showed no entries (both standalone page and Settings-tab version): refactored `_appendConsoleLogs` to write to both `#console-output` and `#console-output-s` simultaneously via `_makeConsoleLine()` helper; `filterConsole()` and `clearConsole()` updated to cover both outputs
- **Bug #27** — Help page German translation broken: `setHelpLang()` now correctly toggles `.help-en`/`.help-de` visibility; `&amp;` entity in `help_title` i18n key replaced with literal `&`
- **Bug #23** — Homepage mobile view: language selector (`🇬🇧 / 🇩🇪`) not visible on small screens; added persistent `#mobile-lang-toggle` (fixed bottom-right, visible only on `max-width:768px`); `setLang()` now syncs both desktop and mobile buttons

### Added
- **Feature #32 — Upgrade toggle per instance**: each Sonarr/Radarr instance now has an independent `search_upgrades` toggle (default: **off**); toggle rendered in instance card in Settings → Sonarr/Radarr tabs; saved via `PATCH /api/instances/<id>`
- **Feature #26 — Improved logging**: `run_now` control action logs "Run now triggered" to activity log; `POST /api/config` saves log "Config saved" to activity log
- **Milestones updated**: v6.4.5 and v6.4.6 added to completed milestones in both DE and EN

### Changed
- `search_upgrades` is now a **per-instance** setting (default `false`) instead of a global config toggle

- ## [v6.4.5] — 2026-03-26

### Added
- **Central `VERSION` file** — single source of truth for the version string; all components read from it automatically:
  - `app/main.py`: reads `VERSION` file at startup via `_VERSION_FILE.read_text().strip()`; fallback to hardcoded string if file missing
  - `app/main.py`: Discord footer (`"Mediastarr " + _CURRENT_VERSION`) — always in sync with no manual change required
  - `templates/index.html`: sidebar version spans and MSLog init receive `{{ version }}` from Flask `render_template()` call
  - `Dockerfile`: `COPY VERSION ./` ensures the file is available inside the container
  - `index.html` (homepage): version bumped in fallback, preview sidebar, screenshots label, section labels
  - `mediastarr.xml` (Unraid template): version bumped
- **Version bumped to v6.4.5** — covers: Help page (❓ Hilfe sidebar nav), Console in Settings tab, Huntarr/fork comparison with exact security incident wording + curl exploit example + researcher quote (DE + EN), Milestones/Roadmap (DE + EN), full Changelog since v1.0.0 in Help tab, homepage badge fix

### Changed
- **Help tab `🔓 Why not Huntarr?`** — rewritten with exact wording from README:
  - Disclaimer: *"Independent project, built from scratch. Not affiliated with Huntarr."*
  - Security incident: February 2026, 21 vulnerabilities (7 critical, 6 high)
  - `curl` exploit example showing unauthenticated API key dump (EN + DE commented)
  - Researcher quote: *"Fixing 21 specific findings doesn't fix the process that created them."*
  - Link to full audit: [github.com/rfsbraz/huntarr-security-review](https://github.com/rfsbraz/huntarr-security-review)
  - Full DE translation of all above

### Developer notes
To release a new version in future: **edit `VERSION` only** — everything else updates automatically on next build/start.

## [v6.4.4] — 2026-03-25

### Added
- **Scheduled maintenance windows**: new section in General settings; up to 10 time windows (HH:MM → HH:MM, local time); overnight windows supported (e.g. 22:00–06:00); search pauses automatically while inside a window with a 60s re-check loop; yellow `⏸ Wartungsfenster aktiv` banner in topbar while active; saves instantly via `/api/config`; exposed in `/api/state` as `maintenance_windows` + `in_maintenance_window`
- **Series Discord webhooks fixed**:
  - Full series object now fetched once per hunt cycle and stored in `series_full` cache (keyed by series ID); injected into every episode dict via `enrich_ep_with_series()` before calling `discord_send()`
  - Poster + fanart now correctly populated from the full series object (was empty when Sonarr omitted images in `wanted/missing` response)
  - Multi-source ratings for Sonarr: now tries nested `ratings.imdb.value` / `ratings.tmdb.value` (Sonarr v4+ format) before falling back to flat `ratings.value`
  - TheTVDB / IMDb / TMDB links: already present in code — now correctly populated because `series_obj.imdbId`, `tvdbId`, `tmdbId` are available from the full series object

## [v6.4.3] — 2026-03-25

### Fixed
- **Bug #22** — Stats-Tabs ignorierten Theme: `<button>`-Elemente erbten Browser-Standardstile; `background:none;border:none` ergänzt
- **Bug #21** — Console zeigte keine Einträge: `_feedConsole` wurde nach jedem `fetchState()` mit `appState` statt einem ungültigen Param aufgerufen; Feldnamen korrigiert (`action`/`item` statt `message`/`source`)
- **Bug #24** — Einstellungsseite nicht volle Breite: `#page-settings.content { grid-template-columns: 1fr; }` ergänzt
- **Bug #23** — Homepage-Version zeigte `v6.3.8`: Hardcoded-Fallback auf `v6.4.3`, GitHub-Release-API beim Laden abgefragt
- **Import pathlib** fehlte — `_setup_file_logging` nutzte `pathlib.Path` in Typ-Annotation, Modul aber nicht importiert → Crash beim Start

### Added
- **Bug #20 — Config-Migration**: `_migrate_config()` läuft bei jedem Start; ergänzt fehlende Keys aus `DEFAULT_CONFIG` (inkl. `discord.*` und Instanz-Defaults) ohne bestehende Werte zu löschen
- **Feature #25 — Upcoming überspringen**: Sonarr-Episoden (`airDateUtc`) und Radarr-Filme (`digitalRelease` / `physicalRelease` / `inCinemas`) mit Zukunftsdatum werden immer automatisch übersprungen — kein Toggle, immer aktiv
- **Konfigurierbares Log-Rotation**: Einstellungen in General-Tab — Max. Dateigröße (1–100 MB, Standard 5 MB), Backup-Anzahl (0–10, Standard 2); `POST /api/log/rotate` und `GET /api/log/status` API-Endpunkte; "🔄 Rotieren" und "📋 Status"-Buttons mit Inline-Ergebnis
- **Persistente Log-Datei**: `/data/logs/mediastarr.log` mit `RotatingFileHandler` — keine neuen Abhängigkeiten
- **Unit-Tests**: 14 Assertions für `_ep_is_released`, `_movie_is_released` und `RotatingFileHandler` — alle bestanden

---

## [v6.4.2] — 2026-03-25

### Fixed
- **Bug #19** — Verlaufstitel abgeschnitten: `max-width: 280px` aus `.hist-title` entfernt
- **Bug #17** — Discord-Embed ohne Serientitel: Embed-Titel enthielt nur Icon+Label, nie den eigentlichen Inhaltsnamen; jetzt: `"Breaking Bad S01E03 — 🔍 Fehlend gesucht"`

### Added
- **Statistiken — Sonarr / Radarr Tabs**: Filter-Tabs "Alle / 📺 Sonarr / 🎬 Radarr" auf der Statistikseite
- **Live Log Console**: Neue Seite (`🖥 Console`) mit Echtzeit-Aktivitätslog, Level-Filter, Textsuche, Auto-Scroll, Fehler-Badge
- **Homepage Version-Badge**: Zeigt aktuelle Version; holt beim Laden die echte Version von der GitHub-Releases-API

---

## [v6.4.1] — 2026-03-24

### Fixed
- Doppeltes `dcToggleUrl()` → zweites korrekt als `toggleDc(key)` benannt
- Fehlende `togglePublicApi()` und `importConfig()` Funktionen ergänzt
- Fehlende i18n-Keys (`lbl_backup`, `btn_export`, `btn_import`, `lbl_public_api`) in T-Dict (DE + EN)
- `public_api_state` nicht in `updateUI()` synchronisiert → gefixt
- `saveInst()` ohne `daily_limit`-Feld → gefixt
- Sidebar-Version war defektes HTML (`<span ...">` ohne `>`) → repariert

### Added
- **Pro-Instanz Tageslimit**: Jede Instanz kann ein eigenes `daily_limit` haben (0 = unbegrenzt); Mini-Fortschrittsbalken in der Instanzkarte
- **Config Export / Import**: `GET /api/config/export` → JSON-Download mit Zeitstempel; `POST /api/config/import` → Upload mit Validierung (Typ-Whitelist, 512 KB Cap), Seite lädt automatisch neu
- **Öffentlicher API-State**: `public_api_state`-Toggle; `/api/state` ohne Login erreichbar wenn aktiv (API-Keys immer entfernt)
- **Neues Icon**: Helles SVG-Radar-Icon (weiß-oranger Kern, Glow-Ringe, Kreuz-Ticks); `favicon.ico` (32×32) in allen Templates
- **Discord-Icon**: URL von `raw.githubusercontent` (404 vor Push) auf `https://mediastarr.de/static/icon.png`
- **GitHub ISSUE_TEMPLATE**: `bug_report.yml`, `feature_request.yml`, `config.yml`; Blank-Issues deaktiviert

---

## [v6.4.0] — 2026-03-24

### Fixed
- Doppelter Key `upgrade_target_resolution` in JS `saveConfig()` — zweiter Wert überschrieb ersten stumm
- `save_config()` ohne Lock → Race-Condition zwischen Hunt-Thread und API; `_cfg_lock` ergänzt
- 6× bare `except:` → `except Exception:` geändert
- `float(last)` konnte bei `None`/korruptem Config-Wert abstürzen → `float(last or 0)`

### Added
- **Discord Rich Embeds**: Poster (Thumbnail) + Fanart/Backdrop (`image`), IMDb/TVDB/TMDB-Links als Buttons, Multi-Source-Ratings (IMDb + TMDB + RT mit Votecount), Genre, Laufzeit, Status, aktuelle Qualität (bei Upgrades)
- **Bot-Avatar**: `avatar_url` + `username` in jedem Webhook-Payload; Author-Zeile zeigt Instanzname + Service mit eigenem Icon
- **Statistiken**: Fortschrittsbalken `████████░░` im Tageslimit-Embed; Pro-Instanz-Tabelle im Stats-Embed
- **Community-Dateien**: `SECURITY.md`, `CONTRIBUTING.md`, `PULL_REQUEST_TEMPLATE.md`, `CODE_OF_CONDUCT.md`
- **Screenshots**: 8× `_de.png` + 8× `_en.png`; Flipchart wechselt Bild automatisch nach UI-Sprache
- **Mobil-Fixes**: Dashboard 480px-Breakpoint; Homepage Hamburger-Nav (☰/✕), fc-Tabs horizontal scrollbar, Vergleichstabelle `overflow-x:auto`
- **Pro-Instanz `today_count`** in `/api/state` für Limit-Fortschrittsbalken in Instanzkarten
