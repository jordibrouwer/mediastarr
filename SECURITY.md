# Security Policy / Sicherheitsrichtlinie

## 🇬🇧 English

### Supported Versions

| Version | Supported |
|---|---|
| v7.1.x (latest) | ✅ Active |
| < v7.1.0 | ❌ No longer supported |

### Reporting a Vulnerability

**Please do NOT open a public GitHub Issue for security vulnerabilities.**

If you discover a security vulnerability — such as authentication bypass, API key exposure, SSRF, or injection — please report it privately:

1. **GitHub Private Advisory** (preferred): Go to [Security → Advisories → Report a vulnerability](https://github.com/kroeberd/mediastarr/security/advisories/new)
2. **Discord DM**: Send a direct message to the maintainer on the [Mediastarr Discord](https://discord.gg/8Vb9cj4ksv)

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Your Mediastarr version and installation method (Docker, Unraid, etc.)

**Expected response time:** within 72 hours.  
**Fix timeline:** Critical issues within 7 days, others within 30 days.

You will be credited in the release notes unless you prefer to remain anonymous.

---

### Security Features (v7.1.x)

- Optional dashboard password (`MEDIASTARR_PASSWORD`)
- CSRF protection on all state-mutating requests
- Brute-force login protection (10 attempts → 5 min IP lockout)
- **AES-256 encryption for API keys and webhook URLs** in `config.json` (via Fernet; auto-generated key in `/data/.secret_key`)
- **API key censoring** in activity log (`_censor_log()`)
- API keys never returned in `/api/state` responses
- Webhook URLs never returned in `/api/state` responses
- SSRF protection on all URL inputs
- SQL parameters — no f-string interpolation in queries
- `config.json` permissions set to `0600` on every save
- `.secret_key` permissions set to `0600`
- Security headers: `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, CSP
- URL redirect validation (login `?next=` parameter verified via `urlparse`)
- Stack trace exposure eliminated from all API responses (CodeQL-verified)

---

## 🇩🇪 Deutsch

### Unterstützte Versionen

| Version | Unterstützt |
|---|---|
| v7.1.x (aktuell) | ✅ Aktiv |
| < v7.1.0 | ❌ Nicht mehr unterstützt |

### Sicherheitslücken melden

**Bitte öffne kein öffentliches GitHub Issue für Sicherheitsprobleme.**

Wenn du eine Sicherheitslücke entdeckst — z.B. Auth-Bypass, API-Key-Exposition, SSRF oder Injection — melde sie bitte privat:

1. **GitHub Private Advisory** (bevorzugt): [Security → Advisories → Report a vulnerability](https://github.com/kroeberd/mediastarr/security/advisories/new)
2. **Discord DM**: Schreib eine Direktnachricht an den Maintainer im [Mediastarr Discord](https://discord.gg/8Vb9cj4ksv)

Bitte angeben:
- Beschreibung der Lücke
- Schritte zur Reproduktion
- Mögliche Auswirkungen
- Deine Mediastarr-Version und Installationsmethode

**Reaktionszeit:** innerhalb von 72 Stunden.  
**Behebungszeitraum:** Kritische Probleme innerhalb von 7 Tagen, andere innerhalb von 30 Tagen.

Du wirst in den Release Notes erwähnt — sofern du das möchtest.

---

### Sicherheitsfunktionen (v7.1.x)

- Optionales Dashboard-Passwort (`MEDIASTARR_PASSWORD`)
- CSRF-Schutz bei allen zustandsändernden Anfragen
- Brute-Force-Login-Schutz (10 Versuche → 5 Min. IP-Sperre)
- **AES-256-Verschlüsselung** für API-Keys und Webhook-URLs in `config.json` (via Fernet; auto-generierter Schlüssel in `/data/.secret_key`)
- **API-Key-Zensierung** im Aktivitätslog (`_censor_log()`)
- API-Keys werden nie in `/api/state`-Antworten zurückgegeben
- Webhook-URLs werden nie in `/api/state`-Antworten zurückgegeben
- SSRF-Schutz auf alle URL-Eingaben
- SQL-Parameter — keine f-String-Interpolation in Queries
- `config.json`-Berechtigungen: `0600` bei jedem Speichern
- `.secret_key`-Berechtigungen: `0600`
- Security-Header: `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, CSP
- URL-Redirect-Validierung (Login `?next=`-Parameter per `urlparse` geprüft)
- Stack-Trace-Exposition aus allen API-Antworten entfernt (CodeQL-verifiziert)
