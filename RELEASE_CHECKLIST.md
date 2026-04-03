# Mediastarr — Release Checklist

Every version bump **must** touch all files in this list.  
No exceptions — partial updates cause version drift and user confusion.

---

## 1. Pflicht-Dateien / Required Files

### `VERSION`
```
7.1.x
```
Plain version string, no prefix, no newline at EOF.

---

### `app/main.py`
```python
_CURRENT_VERSION = "v7.1.x"
```
Used for version display, update check, and Discord notifications.

---

### `CHANGELOG.md`
New section at the top:
```markdown
## [v7.1.x] — YYYY-MM-DD

### Fixed
- …

### Added
- …

### Changed
- …
```
- Use flat `### Fixed / Added / Changed` only — no sub-headings.
- Date format: `YYYY-MM-DD`.

---

### `SECURITY.md`
Update the Supported Versions table:
```markdown
| v7.1.x (latest) | ✅ Active |
| < v7.1.0        | ❌ No longer supported |
```

---

### `mediastarr.xml` (Unraid template)
Two places:
1. `<Overview>` — first bold line: `[b]Mediastarr v7.1.x[/b]`
2. `<Description>` — version string at the end

---

### Help Page / i18n strings (`templates/index.html`)
If the help page contains a version reference or "current version" hint:
- Update DE + EN string
- Check both `T['de']` and `T['en']` objects

---

### `README.md`
Update when the release includes **any** of:
- New features visible to users
- Changed Docker env vars or volume paths
- New installation steps
- Updated screenshots
- Changed default values

Minor bugfix-only releases: README update optional but recommended for the version badge.

---

## 2. Optionale Dateien / Optional Files

| File | Update when… |
|---|---|
| `docker-compose.yml` | New env vars or ports added |
| `requirements.txt` | New Python dependency added |
| `Dockerfile` | Base image or build step changed |
| `.github/workflows/docker-publish.yml` | CI/CD changes |
| `static/screenshots/` | UI changed visibly |

---

## 3. Reihenfolge / Order of Operations

```
1. Implement & test all changes
2. Bump VERSION file
3. Update app/main.py (_CURRENT_VERSION)
4. Write CHANGELOG.md entry
5. Update SECURITY.md version table
6. Update mediastarr.xml (Unraid)
7. Update help page i18n if needed
8. Update README.md if needed
9. git commit -m "chore: bump to v7.1.x"
10. git tag v7.1.x
11. git push && git push --tags
    → GitHub Actions builds & pushes Docker image automatically
```

---

## 4. Quick Grep / Schnell-Check

Run this before tagging to catch missed version strings:

```bash
grep -rn "v7\." . \
  --include="*.py" \
  --include="*.md" \
  --include="*.xml" \
  --include="*.html" \
  --include="VERSION" \
  | grep -v ".git"
```

All references should show the **same** version number.

---

## 5. Post-Release

- [ ] GitHub Release created with CHANGELOG entry as body
- [ ] Discord announcement (if significant release)
- [ ] Unraid template repo updated (if `mediastarr.xml` changed)
- [ ] `mediastarr.de` homepage updated (if feature list changed)
