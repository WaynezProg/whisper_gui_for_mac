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

# 全域變數：儲存檔案列表
_file_list = []

# 添加文件到列表框
def add_files(files=None):
    global _file_list
    if files is None:
        files = filedialog.askopenfilenames(filetypes=[("WAV files", "*.wav"), ("MP4 files", "*.mp4")])
    logger.info(f"添加檔案: {len(files) if files else 0} 個")
    for file in files:
        if file not in _file_list:
            _file_list.append(file)
            logger.debug(f"已添加檔案: {os.path.basename(file)}")
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
    logger.info("用戶點擊 CoreML 執行按鈕")
    update_status("正在執行 CoreML 轉錄...", "INFO")
    files = _file_list.copy()
    language = language_combobox.get()

    if not files:
        logger.warning("用戶嘗試執行但沒有添加檔案")
        messagebox.showwarning("警告", "請添加音頻文件。")
        update_status("就緒", "INFO")
        return

    logger.info(f"開始 CoreML Whisper 轉錄，檔案數: {len(files)}, 語言: {language}")

    # 在新線程中運行 CoreML Whisper
    def run_coreml_whisper():
        try:
            actions.coreml_whisper(files, language, update_progress, pause_flag, update_status)
            logger.info("CoreML Whisper 轉錄成功完成")
            update_status("✓ CoreML 轉錄完成", "INFO")
            # 使用 root.after() 確保在主線程中顯示 messagebox
            root.after(0, lambda: messagebox.showinfo("完成", f"CoreML 轉錄完成。\n\n已處理 {len(files)} 個檔案。"))
        except KeyboardInterrupt:
            logger.warning("用戶中斷 CoreML Whisper 轉錄")
            update_status("已取消", "WARNING")
            root.after(0, lambda: messagebox.showinfo("取消", "轉錄已取消。"))
        except Exception as e:
            logger.exception(f"CoreML Whisper 轉錄發生錯誤: {e}")
            update_status(f"發生錯誤: {str(e)[:50]}...", "ERROR")
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
            root.after(0, lambda: messagebox.showerror("錯誤", final_error_msg))
            import traceback
            traceback.print_exc()  # 在終端機印出完整錯誤

    threading.Thread(target=run_coreml_whisper).start()

# 執行 CPU Whisper 轉錄
def cpu_whisper():
    logger.info("用戶點擊 CPU 執行按鈕")
    update_status("正在執行 CPU 轉錄...", "INFO")
    files = _file_list.copy()
    language = language_combobox.get()
    translate_to = translate_combobox.get()

    if not files:
        logger.warning("用戶嘗試執行但沒有添加檔案")
        messagebox.showwarning("警告", "請添加音頻文件。")
        update_status("就緒", "INFO")
        return

    logger.info(f"開始 CPU Whisper 轉錄，檔案數: {len(files)}, 語言: {language}")

    # 在新線程中運行 CPU Whisper
    def run_cpu_whisper():
        try:
            actions.cpu_whisper(files, language, translate_to, update_progress, pause_flag, update_status)
            logger.info("CPU Whisper 轉錄成功完成")
            update_status("✓ CPU 轉錄完成", "INFO")
            root.after(0, lambda: messagebox.showinfo("完成", f"CPU 轉錄完成。\n\n已處理 {len(files)} 個檔案。"))
        except KeyboardInterrupt:
            logger.warning("用戶中斷 CPU Whisper 轉錄")
            update_status("已取消", "WARNING")
            root.after(0, lambda: messagebox.showinfo("取消", "轉錄已取消。"))
        except Exception as e:
            logger.exception(f"CPU Whisper 轉錄發生錯誤: {e}")
            update_status(f"發生錯誤: {str(e)[:50]}...", "ERROR")
            error_msg = str(e)
            # 截斷過長的錯誤訊息
            if len(error_msg) > 500:
                error_msg = error_msg[:500] + "..."
            final_error_msg = error_msg  # 閉包變數
            root.after(0, lambda: messagebox.showerror("錯誤", f"發生錯誤: {final_error_msg}"))
            import traceback
            traceback.print_exc()  # 在終端機印出完整錯誤

    threading.Thread(target=run_cpu_whisper).start()

# 執行翻譯
def translate_srt_files():
    logger.info("用戶點擊翻譯按鈕")
    # 延遲導入 ai_translate，避免 macOS 版本檢查問題
    try:
        import ai_translate
    except Exception as e:
        logger.error(f"無法載入翻譯模組: {e}")
        messagebox.showerror("錯誤", f"無法載入翻譯模組: {e}\n\n可能是 macOS 版本兼容性問題。")
        update_status("翻譯功能不可用", "ERROR")
        return
    
    update_status("正在翻譯...", "INFO")
    files = _file_list.copy()
    target_language = translate_combobox.get()

    if not files:
        logger.warning("用戶嘗試翻譯但沒有添加檔案")
        messagebox.showwarning("警告", "請添加音頻文件。")
        update_status("就緒", "INFO")
        return

    logger.info(f"開始翻譯，檔案數: {len(files)}, 目標語言: {target_language}")

    # 在新線程中運行翻譯
    def run_translate_srt_files():
        translated_count = 0
        try:
            for file in files:
                if pause_flag.is_set():
                    logger.warning("翻譯已暫停")
                    break
                srt_file = file.replace('.wav', '.srt').replace('.mp4', '.srt')
                if os.path.exists(srt_file):
                    logger.info(f"翻譯檔案: {os.path.basename(srt_file)}")
                    # 不指定 output_srt_path，讓 translate_srt 自動生成帶語言後綴的檔案名
                    ai_translate.translate_srt(srt_file, output_srt_path=None, target_language=target_language, pause_flag=pause_flag)
                    translated_count += 1
                    # 更新進度
                    progress = (translated_count / len(files)) * 100
                    update_progress(progress)
            logger.info(f"翻譯成功完成，共翻譯 {translated_count} 個檔案")
            # 先更新狀態，再顯示訊息框
            update_status(f"✓ 翻譯完成（{translated_count}/{len(files)} 個檔案）", "INFO")
            # 延遲顯示訊息框，確保狀態先更新
            final_count = translated_count
            final_total = len(files)
            root.after(100, lambda: messagebox.showinfo("完成", f"翻譯完成。\n\n已翻譯 {final_count} 個檔案。"))
        except Exception as e:
            logger.exception(f"翻譯發生錯誤: {e}")
            update_status(f"發生錯誤: {str(e)[:50]}...", "ERROR")
            root.after(0, lambda: messagebox.showerror("錯誤", f"發生錯誤: {e}"))

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
    logger.info("用戶點擊暫停按鈕")
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
                    logger.warning("轉換已暫停")
                    break
                srt_file = file.replace('.wav', '.srt').replace('.mp4', '.srt')
                if os.path.exists(srt_file):
                    logger.info(f"轉換檔案: {os.path.basename(srt_file)}")
                    # 使用 get_unique_output_path 生成不重複的檔案名
                    from actions import get_unique_output_path
                    base_path = os.path.splitext(srt_file)[0]
                    output_srt_file = get_unique_output_path(base_path, 'katakana')
                    convert_to_katakana(srt_file, output_srt_file)
                    converted_count += 1
                    # 更新進度
                    progress = ((i + 1) / len(files)) * 100
                    update_progress(progress)
            logger.info(f"日文轉片假名成功完成，共轉換 {converted_count} 個檔案")
            update_status(f"✓ 片假名轉換完成（{converted_count}/{len(files)} 個檔案）", "INFO")
            root.after(0, lambda: messagebox.showinfo("完成", f"日文轉換成片假名完成。\n\n已轉換 {converted_count} 個檔案。"))
        except Exception as e:
            logger.exception(f"日文轉片假名發生錯誤: {e}")
            update_status(f"發生錯誤: {str(e)[:50]}...", "ERROR")
            root.after(0, lambda: messagebox.showerror("錯誤", f"發生錯誤: {e}"))

    threading.Thread(target=run_japanese_to_katakana).start()

# 主函數，創建 GUI 並運行
# 在文件頂部添加全局變量聲明
global root

def run():
    global root, file_listbox, language_combobox, translate_combobox
    global coreml_button, cpu_button, translate_button, katakana_button, pause_button
    global add_button, add_folder_button, remove_button, log_textbox, log_queue

    logger.info("啟動 Whisper GUI 應用程式")
    # 設定外觀模式和顏色主題
    ctk.set_appearance_mode("system")  # "light", "dark", 或 "system"（跟隨系統）
    ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
    
    # 建立主視窗
    root = ctk.CTk()
    root.title("Whisper Transcription GUI")
    root.geometry("900x750")  # 調整高度以容納日誌區域
    logger.info("GUI 視窗已建立")
    
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
    add_button = ctk.CTkButton(file_button_frame, text="添加", command=add_files, width=100, height=32)
    add_button.pack(side="left", padx=10)
    add_folder_button = ctk.CTkButton(file_button_frame, text="添加資料夾", command=add_folder, width=120, height=32)
    add_folder_button.pack(side="left", padx=10)
    remove_button = ctk.CTkButton(file_button_frame, text="刪除", command=remove_files, width=100, height=32)
    remove_button.pack(side="left", padx=10)

    # 拼讀語言
    language_label = ctk.CTkLabel(root, text="拼讀語言:", font=ctk.CTkFont(size=14))
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
    translate_label = ctk.CTkLabel(root, text="翻譯為:", font=ctk.CTkFont(size=14))
    translate_label.pack(pady=5)
    translate_combobox = ctk.CTkComboBox(
        root, 
        values=["英文", "中文", "日文", "韓文", "法文", "德文"],
        width=200,
        height=32
    )
    translate_combobox.set("英文")  # 設定預設值
    translate_combobox.pack(pady=5)

    # CoreML 和 CPU 執行按鈕
    button_frame = ctk.CTkFrame(root)
    button_frame.pack(pady=10)
    coreml_button = ctk.CTkButton(button_frame, text="CoreML 執行", command=coreml_whisper, width=120, height=32)
    coreml_button.pack(side="left", padx=10)
    cpu_button = ctk.CTkButton(button_frame, text="CPU 執行", command=cpu_whisper, width=120, height=32)
    cpu_button.pack(side="left", padx=10)
    translate_button = ctk.CTkButton(button_frame, text="翻譯", command=translate_srt_files, width=100, height=32)
    translate_button.pack(side="left", padx=10)
    pause_button = ctk.CTkButton(button_frame, text="暫停", command=pause_task, width=100, height=32)
    pause_button.pack(side="left", padx=10)
    katakana_button = ctk.CTkButton(button_frame, text="日文轉片假名", command=japanese_to_katakana, width=140, height=32)
    katakana_button.pack(side="left", padx=10)

    # 日誌顯示區域
    log_frame = ctk.CTkFrame(root)
    log_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    log_label = ctk.CTkLabel(log_frame, text="執行日誌:", font=ctk.CTkFont(size=12))
    log_label.pack(anchor="w", padx=10, pady=(10, 5))
    
    log_textbox = ctk.CTkTextbox(log_frame, width=860, height=200, state="disabled", font=ctk.CTkFont(size=11))
    log_textbox.pack(pady=5, padx=10, fill="both", expand=True)
    logger.info("日誌顯示區域已初始化")
    
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
            logger.error(f"處理日誌隊列時發生錯誤: {e}")
        
        # 每 100ms 檢查一次
        root.after(100, process_log_queue)
    
    # 開始處理日誌隊列
    process_log_queue()

    # 版權信息
    license_label = ctk.CTkLabel(root, text="MIT License\n製作: Wayne", font=ctk.CTkFont(size=10))
    license_label.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    run()