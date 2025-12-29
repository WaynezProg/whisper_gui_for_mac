# 配置說明

## 概述

專案使用 `config.py` 統一管理所有配置，支援以下方式設定：

1. **環境變數**（優先順序最高）
2. **.env 檔案**（如果安裝了 `python-dotenv`）
3. **預設值**（在 `config.py` 中定義）

## 快速開始

### 方法一：使用 .env 檔案（推薦）

1. **複製範例檔案**
   ```bash
   cp env.example .env
   ```

2. **編輯 .env 檔案**
   ```bash
   # 使用你喜歡的編輯器
   nano .env
   # 或
   code .env
   ```

3. **填入你的配置**
   ```env
   OPENAI_API_KEY=sk-your-actual-api-key-here
   WHISPER_CPP_PATH=/Users/yourname/whisper.cpp/main
   WHISPER_MODEL_PATH=/Users/yourname/whisper.cpp/models/ggml-large-v3.bin
   ```

4. **確認 .env 已加入 .gitignore**（已預設加入）

### 方法二：使用環境變數

```bash
# 在終端機中設定
export OPENAI_API_KEY='sk-your-api-key-here'
export WHISPER_CPP_PATH='/Users/yourname/whisper.cpp/main'
export WHISPER_MODEL_PATH='/Users/yourname/whisper.cpp/models/ggml-large-v3.bin'

# 啟動應用程式
python main.py
```

### 方法三：直接修改 config.py（不推薦）

如果不想使用環境變數，可以直接修改 `config.py` 中的預設值：

```python
# config.py
WHISPER_CPP_PATH = '/Users/yourname/whisper.cpp/main'
WHISPER_MODEL_PATH = '/Users/yourname/whisper.cpp/models/ggml-large-v3.bin'
```

**注意**: 這種方式不建議，因為會將敏感資訊提交到 Git。

---

## 配置項目說明

### OpenAI API 設定

| 變數名稱 | 說明 | 預設值 | 必填 |
|---------|------|--------|------|
| `OPENAI_API_KEY` | OpenAI API Key | `''` | 翻譯功能需要 |
| `OPENAI_MODEL` | 使用的 OpenAI 模型 | `gpt-4o` | 否 |
| `OPENAI_MAX_CHUNK_SIZE` | 翻譯時每段文字的最大字數 | `500` | 否 |

**取得 API Key**:
1. 前往 https://platform.openai.com/api-keys
2. 登入你的帳號
3. 建立新的 API Key
4. 複製並貼到 `.env` 檔案中

### Whisper.cpp 路徑設定

| 變數名稱 | 說明 | 預設值 | 必填 |
|---------|------|--------|------|
| `WHISPER_CPP_PATH` | whisper.cpp 執行檔路徑 | `/Users/waynetu/...` | CoreML 模式需要 |
| `WHISPER_MODEL_PATH` | Whisper 模型檔案路徑 | `/Users/waynetu/...` | CoreML 模式需要 |

**設定路徑**:
```env
# 範例（注意：新版本使用 whisper-cli，不是 main）
WHISPER_CPP_PATH=/Users/yourname/whisper.cpp/build/bin/whisper-cli
WHISPER_MODEL_PATH=/Users/yourname/whisper.cpp/models/ggml-large-v3.bin
```

**重要**: whisper.cpp 新版本已棄用 `main`，改用 `whisper-cli`。執行檔位置通常在 `build/bin/whisper-cli`。

---

## 詳細設定步驟

### 步驟 1: 複製範例檔案

```bash
cd /Users/waynetu/my_github_repo/whisper_gui
cp env.example .env
```

### 步驟 2: 編輯 .env 檔案

```bash
# 使用你喜歡的編輯器
nano .env
# 或
code .env
# 或
open -e .env
```

### 步驟 3: 填入你的路徑

編輯 `.env` 檔案，修改以下兩行：

```env
# whisper.cpp 執行檔的完整路徑（注意：使用 whisper-cli，不是 main）
WHISPER_CPP_PATH=/Users/yourname/whisper.cpp/build/bin/whisper-cli

# Whisper 模型檔案的完整路徑
WHISPER_MODEL_PATH=/Users/yourname/whisper.cpp/models/ggml-large-v3.bin
```

### 步驟 4: 檢查路徑是否正確

```bash
# 檢查執行檔是否存在
ls -la /Users/yourname/whisper.cpp/build/bin/whisper-cli

# 檢查模型檔案是否存在
ls -la /Users/yourname/whisper.cpp/models/ggml-large-v3.bin
```

### 步驟 5: 驗證配置

```bash
python check_config.py
```

---

## 如何找到你的路徑

### 找到 whisper.cpp 執行檔

```bash
# 如果你知道 whisper.cpp 在哪裡
find ~ -name "whisper.cpp" -type d 2>/dev/null

# 檢查常見位置
ls -la ~/whisper.cpp/build/bin/whisper-cli
ls -la /opt/whisper.cpp/build/bin/whisper-cli

# 或搜尋 whisper-cli
find ~ -name "whisper-cli" -type f 2>/dev/null
```

### 找到模型檔案

```bash
# 在 whisper.cpp 目錄下
ls -la ~/whisper.cpp/models/

# 或搜尋
find ~ -name "ggml-large-v3.bin" 2>/dev/null
```

### 下載模型檔案

如果沒有模型檔案，可以下載：

```bash
cd /path/to/whisper.cpp/models
./download-ggml-model.sh large-v3
```

---

## 常見問題

### Q: 我不知道我的 whisper.cpp 在哪裡

A: 執行以下指令尋找：
```bash
find ~ -name "whisper-cli" -type f 2>/dev/null
```

### Q: 我沒有編譯 whisper.cpp

A: 參考 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) 中的「Whisper.cpp 與 CoreML 說明」章節，或使用 CPU 模式（不需要 whisper.cpp）。

### Q: 我沒有模型檔案

A: 參考上面的「下載模型檔案」步驟，或使用 CPU 模式（會自動下載模型）。

### Q: 我想使用 CPU 模式，還需要設定這些路徑嗎？

A: 不需要。CPU 模式不需要 whisper.cpp，只需要安裝 `openai-whisper`（已包含在 requirements.txt 中）。

### Q: 為什麼找不到 `main` 執行檔？

A: whisper.cpp 新版本已棄用 `main`，改用 `whisper-cli`。執行檔位置在 `build/bin/whisper-cli`。

---

### CPU Whisper 設定

| 變數名稱 | 說明 | 預設值 | 必填 |
|---------|------|--------|------|
| `CPU_WHISPER_MODEL` | CPU 模式使用的模型 | `turbo` | 否 |

**可用模型**:
- `tiny` - 最快，準確度最低
- `base` - 快速
- `small` - 平衡
- `medium` - 較慢，較準確
- `large` - 慢，準確
- `large-v2` - 更準確
- `large-v3` - 最準確（推薦）

### 翻譯設定

| 變數名稱 | 說明 | 預設值 | 必填 |
|---------|------|--------|------|
| `TRANSLATE_CHUNK_SIZE` | 翻譯時每段文字的最大字數 | `500` | 否 |
| `TRANSLATE_SYSTEM_PROMPT` | 翻譯系統提示詞 | 自動生成 | 否 |

---

## 驗證配置

### 在 Python 中驗證

```python
from config import config

# 檢查配置
errors = config.validate()
if errors:
    for error in errors:
        print(error)
else:
    print("✓ 配置正確")

# 印出當前配置（隱藏敏感資訊）
config.print_config()
```

### 在應用程式中驗證

啟動應用程式時，如果配置有問題，會顯示錯誤訊息。

---

## 配置優先順序

1. **環境變數** - 最高優先順序
2. **.env 檔案** - 如果安裝了 `python-dotenv`
3. **config.py 預設值** - 最低優先順序

**範例**:
```bash
# 環境變數
export WHISPER_CPP_PATH='/path/from/env'

# .env 檔案
WHISPER_CPP_PATH=/path/from/envfile

# config.py
WHISPER_CPP_PATH = '/path/from/config'
```

結果: 使用 `/path/from/env`（環境變數優先）

---

## 安全注意事項

### ✅ 應該做的

1. **使用 .env 檔案**
   - `.env` 已加入 `.gitignore`
   - 不會被提交到 Git

2. **使用環境變數**
   - 適合 CI/CD 環境
   - 不會出現在程式碼中

3. **使用 `env.example`**
   - 提供範例配置
   - 不包含真實的 API Key

### ❌ 不應該做的

1. **不要在程式碼中硬編碼 API Key**
   ```python
   # ❌ 錯誤
   api_key = 'sk-xxx'
   ```

2. **不要提交 .env 檔案**
   - 確認 `.gitignore` 包含 `.env`

3. **不要在公開場所分享 API Key**
   - 不要在 Issue、Pull Request 中分享
   - 不要在社群媒體上分享

---

## 常見問題

### Q: 如何知道配置是否正確？

A: 執行以下指令：
```python
from config import config
config.print_config()
```

### Q: 為什麼我的配置沒有生效？

A: 檢查優先順序：
1. 確認環境變數是否設定
2. 確認 .env 檔案是否存在且格式正確
3. 確認 config.py 中的預設值

### Q: 可以同時使用多種配置方式嗎？

A: 可以，但環境變數優先順序最高。

### Q: 如何在不同環境使用不同配置？

A: 使用不同的 .env 檔案：
```bash
# 開發環境
cp .env.development .env

# 生產環境
cp .env.production .env
```

---

## 參考資源

- [python-dotenv 文檔](https://github.com/theskumar/python-dotenv)
- [環境變數最佳實踐](https://12factor.net/config)

