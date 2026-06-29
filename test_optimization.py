import os
os.environ["BOT_TOKEN"] = "123456:fake_token"
os.environ["VIRUSTOTAL_API_KEY"] = "fake_vt_key"

import asyncio
from datetime import datetime, timedelta
import sqlite3

from app.container import build_container
from app.models import ItemType, ScanVerdict
from app.repositories.base import get_conn
from app.repositories.schema import init_schema

def setup_test_db():
    init_schema()
    # Clean tables
    with get_conn() as conn:
        conn.execute("DELETE FROM url_scan_cache")
        conn.execute("DELETE FROM ai_text_cache")
        conn.execute("DELETE FROM user_subscriptions")
        conn.execute("DELETE FROM group_subscriptions")
        conn.execute("DELETE FROM ai_quota_usage")
        conn.execute("DELETE FROM groups")

async def test_url_cache():
    print("--- Testing URL Cache ---")
    c = build_container()
    url = "https://phishing-scam-test-123.com"
    
    # 1. Verify get on empty cache returns None
    cached = c.url_cache.get(url)
    assert cached is None, "Cache should be empty initially"
    
    # 2. Set cache
    c.url_cache.set(url, "DANGEROUS", 5, 2, 0, 0)
    cached = c.url_cache.get(url)
    assert cached is not None, "Cache should return result after set"
    assert cached["verdict"] == "DANGEROUS"
    assert cached["malicious"] == 5
    
    # 3. Test expiration of SAFE verdict
    safe_url = "https://safe-google.com"
    c.url_cache.set(safe_url, "SAFE", 0, 0, 10, 0)
    
    # Manually backdate checked_at in SQLite to simulate 25 hours ago
    past_time = (datetime.now() - timedelta(hours=25)).strftime("%Y-%m-%d %H:%M:%S")
    with get_conn() as conn:
        conn.execute("UPDATE url_scan_cache SET checked_at = ? WHERE url = ?", (past_time, safe_url))
        
    cached = c.url_cache.get(safe_url)
    assert cached is None, "Expired cache entry should return None"
    print("[OK] URL cache checks passed!")

async def test_nlp_cache():
    print("--- Testing NLP Cache ---")
    c = build_container()
    text = "Assalomu alaykum, click orqali pul yutib oling!"
    normalized = c.nlp.normalize_text(text)
    h = c.ai_cache.hash_text(normalized)
    
    # 1. Verify get on empty cache returns None
    cached = c.ai_cache.get(h)
    assert cached is None, "Cache should be empty initially"
    
    # 2. Set cache
    c.ai_cache.set(h, True, "cybercrime", "Phishing attempt")
    cached = c.ai_cache.get(h)
    assert cached is not None
    assert cached["is_violation"] is True
    assert cached["category"] == "cybercrime"
    print("[OK] NLP cache checks passed!")

async def test_group_quota():
    print("--- Testing Group Quotas ---")
    c = build_container()
    chat_id = 999111
    
    # 1. Register group and user who added it
    user_id = 888777
    with get_conn() as conn:
        conn.execute("INSERT OR REPLACE INTO groups (chat_id, title, added_by) VALUES (?, ?, ?)", (chat_id, "Test Group", user_id))
    
    # 2. Default plan should be Free (limit 50)
    plan = c.subscriptions.get_group_plan(chat_id)
    assert plan["plan"] == "free", "Should default to free plan"
    
    usage = c.subscriptions.get_ai_usage_today(chat_id)
    assert usage == 0, "Daily usage should be 0 initially"
    
    # 3. Test increment
    c.subscriptions.increment_ai_usage(chat_id)
    usage = c.subscriptions.get_ai_usage_today(chat_id)
    assert usage == 1, "Usage should increment to 1"
    
    # 4. Activate Premium for User
    c.subscriptions.activate_user_premium(user_id, 30, "1 oylik")
    plan = c.subscriptions.get_group_plan(chat_id)
    assert plan["plan"] == "premium", "Group should be premium because creator is premium"
    assert plan["plan_label"] == "1 oylik"
    
    print("[OK] Group quota checks passed!")

async def test_referral_system():
    print("--- Testing Referral System ---")
    c = build_container()
    
    # Register referrer
    c.users.save(999, "Referrer", "ref_user", "998901234567")
    
    # Save a referred user
    c.users.save(888, "Referred User", "ref_u2", "998907654321", referred_by=999)
    
    # Simulate increment
    with get_conn() as conn:
        conn.execute("UPDATE users SET referral_count = referral_count + 1 WHERE user_id = 999")
        
    ref_count = c.users.get_referred_count(999)
    assert ref_count == 1, "Referrer should have 1 referral"
    
    # Test activate user premium with label
    c.subscriptions.activate_user_premium(999, 7, "1 haftalik")
    plan = c.subscriptions.get_user_plan(999)
    assert plan["plan"] == "premium"
    assert plan["plan_label"] == "1 haftalik"
    
    print("[OK] Referral system checks passed!")

async def run_all():
    setup_test_db()
    await test_url_cache()
    await test_nlp_cache()
    await test_group_quota()
    await test_referral_system()
    print("ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_all())
