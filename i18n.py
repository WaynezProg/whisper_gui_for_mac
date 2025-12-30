"""
Internationalization (i18n) module / 國際化（i18n）模組
Provides multi-language support functionality / 提供多語言支援功能
"""

import json
import os
from pathlib import Path

# Language files directory / 語言文件目錄
LANG_DIR = Path(__file__).parent / "lang"

# Default language / 預設語言
DEFAULT_LANGUAGE = "zh_TW"

# Current language / 當前語言
_current_language = DEFAULT_LANGUAGE
_translations = {}


def get_lang_file(lang_code):
    """
    Get language file path / 取得語言文件路徑
    
    Args:
        lang_code: Language code (e.g., 'en_US', 'zh_TW') / 語言代碼（例如：'en_US'、'zh_TW'）
    
    Returns:
        Path: Path to the language file / 語言文件的路徑
    """
    return LANG_DIR / f"{lang_code}.json"


def load_language(lang_code):
    """
    Load specified language / 載入指定語言
    
    Args:
        lang_code: Language code to load / 要載入的語言代碼
    
    Returns:
        bool: True if loaded successfully, False otherwise / 成功載入返回 True，否則返回 False
    """
    global _current_language, _translations
    
    lang_file = get_lang_file(lang_code)
    
    if not lang_file.exists():
        # If language file doesn't exist, try to use default language / 如果語言文件不存在，嘗試使用預設語言
        if lang_code != DEFAULT_LANGUAGE:
            return load_language(DEFAULT_LANGUAGE)
        # If default language also doesn't exist, return empty dict / 如果預設語言也不存在，返回空字典
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
    """
    Get current language code / 取得當前語言代碼
    
    Returns:
        str: Current language code / 當前語言代碼
    """
    return _current_language


def get_available_languages():
    """
    Get list of available languages / 取得可用的語言列表
    
    Returns:
        dict: Dictionary mapping language codes to language names / 語言代碼到語言名稱的字典
    """
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
    Translation function / 翻譯函數
    
    Args:
        key: Translation key (supports dot-separated nested keys, e.g., 'button.add') / 翻譯鍵值（可以使用點號分隔的嵌套鍵，如 'button.add'）
        default: Default value to return if translation not found / 如果找不到翻譯時返回的預設值
    
    Returns:
        str: Translated text, or key/default if not found / 翻譯後的文字，如果找不到則返回 key 或 default
    """
    global _translations
    
    if not _translations:
        return default if default is not None else key
    
    # Support dot-separated nested keys / 支援點號分隔的嵌套鍵
    keys = key.split('.')
    value = _translations
    
    try:
        for k in keys:
            value = value[k]
        return value if value else (default if default is not None else key)
    except (KeyError, TypeError):
        return default if default is not None else key


# Initialize: Load language setting from config / 初始化：從 config 載入語言設定
try:
    from config import config
    initial_lang = getattr(config, 'GUI_LANGUAGE', DEFAULT_LANGUAGE)
    load_language(initial_lang)
except:
    # If config loading fails, use default language / 如果 config 載入失敗，使用預設語言
    load_language(DEFAULT_LANGUAGE)

