"""
日誌管理模組

提供統一的日誌功能，支援：
- 控制台輸出（彩色）
- 檔案輸出（logs/whisper_gui.log）
- GUI 輸出（可選）
- 不同日誌級別（DEBUG, INFO, WARNING, ERROR）
"""

import logging
import os
import queue
from datetime import datetime
from pathlib import Path

# 日誌目錄
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日誌檔案路徑（每天一個檔案）
LOG_FILE = LOG_DIR / f"whisper_gui_{datetime.now().strftime('%Y%m%d')}.log"


class ColoredFormatter(logging.Formatter):
    """彩色日誌格式化器（僅用於控制台）"""
    
    # ANSI 顏色代碼
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 綠色
        'WARNING': '\033[33m',   # 黃色
        'ERROR': '\033[31m',      # 紅色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }
    
    def format(self, record):
        # 添加顏色
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class GUIHandler(logging.Handler):
    """GUI 日誌處理器，將日誌輸出到 GUI 文字區域"""
    
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue
        # 簡化的格式化器（不包含時間戳和模組名，只顯示級別和訊息）
        self.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    
    def emit(self, record):
        """發送日誌記錄到隊列"""
        try:
            msg = self.format(record)
            self.log_queue.put(msg)
        except Exception:
            self.handleError(record)


def setup_logger(name="whisper_gui", level=logging.INFO, gui_handler=None):
    """
    設定日誌器
    
    Args:
        name: 日誌器名稱
        level: 日誌級別（預設: INFO）
        gui_handler: GUI 日誌處理器（可選）
    
    Returns:
        logging.Logger: 配置好的日誌器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重複添加 handler
    if logger.handlers:
        # 如果已經有 handler，檢查是否需要添加 GUI handler
        if gui_handler and not any(isinstance(h, GUIHandler) for h in logger.handlers):
            logger.addHandler(gui_handler)
        return logger
    
    # 控制台 handler（彩色輸出）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 檔案 handler（完整輸出）
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # 檔案記錄所有級別
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # GUI handler（如果提供）
    if gui_handler:
        logger.addHandler(gui_handler)
    
    return logger


# 建立全域日誌器（初始不包含 GUI handler）
logger = setup_logger()

