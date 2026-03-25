<div align="center">

<img src="https://raw.githubusercontent.com/kroeberd/mediastarr/main/static/icon.png" width="128" alt="Mediastarr Logo"/>

# Mediastarr

**EN** · [DE](#de)

[![Website](https://img.shields.io/badge/Website-mediastarr.de-ff6b2b?logo=googlechrome&logoColor=white)](https://mediastarr.de/)
[![Docker Hub](https://img.shields.io/docker/pulls/kroeberd/mediastarr?label=Docker%20Pulls&logo=docker&logoColor=white)](https://hub.docker.com/r/kroeberd/mediastarr)
[![GitHub Release](https://img.shields.io/github/v/release/kroeberd/mediastarr?color=ff6b2b&label=Version)](https://github.com/kroeberd/mediastarr/releases)
[![License](https://img.shields.io/badge/License-MIT-3de68b)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-Join-5865f2?logo=discord&logoColor=white)](https://discord.gg/8Vb9cj4ksv)

</div>

---

<!-- ENGLISH -->
<a name="en"></a>

**Automated missing-content and quality-upgrade search for Sonarr & Radarr.**  
Runs on a configurable schedule, keeps a SQLite history, sends rich Discord embeds, and has a first-run browser wizard. No config file editing required.

> **Independent project.** Not affiliated with Sonarr, Radarr, or Huntarr.

---

## ✨ Features

| Feature | Details |
|---|---|
| 📺 Multiple Sonarr instances | Missing + Upgrades · Episode / Season / Series mode |
| 🎬 Multiple Radarr instances | Missing + Upgrades |
| 🏷️ Custom names | Sonarr 4K, Anime, Radarr HD — each with its own card |
| 🧙 First-run wizard | Browser-based, no config file editing |
| 🗄️ SQLite history | Title, year, type, result, search count, timestamps |
| ⏳ Cooldown | 1–365 days, resets automatically |
| 📊 Daily limit | Max searches/day (0 = unlimited) |
| 🎲 Random selection | Items picked randomly per cycle for even coverage |
| ⭐ IMDb filter | Min. rating — global or per Sonarr/Radarr tab |
| 🎯 Target resolution | Only upgrade below your quality target |
| ⏱ Jitter | Random ±N sec offset per cycle |
| 🔔 Discord | Rich embeds: poster + fanart, IMDb/TVDB/TMDB links, ratings, genres, runtime |
| 📊 Stats report | Periodic Discord embed with progress bar + per-instance table |
| 🌐 Multilingual | German & English (UI, logs, Discord messages) |
| 🎨 4 themes | Dark / Light / OLED / System |
| 🕐 Timezone | IANA timezone picker, respects `TZ` env var |
| 🔒 Security | CSRF protection, optional password, brute-force lockout, `config.json` set 0600 |
| 🖥 MSLog | Browser console logger: TRACE/DEBUG/INFO/WARN/ERROR with timestamps |
| 📅 Per-instance daily limit | Each instance can have its own search limit per day |
| 💾 Config backup | Export / import full config as JSON (incl. API keys) |
| 🔓 Public API mode | `/api/state` optionally accessible without login — for external tools |

---

## 🚀 Quick Start

```bash
docker run -d \
  --name mediastarr \
  --restart unless-stopped \
  -p 7979:7979 \
  -v /your/appdata/mediastarr:/data \
  -e TZ=Europe/Berlin \
  kroeberd/mediastarr:latest
```

Open **http://your-server:7979** — the setup wizard starts automatically.

## 🐳 Docker Compose

```yaml
services:
  mediastarr:
    image: kroeberd/mediastarr:latest
    container_name: mediastarr
    restart: unless-stopped
    ports:
      - "7979:7979"
    volumes:
      - /your/appdata/mediastarr:/data
    environment:
      - TZ=Europe/Berlin
      # - MEDIASTARR_PASSWORD=change-me   # optional
```

## 📦 Unraid

Install via **Community Apps** — search for `Mediastarr`.  
Or use the template: [`mediastarr.xml`](mediastarr.xml)

## ⚙️ Environment Variables

| Variable | Default | Description |
|---|---|---|
| `TZ` | `UTC` | IANA timezone, e.g. `Europe/Berlin` |
| `MEDIASTARR_PASSWORD` | *(empty)* | Dashboard + API password. Leave empty for open access. |
| `SONARR_URL` | *(empty)* | Pre-fill Sonarr URL (skips wizard for this instance) |
| `SONARR_API_KEY` | *(empty)* | Pre-fill Sonarr API key (requires `SONARR_URL`) |
| `RADARR_URL` | *(empty)* | Pre-fill Radarr URL |
| `RADARR_API_KEY` | *(empty)* | Pre-fill Radarr API key (requires `RADARR_URL`) |

## 🔔 Discord Notifications

Settings → **Discord** tab:

1. In Discord: Right-click channel → **Edit Channel** → Integrations → Webhooks → **New Webhook**
2. Copy the URL (`https://discord.com/api/webhooks/ID/TOKEN`)
3. Paste into Mediastarr → **Save** → **Send test**

**6 event types** — each with a message preview in the UI:

| Event | Embed | Colour |
|---|---|---|
| 🔍 Missing searched | Poster + fanart, links, rating, genre, runtime, status | 🟢 Green |
| ⬆️ Upgrade searched | Same as missing + current quality field | 🟡 Yellow |
| ⏳ Cooldown expired | Item count, next run, cooldown setting | 🔵 Blue |
| 🚫 Daily limit reached | Progress bar `████████░░`, reset time | 🔴 Red |
| 📡 Instance offline | Error message, URL, service type | ⚫ Grey |
| 📊 Statistics report | Progress bar, KPIs, per-instance table | 🟠 Orange |

## 🛡️ Security

- Optional password via `MEDIASTARR_PASSWORD` env var
- CSRF token on all state-mutating requests
- Brute-force protection: 10 failed logins → 5 min IP lockout
- API keys never returned in `/api/state` responses
- SSRF protection on all URL inputs
- `config.json` chmod 0600 on every save
- Security headers: `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, CSP

## 📸 Screenshots

| Dashboard | Settings | Discord |
|:---:|:---:|:---:|
| ![Dashboard](static/screen_dashboard_en.png) | ![Settings](static/screen_settings_en.png) | ![Discord](static/screen_discord_en.png) |

| History | DC Notifications | Console Logger |
|:---:|:---:|:---:|
| ![History](static/screen_history_en.png) | ![Notify](static/screen_notify_missing_en.png) | ![Console](static/screen_console_en.png) |

## 🗺️ Roadmap / Ideas

- [x] Per-instance daily limits *(v6.4.1)*
- [x] Export/import config *(v6.4.1)*
- [x] Read-only API mode (no auth required for `/api/state`) *(v6.4.1)*
- [x] Skip upcoming/unreleased content *(v6.4.3)*
- [ ] Webhook endpoint to trigger cycle from external automation
- [ ] Push via Gotify / Apprise (alternative to Discord)
- [ ] Scheduled maintenance windows (pause during certain hours)

---

<!-- DEUTSCH -->
<a name="de"></a>

---

<div align="center">

**DE** · [EN](#en)

</div>

---

**Automatische Suche nach fehlenden Inhalten und Qualitäts-Upgrades für Sonarr & Radarr.**  
Läuft nach einem konfigurierbaren Zeitplan, führt eine SQLite-Historie, sendet reiche Discord-Embeds und hat einen Browser-Einrichtungsassistenten. Kein Bearbeiten von Config-Dateien erforderlich.

> **Eigenständiges Projekt.** Nicht mit Sonarr, Radarr oder Huntarr verbunden.

---

## ✨ Features

| Feature | Details |
|---|---|
| 📺 Mehrere Sonarr-Instanzen | Fehlend + Upgrades · Modus: Episode / Staffel / Serie |
| 🎬 Mehrere Radarr-Instanzen | Fehlend + Upgrades |
| 🏷️ Eigene Namen | Sonarr 4K, Anime, Radarr HD — jede mit eigener Karte |
| 🧙 Erster-Start-Assistent | Browser-basiert, keine Config-Datei nötig |
| 🗄️ SQLite-Historie | Titel, Jahr, Typ, Ergebnis, Suchanzahl, Zeitstempel |
| ⏳ Cooldown | 1–365 Tage, automatisches Zurücksetzen |
| 📊 Tageslimit | Max. Suchen/Tag (0 = unbegrenzt) |
| 🎲 Zufällige Auswahl | Items zufällig gewählt für gleichmäßige Abdeckung |
| ⭐ IMDb-Filter | Mindestbewertung — global oder pro Sonarr/Radarr-Tab |
| 🎯 Zielauflösung | Nur upgraden wenn unter der Zielqualität |
| ⏱ Jitter | Zufälliger ±N-Sek-Offset pro Zyklus |
| 🔔 Discord | Reiche Embeds: Poster + Fanart, IMDb/TVDB/TMDB-Links, Bewertungen, Genre, Laufzeit |
| 📊 Statistik-Bericht | Periodisches Discord-Embed mit Fortschrittsbalken + Instanz-Tabelle |
| 🌐 Mehrsprachig | Deutsch & Englisch (UI, Logs, Discord-Nachrichten) |
| 🎨 4 Themes | Dark / Light / OLED / System |
| 🕐 Zeitzone | IANA-Zeitzonenwahl, respektiert `TZ`-Umgebungsvariable |
| 🔒 Sicherheit | CSRF-Schutz, optionales Passwort, Brute-Force-Lockout, `config.json` 0600 |
| 🖥 MSLog | Browser-Konsolen-Logger: TRACE/DEBUG/INFO/WARN/ERROR |
| 📅 Pro-Instanz Tageslimit | Jede Instanz kann ihr eigenes Tageslimit haben |
| 💾 Config-Backup | Export / Import der gesamten Konfiguration als JSON (inkl. API-Keys) |
| 🔓 Öffentlicher API-Modus | `/api/state` optional ohne Login erreichbar — für externe Tools |

---

## 🚀 Schnellstart

```bash
docker run -d \
  --name mediastarr \
  --restart unless-stopped \
  -p 7979:7979 \
  -v /dein/appdata/mediastarr:/data \
  -e TZ=Europe/Berlin \
  kroeberd/mediastarr:latest
```

Öffne **http://dein-server:7979** — der Setup-Assistent startet automatisch.

## 🐳 Docker Compose

```yaml
services:
  mediastarr:
    image: kroeberd/mediastarr:latest
    container_name: mediastarr
    restart: unless-stopped
    ports:
      - "7979:7979"
    volumes:
      - /dein/appdata/mediastarr:/data
    environment:
      - TZ=Europe/Berlin
      # - MEDIASTARR_PASSWORD=change-me   # optional
```

## 📦 Unraid

Installation über **Community Apps** — nach `Mediastarr` suchen.  
Oder Template verwenden: [`mediastarr.xml`](mediastarr.xml)

## ⚙️ Umgebungsvariablen

| Variable | Standard | Beschreibung |
|---|---|---|
| `TZ` | `UTC` | IANA-Zeitzone, z.B. `Europe/Berlin` |
| `MEDIASTARR_PASSWORD` | *(leer)* | Dashboard + API-Passwort. Leer lassen für offenen Zugang. |
| `SONARR_URL` | *(leer)* | Sonarr-URL vorausfüllen (überspringt Wizard für diese Instanz) |
| `SONARR_API_KEY` | *(leer)* | Sonarr-API-Key vorausfüllen (benötigt `SONARR_URL`) |
| `RADARR_URL` | *(leer)* | Radarr-URL vorausfüllen |
| `RADARR_API_KEY` | *(leer)* | Radarr-API-Key vorausfüllen (benötigt `RADARR_URL`) |

## 🛡️ Sicherheit

- Optionales Passwort über `MEDIASTARR_PASSWORD`
- CSRF-Token bei allen zustandsändernden Requests
- Brute-Force-Schutz: 10 Fehlversuche → 5 Min. IP-Lockout
- API-Keys nie in `/api/state`-Antworten enthalten
- SSRF-Schutz auf allen URL-Eingaben
- `config.json` chmod 0600 bei jedem Speichern
- Sicherheits-Header: `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, CSP

## 🗺️ Roadmap / Ideen

- [x] Pro-Instanz Tageslimits *(v6.4.1)*
- [x] Konfiguration exportieren/importieren *(v6.4.1)*
- [x] Read-only-API-Modus (kein Auth für `/api/state`) *(v6.4.1)*
- [x] Upcoming/unveröffentlichte Inhalte überspringen *(v6.4.3)*
- [ ] Webhook-Endpunkt zum Auslösen eines Zyklus von externer Automatisierung
- [ ] Push via Gotify / Apprise (Alternative zu Discord)
- [ ] Wartungsfenster (Pause zu bestimmten Uhrzeiten)

## 📸 Screenshots

| Dashboard | Einstellungen | Discord |
|:---:|:---:|:---:|
| ![Dashboard](static/screen_dashboard_de.png) | ![Einstellungen](static/screen_settings_de.png) | ![Discord](static/screen_discord_de.png) |

| Verlauf | DC Benachrichtigungen | Console Logger |
|:---:|:---:|:---:|
| ![Verlauf](static/screen_history_de.png) | ![Benachrichtigungen](static/screen_notify_missing_de.png) | ![Console](static/screen_console_de.png) |

---

## 🤝 Contributing & Community

- **Contributing:** See [CONTRIBUTING.md](.github/CONTRIBUTING.md)
- **Security:** Report vulnerabilities via [SECURITY.md](.github/SECURITY.md) — please **do not** use public issues
- **Discord:** [discord.gg/8Vb9cj4ksv](https://discord.gg/8Vb9cj4ksv) for questions and support
- **Issues:** [Bug reports](.github/ISSUE_TEMPLATE/bug_report.yml) and [feature requests](.github/ISSUE_TEMPLATE/feature_request.yml) via GitHub

<div align="center">

Made with ❤️ · [mediastarr.de](https://mediastarr.de) · [Discord](https://discord.gg/8Vb9cj4ksv) · [Buy Me a Coffee](https://buymeacoffee.com/kroeberd)

</div>
