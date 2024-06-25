import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox, Progressbar
from tkinterdnd2 import TkinterDnD, DND_FILES
import threading
import actions  # 引入動作檔案
import os
import ai_translate  # 引入翻譯檔案

# 添加文件到列表框
def add_files(files=None):
    if files is None:
        files = filedialog.askopenfilenames(filetypes=[("WAV files", "*.wav"), ("MP4 files", "*.mp4")])
    for file in files:
        file_listbox.insert(tk.END, file)

# 添加資料夾中的文件到列表框
def add_folder():
    folder = filedialog.askdirectory()
    if folder:
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(('.mp4', '.wav')):
                    file_listbox.insert(tk.END, os.path.join(root, file))

# 從列表框中刪除選中的文件
def remove_files():
    selected_files = file_listbox.curselection()
    for index in reversed(selected_files):
        file_listbox.delete(index)

# 暫停標誌
pause_flag = threading.Event()

# 執行 CoreML Whisper 轉錄
def coreml_whisper():
    update_status("正在執行...")
    files = file_listbox.get(0, tk.END)
    language = language_combobox.get()

    if not files:
        messagebox.showwarning("警告", "請添加音頻文件。")
        update_status("")
        return

    progress_bar["maximum"] = 100
    progress_bar["value"] = 0

    # 在新線程中運行 CoreML Whisper
    def run_coreml_whisper():
        try:
            actions.coreml_whisper(files, language, update_progress, pause_flag)
            update_status("完成")
            messagebox.showinfo("完成", "CoreML 轉錄完成。")
        except Exception as e:
            update_status("發生錯誤")
            messagebox.showerror("錯誤", f"發生錯誤: {e}")

    threading.Thread(target=run_coreml_whisper).start()

# 執行 CPU Whisper 轉錄
def cpu_whisper():
    update_status("正在執行...")
    files = file_listbox.get(0, tk.END)
    language = language_combobox.get()
    translate_to = translate_combobox.get()

    if not files:
        messagebox.showwarning("警告", "請添加音頻文件。")
        update_status("")
        return

    progress_bar["maximum"] = 100
    progress_bar["value"] = 0

    # 在新線程中運行 CPU Whisper
    def run_cpu_whisper():
        try:
            actions.cpu_whisper(files, language, translate_to, update_progress, pause_flag)
            update_status("完成")
            messagebox.showinfo("完成", "CPU 轉錄完成。")
        except Exception as e:
            update_status("發生錯誤")
            messagebox.showerror("錯誤", f"發生錯誤: {e}")

    threading.Thread(target=run_cpu_whisper).start()

# 執行翻譯
def translate_srt_files():
    update_status("正在翻譯...")
    files = file_listbox.get(0, tk.END)
    target_language = translate_combobox.get()

    if not files:
        messagebox.showwarning("警告", "請添加音頻文件。")
        update_status("")
        return

    progress_bar["maximum"] = 100
    progress_bar["value"] = 0

    # 在新線程中運行翻譯
    def run_translate_srt_files():
        try:
            for file in files:
                if pause_flag.is_set():
                    break
                srt_file = file.replace('.wav', '.srt').replace('.mp4', '.srt')
                if os.path.exists(srt_file):
                    ai_translate.translate_srt(srt_file, target_language=target_language, pause_flag=pause_flag)
            update_status("翻譯完成")
            messagebox.showinfo("完成", "翻譯完成。")
        except Exception as e:
            update_status("發生錯誤")
            messagebox.showerror("錯誤", f"發生錯誤: {e}")

    threading.Thread(target=run_translate_srt_files).start()

# 更新進度條
def update_progress(progress):
    progress_bar["value"] = progress

# 更新狀態標籤
def update_status(message):
    status_label.config(text=message)

# 處理拖放事件
def on_drop(event):
    files = root.tk.splitlist(event.data)
    add_files(files)

# 暫停任務
def pause_task():
    pause_flag.set()
    update_status("任務已暫停，結果已保存。")
    messagebox.showinfo("暫停", "任務已暫停，結果已保存。")

# 主函數，創建 GUI 並運行
# 在文件頂部添加全局變量聲明
global root

def run():
    global root, file_listbox, language_combobox, translate_combobox, progress_bar, status_label

    root = TkinterDnD.Tk()
    root.title("Whisper Transcription GUI")

    # 添加音頻文件
    file_frame = tk.Frame(root)
    file_frame.pack(pady=10)
    file_listbox = tk.Listbox(file_frame, width=80, height=10)
    file_listbox.pack(side=tk.LEFT, padx=10)
    file_scrollbar = tk.Scrollbar(file_frame, orient=tk.VERTICAL)
    file_scrollbar.config(command=file_listbox.yview)
    file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    file_listbox.config(yscrollcommand=file_scrollbar.set)

    file_button_frame = tk.Frame(root)
    file_button_frame.pack(pady=5)
    add_button = tk.Button(file_button_frame, text="添加", command=add_files)
    add_button.pack(side=tk.LEFT, padx=10)
    add_folder_button = tk.Button(file_button_frame, text="添加資料夾", command=add_folder)
    add_folder_button.pack(side=tk.LEFT, padx=10)
    remove_button = tk.Button(file_button_frame, text="刪除", command=remove_files)
    remove_button.pack(side=tk.LEFT, padx=10)

    # 拼讀語言
    language_label = tk.Label(root, text="拼讀語言:")
    language_label.pack(pady=5)
    language_combobox = Combobox(root, values=["auto", "en", "zh", "ja", "ko", "fr", "de"])
    language_combobox.current(0)
    language_combobox.pack(pady=5)

    # 翻譯語言
    translate_label = tk.Label(root, text="翻譯為:")
    translate_label.pack(pady=5)
    translate_combobox = Combobox(root, values=["英文", "中文", "日文", "韓文", "法文", "德文"])
    translate_combobox.current(0)
    translate_combobox.pack(pady=5)

    # CoreML 和 CPU 執行按鈕
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)
    coreml_button = tk.Button(button_frame, text="CoreML 執行", command=coreml_whisper)
    coreml_button.pack(side=tk.LEFT, padx=10)
    cpu_button = tk.Button(button_frame, text="CPU 執行", command=cpu_whisper)
    cpu_button.pack(side=tk.LEFT, padx=10)
    translate_button = tk.Button(button_frame, text="翻譯", command=translate_srt_files)
    translate_button.pack(side=tk.LEFT, padx=10)
    pause_button = tk.Button(button_frame, text="暫停", command=pause_task)
    pause_button.pack(side=tk.LEFT, padx=10)

    # 進度條
    progress_bar = Progressbar(root, length=400, mode='determinate')
    progress_bar.pack(pady=10)

    # 進度狀態標籤
    status_label = tk.Label(root, text="")
    status_label.pack(pady=5)

    # 版權信息
    license_label = tk.Label(root, text="MIT License\n製作: Wayne")
    license_label.pack(pady=10)

    # 綁定拖曳事件
    file_listbox.drop_target_register(DND_FILES)
    file_listbox.dnd_bind('<<Drop>>', on_drop)

    root.mainloop()

if __name__ == "__main__":
    run()