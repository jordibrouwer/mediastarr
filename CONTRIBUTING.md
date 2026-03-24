# Contributing to Mediastarr
**🇬🇧 English** · [🇩🇪 Deutsch](#deutsch)
Thank you for your interest in improving Mediastarr!
---
## 🇬🇧 English
### Ways to Contribute
| Type | How |
|---|---|
| 🐛 Bug report | Open a [Bug Report](https://github.com/kroeberd/mediastarr/issues/new?template=bug_report.yml) |
| 💡 Feature idea | Open a [Feature Request](https://github.com/kroeberd/mediastarr/issues/new?template=feature_request.yml) |
| 💬 Questions / support | Join the [Discord](https://discord.gg/8Vb9cj4ksv) |
| 🔒 Security issue | See [SECURITY.md](SECURITY.md) — do not open public issues |
| ☕ Financial support | [Buy me a coffee](https://buymeacoffee.com/kroeberd) |
### Pull Requests
1. **Fork** the repository and create a branch from `main`
2. **Test locally** — run `docker compose up --build` and verify your change works
3. **Keep it focused** — one feature or fix per PR
4. **Follow the existing code style** — Python (Flask), vanilla JS, no new runtime dependencies without discussion
5. **Update documentation** if your change affects user-facing behaviour (README, CHANGELOG)
6. Open the PR against `main` with a clear description of what and why
### Local Development
```bash
git clone https://github.com/kroeberd/mediastarr.git
cd mediastarr
mkdir data
pip install -r requirements.txt
# Run directly (dev mode)
python app/main.py
# Or with Docker
docker compose up --build
```
The app runs on **http://localhost:7979**.  
Config is stored in `data/config.json`, history in `data/history.db`.
### What We're Looking For
- Bug fixes with a clear reproduction case
- Translations or i18n improvements
- Performance improvements with measurable impact
- UX refinements that stay consistent with the existing design
### What to Discuss First
Please open an issue before starting work on:
- New dependencies (Python packages, JS libraries)
- Architectural changes
- New API endpoints
- Changes to the database schema
---
<a name="deutsch"></a>
## 🇩🇪 Deutsch
### Möglichkeiten zum Beitragen
| Art | Wie |
|---|---|
| 🐛 Fehler melden | [Bug Report](https://github.com/kroeberd/mediastarr/issues/new?template=bug_report.yml) öffnen |
| 💡 Feature-Idee | [Feature Request](https://github.com/kroeberd/mediastarr/issues/new?template=feature_request.yml) öffnen |
| 💬 Fragen / Support | Im [Discord](https://discord.gg/8Vb9cj4ksv) melden |
| 🔒 Sicherheitsproblem | Siehe [SECURITY.md](SECURITY.md) — kein öffentliches Issue |
| ☕ Finanzielle Unterstützung | [Buy me a coffee](https://buymeacoffee.com/kroeberd) |
### Pull Requests
1. **Fork** des Repos, Branch von `main` erstellen
2. **Lokal testen** — `docker compose up --build` ausführen und sicherstellen dass alles funktioniert
3. **Fokussiert bleiben** — pro PR nur eine Funktion oder ein Fix
4. **Code-Stil beibehalten** — Python (Flask), Vanilla JS, keine neuen Abhängigkeiten ohne Absprache
5. **Dokumentation aktualisieren** wenn die Änderung User-Facing-Verhalten betrifft (README, CHANGELOG)
6. PR gegen `main` öffnen mit klarer Beschreibung was und warum
### Lokale Entwicklung
```bash
git clone https://github.com/kroeberd/mediastarr.git
cd mediastarr
mkdir data
pip install -r requirements.txt
# Direkt starten (Dev-Modus)
python app/main.py
# Oder mit Docker
docker compose up --build
```
Die App läuft auf **http://localhost:7979**.
### Was wir suchen
- Bugfixes mit klarem Reproduktionsfall
- Übersetzungen oder i18n-Verbesserungen
- Performance-Verbesserungen mit messbarem Effekt
- UX-Verbesserungen die zum bestehenden Design passen
### Was vorher besprochen werden sollte
Bitte erst ein Issue öffnen vor:
- Neuen Abhängigkeiten (Python-Pakete, JS-Bibliotheken)
- Architekturellen Änderungen
- Neuen API-Endpunkten
- Änderungen am Datenbankschema
- 
