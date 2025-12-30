# main.py
import gui
from logger import logger

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Whisper GUI 應用程式啟動")
    logger.info("=" * 60)
    try:
        gui.run()
    except KeyboardInterrupt:
        logger.info("應用程式被用戶中斷")
    except Exception as e:
        logger.exception(f"應用程式發生未預期的錯誤: {e}")
        raise
    finally:
        logger.info("Whisper GUI 應用程式結束")
