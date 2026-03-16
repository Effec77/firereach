import sqlite3
import json
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "firereach.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS outreach_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            company TEXT NOT NULL,
            icp TEXT,
            recipient_email TEXT,
            contact_name TEXT,
            contact_title TEXT,
            contact_source TEXT,
            signals JSON,
            high_confidence_count INTEGER DEFAULT 0,
            account_brief TEXT,
            email_subject TEXT,
            generated_email TEXT,
            send_status TEXT
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

def get_cached_signals(company: str, max_age_hours: int = 24):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM signal_cache WHERE company = ?",
        (company.lower().strip(),)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    cached_at = datetime.fromisoformat(row["cached_at"])
    if datetime.now() - cached_at > timedelta(hours=max_age_hours):
        return None
    
    return {
        "company": company,
        "signals": json.loads(row["signals"]),
        "contact": json.loads(row["contact"]),
        "high_confidence_count": row["high_confidence_count"],
        "signal_summary": json.loads(row["signal_summary"]),
        "from_cache": True,
        "cached_at": row["cached_at"]
    }

def save_signal_cache(company: str, harvested: dict):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO signal_cache (company, signals, contact, high_confidence_count, signal_summary, cached_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(company) DO UPDATE SET
            signals = excluded.signals,
            contact = excluded.contact,
            high_confidence_count = excluded.high_confidence_count,
            signal_summary = excluded.signal_summary,
            cached_at = excluded.cached_at
    """, (
        company.lower().strip(),
        json.dumps(harvested["signals"]),
        json.dumps(harvested["contact"]),
        harvested.get("high_confidence_count", 0),
        json.dumps(harvested.get("signal_summary", [])),
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()

def save_outreach_run(company, icp, recipient_email, contact, signals,
                      high_confidence_count, account_brief,
                      email_subject, generated_email, send_status):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO outreach_runs (
            company, icp, recipient_email,
            contact_name, contact_title, contact_source,
            signals, high_confidence_count,
            account_brief, email_subject, generated_email, send_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        company, icp, recipient_email,
        contact.get("name", ""),
        contact.get("title", ""),
        contact.get("source", ""),
        json.dumps(signals),
        high_confidence_count,
        account_brief,
        email_subject,
        generated_email,
        send_status
    ))
    
    conn.commit()
    conn.close()

def get_recent_runs(limit: int = 10) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, created_at, company, icp, recipient_email,
               contact_name, contact_title, contact_source,
               signals, high_confidence_count, email_subject, send_status
        FROM outreach_runs
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "id": row["id"],
            "created_at": row["created_at"],
            "company": row["company"],
            "icp": row["icp"],
            "recipient_email": row["recipient_email"],
            "contact_name": row["contact_name"],
            "contact_title": row["contact_title"],
            "contact_source": row["contact_source"],
            "signals": json.loads(row["signals"]) if row["signals"] else [],
            "high_confidence_count": row["high_confidence_count"],
            "email_subject": row["email_subject"],
            "send_status": row["send_status"]
        })
    
    return results

def get_run_detail(run_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM outreach_runs WHERE id = ?", (run_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "company": row["company"],
        "icp": row["icp"],
        "recipient_email": row["recipient_email"],
        "contact_name": row["contact_name"],
        "contact_title": row["contact_title"],
        "contact_source": row["contact_source"],
        "signals": json.loads(row["signals"]) if row["signals"] else [],
        "high_confidence_count": row["high_confidence_count"],
        "account_brief": row["account_brief"],
        "email_subject": row["email_subject"],
        "generated_email": row["generated_email"],
        "send_status": row["send_status"]
    }
