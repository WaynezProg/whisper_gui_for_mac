"""
國際化（i18n）模組
提供多語言支援功能
"""

import json
import os
from pathlib import Path

# 語言文件目錄
LANG_DIR = Path(__file__).parent / "lang"

# 預設語言
DEFAULT_LANGUAGE = "zh_TW"

# 當前語言
_current_language = DEFAULT_LANGUAGE
_translations = {}


def get_lang_file(lang_code):
    """取得語言文件路徑"""
    return LANG_DIR / f"{lang_code}.json"


def load_language(lang_code):
    """載入指定語言"""
    global _current_language, _translations
    
    lang_file = get_lang_file(lang_code)
    
    if not lang_file.exists():
        # 如果語言文件不存在，嘗試使用預設語言
        if lang_code != DEFAULT_LANGUAGE:
            return load_language(DEFAULT_LANGUAGE)
        # 如果預設語言也不存在，返回空字典
        _translations = {}
        _current_language = lang_code
        return False
    
    try:
        with open(lang_file, 'r', encoding='utf-8') as f:
            _translations = json.load(f)
        _current_language = lang_code
        return True
    except Exception as e:
        print(f"Error loading language file {lang_file}: {e}")
        _translations = {}
        _current_language = lang_code
        return False


def get_current_language():
    """取得當前語言代碼"""
    return _current_language


def get_available_languages():
    """取得可用的語言列表"""
    languages = {}
    if LANG_DIR.exists():
        for lang_file in LANG_DIR.glob("*.json"):
            lang_code = lang_file.stem
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    lang_data = json.load(f)
                    languages[lang_code] = lang_data.get('language_name', lang_code)
            except:
                pass
    return languages


def t(key, default=None):
    """
    翻譯函數
    
    Args:
        key: 翻譯鍵值（可以使用點號分隔的嵌套鍵，如 'button.add'）
        default: 如果找不到翻譯時返回的預設值
    
    Returns:
        翻譯後的文字，如果找不到則返回 key 或 default
    """
    global _translations
    
    if not _translations:
        return default if default is not None else key
    
    # 支援點號分隔的嵌套鍵
    keys = key.split('.')
    value = _translations
    
    try:
        for k in keys:
            value = value[k]
        return value if value else (default if default is not None else key)
    except (KeyError, TypeError):
        return default if default is not None else key


# 初始化：從 config 載入語言設定
try:
    from config import config
    initial_lang = getattr(config, 'GUI_LANGUAGE', DEFAULT_LANGUAGE)
    load_language(initial_lang)
except:
    # 如果 config 載入失敗，使用預設語言
    load_language(DEFAULT_LANGUAGE)

