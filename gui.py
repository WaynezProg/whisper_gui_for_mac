import customtkinter as ctk
from tkinter import filedialog, messagebox  # 對話框仍使用 tkinter
import threading
import queue
import logging
import actions  # 引入動作檔案
import os
# import ai_translate  # 延遲導入，避免 macOS 版本檢查問題
from pykakasi import kakasi
from logger import logger, GUIHandler, setup_logger
from i18n import t, load_language, get_current_language, get_available_languages

# 全域變數：儲存檔案列表
_file_list = []

# 翻譯日誌訊息的輔助函數
def log_t(key, level="info", **kwargs):
    """記錄翻譯後的日誌訊息"""
    message = t(f"log.{key}", key)
    # 如果有參數，進行格式化
    if kwargs:
        try:
            message = message.format(**kwargs)
        except KeyError:
            # 如果格式化失敗，返回原始訊息
            pass
    if level == "info":
        logger.info(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "error":
        logger.error(message)
    elif level == "debug":
        logger.debug(message)
    return message

# 添加文件到列表框
def add_files(files=None):
    global _file_list
    if files is None:
        files = filedialog.askopenfilenames(filetypes=[("WAV files", "*.wav"), ("MP4 files", "*.mp4")])
    log_t("added_files", count=len(files) if files else 0)
    for file in files:
        if file not in _file_list:
            _file_list.append(file)
            log_t("file_added", level="debug", filename=os.path.basename(file))
    update_file_display()

# 添加資料夾中的文件到列表框
def add_folder():
    global _file_list
    folder = filedialog.askdirectory()
    if folder:
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(('.mp4', '.wav')):
                    file_path = os.path.join(root, file)
                    if file_path not in _file_list:
                        _file_list.append(file_path)
    update_file_display()

# 從列表框中刪除選中的文件
def remove_files():
    global _file_list
    if _file_list:
        _file_list.pop()  # 刪除最後一個檔案
        update_file_display()

# 暫停標誌
pause_flag = threading.Event()

# 執行 CoreML Whisper 轉錄
def coreml_whisper():
    log_t("user_clicked_coreml")
    update_status(t("status.coreml_transcribing"), "INFO")
    files = _file_list.copy()
    language = language_combobox.get()

    if not files:
        log_t("no_files_warning", level="warning")
        messagebox.showwarning(t("message.warning.title", "警告"), t("message.warning.no_files"))
        update_status(t("status.ready"), "INFO")
        return

    log_t("start_coreml", count=len(files), language=language)

    # 在新線程中運行 CoreML Whisper
    def run_coreml_whisper():
        try:
            actions.coreml_whisper(files, language, update_progress, pause_flag, update_status)
            log_t("coreml_completed")
            update_status(t("status.coreml_completed"), "INFO")
            # 使用 root.after() 確保在主線程中顯示 messagebox
            root.after(0, lambda: messagebox.showinfo(t("message.info.completed"), t("message.info.coreml_completed").format(count=len(files))))
        except KeyboardInterrupt:
            log_t("coreml_cancelled", level="warning")
            update_status(t("status.cancelled"), "WARNING")
            root.after(0, lambda: messagebox.showinfo(t("message.info.cancelled", "取消"), t("message.info.cancelled")))
        except Exception as e:
            logger.exception(t("message.error.generic_error").format(error=str(e)))
            update_status(t("status.error").format(error=str(e)[:50]), "ERROR")
            error_msg = str(e)
            
            # 特別處理 segmentation fault 錯誤
            if "Segmentation Fault" in error_msg or "段錯誤" in error_msg:
                error_msg = (
                    "Whisper 發生 Segmentation Fault（段錯誤）\n\n"
                    "可能原因：\n"
                    "1. 檔案路徑包含特殊字元\n"
                    "2. whisper.cpp 執行檔問題\n"
                    "3. 模型檔案問題\n\n"
                    "建議：\n"
                    "• 嘗試使用「CPU 執行」模式（較穩定）\n"
                    "• 檢查 whisper.cpp 是否正確編譯\n"
                    "• 檢查模型檔案是否完整"
                )
            
            # 截斷過長的錯誤訊息
            if len(error_msg) > 1000:
                error_msg = error_msg[:1000] + "..."
            
            final_error_msg = error_msg  # 閉包變數
            root.after(0, lambda: messagebox.showerror(t("message.error.title"), final_error_msg))
            import traceback
            traceback.print_exc()  # 在終端機印出完整錯誤

    threading.Thread(target=run_coreml_whisper).start()

# 執行 CPU Whisper 轉錄
def cpu_whisper():
    log_t("user_clicked_cpu")
    update_status(t("status.cpu_transcribing"), "INFO")
    files = _file_list.copy()
    language = language_combobox.get()
    translate_to = translate_combobox.get()

    if not files:
        log_t("no_files_warning", level="warning")
        messagebox.showwarning(t("message.warning.title", "警告"), t("message.warning.no_files"))
        update_status(t("status.ready"), "INFO")
        return

    log_t("start_cpu", count=len(files), language=language)

    # 在新線程中運行 CPU Whisper
    def run_cpu_whisper():
        try:
            actions.cpu_whisper(files, language, translate_to, update_progress, pause_flag, update_status)
            log_t("cpu_completed")
            update_status(t("status.cpu_completed"), "INFO")
            root.after(0, lambda: messagebox.showinfo(t("message.info.completed"), t("message.info.cpu_completed").format(count=len(files))))
        except KeyboardInterrupt:
            log_t("cpu_cancelled", level="warning")
            update_status(t("status.cancelled"), "WARNING")
            root.after(0, lambda: messagebox.showinfo(t("message.info.cancelled", "取消"), t("message.info.cancelled")))
        except Exception as e:
            logger.exception(t("message.error.generic_error").format(error=str(e)))
            update_status(t("status.error").format(error=str(e)[:50]), "ERROR")
            error_msg = str(e)
            # 截斷過長的錯誤訊息
            if len(error_msg) > 500:
                error_msg = error_msg[:500] + "..."
            final_error_msg = error_msg  # 閉包變數
            root.after(0, lambda: messagebox.showerror(t("message.error.title"), t("message.error.generic_error").format(error=final_error_msg)))
            import traceback
            traceback.print_exc()  # 在終端機印出完整錯誤

    threading.Thread(target=run_cpu_whisper).start()

# 執行翻譯
def translate_srt_files():
    log_t("user_clicked_translate")
    # 延遲導入 ai_translate，避免 macOS 版本檢查問題
    try:
        import ai_translate
    except Exception as e:
        logger.error(t("message.error.translation_module_error").format(error=str(e)))
        messagebox.showerror(t("message.error.title"), t("message.error.translation_module_error").format(error=str(e)))
        update_status(t("status.translation_unavailable"), "ERROR")
        return
    
    update_status(t("status.translating"), "INFO")
    files = _file_list.copy()
    target_language = translate_combobox.get()

    if not files:
        log_t("no_files_warning", level="warning")
        messagebox.showwarning(t("message.warning.title", "警告"), t("message.warning.no_files"))
        update_status(t("status.ready"), "INFO")
        return

    log_t("start_translation", count=len(files), language=target_language)

    # 在新線程中運行翻譯
    def run_translate_srt_files():
        translated_count = 0
        try:
            for file in files:
                if pause_flag.is_set():
                    log_t("translation_paused", level="warning")
                    break
                
                # 獲取基礎檔案路徑（不含副檔名）
                base_path = os.path.splitext(file)[0]
                file_dir = os.path.dirname(file) if os.path.dirname(file) else '.'
                
                # 嘗試尋找 SRT 檔案（優先順序：_coreml.srt > _cpu.srt > .srt）
                srt_file = None
                possible_srt_files = [
                    os.path.join(file_dir, f"{os.path.basename(base_path)}_coreml.srt"),
                    os.path.join(file_dir, f"{os.path.basename(base_path)}_cpu.srt"),
                    os.path.join(file_dir, f"{os.path.basename(base_path)}.srt")
                ]
                
                for possible_srt in possible_srt_files:
                    if os.path.exists(possible_srt):
                        srt_file = possible_srt
                        break
                
                if srt_file and os.path.exists(srt_file):
                    log_t("translating_file", filename=os.path.basename(srt_file))
                    # 不指定 output_srt_path，讓 translate_srt 自動生成帶語言後綴的檔案名
                    ai_translate.translate_srt(srt_file, output_srt_path=None, target_language=target_language, pause_flag=pause_flag)
                    translated_count += 1
                    # 更新進度
                    progress = (translated_count / len(files)) * 100
                    update_progress(progress)
                else:
                    log_t("srt_not_found", level="warning", filename=os.path.basename(file))
            log_t("translation_completed", count=translated_count)
            # 先更新狀態，再顯示訊息框
            update_status(t("status.translation_completed").format(translated=translated_count, total=len(files)), "INFO")
            # 延遲顯示訊息框，確保狀態先更新
            final_count = translated_count
            final_total = len(files)
            root.after(100, lambda: messagebox.showinfo(t("message.info.completed"), t("message.info.translation_completed").format(count=final_count)))
        except Exception as e:
            logger.exception(t("message.error.generic_error").format(error=str(e)))
            update_status(t("status.error").format(error=str(e)[:50]), "ERROR")
            root.after(0, lambda: messagebox.showerror(t("message.error.title"), t("message.error.generic_error").format(error=str(e))))

    threading.Thread(target=run_translate_srt_files).start()

# 禁用/啟用按鈕的輔助函數
def set_buttons_state(enabled):
    """
    設定所有按鈕的啟用/禁用狀態
    
    Args:
        enabled: True 啟用按鈕，False 禁用按鈕
    """
    def _set_state():
        global coreml_button, cpu_button, translate_button, katakana_button, pause_button
        global add_button, add_folder_button, remove_button
        
        buttons = [
            coreml_button, cpu_button, translate_button, katakana_button,
            add_button, add_folder_button, remove_button
        ]
        
        state = "normal" if enabled else "disabled"
        for button in buttons:
            if button is not None:
                try:
                    button.configure(state=state)
                except Exception as e:
                    logger.warning(f"更新按鈕狀態失敗: {e}")
        
        # 暫停按鈕在執行時應該可用（用於暫停任務）
        if pause_button is not None:
            try:
                pause_button.configure(state="normal")
            except Exception as e:
                logger.warning(f"更新暫停按鈕狀態失敗: {e}")
        
        logger.info(f"按鈕狀態已更新: {'啟用' if enabled else '禁用'}")
    
    if 'root' in globals() and root is not None:
        # 使用 root.after(0, ...) 確保在主線程中執行
        root.after(0, _set_state)
    else:
        # 如果 root 還未建立，直接執行（應該不會發生）
        _set_state()

# 更新進度條（已移除，保留函數以保持向後兼容）
def update_progress(progress):
    # 進度條已移除，只記錄日誌
    if progress % 10 < 1 or progress >= 99:
        logger.debug(f"進度: {progress:.1f}%")

# 更新狀態標籤（已移除，保留函數以保持向後兼容）
def update_status(message, level="INFO"):
    """
    更新狀態（已移除 UI，只記錄日誌）
    
    Args:
        message: 狀態訊息
        level: 日誌級別（INFO, WARNING, ERROR, DEBUG）
    """
    # 只記錄日誌，不再更新 UI
    if level == "INFO":
        logger.info(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "ERROR":
        logger.error(message)
    else:
        logger.debug(message)

# 更新檔案列表顯示
def update_file_display():
    global _file_list, file_listbox
    if 'file_listbox' in globals() and file_listbox is not None:
        file_listbox.configure(state="normal")
        file_listbox.delete("1.0", "end")
        for i, file in enumerate(_file_list, 1):
            file_listbox.insert("end", f"{i}. {os.path.basename(file)}\n")
        file_listbox.configure(state="disabled")

# 暫停任務
def pause_task():
    log_t("user_clicked_pause")
    pause_flag.set()
    update_status("任務已暫停，結果已保存。", "WARNING")
    # pause_task 在主線程中執行，可以直接調用 messagebox
    messagebox.showinfo("暫停", "任務已暫停，結果已保存。")

# 日文轉換成片假名
def japanese_to_katakana():
    update_status("正在轉換為片假名...", "INFO")
    files = _file_list.copy()

    if not files:
        messagebox.showwarning("警告", "請添加音頻文件。")
        update_status("就緒", "INFO")
        return

    def is_kanji(ch):
        return '一' <= ch <= '\u9FFF' or '豈' <= ch <= '\uFAFF'

    def convert_to_katakana(input_srt_path, output_srt_path):
        # 初始化 kakasi 實例進行轉換
        kakasi_instance = kakasi()
        kakasi_instance.setMode("J", "H")  # 漢字轉平假名
        kakasi_instance.setMode('H', 'K')  # 平假名轉片假名
        conv = kakasi_instance.getConverter()

        with open(input_srt_path, 'r', encoding='utf-8') as file:
            srt_content = file.readlines()

        converted_lines = []
        for line in srt_content:
            if not line.strip():
                converted_lines.append(line)
            elif '-->' in line:
                converted_lines.append(line)
            elif line.strip().isdigit():
                converted_lines.append(line)
            else:
                new_line = ''
                for ch in line:
                    if is_kanji(ch):
                        new_line += conv.do(ch)
                    else:
                        new_line += ch
                converted_lines.append(new_line)

        with open(output_srt_path, 'w', encoding='utf-8') as file:
            file.writelines(converted_lines)

    # 在新線程中運行轉換
    def run_japanese_to_katakana():
        converted_count = 0
        try:
            for i, file in enumerate(files):
                if pause_flag.is_set():
                    log_t("conversion_paused", level="warning")
                    break
                
                # 獲取基礎檔案路徑（不含副檔名）
                base_path = os.path.splitext(file)[0]
                file_dir = os.path.dirname(file) if os.path.dirname(file) else '.'
                
                # 嘗試尋找 SRT 檔案（優先順序：_coreml.srt > _cpu.srt > .srt）
                srt_file = None
                possible_srt_files = [
                    os.path.join(file_dir, f"{os.path.basename(base_path)}_coreml.srt"),
                    os.path.join(file_dir, f"{os.path.basename(base_path)}_cpu.srt"),
                    os.path.join(file_dir, f"{os.path.basename(base_path)}.srt")
                ]
                
                for possible_srt in possible_srt_files:
                    if os.path.exists(possible_srt):
                        srt_file = possible_srt
                        break
                
                if srt_file and os.path.exists(srt_file):
                    log_t("converting_file", filename=os.path.basename(srt_file))
                    # 使用 get_unique_output_path 生成不重複的檔案名
                    from actions import get_unique_output_path
                    base_path = os.path.splitext(srt_file)[0]
                    output_srt_file = get_unique_output_path(base_path, 'katakana')
                    convert_to_katakana(srt_file, output_srt_file)
                    converted_count += 1
                    # 更新進度
                    progress = ((i + 1) / len(files)) * 100
                    update_progress(progress)
                else:
                    log_t("srt_not_found", level="warning", filename=os.path.basename(file))
            log_t("katakana_completed", count=converted_count)
            update_status(t("status.katakana_completed").format(converted=converted_count, total=len(files)), "INFO")
            root.after(0, lambda: messagebox.showinfo(t("message.info.completed"), t("message.info.katakana_completed").format(count=converted_count)))
        except Exception as e:
            logger.exception(t("message.error.generic_error").format(error=str(e)))
            update_status(t("status.error").format(error=str(e)[:50]), "ERROR")
            root.after(0, lambda: messagebox.showerror(t("message.error.title"), t("message.error.generic_error").format(error=str(e))))

    threading.Thread(target=run_japanese_to_katakana).start()

# 主函數，創建 GUI 並運行
# 在文件頂部添加全局變量聲明
global root

def run():
    global root, file_listbox, language_combobox, translate_combobox
    global coreml_button, cpu_button, translate_button, katakana_button, pause_button
    global add_button, add_folder_button, remove_button, log_textbox, log_queue
    global language_label, translate_label, log_label, license_label

    # 載入語言設定
    from config import config
    load_language(getattr(config, 'GUI_LANGUAGE', 'zh_TW'))
    
    log_t("app_started")
    # 設定外觀模式和顏色主題
    ctk.set_appearance_mode("system")  # "light", "dark", 或 "system"（跟隨系統）
    ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
    
    # 建立主視窗
    root = ctk.CTk()
    root.title(t("window.title", "Whisper Transcription GUI"))
    root.geometry("900x750")  # 調整高度以容納日誌區域
    log_t("window_created")
    
    # 建立日誌隊列和 GUI handler
    log_queue = queue.Queue()
    gui_handler = GUIHandler(log_queue)
    # 重新設定 logger 以包含 GUI handler
    setup_logger(level=logging.INFO, gui_handler=gui_handler)

    # 添加音頻文件
    file_frame = ctk.CTkFrame(root)
    file_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    # 使用 CTkTextbox 顯示檔案列表
    file_listbox = ctk.CTkTextbox(file_frame, width=600, height=200, state="disabled")
    file_listbox.pack(pady=10, padx=10, fill="both", expand=True)

    file_button_frame = ctk.CTkFrame(root)
    file_button_frame.pack(pady=5)
    add_button = ctk.CTkButton(file_button_frame, text=t("button.add"), command=add_files, width=100, height=32)
    add_button.pack(side="left", padx=10)
    add_folder_button = ctk.CTkButton(file_button_frame, text=t("button.add_folder"), command=add_folder, width=120, height=32)
    add_folder_button.pack(side="left", padx=10)
    remove_button = ctk.CTkButton(file_button_frame, text=t("button.remove"), command=remove_files, width=100, height=32)
    remove_button.pack(side="left", padx=10)

    # 拼讀語言
    language_label = ctk.CTkLabel(root, text=t("label.language"), font=ctk.CTkFont(size=14))
    language_label.pack(pady=5)
    language_combobox = ctk.CTkComboBox(
        root, 
        values=["auto", "en", "zh", "ja", "ko", "fr", "de"],
        width=200,
        height=32
    )
    language_combobox.set("auto")  # 設定預設值
    language_combobox.pack(pady=5)

    # 翻譯語言
    translate_label = ctk.CTkLabel(root, text=t("label.translate_to"), font=ctk.CTkFont(size=14))
    translate_label.pack(pady=5)
    translate_languages = t("combobox.translate_languages", ["English", "Chinese", "Japanese", "Korean", "French", "German"])
    # 確保 translate_languages 是列表
    if not isinstance(translate_languages, list):
        translate_languages = ["English", "Chinese", "Japanese", "Korean", "French", "German"]
    translate_combobox = ctk.CTkComboBox(
        root, 
        values=translate_languages,
        width=200,
        height=32
    )
    translate_combobox.set(translate_languages[0])  # 設定預設值
    translate_combobox.pack(pady=5)

    # CoreML 和 CPU 執行按鈕
    button_frame = ctk.CTkFrame(root)
    button_frame.pack(pady=10)
    coreml_button = ctk.CTkButton(button_frame, text=t("button.coreml_execute"), command=coreml_whisper, width=120, height=32)
    coreml_button.pack(side="left", padx=10)
    cpu_button = ctk.CTkButton(button_frame, text=t("button.cpu_execute"), command=cpu_whisper, width=120, height=32)
    cpu_button.pack(side="left", padx=10)
    translate_button = ctk.CTkButton(button_frame, text=t("button.translate"), command=translate_srt_files, width=100, height=32)
    translate_button.pack(side="left", padx=10)
    pause_button = ctk.CTkButton(button_frame, text=t("button.pause"), command=pause_task, width=100, height=32)
    pause_button.pack(side="left", padx=10)
    katakana_button = ctk.CTkButton(button_frame, text=t("button.katakana"), command=japanese_to_katakana, width=140, height=32)
    katakana_button.pack(side="left", padx=10)

    # 日誌顯示區域
    log_frame = ctk.CTkFrame(root)
    log_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    log_label = ctk.CTkLabel(log_frame, text=t("label.log"), font=ctk.CTkFont(size=12))
    log_label.pack(anchor="w", padx=10, pady=(10, 5))
    
    log_textbox = ctk.CTkTextbox(log_frame, width=860, height=200, state="disabled", font=ctk.CTkFont(size=11))
    log_textbox.pack(pady=5, padx=10, fill="both", expand=True)
    log_t("log_area_initialized")
    
    # 定期檢查日誌隊列並更新 GUI
    def process_log_queue():
        """處理日誌隊列中的訊息"""
        try:
            while True:
                try:
                    msg = log_queue.get_nowait()
                    # 在主線程中更新 GUI
                    log_textbox.configure(state="normal")
                    log_textbox.insert("end", msg + "\n")
                    # 自動滾動到底部
                    log_textbox.see("end")
                    # 限制日誌行數（保留最後 1000 行）
                    lines = log_textbox.get("1.0", "end").split("\n")
                    if len(lines) > 1000:
                        log_textbox.delete("1.0", f"{len(lines) - 1000}.0")
                    log_textbox.configure(state="disabled")
                except queue.Empty:
                    break
        except Exception as e:
            logger.error(t("log.log_queue_error").format(error=str(e)))
        
        # 每 100ms 檢查一次
        root.after(100, process_log_queue)
    
    # 開始處理日誌隊列
    process_log_queue()

    # 版權信息
    license_label = ctk.CTkLabel(root, text=t("label.license"), font=ctk.CTkFont(size=10))
    license_label.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    run()