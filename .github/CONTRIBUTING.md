# Contributing to Mediastarr

Thanks for your interest in contributing! / Danke für dein Interesse!

---

## 🇬🇧 English

### Before you start

- Check [open issues](https://github.com/kroeberd/mediastarr/issues) to avoid duplicates
- For larger changes, open an issue first to discuss the idea
- Join the [Discord](https://discord.gg/8Vb9cj4ksv) for questions

### How to contribute

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR_NAME/mediastarr.git`
3. **Create a branch**: `git checkout -b feat/your-feature`
4. **Make your changes** (see guidelines below)
5. **Test** your changes locally: `docker compose up --build`
6. **Push** and open a **Pull Request** against `main`

### Guidelines

**Python (`app/main.py`, `app/db.py`)**
- Run `python3 -m py_compile app/main.py app/db.py` before committing — zero warnings expected
- No bare `except:` — use `except Exception:` at minimum
- All new API routes must use `@_api_auth_required`
- Input from requests must go through `safe_str()` / `clamp_int()` / `validate_*()` helpers
- No new dependencies without discussion

**Frontend (`templates/index.html`)**
- Run `node --check` on the extracted JS block before committing
- All user-visible text must go through the `T` dict (DE + EN keys)
- Dynamic HTML must use `escHtml()` — no raw string interpolation into `innerHTML`
- New fetch calls to mutating endpoints must include the CSRF token (the fetch wrapper handles this automatically)

**Commit messages**
```
type: short description

feat:  new feature
fix:   bug fix
sec:   security improvement
docs:  documentation only
style: formatting, no logic change
refactor: refactoring
```

### What we don't accept

- New external Python dependencies without prior discussion
- Changes to security-relevant code (auth, CSRF, input validation) without an issue first
- Breaking changes to the config schema without a migration path

---

## 🇩🇪 Deutsch

### Bevor du anfängst

- Prüfe [offene Issues](https://github.com/kroeberd/mediastarr/issues) um Duplikate zu vermeiden
- Bei größeren Änderungen erst ein Issue öffnen um die Idee zu besprechen
- Tritt dem [Discord](https://discord.gg/8Vb9cj4ksv) für Fragen bei

### Wie du beitragen kannst

1. **Fork** das Repository
2. **Clone** deinen Fork: `git clone https://github.com/DEIN_NAME/mediastarr.git`
3. **Branch erstellen**: `git checkout -b feat/dein-feature`
4. **Änderungen machen** (Richtlinien siehe oben)
5. **Testen** mit: `docker compose up --build`
6. **Push** und **Pull Request** gegen `main` öffnen

### Was wir nicht annehmen

- Neue externe Python-Dependencies ohne vorherige Diskussion
- Änderungen an sicherheitsrelevanten Bereichen ohne vorheriges Issue
- Breaking Changes am Config-Schema ohne Migrationspfad
