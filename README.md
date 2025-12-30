# Whisper Transcription and Translation GUI
[![Demo Video](https://img.youtube.com/vi/2BLUM1b18Dg/0.jpg)](https://youtu.be/2BLUM1b18Dg)

## 📖 介紹

這是一個基於 Whisper 的語音轉錄和翻譯 GUI 應用程式，支援 **CoreML** 和 **CPU** 兩種模式。使用者可以添加音頻文件進行轉錄，並將結果翻譯成多種語言。

### 主要功能

- 🎤 **語音轉錄**: 支援 CoreML 加速（Apple Silicon）和 CPU 模式
- 🌍 **多語言支援**: 自動檢測語言或手動指定
- 🔄 **AI 翻譯**: 使用 OpenAI API 翻譯轉錄結果
- 🇯🇵 **日文處理**: 日文字幕轉換為片假名
- 📁 **批量處理**: 支援單個檔案、多個檔案或整個資料夾
- 🎨 **現代化 UI**: 使用 CustomTkinter，支援深色/淺色主題

---

## 🚀 快速開始

### 前置條件

- **macOS** (建議 macOS 12+)
- **Python 3.9+** (建議使用系統 Python 3.9.6)
- **Xcode Command Line Tools** (用於編譯 whisper.cpp)

### 安裝步驟

#### 1. 克隆專案

```bash
git clone <repository-url>
cd whisper_gui_for_mac
```

#### 2. 建立虛擬環境

```bash
# 使用系統 Python（推薦）
/usr/bin/python3 -m venv venv
source venv/bin/activate

# 或使用 pyenv Python
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安裝 Python 依賴

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. 安裝系統工具（如果需要 CoreML 功能）

```bash
# 安裝 Xcode Command Line Tools
xcode-select --install

# 安裝 ffmpeg（用於音頻轉換）
brew install ffmpeg
```

#### 5. 安裝和編譯 whisper.cpp（CoreML 模式需要）

> **注意**: 如果只需要使用 CPU 模式，可以跳過此步驟。

##### 5.1 下載 whisper.cpp

```bash
# 選擇一個目錄存放 whisper.cpp（建議放在專案外部）
cd ~
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
```

##### 5.2 編譯支援 CoreML 的版本

    ```bash
# 使用 Makefile（推薦）
    make clean
    WHISPER_COREML=1 make -j

# 或使用 CMake
    cmake -B build -DWHISPER_COREML=1
    cmake --build build -j --config Release
    ```

編譯完成後，可執行檔會在：
- Makefile: `./main`
- CMake: `./build/bin/main`

##### 5.3 下載模型檔案

```bash
# 下載 GGML 模型（以 large-v3 為例）
cd models
bash download-ggml-model.sh large-v3

# 或手動下載
# 從 https://huggingface.co/ggerganov/whisper.cpp 下載對應的 .bin 檔案
```

##### 5.4 生成 CoreML 模型（可選，但建議）

    ```bash
# 在 whisper.cpp 目錄下
cd models
bash generate-coreml-model.sh large-v3
```

這會生成 CoreML 格式的模型檔案，可以加速推理。

#### 6. 配置應用程式

專案使用 `config.py` 統一管理配置，支援環境變數和 `.env` 檔案。

**方法一：使用 .env 檔案（推薦）**

```bash
# 複製範例檔案
cp env.example .env

# 編輯 .env 檔案，填入你的配置
nano .env
```

在 `.env` 檔案中設定：

```env
# OpenAI API Key（翻譯功能需要）
OPENAI_API_KEY=sk-your-api-key-here

# Whisper.cpp 路徑（CoreML 模式需要）
WHISPER_CPP_PATH=/Users/yourname/whisper.cpp/main
WHISPER_MODEL_PATH=/Users/yourname/whisper.cpp/models/ggml-large-v3.bin
```

**方法二：使用環境變數**

```bash
export OPENAI_API_KEY='sk-your-api-key-here'
export WHISPER_CPP_PATH='/Users/yourname/whisper.cpp/main'
export WHISPER_MODEL_PATH='/Users/yourname/whisper.cpp/models/ggml-large-v3.bin'
```

**檢查配置**

```bash
python check_config.py
```

**詳細配置說明**: 請參考 [docs/CONFIGURATION.md](docs/CONFIGURATION.md)

---

## 🎯 使用方法

### 啟動應用程式

**方法一：雙擊執行（最簡單，推薦）**
- 雙擊 `Whisper_GUI.command` 檔案即可啟動
- 首次執行時，macOS 可能會提示安全性，請在「系統偏好設定 > 安全性與隱私」中允許執行
- 腳本會自動偵測 `venv` 或 `.venv` 虛擬環境

**方法二：使用啟動腳本**
```bash
./run.sh
```

**方法三：手動啟動**
```bash
source venv/bin/activate  # 或 source .venv/bin/activate
python main.py
```

### GUI 功能說明

#### 基本操作

1. **添加音頻文件**
   - 點擊「添加」按鈕選擇檔案
   - 點擊「添加資料夾」按鈕選擇整個資料夾
   - 支援 `.wav` 和 `.mp4` 格式

2. **選擇語言**
   - 在「拼讀語言」下拉框中選擇語言
   - 選擇「auto」可自動檢測語言

3. **執行轉錄**
   - **CoreML 執行**: 使用 CoreML 加速（需要 whisper.cpp）
   - **CPU 執行**: 使用 CPU 模式（使用 openai-whisper）

4. **翻譯結果**
   - 點擊「翻譯」按鈕
   - 選擇目標語言
   - 需要設定 OpenAI API Key

5. **其他功能**
   - **日文轉片假名**: 將日文字幕轉換為片假名
   - **暫停任務**: 暫停當前執行的任務

#### 輸出檔案命名規則

轉錄完成後，會在音頻檔案同目錄下生成：
- **CoreML 模式**: `filename_coreml.srt`
- **CPU 模式**: `filename_cpu.srt`

翻譯完成後，會生成：
- `filename_語言名稱.srt` - 例如：`filename_英文.srt`、`filename_中文.srt`

片假名轉換後，會生成：
- `filename_katakana.srt`

**注意**: 如果檔案已存在，會自動添加數字後綴（例如：`filename_coreml_1.srt`），避免覆寫現有檔案。

---

## ⚙️ 配置說明

### 模式選擇

#### CoreML 模式（推薦，Apple Silicon）

**優點**:
- ✅ 使用 Apple Neural Engine，速度快
- ✅ 功耗低
- ✅ 適合長時間處理

**需求**:
- ✅ 需要編譯 whisper.cpp
- ✅ 需要下載模型檔案
- ✅ 需要設定路徑

#### CPU 模式

**優點**:
- ✅ 安裝簡單（只需 `pip install openai-whisper`）
- ✅ 不需要編譯
- ✅ 跨平台

**缺點**:
- ❌ 速度較慢
- ❌ 功耗較高

---

## 🔧 故障排除

### 常見問題

#### 1. Tkinter 依賴問題

**錯誤**: `ImportError: Library not loaded: libtk8.6.dylib`

**解決方案**:
```bash
# 使用系統 Python 重新建立虛擬環境
mv venv venv_backup
/usr/bin/python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. whisper.cpp 找不到

**錯誤**: `FileNotFoundError: whisper.cpp/main`

**解決方案**:
- 檢查 `actions.py` 中的路徑是否正確
- 確認 whisper.cpp 已編譯完成
- 確認執行檔有執行權限：`chmod +x /path/to/whisper.cpp/main`

#### 3. 模型檔案找不到

**錯誤**: `Error: model file not found`

**解決方案**:
- 確認模型檔案路徑正確
- 確認模型檔案已下載
- 檢查檔案權限

#### 4. CoreML 功能不可用

**錯誤**: macOS 版本檢查錯誤

**解決方案**:
```bash
# 更新 coremltools
pip install --upgrade coremltools

# 或暫時移除（如果不需要）
pip uninstall coremltools
```

#### 5. 翻譯功能不可用

**錯誤**: OpenAI API 錯誤

**解決方案**:
- 檢查 API Key 是否正確設定
- 確認網路連線正常
- 檢查 API 額度是否足夠

#### 6. 使用故障排除腳本

如果遇到問題，可以使用內建的故障排除腳本：

```bash
./fix.sh
```

腳本提供以下選項：
1. 修復 Tkinter 依賴問題
2. 修復 CoreMLTools 兼容性問題
3. 安裝 python-dotenv
4. 檢查配置
5. 重新安裝所有依賴

### 詳細故障排除

更多問題請參考 [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## 📚 文檔

- [文檔索引](docs/README.md) - 所有文檔的導航頁面
- [配置說明](docs/CONFIGURATION.md) - 詳細的配置指南
- [故障排除指南](docs/TROUBLESHOOTING.md) - 常見問題解決方案
- [開發文檔](docs/DEVELOPMENT.md) - 開發環境設定與專案結構
- [日誌系統](docs/LOGGING.md) - 日誌功能說明
- [已知問題](docs/ISSUES.md) - 技術債務與已知問題追蹤

---

## 🛠️ 開發

### 專案結構

```
whisper_gui_for_mac/
├── main.py              # 應用程式入口
├── gui.py               # GUI 主程式（CustomTkinter）
├── actions.py           # 轉錄動作處理（CoreML/CPU）
├── ai_translate.py      # AI 翻譯功能
├── config.py            # 配置管理（環境變數、.env）
├── logger.py            # 日誌系統
├── check_config.py      # 配置檢查工具
├── requirements.txt     # Python 依賴
├── env.example          # 環境變數範例
├── run.sh               # 啟動腳本
├── fix.sh               # 故障排除腳本
├── Whisper_GUI.command  # 雙擊執行檔案（macOS）
├── docs/                # 文檔目錄
│   ├── README.md        # 文檔索引
│   ├── CONFIGURATION.md # 配置說明
│   ├── TROUBLESHOOTING.md # 故障排除
│   ├── DEVELOPMENT.md   # 開發文檔
│   ├── LOGGING.md       # 日誌說明
│   └── ISSUES.md        # 已知問題
└── logs/                # 日誌檔案目錄
```

### 技術棧

- **GUI 框架**: CustomTkinter 5.2+
- **Python 版本**: 3.9+（建議使用系統 Python）
- **核心功能**:
  - Whisper 語音轉錄（CoreML / CPU）
  - OpenAI API 翻譯
  - 日文片假名轉換

### 開發環境設定

詳見 [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

---

## 📝 授權

MIT License

---

## 👤 開發者

製作: Wayne

---

## 🙏 致謝

- [whisper.cpp](https://github.com/ggerganov/whisper.cpp) - 高效的 Whisper 實作
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - 現代化 GUI 框架
- [OpenAI Whisper](https://github.com/openai/whisper) - 語音轉錄模型

---

## 📞 支援

如果遇到問題或有建議，請：
1. 查看 [故障排除指南](docs/TROUBLESHOOTING.md)
2. 檢查 [已知問題](docs/ISSUES.md)
3. 提交 Issue 或 Pull Request

---

## 🔄 更新日誌

### 最新版本

- ✅ 遷移到 CustomTkinter（現代化 UI）
- ✅ 日文片假名轉換功能
- ✅ 改進錯誤處理
- ✅ 完整的文檔

---

## ⚠️ 注意事項

1. **API Key 安全**: 請勿將 API Key 提交到公開倉庫，使用 `.env` 檔案管理
2. **模型檔案大小**: Whisper 模型檔案較大（數 GB），請確保有足夠空間
3. **編譯時間**: 編譯 whisper.cpp 可能需要 10-20 分鐘
4. **系統需求**: CoreML 模式需要 Apple Silicon（M1/M2/M3）或支援 CoreML 的 Mac
5. **外部依賴**: 應用程式需要用戶自行安裝和配置 `whisper.cpp` 和模型檔案，這些外部資源不會被打包到應用程式中

---

## 🎓 學習資源

- [Whisper.cpp 官方文檔](https://github.com/ggerganov/whisper.cpp)
- [CustomTkinter 文檔](https://customtkinter.tomschimansky.com/)
- [OpenAI Whisper 文檔](https://github.com/openai/whisper)
