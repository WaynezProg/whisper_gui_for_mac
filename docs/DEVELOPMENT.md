# 開發文檔

## 專案結構

```
whisper_gui/
├── main.py              # 應用程式入口
├── gui.py               # GUI 主程式（CustomTkinter）
├── actions.py           # 轉錄動作處理
├── ai_translate.py      # AI 翻譯功能
├── requirements.txt     # Python 依賴
├── setup.py            # py2app 打包配置
├── docs/               # 文檔目錄
└── venv/               # 虛擬環境
```

## 技術棧

- **GUI 框架**: CustomTkinter 5.2+
- **Python 版本**: 3.9+（建議使用系統 Python 3.9.6）
- **核心功能**:
  - Whisper 語音轉錄（CoreML / CPU）
  - OpenAI API 翻譯
  - 日文片假名轉換

## 開發環境設定

### 1. 建立虛擬環境

```bash
# 使用系統 Python（推薦）
/usr/bin/python3 -m venv venv
source venv/bin/activate

# 或使用 pyenv Python（需要先解決 tkinter 問題）
python3 -m venv venv
source venv/bin/activate
```

### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

### 3. 啟動應用程式

```bash
python main.py
```

## 已知問題與待辦事項

詳見 [TODO.md](TODO.md) 和 [ISSUES.md](ISSUES.md)

## 遷移記錄

### CustomTkinter 遷移（已完成）

- ✅ 已從 Tkinter 遷移到 CustomTkinter
- ✅ 所有 GUI 元件已更新
- ✅ 檔案列表改用 CTkTextbox + 全域列表管理
- ✅ 進度條更新邏輯已調整

詳見 [CUSTOMTKINTER_MIGRATION_PLAN.md](CUSTOMTKINTER_MIGRATION_PLAN.md)

## 打包應用程式

使用 py2app 打包：

```bash
python setup.py py2app
```

打包後的應用程式會在 `dist/` 目錄中。

## 程式碼規範

- 使用繁體中文註解
- 遵循 PEP 8 風格指南
- 使用 `prettier` 格式化（如果適用）

