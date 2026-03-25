## Description / Beschreibung

<!-- EN: What does this PR do? / DE: Was macht dieser PR? -->

## Type / Typ

- [ ] `feat` — New feature / Neue Funktion
- [ ] `fix` — Bug fix / Fehlerbehebung
- [ ] `sec` — Security improvement / Sicherheitsverbesserung
- [ ] `docs` — Documentation only / Nur Dokumentation
- [ ] `refactor` — Refactoring, no behaviour change

## Checklist

- [ ] `python3 -m py_compile app/main.py app/db.py` passes (no errors)
- [ ] `node --check` on dashboard JS passes
- [ ] New UI text added to `T` dict in both **DE and EN**
- [ ] Dynamic HTML uses `escHtml()` — no raw user data in `innerHTML`
- [ ] New API routes use `@_api_auth_required`
- [ ] Tested locally with `docker compose up --build`

## Screenshots (UI changes)

<!-- Add before/after screenshots if the UI changed -->

## Related issue / Zugehöriges Issue

<!-- Closes #... / Fixes #... -->
