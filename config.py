"""
配置管理模組

支援環境變數和預設值，優先順序：
1. 環境變數
2. .env 檔案（如果安裝了 python-dotenv）
3. 預設值
"""

import os
from pathlib import Path

# 嘗試載入 .env 檔案（如果安裝了 python-dotenv）
try:
    from dotenv import load_dotenv
    # 明確指定 .env 檔案路徑（相對於此檔案的位置）
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
        # 檢查是否成功載入 API Key（不顯示完整內容）
        api_key = os.getenv('OPENAI_API_KEY', '')
        if api_key:
            print(f"✓ 已載入 .env 檔案: {env_path}")
        else:
            print(f"⚠️  .env 檔案存在但 OPENAI_API_KEY 未設定")
    else:
        # 如果不存在，嘗試當前工作目錄
        load_dotenv(override=True)
except ImportError:
    # 如果沒有安裝 python-dotenv，提示用戶安裝
    print("⚠️  python-dotenv 未安裝，無法載入 .env 檔案")
    print("   請執行: pip install python-dotenv")
except Exception as e:
    print(f"⚠️  載入 .env 檔案時發生錯誤: {e}")


class Config:
    """應用程式配置類別"""
    
    # ==================== OpenAI API 設定 ====================
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')
    OPENAI_MAX_CHUNK_SIZE = int(os.getenv('OPENAI_MAX_CHUNK_SIZE', '500'))
    
    # ==================== Whisper.cpp 路徑設定 ====================
    # 預設路徑（可以透過環境變數覆蓋）
    # 注意：whisper.cpp 已棄用 'main'，改用 'whisper-cli'
    WHISPER_CPP_PATH = os.getenv(
        'WHISPER_CPP_PATH',
        '/Users/waynetu/my_tool_box/whisper.cpp/build/bin/whisper-cli'
    )
    WHISPER_MODEL_PATH = os.getenv(
        'WHISPER_MODEL_PATH',
        '/Users/waynetu/my_tool_box/whisper.cpp/models/ggml-large-v3-turbo.bin'
    )
    
    # ==================== CPU Whisper 設定 ====================
    # 注意：openai-whisper 的模型名稱
    # 可用模型：tiny, base, small, medium, large, turbo
    # turbo 是優化版本，速度更快（預設模型）
    # 參考：https://github.com/openai/whisper
    CPU_WHISPER_MODEL = os.getenv('CPU_WHISPER_MODEL', 'turbo')
    
    # ==================== 預設參數 ====================
    DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'auto')
    DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'turbo')  # 注意：openai-whisper 使用 'turbo'，不是 'large-v3-turbo'
    
    # ==================== 翻譯設定 ====================
    TRANSLATE_CHUNK_SIZE = int(os.getenv('TRANSLATE_CHUNK_SIZE', '500'))
    TRANSLATE_SYSTEM_PROMPT = os.getenv(
        'TRANSLATE_SYSTEM_PROMPT',
        '你是一個翻譯專家，幫我翻譯成{target_language}，禁止使用簡體中文。結果要語句通順且好懂的翻譯結果。只需要輸出翻譯結果'
    )
    
    # ==================== GUI 設定 ====================
    GUI_LANGUAGE = os.getenv('GUI_LANGUAGE', 'en_US')  # 預設繁體中文，可設定為 'en_US' 使用英文
    
    @classmethod
    def validate(cls):
        """
        驗證必要配置是否存在
        
        Returns:
            list: 錯誤訊息列表，如果沒有錯誤則返回空列表
        """
        errors = []
        
        # 檢查 OpenAI API Key（如果使用翻譯功能才需要）
        # 這裡不強制要求，因為可能只使用轉錄功能
        
        # 檢查 whisper.cpp 路徑（如果使用 CoreML 模式才需要）
        if cls.WHISPER_CPP_PATH and not Path(cls.WHISPER_CPP_PATH).exists():
            errors.append(
                f"⚠️  Whisper.cpp 路徑不存在: {cls.WHISPER_CPP_PATH}\n"
                f"   請設定環境變數 WHISPER_CPP_PATH 或檢查路徑是否正確"
            )
        
        # 檢查模型路徑（如果使用 CoreML 模式才需要）
        if cls.WHISPER_MODEL_PATH and not Path(cls.WHISPER_MODEL_PATH).exists():
            errors.append(
                f"⚠️  模型路徑不存在: {cls.WHISPER_MODEL_PATH}\n"
                f"   請設定環境變數 WHISPER_MODEL_PATH 或檢查路徑是否正確"
            )
        
        return errors
    
    @classmethod
    def get_whisper_cpp_path(cls):
        """取得 whisper.cpp 執行檔路徑"""
        return cls.WHISPER_CPP_PATH
    
    @classmethod
    def get_whisper_model_path(cls):
        """取得 whisper 模型路徑"""
        return cls.WHISPER_MODEL_PATH
    
    @classmethod
    def get_openai_api_key(cls):
        """取得 OpenAI API Key"""
        return cls.OPENAI_API_KEY
    
    @classmethod
    def is_openai_configured(cls):
        """檢查 OpenAI 是否已配置"""
        return bool(cls.OPENAI_API_KEY and cls.OPENAI_API_KEY != '')
    
    @classmethod
    def is_whisper_cpp_configured(cls):
        """檢查 whisper.cpp 是否已配置"""
        return (
            Path(cls.WHISPER_CPP_PATH).exists() if cls.WHISPER_CPP_PATH else False
        )
    
    @classmethod
    def print_config(cls):
        """印出當前配置（隱藏敏感資訊）"""
        print("=" * 60)
        print("當前配置")
        print("=" * 60)
        print(f"OpenAI API Key: {'已設定' if cls.is_openai_configured() else '未設定'}")
        print(f"OpenAI Model: {cls.OPENAI_MODEL}")
        print(f"Whisper.cpp 路徑: {cls.WHISPER_CPP_PATH}")
        print(f"  └─ 存在: {'是' if cls.is_whisper_cpp_configured() else '否'}")
        print(f"Whisper 模型路徑: {cls.WHISPER_MODEL_PATH}")
        print(f"  └─ 存在: {'是' if Path(cls.WHISPER_MODEL_PATH).exists() else '否'}")
        print(f"CPU Whisper 模型: {cls.CPU_WHISPER_MODEL}")
        print(f"預設語言: {cls.DEFAULT_LANGUAGE}")
        print("=" * 60)


# 建立全域配置實例
config = Config()

