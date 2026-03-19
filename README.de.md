# 🎯 Mediastarr

**Automatische Mediensuche für Sonarr & Radarr** — sucht regelmäßig nach fehlenden Inhalten und Qualitäts-Upgrades. Mit Web-Dashboard, First-Run Wizard, SQLite-Verlauf und Dark / Light / OLED-Themes.

> **⚠️ Hinweis:** Mediastarr ist ein vollständig eigenständiges Projekt, von Grund auf neu gebaut.  
> Es hat **keinerlei Verbindung zu [Huntarr](https://github.com/plexguide/Huntarr.io)** — weder Code noch Logik noch Assets wurden übernommen.  
> Die Idee, \*arr-Anwendungen regelmäßig nach fehlenden Inhalten zu durchsuchen, ist ein verbreitetes Konzept, aber dieses Projekt ist ein unabhängiger Neubau.

---

## ✨ Features

- 📺 **Sonarr** — fehlende Episoden & Qualitäts-Upgrades suchen
- 🎬 **Radarr** — fehlende Filme & Qualitäts-Upgrades suchen
- 🖥️ **Web-Dashboard** — Live-Stats, Aktivitätslog, Service-Status
- 🧙 **First-Run Wizard** — browserbasiertes Setup beim ersten Start
- 🗄️ **SQLite-Verlauf** — jede Suche mit Titel, Zähler, Timestamps und Ergebnis gespeichert
- ⏳ **Cooldown (Tage)** — konfigurierbar 1–365 Tage bevor ein Item erneut gesucht wird
- 📊 **Tageslimit** — maximale tägliche Searches (0 = unbegrenzt)
- 🌐 **Mehrsprachig** — Deutsch & Englisch, im UI umschaltbar
- 🎨 **3 Themes** — Dark, Light, OLED Black
- 🧪 **Dry Run** — simulieren ohne echte Suchen
- ⚡ **Manueller Start** — Zyklus sofort auslösen
- 🔒 **Abgesichertes API** — Validierung, Whitelists, kein Key-Leakage

---

## 🗄️ SQLite-Datenbank

Alle Suchverläufe werden in `/data/mediastarr.db` gespeichert:

| Spalte | Beschreibung |
|---|---|
| `service` | `sonarr` oder `radarr` |
| `item_type` | `episode`, `episode_upgrade`, `movie`, `movie_upgrade` |
| `item_id` | Interne arr-ID |
| `title` | Lesbarer Titel |
| `searched_at` | UTC-Timestamp der letzten Suche |
| `result` | `triggered`, `dry_run`, `skipped_cooldown`, `skipped_daily` |
| `search_count` | Wie oft dieses Item gesucht wurde |
| `last_changed_at` | Letzter Änderungstimestamp aus arr (falls verfügbar) |

Abgelaufene Einträge werden beim nächsten Zyklus automatisch aus der DB entfernt.

---

## 🚀 Schnellstart

```bash
git clone https://github.com/DEIN_USERNAME/mediastarr.git
cd mediastarr
mkdir data
docker compose up -d
open http://localhost:7979
```

---

## 🔑 API Keys finden

In Sonarr / Radarr: **Settings → General → Security → API Key**

---

## ⚙️ Umgebungsvariablen

| Variable | Standard | Beschreibung |
|---|---|---|
| `SONARR_API_KEY` | — | Überspringt Wizard wenn beide gesetzt sind |
| `SONARR_URL` | `http://sonarr:8989` | Sonarr-Adresse |
| `RADARR_API_KEY` | — | Radarr API-Key |
| `RADARR_URL` | `http://radarr:7878` | Radarr-Adresse |
| `HUNT_MISSING_DELAY` | `900` | Sekunden zwischen Missing-Suchen |
| `HUNT_UPGRADE_DELAY` | `1800` | Sekunden zwischen Upgrade-Suchen |
| `MAX_SEARCHES_PER_RUN` | `10` | Max. Items pro Zyklus/Service |
| `DAILY_LIMIT` | `20` | Max. Searches pro Tag (0 = unbegrenzt) |
| `COOLDOWN_DAYS` | `7` | Tage bevor ein Item erneut gesucht wird |
| `DRY_RUN` | `false` | Nur simulieren |
| `AUTO_START` | `true` | Nach Setup automatisch starten |
| `LANGUAGE` | `de` | `de` oder `en` |
| `DATA_DIR` | `/data` | Pfad für config.json und mediastarr.db |

---

*MIT Lizenz — Eigenständiges Projekt, komplett neu gebaut*
