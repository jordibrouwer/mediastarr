# Changelog

## [v6.4.3] — 2026-03-25

### Changed
- **`skip_upcoming` hardwired to `True`** — upcoming/unreleased content is always filtered; the toggle has been removed from the UI and DEFAULT_CONFIG; both Sonarr (by `airDateUtc`) and Radarr (by `digitalRelease` / `physicalRelease` / `inCinemas`) filter unreleased items before every run; skipped count logged at INFO level

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

