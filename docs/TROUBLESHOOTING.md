# 故障排除指南

## 常見問題與解決方案

### 1. Tkinter 依賴問題

**錯誤訊息**:
```
ImportError: dlopen(...): Library not loaded: /opt/homebrew/opt/tcl-tk/lib/libtk8.6.dylib
```

**原因**: Python（透過 pyenv 安裝）找不到 tcl-tk 系統庫。

**解決方案**:

#### 方案 A: 使用系統 Python（推薦，最快）

```bash
# 重新建立虛擬環境，使用系統 Python
cd /Users/waynetu/my_github_repo/whisper_gui_for_mac
mv venv venv_backup
/usr/bin/python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

#### 方案 B: 安裝 tcl-tk 並重新編譯 Python

```bash
# 安裝 tcl-tk
brew install tcl-tk

# 設定環境變數
export PATH="$(brew --prefix tcl-tk)/bin:$PATH"
export LDFLAGS="-L$(brew --prefix tcl-tk)/lib"
export CPPFLAGS="-I$(brew --prefix tcl-tk)/include"

# 重新編譯 Python（需要 10-20 分鐘）
pyenv install --force 3.12.0
pyenv global 3.12.0
exec $SHELL
```

---

### 2. macOS 版本檢查錯誤

**錯誤訊息**:
```
macOS 26 (2602) or later required, have instead 16 (1602) !
```

**原因**: 某些套件（如 `coremltools`、`ane_transformers`）的版本檢查邏輯與 macOS 26 不兼容。

**解決方案**:

#### 方案 A: 更新套件

```bash
source venv/bin/activate
pip install --upgrade coremltools ane_transformers
```

#### 方案 B: 暫時移除（如果不需要 CoreML 功能）

```bash
source venv/bin/activate
pip uninstall -y coremltools ane_transformers

# 編輯 requirements.txt，註解掉：
# coremltools==7.2
# ane_transformers==0.1.1
```

#### 方案 C: 使用環境變數繞過檢查

```bash
export COREMLTOOLS_SKIP_VERSION_CHECK=1
export ANE_TRANSFORMERS_SKIP_VERSION_CHECK=1
python main.py
```

---

### 3. Python 版本兼容性問題

**錯誤訊息**:
```
ERROR: Could not find a version that satisfies the requirement networkx==3.3
```

**原因**: 某些套件需要 Python >=3.10，但使用的是 Python 3.9。

**解決方案**:

已更新 `requirements.txt`，將不兼容的版本改為 Python 3.9 可用的版本：
- `networkx==3.3` → `networkx==2.8.8`
- `numpy==2.0.0` → `numpy==1.26.4`

如果仍有問題，請使用 `requirements_py39.txt`：
```bash
pip install -r requirements_py39.txt
```

---

### 4. 依賴安裝失敗

**解決方案**:

```bash
# 確保在虛擬環境中
source venv/bin/activate

# 升級 pip
pip install --upgrade pip

# 重新安裝依賴
pip install -r requirements.txt
```

---

### 5. 拖放功能不工作

**原因**: `tkinterdnd2` 與 CustomTkinter 的相容性問題。

**解決方案**:

1. 檢查終端機是否有錯誤訊息
2. 如果拖放不工作，可以使用「添加」按鈕選擇檔案
3. 未來可以考慮改用其他拖放方案

---

### 6. Segmentation Fault（段錯誤）

**錯誤訊息**:
```
[1] 84328 segmentation fault  python main.py
```

**可能原因**:

1. **檔案路徑包含特殊字元**（如日文字元）
   - whisper.cpp 可能無法正確處理 Unicode 路徑
   - 已在 `actions.py` 中自動處理，會複製到臨時檔案

2. **whisper.cpp 執行檔問題**
   - 編譯不完整
   - 與系統不兼容
   - 記憶體問題

3. **模型檔案問題**
   - 模型檔案損壞
   - 模型格式不正確

4. **GUI 線程問題**
   - 從非主線程直接操作 GUI 組件
   - 已在 `gui.py` 中使用 `root.after()` 修正

**解決方案**:

#### 方案 A: 使用 CPU 模式（推薦，最穩定）

如果 CoreML 模式有問題，可以暫時使用 CPU 模式：
- 在 GUI 中點擊「CPU 執行」而不是「CoreML 執行」
- CPU 模式功能相同，但較慢但更穩定

#### 方案 B: 檢查 whisper.cpp 執行檔

```bash
# 檢查執行檔
file /path/to/whisper.cpp/build/bin/whisper-cli

# 測試執行
/path/to/whisper.cpp/build/bin/whisper-cli -h

# 如果無法執行，可能需要重新編譯
cd /path/to/whisper.cpp
make clean
WHISPER_COREML=1 make -j
```

#### 方案 C: 檢查檔案路徑

如果檔案路徑包含特殊字元，程式會自動處理，但也可以手動複製到簡單路徑：

```bash
# 複製到簡單路徑
cp "/path/to/複雜檔名.mp4" /tmp/input.mp4
```

**診斷步驟**:

1. **檢查配置**
   ```bash
   python check_config.py
   ```

2. **手動測試 whisper.cpp**
   ```bash
   /path/to/whisper.cpp/build/bin/whisper-cli -m /path/to/model.bin /path/to/audio.wav -osrt -of output -l ja
   ```

3. **檢查記憶體**
   - 確保有足夠的記憶體
   - 大模型可能需要大量記憶體

---

### 7. Whisper.cpp 執行失敗（退出碼 1）

**錯誤訊息**:
```
WARNING: The binary 'main' is deprecated.
Please use 'whisper-cli' instead.
Whisper 執行失敗 (退出碼: 1)
```

**原因**: 使用了已棄用的 `main` 執行檔，應改用 `whisper-cli`。

**解決方案**:

1. **確認使用正確的執行檔**
   - 舊版本：`whisper.cpp/main`
   - 新版本：`whisper.cpp/build/bin/whisper-cli`

2. **更新配置**
   ```env
   # .env 檔案
   WHISPER_CPP_PATH=/path/to/whisper.cpp/build/bin/whisper-cli
   ```

3. **檢查參數格式**
   - `whisper-cli` 的檔案參數應直接傳遞，不使用 `-f`
   - 正確格式：`whisper-cli [options] file0 file1 ...`

---

### 8. Whisper.cpp 與 CoreML 說明

#### 核心概念

**Whisper.cpp** 是一個**需要編譯的 C++ 專案**，不是 macOS 系統內建的庫。它是一個獨立的可執行檔（binary executable）。

**CoreML** 是 **macOS/iOS 系統內建的框架**，用於機器學習推理。它已經包含在 macOS 中，不需要額外安裝。

#### 工作流程

1. **Whisper.cpp 的編譯與安裝**
   ```bash
   # 下載源碼
   git clone https://github.com/ggerganov/whisper.cpp.git
   cd whisper.cpp
   
   # 編譯支援 CoreML 的版本
   cmake -B build -DWHISPER_COREML=1
   cmake --build build -j --config Release
   ```
   
   編譯結果會產生 `build/bin/whisper-cli` 可執行檔。

2. **下載模型檔案**
   ```bash
   cd models
   ./download-ggml-model.sh large-v3
   ```

3. **在程式碼中的使用**
   - 透過 `subprocess.run()` 調用 `whisper-cli` 執行檔
   - 已在 `actions.py` 中實作

#### 與 CPU 模式的對比

**CoreML 模式（使用 whisper.cpp）**:
- ✅ 需要編譯 whisper.cpp
- ✅ 需要模型檔案
- ✅ 使用 Apple Silicon 的 Neural Engine（更快）
- ✅ 需要手動管理路徑

**CPU 模式（使用 openai-whisper）**:
- ✅ 透過 pip 安裝即可
- ✅ 不需要編譯
- ✅ 使用 CPU 運算（較慢）
- ✅ 自動管理依賴

---

## 診斷工具

### 診斷導入問題

```bash
source venv/bin/activate
python diagnose_import.py
```

### 測試各個模組

```bash
# 測試 tkinter
python -c "import tkinter; print('✓ Tkinter 可用')"

# 測試 customtkinter
python -c "import customtkinter; print('✓ CustomTkinter 可用')"

# 測試所有依賴
python -c "import actions; import ai_translate; print('✓ 所有模組可用')"
```

---

## 快速修復流程

如果遇到問題，按以下順序嘗試：

1. **重新建立虛擬環境**（最徹底）
   ```bash
   mv venv venv_backup
   /usr/bin/python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **更新有問題的套件**
   ```bash
   pip install --upgrade coremltools customtkinter
   ```

3. **暫時移除問題套件**（如果不需要相關功能）
   ```bash
   pip uninstall -y coremltools ane_transformers
   ```

4. **檢查錯誤訊息**，根據具體錯誤調整

---

## 參考資源

- [CustomTkinter 官方文檔](https://customtkinter.tomschimansky.com/)
- [Python tkinter 文檔](https://docs.python.org/3/library/tkinter.html)
- [pyenv 官方文檔](https://github.com/pyenv/pyenv)

