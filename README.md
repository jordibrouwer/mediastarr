# 🎯 Mediastarr

**Automated media search for Sonarr & Radarr** — hunts missing episodes/movies and quality upgrades on a configurable schedule. Features a modern web dashboard, first-run setup wizard, SQLite search history, and Dark / Light / OLED themes.

> **⚠️ Disclaimer:** Mediastarr is a completely independent project, built from scratch.  
> It is **not affiliated with, derived from, or based on [Huntarr](https://github.com/plexguide/Huntarr.io)** in any way.  
> The concept of periodically searching \*arr applications for missing content is a common use case, but this codebase shares no code, logic, or assets with any other project.

![License](https://img.shields.io/badge/license-MIT-orange) ![Docker](https://img.shields.io/badge/docker-ready-blue) ![Platform](https://img.shields.io/badge/platform-unraid%20%7C%20linux-lightgrey)

---

## ✨ Features

- 📺 **Sonarr** — search for missing episodes & quality upgrades
- 🎬 **Radarr** — search for missing movies & quality upgrades
- 🖥️ **Web Dashboard** — live stats, activity log, service status
- 🧙 **First-Run Wizard** — browser-based setup on first start, no config editing required
- 🗄️ **SQLite History** — stores every search with title, count, timestamps, and result
- ⏳ **Cooldown (days)** — configurable 1–365 days before re-searching an item
- 📊 **Daily Limit** — cap total daily searches (0 = unlimited)
- 🌐 **Multilingual** — German & English, switchable in the UI
- 🎨 **3 Themes** — Dark, Light, OLED Black
- 🧪 **Dry Run** — simulate without triggering real searches
- ⚡ **Manual trigger** — run a cycle instantly
- 🔒 **Hardened API** — input validation, whitelists, no key exposure, security headers

---

## 🗄️ SQLite Database

All search history is stored in `/data/mediastarr.db`. For each item searched, the DB records:

| Column | Description |
|---|---|
| `service` | `sonarr` or `radarr` |
| `item_type` | `episode`, `episode_upgrade`, `movie`, `movie_upgrade` |
| `item_id` | Internal arr ID |
| `title` | Human-readable title |
| `searched_at` | UTC timestamp of last search |
| `result` | `triggered`, `dry_run`, `skipped_cooldown`, `skipped_daily` |
| `search_count` | How many times this item has been searched |
| `last_changed_at` | Last modification timestamp from arr (if available) |

Items are automatically **pruned** from the DB when their cooldown expires — they become searchable again.

---

## 🚀 Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/mediastarr.git
cd mediastarr
mkdir data
docker compose up -d
open http://localhost:7979
```

The setup wizard opens automatically and guides you through Sonarr & Radarr configuration.

---

## 🔑 Finding API Keys

In Sonarr / Radarr: **Settings → General → Security → API Key**

---

## 🐳 Docker Run

```bash
docker run -d \
  --name mediastarr \
  --restart unless-stopped \
  -p 7979:7979 \
  -v /mnt/user/appdata/mediastarr:/data \
  --network arr-network \
  ghcr.io/YOUR_USERNAME/mediastarr:latest
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SONARR_API_KEY` | — | Skips wizard if both keys are set |
| `SONARR_URL` | `http://sonarr:8989` | Sonarr address |
| `RADARR_API_KEY` | — | Radarr API key |
| `RADARR_URL` | `http://radarr:7878` | Radarr address |
| `HUNT_MISSING_DELAY` | `900` | Seconds between missing searches |
| `HUNT_UPGRADE_DELAY` | `1800` | Seconds between upgrade searches |
| `MAX_SEARCHES_PER_RUN` | `10` | Max items per cycle per service |
| `DAILY_LIMIT` | `20` | Max searches per day (0 = unlimited) |
| `COOLDOWN_DAYS` | `7` | Days before re-searching an item |
| `DRY_RUN` | `false` | Simulate without actually searching |
| `AUTO_START` | `true` | Start hunting after setup |
| `LANGUAGE` | `de` | `de` or `en` |
| `DATA_DIR` | `/data` | Path for `config.json` and `mediastarr.db` |

---

## 🌐 Network

**Same Docker network:** use container name (`http://sonarr:8989`), set `arr-network` in `docker-compose.yml`.  
**No shared network:** add `extra_hosts: ["host.docker.internal:host-gateway"]`, use `http://host.docker.internal:8989`.  
**Direct IP:** use `http://192.168.1.100:8989` in the wizard.

---

## 📡 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `GET /api/state` | GET | Status, stats, config, activity log |
| `POST /api/control` | POST | `{"action":"start\|stop\|run_now"}` |
| `POST /api/config` | POST | Update configuration |
| `GET /api/ping/<svc>` | GET | Test connection |
| `GET /api/history` | GET | Search history (filterable) |
| `GET /api/history/stats` | GET | DB stats per service |
| `POST /api/history/clear` | POST | Clear all history |
| `POST /api/history/clear/<svc>` | POST | Clear one service |
| `POST /api/setup/reset` | POST | Re-run setup wizard |

---

## 🔒 Security

- All inputs validated and sanitised
- API keys never returned in responses
- Service, URL scheme, theme, action whitelists
- Security headers: CSP, X-Frame-Options, nosniff, Referrer-Policy
- `Cache-Control: no-store` on all API routes
- SQLite WAL mode — safe concurrent access

---

*MIT License — Built from scratch, independent project*
