"""
Logging management module / 日誌管理模組

Provides unified logging functionality, supports: / 提供統一的日誌功能，支援：
- Console output (colored) / 控制台輸出（彩色）
- File output (logs/whisper_gui.log) / 檔案輸出（logs/whisper_gui.log）
- GUI output (optional) / GUI 輸出（可選）
- Different log levels (DEBUG, INFO, WARNING, ERROR) / 不同日誌級別（DEBUG, INFO, WARNING, ERROR）
"""

import logging
import os
import queue
from datetime import datetime
from pathlib import Path

# Log directory / 日誌目錄
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log file path (one file per day) / 日誌檔案路徑（每天一個檔案）
LOG_FILE = LOG_DIR / f"whisper_gui_{datetime.now().strftime('%Y%m%d')}.log"


class ColoredFormatter(logging.Formatter):
    """
    Colored log formatter (only for console) / 彩色日誌格式化器（僅用於控制台）
    """
    
    # ANSI color codes / ANSI 顏色代碼
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan / 青色
        'INFO': '\033[32m',       # Green / 綠色
        'WARNING': '\033[33m',   # Yellow / 黃色
        'ERROR': '\033[31m',      # Red / 紅色
        'CRITICAL': '\033[35m',   # Magenta / 紫色
        'RESET': '\033[0m'        # Reset / 重置
    }
    
    def format(self, record):
        # Add color / 添加顏色
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class GUIHandler(logging.Handler):
    """
    GUI log handler, outputs logs to GUI text area / GUI 日誌處理器，將日誌輸出到 GUI 文字區域
    """
    
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue
        # Simplified formatter (no timestamp and module name, only level and message) / 簡化的格式化器（不包含時間戳和模組名，只顯示級別和訊息）
        self.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    
    def emit(self, record):
        """
        Send log record to queue / 發送日誌記錄到隊列
        
        Args:
            record: Log record / 日誌記錄
        """
        try:
            msg = self.format(record)
            self.log_queue.put(msg)
        except Exception:
            self.handleError(record)


def setup_logger(name="whisper_gui", level=logging.INFO, gui_handler=None):
    """
    Setup logger / 設定日誌器
    
    Args:
        name: Logger name / 日誌器名稱
        level: Log level (default: INFO) / 日誌級別（預設: INFO）
        gui_handler: GUI log handler (optional) / GUI 日誌處理器（可選）
    
    Returns:
        logging.Logger: Configured logger / 配置好的日誌器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers / 避免重複添加 handler
    if logger.handlers:
        # If handlers already exist, check if GUI handler needs to be added / 如果已經有 handler，檢查是否需要添加 GUI handler
        if gui_handler and not any(isinstance(h, GUIHandler) for h in logger.handlers):
            logger.addHandler(gui_handler)
        return logger
    
    # Console handler (colored output) / 控制台 handler（彩色輸出）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (full output) / 檔案 handler（完整輸出）
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # File records all levels / 檔案記錄所有級別
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # GUI handler (if provided) / GUI handler（如果提供）
    if gui_handler:
        logger.addHandler(gui_handler)
    
    return logger


# Create global logger (initially without GUI handler) / 建立全域日誌器（初始不包含 GUI handler）
logger = setup_logger()

