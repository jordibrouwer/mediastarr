"""config.py — Typed config layer on SQLite"""
import os
import database as db

DEFAULTS = {
    "setup_complete":"false","language":"de","theme":"dark",
    "sonarr_enabled":"true","sonarr_url":"http://sonarr:8989","sonarr_api_key":"",
    "radarr_enabled":"true","radarr_url":"http://radarr:7878","radarr_api_key":"",
    "hunt_missing_delay":"900","hunt_upgrade_delay":"1800","max_searches_per_run":"10",
    "daily_limit":"20","cooldown_days":"7","dry_run":"false","auto_start":"true",
}

def _ensure_defaults():
    existing = db.cfg_all()
    missing = {k: v for k, v in DEFAULTS.items() if k not in existing}
    if missing:
        db.cfg_set_many(missing)
    if existing.get("setup_complete","false") == "false":
        env_map = {
            "sonarr_api_key": os.environ.get("SONARR_API_KEY","").strip(),
            "sonarr_url":     os.environ.get("SONARR_URL","").strip(),
            "radarr_api_key": os.environ.get("RADARR_API_KEY","").strip(),
            "radarr_url":     os.environ.get("RADARR_URL","").strip(),
        }
        updates = {k: v for k, v in env_map.items() if v}
        if updates:
            db.cfg_set_many(updates)
        if env_map.get("sonarr_api_key") and env_map.get("radarr_api_key"):
            db.cfg_set("setup_complete","true")

def get(key, default=None):
    return db.cfg_get(key, default if default is not None else DEFAULTS.get(key))

def get_bool(key):
    return str(get(key, DEFAULTS.get(key,"false"))).lower() in ("true","1","yes")

def get_int(key):
    try: return int(float(get(key, DEFAULTS.get(key,"0"))))
    except: return 0

def get_float(key):
    try: return float(get(key, DEFAULTS.get(key,"0")))
    except: return 0.0

def set(key, value):
    db.cfg_set(key, value)

def set_many(pairs):
    db.cfg_set_many(pairs)

def as_dict():
    return {
        "setup_complete":       get_bool("setup_complete"),
        "language":             get("language"),
        "theme":                get("theme","dark"),
        "sonarr_enabled":       get_bool("sonarr_enabled"),
        "sonarr_url":           get("sonarr_url"),
        "sonarr_configured":    bool(get("sonarr_api_key")),
        "radarr_enabled":       get_bool("radarr_enabled"),
        "radarr_url":           get("radarr_url"),
        "radarr_configured":    bool(get("radarr_api_key")),
        "hunt_missing_delay":   get_int("hunt_missing_delay"),
        "hunt_upgrade_delay":   get_int("hunt_upgrade_delay"),
        "max_searches_per_run": get_int("max_searches_per_run"),
        "daily_limit":          get_int("daily_limit"),
        "cooldown_days":        get_float("cooldown_days"),
        "dry_run":              get_bool("dry_run"),
        "auto_start":           get_bool("auto_start"),
    }
