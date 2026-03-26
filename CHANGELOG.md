# Changelog

## [v6.4.6] — 2026-03-26

### Fixed
- **Bug #29** — Startup log showed `Mediastarr v6.3.8 started` instead of current version; now uses `_CURRENT_VERSION` dynamically in both DE and EN messages, and in the Discord stats embed version field
- **Bug #21 / #28** — Console showed no entries (both standalone page and Settings-tab version): refactored `_appendConsoleLogs` to write to both `#console-output` and `#console-output-s` simultaneously via `_makeConsoleLine()` helper; `filterConsole()` and `clearConsole()` updated to cover both outputs
- **Bug #27** — Help page German translation broken: `setHelpLang()` now correctly toggles `.help-en`/`.help-de` visibility; `&amp;` entity in `help_title` i18n key replaced with literal `&`
- **Bug #23** — Homepage mobile view: language selector (`🇬🇧 / 🇩🇪`) not visible on small screens; added persistent `#mobile-lang-toggle` (fixed bottom-right, visible only on `max-width:768px`); `setLang()` now syncs both desktop and mobile buttons

### Added
- **Feature #32 — Upgrade toggle per instance**: each Sonarr/Radarr instance now has an independent `search_upgrades` toggle (default: **off**); toggle rendered in instance card in Settings → Sonarr/Radarr tabs; saved via `PATCH /api/instances/<id>`; `hunt_sonarr_instance()` and `hunt_radarr_instance()` read from `inst.search_upgrades` instead of global config; exposed in `/api/state` instances list; `_migrate_config()` adds `search_upgrades: false` to all existing instances
- **Feature #26 — Improved logging**: `run_now` control action logs `"Run now triggered"` to activity log; `POST /api/config` saves log `"Config saved"` (DE: `"Config gespeichert"`) to activity log; i18n key `"trigger"` added to both DE and EN message tables
- **Help page restructured into 6 tabs** (order: How it works · Milestones & Roadmap · Security & Warnings · API Reference · Changelog · Why not Huntarr?); `switchHelpTab(id)` function added; tab buttons use same `.tab-btn` / `.tab-pane` system as Settings tabs; language toggle preserved
- **Milestones updated**: v6.4.5 and v6.4.6 added to completed milestones in both DE and EN

### Changed
- `search_upgrades` is now a **per-instance** setting (default `false`) instead of a global config toggle; global `search_upgrades` key removed from active use (migration preserves existing instances)

## [v6.4.5] — 2026-03-26

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

