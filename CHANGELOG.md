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
