import sqlite3
import json
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "firereach.db")

PLAN_LIMITS = {
    "free": 3,
    "pro": 10,
    "plus": 25
}

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS icp_campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            icp TEXT NOT NULL,
            plan_tier TEXT DEFAULT 'free',
            max_companies INTEGER DEFAULT 3,
            companies_found INTEGER DEFAULT 0,
            companies_approved INTEGER DEFAULT 0,
            companies_sent INTEGER DEFAULT 0,
            status TEXT DEFAULT 'discovering'
        );

        CREATE TABLE IF NOT EXISTS company_prospects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER REFERENCES icp_campaigns(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            company_name TEXT NOT NULL,
            business_summary TEXT,
            website TEXT,
            signals JSON,
            high_confidence_count INTEGER DEFAULT 0,
            target_designation TEXT,
            signal_score INTEGER DEFAULT 0,
            approval_status TEXT DEFAULT 'pending',
            contact_name TEXT,
            contact_email TEXT,
            contact_title TEXT,
            contact_source TEXT,
            account_brief TEXT,
            email_subject TEXT,
            generated_email TEXT,
            pdf_path TEXT,
            send_status TEXT DEFAULT 'pending'
        );

        CREATE TABLE IF NOT EXISTS signal_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL UNIQUE,
            signals JSON NOT NULL,
            contact JSON NOT NULL,
            high_confidence_count INTEGER DEFAULT 0,
            signal_summary JSON,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

# ── Plan Utils ───────────────────────────────────────────────

def get_plan_limit(plan_tier: str) -> int:
    return PLAN_LIMITS.get(plan_tier.lower(), 3)

# ── Campaign Functions ───────────────────────────────────────

def create_campaign(icp: str, plan_tier: str) -> int:
    limit = get_plan_limit(plan_tier)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO icp_campaigns (icp, plan_tier, max_companies, status)
        VALUES (?, ?, ?, 'discovering')
    """, (icp, plan_tier, limit))
    campaign_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return campaign_id

def update_campaign_status(campaign_id: int, status: str, **kwargs):
    conn = get_connection()
    fields = ", ".join([f"{k} = ?" for k in kwargs])
    values = list(kwargs.values()) + [campaign_id]
    
    if fields:
        conn.execute(f"UPDATE icp_campaigns SET status = ?, {fields} WHERE id = ?",
                    [status] + list(kwargs.values()) + [campaign_id])
    else:
        conn.execute("UPDATE icp_campaigns SET status = ? WHERE id = ?",
                    [status, campaign_id])
    conn.commit()
    conn.close()

def get_campaign(campaign_id: int) -> dict:
    conn = get_connection()
    row = conn.execute("SELECT * FROM icp_campaigns WHERE id = ?", (campaign_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)

def get_recent_campaigns(limit: int = 10) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT c.*, COUNT(p.id) as total_prospects,
               SUM(CASE WHEN p.send_status = 'sent' THEN 1 ELSE 0 END) as sent_count
        FROM icp_campaigns c
        LEFT JOIN company_prospects p ON p.campaign_id = c.id
        GROUP BY c.id
        ORDER BY c.created_at DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Prospect Functions ───────────────────────────────────────

def save_prospect(campaign_id: int, data: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO company_prospects (
            campaign_id, company_name, business_summary, website,
            signals, high_confidence_count, target_designation,
            signal_score, approval_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
    """, (
        campaign_id,
        data.get("company_name", ""),
        data.get("business_summary", ""),
        data.get("website", ""),
        json.dumps(data.get("signals", [])),
        data.get("high_confidence_count", 0),
        data.get("target_designation", ""),
        data.get("signal_score", 0)
    ))
    prospect_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return prospect_id

def update_prospect(prospect_id: int, data: dict):
    conn = get_connection()
    allowed = ["approval_status", "contact_name", "contact_email",
               "contact_title", "contact_source", "account_brief",
               "email_subject", "generated_email", "pdf_path", "send_status"]
    
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        conn.close()
        return
    
    fields = ", ".join([f"{k} = ?" for k in updates])
    conn.execute(f"UPDATE company_prospects SET {fields} WHERE id = ?",
                list(updates.values()) + [prospect_id])
    conn.commit()
    conn.close()

def get_prospect(prospect_id: int) -> dict:
    conn = get_connection()
    row = conn.execute("SELECT * FROM company_prospects WHERE id = ?", (prospect_id,)).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    if d.get("signals"):
        d["signals"] = json.loads(d["signals"])
    return d

def get_campaign_prospects(campaign_id: int) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM company_prospects
        WHERE campaign_id = ?
        ORDER BY signal_score DESC
    """, (campaign_id,)).fetchall()
    conn.close()
    
    results = []
    for row in rows:
        d = dict(row)
        if d.get("signals"):
            d["signals"] = json.loads(d["signals"])
        results.append(d)
    return results

# ── Signal Cache ─────────────────────────────────────────────

def get_cached_signals(company: str, max_age_hours: int = 24):
    conn = get_connection()
    row = conn.execute("SELECT * FROM signal_cache WHERE company = ?",
                      (company.lower().strip(),)).fetchone()
    conn.close()
    
    if not row:
        return None
    
    if datetime.now() - datetime.fromisoformat(row["cached_at"]) > timedelta(hours=max_age_hours):
        return None
    
    return {
        "signals": json.loads(row["signals"]),
        "contact": json.loads(row["contact"]),
        "high_confidence_count": row["high_confidence_count"],
        "signal_summary": json.loads(row["signal_summary"]),
        "from_cache": True
    }

def save_signal_cache(company: str, data: dict):
    conn = get_connection()
    conn.execute("""
        INSERT INTO signal_cache
        (company, signals, contact, high_confidence_count, signal_summary, cached_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(company) DO UPDATE SET
            signals = excluded.signals,
            contact = excluded.contact,
            high_confidence_count = excluded.high_confidence_count,
            signal_summary = excluded.signal_summary,
            cached_at = excluded.cached_at
    """, (
        company.lower().strip(),
        json.dumps(data.get("signals", [])),
        json.dumps(data.get("contact", {})),
        data.get("high_confidence_count", 0),
        json.dumps(data.get("signal_summary", [])),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()