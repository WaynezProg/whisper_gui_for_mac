# 日誌系統說明

## 概述

Whisper GUI 現在具備完整的日誌功能，可以追蹤應用程式的執行過程，幫助除錯和監控。

## 日誌輸出位置

### 1. 控制台輸出（彩色）
- 執行應用程式時，日誌會即時顯示在終端機
- 不同級別使用不同顏色：
  - **DEBUG**: 青色
  - **INFO**: 綠色
  - **WARNING**: 黃色
  - **ERROR**: 紅色
  - **CRITICAL**: 紫色

### 2. 檔案輸出
- 日誌檔案位置：`logs/whisper_gui_YYYYMMDD.log`
- 每天自動建立一個新的日誌檔案
- 檔案包含完整的執行資訊，包括函數名稱和行號

## 日誌級別

- **DEBUG**: 詳細的除錯資訊（檔案路徑、指令參數等）
- **INFO**: 一般資訊（開始/完成任務、檔案處理進度等）
- **WARNING**: 警告訊息（任務暫停、檔案不存在等）
- **ERROR**: 錯誤訊息（執行失敗、檔案讀取錯誤等）
- **CRITICAL**: 嚴重錯誤（Segmentation Fault 等）

## 日誌內容範例

### 轉錄過程
```
16:35:02 | INFO | whisper_gui | 開始 CoreML Whisper 轉錄，共 2 個檔案，語言: auto
16:35:02 | INFO | whisper_gui | 總音頻時長: 120.50 秒
16:35:02 | INFO | whisper_gui | [1/2] 處理檔案: video1.mp4
16:35:02 | INFO | whisper_gui | 開始轉換 MP4 為 WAV: video1.mp4
16:35:05 | INFO | whisper_gui | ✓ 轉換完成: video1.wav
16:35:05 | INFO | whisper_gui | 開始 CoreML Whisper 轉錄: video1.wav -> video1.srt
16:35:05 | DEBUG | whisper_gui | 執行指令: /path/to/whisper.cpp/main -m /path/to/model.bin ...
16:35:10 | INFO | whisper_gui | Whisper.cpp 執行成功
16:35:10 | INFO | whisper_gui | ✓ [1/2] 完成: video1.srt
```

### 翻譯過程
```
16:40:00 | INFO | whisper_gui | 開始翻譯 SRT 檔案: video1.srt
16:40:00 | INFO | whisper_gui | 已解析字幕，共 150 條
16:40:00 | INFO | whisper_gui | 翻譯字幕 [1/150]: 這是第一段字幕...
16:40:02 | INFO | whisper_gui | ✓ 字幕 1 翻譯完成
```

### 錯誤訊息
```
16:45:00 | ERROR | whisper_gui | Whisper.cpp 執行檔不存在: /path/to/main
16:45:00 | CRITICAL | whisper_gui | Whisper 發生 Segmentation Fault（段錯誤）
```

## 查看日誌

### 即時查看（終端機）
執行應用程式時，日誌會自動顯示在終端機。

### 查看日誌檔案
```bash
# 查看今天的日誌
cat logs/whisper_gui_$(date +%Y%m%d).log

# 查看最新的日誌（最後 50 行）
tail -n 50 logs/whisper_gui_$(date +%Y%m%d).log

# 即時監控日誌
tail -f logs/whisper_gui_$(date +%Y%m%d).log
```

### 搜尋特定內容
```bash
# 搜尋錯誤訊息
grep ERROR logs/whisper_gui_*.log

# 搜尋特定檔案
grep "video1.mp4" logs/whisper_gui_*.log

# 搜尋特定日期範圍
grep "2025-12-29" logs/whisper_gui_*.log
```

## 日誌檔案管理

- 日誌檔案會自動建立，無需手動設定
- 建議定期清理舊的日誌檔案以節省空間
- 日誌檔案使用 UTF-8 編碼，支援中文顯示

## 除錯技巧

1. **查看完整錯誤堆疊**：日誌檔案包含完整的錯誤堆疊資訊
2. **追蹤執行流程**：使用 `grep` 搜尋特定檔案或任務的執行過程
3. **比對時間戳記**：日誌包含精確的時間戳記，可以追蹤執行時間
4. **檢查配置**：啟動時會記錄配置資訊，可以確認路徑是否正確

## 注意事項

- 日誌檔案可能包含敏感資訊（如檔案路徑），請妥善保管
- 日誌檔案會持續增長，建議定期清理
- 如果遇到問題，可以將日誌檔案提供給開發者協助除錯

