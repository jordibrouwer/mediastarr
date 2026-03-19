"""database.py — SQLite layer for Mediastarr"""
import sqlite3, logging
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager

logger = logging.getLogger(__name__)
DB_PATH = None

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS searched_items (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    service        TEXT    NOT NULL,
    item_type      TEXT    NOT NULL,
    item_id        INTEGER NOT NULL,
    title          TEXT    NOT NULL DEFAULT '',
    searched_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    cooldown_until TEXT    NOT NULL,
    was_dry_run    INTEGER NOT NULL DEFAULT 0
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_searched_unique ON searched_items(service,item_type,item_id);
CREATE INDEX IF NOT EXISTS idx_searched_cooldown ON searched_items(cooldown_until);
CREATE TABLE IF NOT EXISTS cycle_stats (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    date          TEXT NOT NULL,
    cycle_number  INTEGER NOT NULL,
    sonarr_missing_found    INTEGER DEFAULT 0,
    sonarr_missing_searched INTEGER DEFAULT 0,
    sonarr_upgrades_found   INTEGER DEFAULT 0,
    sonarr_upgrades_searched INTEGER DEFAULT 0,
    radarr_missing_found    INTEGER DEFAULT 0,
    radarr_missing_searched INTEGER DEFAULT 0,
    radarr_upgrades_found   INTEGER DEFAULT 0,
    radarr_upgrades_searched INTEGER DEFAULT 0,
    skipped_cooldown INTEGER DEFAULT 0,
    skipped_daily    INTEGER DEFAULT 0,
    started_at    TEXT NOT NULL DEFAULT (datetime('now')),
    finished_at   TEXT
);
CREATE INDEX IF NOT EXISTS idx_cycle_date ON cycle_stats(date);
CREATE TABLE IF NOT EXISTS errors (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    service     TEXT NOT NULL,
    error_type  TEXT NOT NULL,
    message     TEXT NOT NULL,
    occurred_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

def init_db(data_dir):
    global DB_PATH
    DB_PATH = Path(data_dir) / "mediastarr.db"
    with _conn() as con:
        con.executescript(SCHEMA)
    logger.info(f"DB ready: {DB_PATH}")

@contextmanager
def _conn():
    con = sqlite3.connect(str(DB_PATH), timeout=10)
    con.row_factory = sqlite3.Row
    try:
        yield con; con.commit()
    except Exception:
        con.rollback(); raise
    finally:
        con.close()

# Config
def cfg_get(key, default=None):
    with _conn() as con:
        r = con.execute("SELECT value FROM config WHERE key=?", (key,)).fetchone()
        return r["value"] if r else default

def cfg_set(key, value):
    ts = datetime.utcnow().isoformat()
    with _conn() as con:
        con.execute("""INSERT INTO config(key,value,updated_at) VALUES(?,?,?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
            (key, str(value), ts))

def cfg_set_many(pairs):
    ts = datetime.utcnow().isoformat()
    with _conn() as con:
        for k, v in pairs.items():
            con.execute("""INSERT INTO config(key,value,updated_at) VALUES(?,?,?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=excluded.updated_at""",
                (k, str(v), ts))

def cfg_all():
    with _conn() as con:
        return {r["key"]: r["value"] for r in con.execute("SELECT key,value FROM config").fetchall()}

# Cooldown
def is_on_cooldown(service, item_type, item_id):
    now = datetime.utcnow().isoformat()
    with _conn() as con:
        r = con.execute("SELECT cooldown_until FROM searched_items WHERE service=? AND item_type=? AND item_id=?",
                        (service, item_type, item_id)).fetchone()
        return bool(r and r["cooldown_until"] > now)

def upsert_searched(service, item_type, item_id, title, cooldown_days, dry_run):
    until = (datetime.utcnow() + timedelta(days=float(cooldown_days))).isoformat()
    now   = datetime.utcnow().isoformat()
    with _conn() as con:
        con.execute("""INSERT INTO searched_items(service,item_type,item_id,title,searched_at,cooldown_until,was_dry_run)
            VALUES(?,?,?,?,?,?,?)
            ON CONFLICT(service,item_type,item_id) DO UPDATE SET
                title=excluded.title,searched_at=excluded.searched_at,
                cooldown_until=excluded.cooldown_until,was_dry_run=excluded.was_dry_run""",
            (service, item_type, item_id, title[:200], now, until, 1 if dry_run else 0))

def count_on_cooldown():
    now = datetime.utcnow().isoformat()
    with _conn() as con:
        return con.execute("SELECT COUNT(*) FROM searched_items WHERE cooldown_until>?", (now,)).fetchone()[0]

def count_searched_today():
    today = datetime.utcnow().strftime("%Y-%m-%d") + "T00:00:00"
    with _conn() as con:
        return con.execute("SELECT COUNT(*) FROM searched_items WHERE searched_at>=? AND was_dry_run=0", (today,)).fetchone()[0]

def get_history(limit=500, service=None, only_active=False):
    now = datetime.utcnow().isoformat()
    q = "SELECT service,item_type,item_id,title,searched_at,cooldown_until,was_dry_run FROM searched_items"
    conds, params = [], []
    if service:      conds.append("service=?");          params.append(service)
    if only_active:  conds.append("cooldown_until>?");   params.append(now)
    if conds:        q += " WHERE " + " AND ".join(conds)
    q += " ORDER BY searched_at DESC LIMIT ?"
    params.append(limit)
    with _conn() as con:
        return [dict(r) for r in con.execute(q, params).fetchall()]

def clear_history(service=None):
    with _conn() as con:
        if service: con.execute("DELETE FROM searched_items WHERE service=?", (service,))
        else:       con.execute("DELETE FROM searched_items")

# Cycle stats
def insert_cycle(cycle_number):
    date = datetime.utcnow().strftime("%Y-%m-%d")
    with _conn() as con:
        return con.execute("INSERT INTO cycle_stats(date,cycle_number) VALUES(?,?)", (date, cycle_number)).lastrowid

def finish_cycle(row_id, stats):
    with _conn() as con:
        con.execute("""UPDATE cycle_stats SET
            sonarr_missing_found=:smf,sonarr_missing_searched=:sms,
            sonarr_upgrades_found=:suf,sonarr_upgrades_searched=:sus,
            radarr_missing_found=:rmf,radarr_missing_searched=:rms,
            radarr_upgrades_found=:ruf,radarr_upgrades_searched=:rus,
            skipped_cooldown=:sc,skipped_daily=:sd,finished_at=:fa WHERE id=:id""",
            {**{k: stats.get(k,0) for k in ["smf","sms","suf","sus","rmf","rms","ruf","rus","sc","sd"]},
             "smf":stats.get("sonarr_missing_found",0),"sms":stats.get("sonarr_missing_searched",0),
             "suf":stats.get("sonarr_upgrades_found",0),"sus":stats.get("sonarr_upgrades_searched",0),
             "rmf":stats.get("radarr_missing_found",0),"rms":stats.get("radarr_missing_searched",0),
             "ruf":stats.get("radarr_upgrades_found",0),"rus":stats.get("radarr_upgrades_searched",0),
             "sc":stats.get("skipped_cooldown",0),"sd":stats.get("skipped_daily",0),
             "fa":datetime.utcnow().isoformat(),"id":row_id})

def get_cycle_stats(days=7):
    cutoff = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    with _conn() as con:
        rows = con.execute("""SELECT date,
            SUM(sonarr_missing_searched+radarr_missing_searched) as missing_total,
            SUM(sonarr_upgrades_searched+radarr_upgrades_searched) as upgrade_total,
            SUM(skipped_cooldown) as skipped_cooldown,SUM(skipped_daily) as skipped_daily,
            COUNT(*) as cycles FROM cycle_stats WHERE date>=? GROUP BY date ORDER BY date DESC""", (cutoff,)).fetchall()
        return [dict(r) for r in rows]

def get_recent_cycles(limit=10):
    with _conn() as con:
        return [dict(r) for r in con.execute("SELECT * FROM cycle_stats ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]

# Errors
def log_error(service, error_type, message):
    with _conn() as con:
        con.execute("INSERT INTO errors(service,error_type,message) VALUES(?,?,?)",
                    (service, error_type, str(message)[:1000]))

def get_errors(limit=50):
    with _conn() as con:
        return [dict(r) for r in con.execute("SELECT * FROM errors ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]

def clear_old_errors(days=30):
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    with _conn() as con:
        con.execute("DELETE FROM errors WHERE occurred_at<?", (cutoff,))
