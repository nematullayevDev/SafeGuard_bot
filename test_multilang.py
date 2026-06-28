import sys
import os

# Set mock environment variables
os.environ["BOT_TOKEN"] = "123456:mock_token"
os.environ["VIRUSTOTAL_API_KEY"] = "mock_vt_api_key"
os.environ["ADMIN_ID"] = "123456"
os.environ["BOT_USERNAME"] = "safeguard_uz_bot"

# Add workspace directory to python path
sys.path.append(r"C:\Users\user\.gemini\antigravity\scratch\SafeGuard_bot")

import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

from app.repositories.schema import init_schema
from app.repositories import UserRepository, GroupRepository
from app.views.texts import get_text
from app.views import formatters, keyboards

def test_translation_texts():
    print("=== Testing Translation Texts (get_text) ===")
    
    # 1. Test Welcome text in 4 languages
    langs = ["uz", "uz_cyr", "ru", "en"]
    for lang in langs:
        wel = get_text("welcome", lang)
        print(f"Lang '{lang}': welcome text exists: {bool(wel)} (length={len(wel)})")
        assert wel, f"Welcome text missing for lang: {lang}"
        assert "{name}" in wel, f"Welcome text for {lang} does not contain {{name}}"
        
    # 2. Test fallback language
    fallback = get_text("welcome", "nonexistent_lang")
    assert fallback == get_text("welcome", "uz"), "Fallback should be 'uz'"
    print("All translation text checks passed successfully!\n")


def test_localized_formatters():
    print("=== Testing Localized Formatters ===")
    
    # 1. Test group settings text
    filters = {"filter_links": True, "filter_files": False, "filter_nlp": True}
    g_settings = {"warnings_limit": 3, "custom_keywords": "spam,reklama", "whitelisted_domains": "google.com", "language": "ru"}
    
    res_ru = formatters.group_settings_text("Test Group", filters, g_settings, lang="ru")
    print(f"Group Settings (ru):\n{res_ru}\n")
    assert "Настройки Защиты" in res_ru
    assert "Лимит Предупреждений" in res_ru
    assert "Активен" in res_ru
    
    res_en = formatters.group_settings_text("Test Group", filters, g_settings, lang="en")
    print(f"Group Settings (en):\n{res_en}\n")
    assert "Group Protection Settings" in res_en
    assert "Warnings Limit" in res_en
    assert "Active" in res_en

    # 2. Test Quiz Result text
    res_passed_uz = formatters.quiz_result_text(score=5, passed=True, lang="uz")
    print(f"Quiz Result passed (uz):\n{res_passed_uz}\n")
    assert "PASS — TABRIKLAYMIZ!" in res_passed_uz
    
    res_failed_cyr = formatters.quiz_result_text(score=2, passed=False, lang="uz_cyr")
    print(f"Quiz Result failed (uz_cyr):\n{res_failed_cyr}\n")
    assert "FAILED — Қайтадан уриниб кўринг" in res_failed_cyr
    
    print("Localized formatters checks passed successfully!\n")


def test_localized_keyboards():
    print("=== Testing Localized Keyboards ===")
    
    # 1. Test main menu
    kb_uz = keyboards.main_menu(is_admin_user=False, lang="uz")
    buttons_uz = [btn.text for row in kb_uz.inline_keyboard for btn in row]
    print(f"Main Menu Buttons (uz): {buttons_uz}")
    assert "🚫 Spam Filter" in buttons_uz
    assert "📋 Qora Ro'yxat" in buttons_uz
    
    kb_ru = keyboards.main_menu(is_admin_user=False, lang="ru")
    buttons_ru = [btn.text for row in kb_ru.inline_keyboard for btn in row]
    print(f"Main Menu Buttons (ru): {buttons_ru}")
    assert "📋 Черный Список" in buttons_ru
    assert "🌐 Сменить язык" in buttons_ru
    
    # 2. Test Group settings keyboard
    filters = {"filter_links": True, "filter_files": True, "filter_nlp": True}
    g_settings = {"warnings_limit": 3, "language": "en"}
    kb_gset = keyboards.group_settings_kb(12345, filters, g_settings, lang="en")
    buttons_gset = [btn.text for row in kb_gset.inline_keyboard for btn in row]
    print(f"Group Settings Buttons (en): {buttons_gset}")
    assert "🔗 Links" in buttons_gset
    assert "✅ Whitelist" in buttons_gset
    assert "English 🇬🇧" in buttons_gset
    
    print("Localized keyboards checks passed successfully!\n")


def test_database_language_integration():
    print("=== Testing Database Language Integration ===")
    init_schema()
    
    user_repo = UserRepository()
    group_repo = GroupRepository()
    
    test_user_id = 999111222
    test_chat_id = -100888777
    
    # 1. Save user with a language and check
    user_repo.save(test_user_id, "Test User", "test_user", "+998901234567", language="ru")
    saved_lang = user_repo.get_language(test_user_id)
    print(f"Saved User Language: '{saved_lang}' (Expected: 'ru')")
    assert saved_lang == "ru"
    
    # Update language
    user_repo.set_language(test_user_id, "en")
    updated_lang = user_repo.get_language(test_user_id)
    print(f"Updated User Language: '{updated_lang}' (Expected: 'en')")
    assert updated_lang == "en"
    
    # 2. Set group language and check
    group_repo.save(test_chat_id, "Test Chat", "", "", 0)
    group_repo.set_language(test_chat_id, "uz_cyr")
    
    g_settings = group_repo.get_custom_settings(test_chat_id)
    saved_group_lang = g_settings.get("language", "uz")
    print(f"Saved Group Language: '{saved_group_lang}' (Expected: 'uz_cyr')")
    assert saved_group_lang == "uz_cyr"
    
    # Clean up test rows
    from app.repositories.base import get_conn
    with get_conn() as conn:
        conn.execute("DELETE FROM users WHERE user_id = ?", (test_user_id,))
        conn.execute("DELETE FROM groups WHERE chat_id = ?", (test_chat_id,))
        conn.execute("DELETE FROM group_settings WHERE chat_id = ?", (test_chat_id,))
        
    print("Database language integration checks passed successfully!\n")


if __name__ == "__main__":
    try:
        test_translation_texts()
        test_localized_formatters()
        test_localized_keyboards()
        test_database_language_integration()
        print("ALL MULTI-LANGUAGE TESTS PASSED SUCCESSFULLY!")
    except Exception as e:
        print(f"TEST FAILURE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
