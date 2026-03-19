"""
Mediastarr v4 — main.py
Automated missing-content & upgrade search for Sonarr and Radarr.

This is an independent project and is NOT affiliated with, derived from,
or based on Huntarr. Built from scratch.
"""
import os, re, json, time, logging, threading, requests
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse
from flask import Flask, render_template, jsonify, request, redirect
from collections import deque
import db

app = Flask(__name__, template_folder='../templates', static_folder='../static')
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

ALLOWED_SERVICES   = frozenset({"sonarr","radarr"})
ALLOWED_LANGUAGES  = frozenset({"de","en"})
ALLOWED_ACTIONS    = frozenset({"start","stop","run_now"})
ALLOWED_SCHEMES    = frozenset({"http","https"})
ALLOWED_THEMES     = frozenset({"dark","light","oled"})
DELAY_MIN, DELAY_MAX = 60, 86400
API_KEY_RE = re.compile(r'^[A-Za-z0-9\-_]{8,128}$')
URL_MAX_LEN = 256

DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
CFG_FILE = DATA_DIR / "config.json"
DB_FILE  = DATA_DIR / "mediastarr.db"
DATA_DIR.mkdir(parents=True, exist_ok=True)
db.init(DB_FILE)

DEFAULT_CONFIG = {
    "setup_complete": False, "language": "de", "theme": "dark",
    "sonarr": {"enabled": True,  "url": "http://sonarr:8989", "api_key": ""},
    "radarr": {"enabled": True,  "url": "http://radarr:7878", "api_key": ""},
    "hunt_missing_delay": 900, "hunt_upgrade_delay": 1800,
    "max_searches_per_run": 10, "daily_limit": 20, "cooldown_days": 7,
    "dry_run": False, "auto_start": True,
}

def load_config():
    if CFG_FILE.exists():
        try:
            raw = json.loads(CFG_FILE.read_text())
            m = DEFAULT_CONFIG.copy()
            m.update({k:v for k,v in raw.items() if k not in ("sonarr","radarr")})
            for s in ("sonarr","radarr"):
                if s in raw and isinstance(raw[s], dict):
                    m[s] = {**DEFAULT_CONFIG[s], **raw[s]}
            return m
        except Exception as e: logger.warning(f"Config load failed: {e}")
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    tmp = CFG_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, indent=2))
    tmp.replace(CFG_FILE)

CONFIG = load_config()

if not CONFIG["setup_complete"]:
    for svc, ek, eu in [("sonarr","SONARR_API_KEY","SONARR_URL"),("radarr","RADARR_API_KEY","RADARR_URL")]:
        k = os.environ.get(ek,"").strip()
        if k:
            CONFIG[svc]["api_key"] = k
            u = os.environ.get(eu,"").strip()
            if u: CONFIG[svc]["url"] = u
    if CONFIG["sonarr"]["api_key"] and CONFIG["radarr"]["api_key"]:
        CONFIG["setup_complete"] = True; save_config(CONFIG)

STATE = {
    "running": False, "last_run": None, "next_run": None, "cycle_count": 0,
    "stats": {
        s: {"missing_found":0,"missing_searched":0,"upgrades_found":0,"upgrades_searched":0,
            "skipped_cooldown":0,"skipped_daily":0,"status":"unknown","version":"?"}
        for s in ("sonarr","radarr")
    },
    "activity_log": deque(maxlen=300),
}
STOP_EVENT = threading.Event()
hunt_thread = None

def validate_url(url):
    if not url or not isinstance(url, str): return False, "URL missing"
    if len(url) > URL_MAX_LEN: return False, "URL too long"
    try: p = urlparse(url)
    except: return False, "Parse error"
    if p.scheme not in ALLOWED_SCHEMES: return False, f"Scheme '{p.scheme}' not allowed"
    if not p.hostname: return False, "No hostname"
    return True, ""

def validate_api_key(key):
    if not key or not isinstance(key, str): return False, "Missing"
    if not API_KEY_RE.match(key): return False, "Invalid format"
    return True, ""

def clamp_int(val, lo, hi, default):
    try: return max(lo, min(hi, int(val)))
    except: return default

def safe_str(val, max_len=256):
    return val[:max_len] if isinstance(val, str) else ""

@app.after_request
def sec_headers(r):
    r.headers.update({
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "same-origin",
        "Content-Security-Policy": (
            "default-src 'self'; script-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://fonts.gstatic.com; "
            "font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self';"
        ),
    })
    if request.path.startswith("/api/"):
        r.headers["Cache-Control"] = "no-store"; r.headers["Pragma"] = "no-cache"
    return r

@app.errorhandler(400)
def e400(e): return jsonify({"ok":False,"error":"Bad request"}), 400
@app.errorhandler(404)
def e404(e): return jsonify({"ok":False,"error":"Not found"}), 404
@app.errorhandler(405)
def e405(e): return jsonify({"ok":False,"error":"Method not allowed"}), 405
@app.errorhandler(500)
def e500(e): logger.error(f"500: {e}"); return jsonify({"ok":False,"error":"Internal server error"}), 500

class ArrClient:
    def __init__(self, name, url, api_key):
        self.name = name; self.url = url.rstrip("/")
        self._h = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    def get(self, path, params=None):
        r = requests.get(f"{self.url}/api/v3/{path}", headers=self._h, params=params, timeout=30)
        r.raise_for_status(); return r.json()
    def post(self, path, data=None):
        r = requests.post(f"{self.url}/api/v3/{path}", headers=self._h, json=data, timeout=30)
        r.raise_for_status(); return r.json()
    def ping(self):
        try: d = self.get("system/status"); return True, str(d.get("version","?"))[:20]
        except Exception as e: return False, str(e)[:200]

def log_act(service, action, item, status="info"):
    STATE["activity_log"].appendleft({
        "ts": datetime.now().strftime("%H:%M:%S"),
        "service": safe_str(service, 20), "action": safe_str(action, 50),
        "item": safe_str(item, 200),
        "status": status if status in ("info","success","warning","error") else "info",
    })
    logger.info(f"[{service}] {action}: {item}")

def daily_limit_reached():
    limit = CONFIG.get("daily_limit", 0)
    return limit > 0 and db.count_today() >= limit

def should_search(svc, item_type, item_id):
    if daily_limit_reached(): return False, "daily_limit"
    if db.is_on_cooldown(svc, item_type, item_id, CONFIG.get("cooldown_days", 7)):
        return False, "cooldown"
    return True, ""

def do_search(client, svc, item_type, item_id, title, command, changed=None, year=None):
    result = "dry_run" if CONFIG["dry_run"] else "triggered"
    if not CONFIG["dry_run"]: client.post("command", command)
    db.upsert_search(svc, item_type, item_id, title, result, changed, year)
    return result

def _year(val):
    """Safely extract a 4-digit year from various arr API fields."""
    if val is None: return None
    try:
        y = int(str(val)[:4])
        return y if 1900 < y < 2100 else None
    except (ValueError, TypeError):
        return None

def hunt_sonarr(client):
    svc = "sonarr"
    try:
        data = client.get("wanted/missing", params={"pageSize":500,"sortKey":"airDateUtc","sortDir":"desc"})
        recs = data.get("records", [])
        STATE["stats"][svc]["missing_found"] = int(data.get("totalRecords", len(recs)))
        searched = 0
        for ep in recs:
            if STOP_EVENT.is_set() or searched >= CONFIG["max_searches_per_run"]: break
            title = f"{ep.get('series',{}).get('title','?')[:60]} S{ep.get('seasonNumber',0):02d}E{ep.get('episodeNumber',0):02d}"
            ok, reason = should_search(svc, "episode", ep["id"])
            if not ok:
                STATE["stats"][svc][f"skipped_{reason}"] += 1
                if reason == "daily_limit": log_act("Sonarr","Daily Limit Reached",f"{db.count_today()}/{CONFIG['daily_limit']}","warning"); return
                continue
            year = _year(ep.get("series",{}).get("year") or ep.get("airDate","")[:4])
            do_search(client, svc, "episode", ep["id"], title, {"name":"EpisodeSearch","episodeIds":[ep["id"]]}, ep.get("series",{}).get("lastInfoSync"), year)
            STATE["stats"][svc]["missing_searched"] += 1; searched += 1
            log_act("Sonarr","Missing",title,"success"); time.sleep(1.5)
    except Exception as e: log_act("Sonarr","Error",str(e)[:200],"error")

    try:
        data = client.get("wanted/cutoff", params={"pageSize":500})
        recs = data.get("records", [])
        STATE["stats"][svc]["upgrades_found"] = int(data.get("totalRecords", len(recs)))
        searched = 0
        for ep in recs:
            if STOP_EVENT.is_set() or searched >= CONFIG["max_searches_per_run"]: break
            title = f"{ep.get('series',{}).get('title','?')[:60]} S{ep.get('seasonNumber',0):02d}E{ep.get('episodeNumber',0):02d}"
            ok, reason = should_search(svc, "episode_upgrade", ep["id"])
            if not ok:
                STATE["stats"][svc][f"skipped_{reason}"] += 1
                if reason == "daily_limit": return
                continue
            year = _year(ep.get("series",{}).get("year") or ep.get("airDate","")[:4])
            do_search(client, svc, "episode_upgrade", ep["id"], title, {"name":"EpisodeSearch","episodeIds":[ep["id"]]}, year=year)
            STATE["stats"][svc]["upgrades_searched"] += 1; searched += 1
            log_act("Sonarr","Upgrade",title,"warning"); time.sleep(1.5)
    except Exception as e: log_act("Sonarr","Error",str(e)[:200],"error")

def hunt_radarr(client):
    svc = "radarr"
    try:
        movies = client.get("movie")
        missing = [m for m in movies if not m.get("hasFile") and m.get("monitored")]
        STATE["stats"][svc]["missing_found"] = len(missing)
        searched = 0
        for movie in missing:
            if STOP_EVENT.is_set() or searched >= CONFIG["max_searches_per_run"]: break
            title = str(movie.get("title","?"))[:100]
            ok, reason = should_search(svc, "movie", movie["id"])
            if not ok:
                STATE["stats"][svc][f"skipped_{reason}"] += 1
                if reason == "daily_limit": log_act("Radarr","Daily Limit Reached",f"{db.count_today()}/{CONFIG['daily_limit']}","warning"); return
                continue
            year = _year(movie.get("year"))
            do_search(client, svc, "movie", movie["id"], title, {"name":"MoviesSearch","movieIds":[movie["id"]]}, movie.get("lastInfoSync"), year)
            STATE["stats"][svc]["missing_searched"] += 1; searched += 1
            log_act("Radarr","Missing",title,"success"); time.sleep(1.5)
    except Exception as e: log_act("Radarr","Error",str(e)[:200],"error")

    try:
        data = client.get("wanted/cutoff", params={"pageSize":500})
        recs = data.get("records", [])
        STATE["stats"][svc]["upgrades_found"] = int(data.get("totalRecords", len(recs)))
        searched = 0
        for movie in recs:
            if STOP_EVENT.is_set() or searched >= CONFIG["max_searches_per_run"]: break
            title = str(movie.get("title","?"))[:100]
            ok, reason = should_search(svc, "movie_upgrade", movie["id"])
            if not ok:
                STATE["stats"][svc][f"skipped_{reason}"] += 1
                if reason == "daily_limit": return
                continue
            year = _year(movie.get("year"))
            do_search(client, svc, "movie_upgrade", movie["id"], title, {"name":"MoviesSearch","movieIds":[movie["id"]]}, year=year)
            STATE["stats"][svc]["upgrades_searched"] += 1; searched += 1
            log_act("Radarr","Upgrade",title,"warning"); time.sleep(1.5)
    except Exception as e: log_act("Radarr","Error",str(e)[:200],"error")

def ping_all():
    for svc in ("sonarr","radarr"):
        if not CONFIG[svc]["enabled"] or not CONFIG[svc]["api_key"]:
            STATE["stats"][svc]["status"] = "disabled"; continue
        ok, ver = ArrClient(svc, CONFIG[svc]["url"], CONFIG[svc]["api_key"]).ping()
        STATE["stats"][svc]["status"] = "online" if ok else "offline"
        STATE["stats"][svc]["version"] = ver

def run_cycle():
    STATE["cycle_count"] += 1
    STATE["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_act("System","Cycle Start",f"#{STATE['cycle_count']}  Today: {db.count_today()}/{CONFIG.get('daily_limit',0) or '∞'}","info")
    for svc in ("sonarr","radarr"):
        for k in ("missing_searched","upgrades_searched","skipped_cooldown","skipped_daily"):
            STATE["stats"][svc][k] = 0
    ping_all()
    removed = db.purge_expired(CONFIG.get("cooldown_days", 7))
    if removed: log_act("System","DB Pruned",f"{removed} expired entries","info")
    if CONFIG["sonarr"]["enabled"] and CONFIG["sonarr"]["api_key"] and STATE["stats"]["sonarr"]["status"]=="online":
        hunt_sonarr(ArrClient("Sonarr",CONFIG["sonarr"]["url"],CONFIG["sonarr"]["api_key"]))
    if CONFIG["radarr"]["enabled"] and CONFIG["radarr"]["api_key"] and STATE["stats"]["radarr"]["status"]=="online" and not STOP_EVENT.is_set():
        hunt_radarr(ArrClient("Radarr",CONFIG["radarr"]["url"],CONFIG["radarr"]["api_key"]))
    log_act("System","Cycle Done",f"#{STATE['cycle_count']}  Today: {db.count_today()}","info")

def hunt_loop():
    while not STOP_EVENT.is_set():
        STATE["running"] = True
        try: run_cycle()
        except Exception as e: log_act("System","Fatal",str(e)[:200],"error")
        delay = CONFIG["hunt_missing_delay"]
        STATE["next_run"] = datetime.fromtimestamp(time.time()+delay).strftime("%H:%M:%S")
        for _ in range(delay):
            if STOP_EVENT.is_set(): break
            time.sleep(1)
    STATE["running"] = False; STATE["next_run"] = None

@app.route("/")
def index():
    if not CONFIG.get("setup_complete"): return redirect("/setup")
    return render_template("index.html")

@app.route("/setup")
def setup_page(): return render_template("setup.html")

@app.route("/api/setup/ping", methods=["POST"])
def api_setup_ping():
    d = request.get_json(silent=True) or {}
    svc = safe_str(d.get("service",""), 20)
    if svc not in ALLOWED_SERVICES: return jsonify({"ok":False,"msg":"Unknown service"}), 400
    url = safe_str(d.get("url",""), URL_MAX_LEN)
    ok, err = validate_url(url)
    if not ok: return jsonify({"ok":False,"msg":f"Invalid URL: {err}"}), 400
    key = safe_str(d.get("api_key",""), 128)
    ok, err = validate_api_key(key)
    if not ok: return jsonify({"ok":False,"msg":f"Invalid API key: {err}"}), 400
    try: ok, ver = ArrClient(svc,url,key).ping(); return jsonify({"ok":ok,"version":ver})
    except: return jsonify({"ok":False,"msg":"Connection failed"})

@app.route("/api/setup/complete", methods=["POST"])
def api_setup_complete():
    d = request.get_json(silent=True) or {}
    errors = []
    se = bool(d.get("sonarr_enabled",True)); re_ = bool(d.get("radarr_enabled",True))
    su = safe_str(d.get("sonarr_url",CONFIG["sonarr"]["url"]),URL_MAX_LEN)
    sk = safe_str(d.get("sonarr_key",""),128)
    ru = safe_str(d.get("radarr_url",CONFIG["radarr"]["url"]),URL_MAX_LEN)
    rk = safe_str(d.get("radarr_key",""),128)
    if se:
        ok,e = validate_url(su);     errors += [f"Sonarr URL: {e}"]  if not ok else []
        ok,e = validate_api_key(sk); errors += [f"Sonarr Key: {e}"] if not ok else []
    if re_:
        ok,e = validate_url(ru);     errors += [f"Radarr URL: {e}"]  if not ok else []
        ok,e = validate_api_key(rk); errors += [f"Radarr Key: {e}"] if not ok else []
    if errors: return jsonify({"ok":False,"errors":errors}), 400
    lang = safe_str(d.get("language","de"),5)
    if lang not in ALLOWED_LANGUAGES: lang = "de"
    CONFIG["sonarr"].update({"url":su,"api_key":sk,"enabled":se})
    CONFIG["radarr"].update({"url":ru,"api_key":rk,"enabled":re_})
    CONFIG["language"] = lang; CONFIG["setup_complete"] = True; save_config(CONFIG)
    global hunt_thread
    if CONFIG.get("auto_start") and not STATE["running"]:
        STOP_EVENT.clear()
        hunt_thread = threading.Thread(target=hunt_loop, daemon=True); hunt_thread.start()
    return jsonify({"ok":True})

@app.route("/api/setup/reset", methods=["POST"])
def api_setup_reset():
    CONFIG["setup_complete"] = False; save_config(CONFIG); STOP_EVENT.set()
    return jsonify({"ok":True})

@app.route("/api/state")
def api_state():
    today_n = db.count_today(); limit = CONFIG.get("daily_limit",0)
    return jsonify({
        "running": STATE["running"], "last_run": STATE["last_run"],
        "next_run": STATE["next_run"], "cycle_count": STATE["cycle_count"],
        "total_searches": db.total_count(), "daily_count": today_n,
        "daily_limit": limit,
        "daily_remaining": max(0,limit-today_n) if limit > 0 else None,
        "stats": STATE["stats"], "activity_log": list(STATE["activity_log"])[:60],
        "config": {
            "hunt_missing_delay": CONFIG["hunt_missing_delay"],
            "hunt_upgrade_delay": CONFIG["hunt_upgrade_delay"],
            "max_searches_per_run": CONFIG["max_searches_per_run"],
            "daily_limit": CONFIG.get("daily_limit",20),
            "cooldown_days": CONFIG.get("cooldown_days",7),
            "dry_run": CONFIG["dry_run"], "language": CONFIG["language"],
            "theme": CONFIG.get("theme","dark"), "auto_start": CONFIG["auto_start"],
            "sonarr": {"enabled":CONFIG["sonarr"]["enabled"],"url":CONFIG["sonarr"]["url"]},
            "radarr": {"enabled":CONFIG["radarr"]["enabled"],"url":CONFIG["radarr"]["url"]},
            "sonarr_configured": bool(CONFIG["sonarr"]["api_key"]),
            "radarr_configured": bool(CONFIG["radarr"]["api_key"]),
        },
    })

@app.route("/api/control", methods=["POST"])
def api_control():
    global hunt_thread
    d = request.get_json(silent=True) or {}
    action = d.get("action")
    if action not in ALLOWED_ACTIONS: return jsonify({"ok":False,"error":"Invalid action"}), 400
    if action == "start" and not STATE["running"]:
        STOP_EVENT.clear(); hunt_thread = threading.Thread(target=hunt_loop,daemon=True); hunt_thread.start()
    elif action == "stop": STOP_EVENT.set()
    elif action == "run_now":
        if not STATE["running"]: STOP_EVENT.clear(); hunt_thread = threading.Thread(target=hunt_loop,daemon=True); hunt_thread.start()
        else: threading.Thread(target=run_cycle,daemon=True).start()
    return jsonify({"ok":True})

@app.route("/api/config", methods=["POST"])
def api_config():
    d = request.get_json(silent=True)
    if d is None: return jsonify({"ok":False,"error":"Invalid JSON"}), 400
    CONFIG["hunt_missing_delay"]   = clamp_int(d.get("hunt_missing_delay",   CONFIG["hunt_missing_delay"]),   60, 86400, CONFIG["hunt_missing_delay"])
    CONFIG["hunt_upgrade_delay"]   = clamp_int(d.get("hunt_upgrade_delay",   CONFIG["hunt_upgrade_delay"]),   60, 86400, CONFIG["hunt_upgrade_delay"])
    CONFIG["max_searches_per_run"] = clamp_int(d.get("max_searches_per_run", CONFIG["max_searches_per_run"]), 1, 500, CONFIG["max_searches_per_run"])
    CONFIG["daily_limit"]          = clamp_int(d.get("daily_limit",          CONFIG.get("daily_limit",20)),   0, 9999, CONFIG.get("daily_limit",20))
    CONFIG["cooldown_days"]        = clamp_int(d.get("cooldown_days",        CONFIG.get("cooldown_days",7)),  1, 365, CONFIG.get("cooldown_days",7))
    if "dry_run"    in d: CONFIG["dry_run"]    = bool(d["dry_run"])
    if "auto_start" in d: CONFIG["auto_start"] = bool(d["auto_start"])
    theme = safe_str(d.get("theme", CONFIG.get("theme","dark")), 10)
    if theme in ALLOWED_THEMES: CONFIG["theme"] = theme
    lang = safe_str(d.get("language", CONFIG["language"]), 5)
    if lang in ALLOWED_LANGUAGES: CONFIG["language"] = lang
    for svc in ("sonarr","radarr"):
        sd = d.get(svc)
        if not isinstance(sd, dict): continue
        if "enabled" in sd: CONFIG[svc]["enabled"] = bool(sd["enabled"])
        if "url" in sd:
            url = safe_str(sd["url"],URL_MAX_LEN)
            ok,_ = validate_url(url)
            if ok: CONFIG[svc]["url"] = url
        key = safe_str(sd.get("api_key",""),128)
        if key:
            ok,_ = validate_api_key(key)
            if ok: CONFIG[svc]["api_key"] = key
    save_config(CONFIG); return jsonify({"ok":True})

@app.route("/api/ping/<service>")
def api_ping(service):
    if service not in ALLOWED_SERVICES: return jsonify({"ok":False,"error":"Unknown service"}), 404
    cfg = CONFIG.get(service)
    if not cfg or not cfg.get("api_key"): return jsonify({"ok":False,"msg":"Not configured"})
    try:
        ok, ver = ArrClient(service, cfg["url"], cfg["api_key"]).ping()
        STATE["stats"][service]["status"] = "online" if ok else "offline"
        STATE["stats"][service]["version"] = ver
        return jsonify({"ok":ok,"version":ver})
    except: return jsonify({"ok":False,"msg":"Connection failed"})

@app.route("/api/history")
def api_history():
    svc      = safe_str(request.args.get("service",""), 20)
    only_cd  = request.args.get("cooldown_only") == "1"
    cd_days  = CONFIG.get("cooldown_days", 7)
    rows = db.get_history(300, svc if svc in ALLOWED_SERVICES else "", only_cd, cd_days)
    now = datetime.utcnow()
    for r in rows:
        ts  = datetime.fromisoformat(r["searched_at"])
        ago = now - ts
        mins = int(ago.total_seconds() / 60)
        r["ago_label"] = f"vor {mins}min" if mins < 60 else f"vor {mins//60}h" if mins < 1440 else f"vor {mins//1440}d"
        r["expires_label"] = (ts + timedelta(days=cd_days)).strftime("%d.%m. %H:%M")
    return jsonify({"ok":True,"count":len(rows),"history":rows})

@app.route("/api/history/stats")
def api_history_stats():
    return jsonify({"ok":True,"total":db.total_count(),"today":db.count_today(),"by_service":db.stats_by_service(),"by_year":db.year_stats()})

@app.route("/api/history/clear", methods=["POST"])
def api_history_clear():
    n = db.clear_all(); log_act("System","History Cleared",f"{n} entries","warning")
    return jsonify({"ok":True,"removed":n})

@app.route("/api/history/clear/<service>", methods=["POST"])
def api_history_clear_svc(service):
    if service not in ALLOWED_SERVICES: return jsonify({"ok":False,"error":"Unknown service"}), 404
    n = db.clear_service(service); log_act("System",f"History Cleared ({service})",f"{n}","warning")
    return jsonify({"ok":True,"removed":n})

if __name__ == "__main__":
    log_act("System","Start","Mediastarr v4.0","info")
    if CONFIG.get("setup_complete"):
        ping_all()
        if CONFIG.get("auto_start",True):
            hunt_thread = threading.Thread(target=hunt_loop,daemon=True); hunt_thread.start()
            log_act("System","Auto-Start","Hunt loop running","info")
    else:
        log_act("System","Setup Required","Visit http://localhost:7979/setup","warning")
    app.run(host="0.0.0.0", port=7979, debug=False)
