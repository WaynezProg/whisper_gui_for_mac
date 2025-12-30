"""
Transcription action handlers / 轉錄動作處理模組
Handles CoreML and CPU mode transcription / 處理 CoreML 和 CPU 模式的轉錄
"""
import os
import subprocess
import wave
import shutil
import tempfile
import signal
import sys
from pathlib import Path
from config import config
from logger import logger


def get_unique_output_path(base_path, suffix):
    """
    Generate unique output file path / 生成不重複的輸出檔案路徑
    
    Args:
        base_path: Base file path (without extension) / 基礎檔案路徑（不含副檔名）
        suffix: Suffix to add (e.g., 'coreml', 'cpu', 'English') / 要添加的後綴（例如 'coreml', 'cpu', '英文'）
    
    Returns:
        str: Unique file path / 不重複的檔案路徑
    """
    # If base_path contains extension, remove it first / 如果 base_path 包含副檔名，先移除
    if '.' in os.path.basename(base_path):
        base_path_no_ext = os.path.splitext(base_path)[0]
        ext = os.path.splitext(base_path)[1]
        output_dir = os.path.dirname(base_path)
    else:
        base_path_no_ext = base_path
        ext = '.srt'  # Default to .srt / 預設為 .srt
        output_dir = os.path.dirname(base_path) if os.path.dirname(base_path) else '.'
    
    # Generate filename: base_name_suffix.ext / 生成檔案名稱：base_name_suffix.ext
    output_path = os.path.join(output_dir, f"{os.path.basename(base_path_no_ext)}_{suffix}{ext}")
    
    # If file exists, add numeric suffix / 如果檔案已存在，添加數字後綴
    counter = 1
    original_output_path = output_path
    while os.path.exists(output_path):
        base_name = os.path.basename(base_path_no_ext)
        output_path = os.path.join(output_dir, f"{base_name}_{suffix}_{counter}{ext}")
        counter += 1
    
    if counter > 1:
        logger.info(f"檔案 {original_output_path} 已存在，使用新名稱: {output_path}")
    
    return output_path

def convert_mp4_to_wav(video_file_path, audio_file_path):
    """
    Convert MP4 video to WAV audio file / 將 MP4 影片轉換為 WAV 音頻檔案
    
    Args:
        video_file_path: Path to input MP4 video file / 輸入 MP4 影片檔案路徑
        audio_file_path: Path to output WAV audio file / 輸出 WAV 音頻檔案路徑
    """
    logger.info(f"開始轉換 MP4 為 WAV: {os.path.basename(video_file_path)}")
    # Check if input file exists / 檢查輸入檔案是否存在
    if not os.path.exists(video_file_path):
        logger.error(f"影片檔案不存在: {video_file_path}")
        raise FileNotFoundError(f"影片檔案不存在: {video_file_path}")
    
    extract_audio_cmd = ['ffmpeg', '-y', '-i', video_file_path, '-acodec', 'pcm_s16le', '-ar', '16000', audio_file_path]
    logger.debug(f"執行 ffmpeg 指令: {' '.join(extract_audio_cmd)}")
    
    try:
        result = subprocess.run(
            extract_audio_cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout / 10 分鐘超時
        )
        # Check if output file was successfully created / 檢查輸出檔案是否成功建立
        if not os.path.exists(audio_file_path):
            logger.error(f"轉換失敗：輸出檔案不存在: {audio_file_path}")
            raise RuntimeError(f"轉換失敗：輸出檔案不存在: {audio_file_path}")
        logger.info(f"✓ 轉換完成: {os.path.basename(audio_file_path)}")
    except subprocess.TimeoutExpired:
        logger.error(f"ffmpeg 轉換超時（超過 10 分鐘）: {video_file_path}")
        raise RuntimeError(f"ffmpeg 轉換超時（超過 10 分鐘）: {video_file_path}")
    except subprocess.CalledProcessError as e:
        error_msg = f"ffmpeg 轉換失敗 (退出碼: {e.returncode})"
        if e.stderr:
            # ffmpeg error messages are usually in stderr / ffmpeg 的錯誤訊息通常在 stderr
            error_msg += f"\n錯誤訊息: {e.stderr[-1000:]}"  # Show last 1000 characters / 顯示最後 1000 字元
        logger.error(f"{error_msg}")
        raise RuntimeError(error_msg)

def get_audio_duration(file_path):
    """
    Get audio file duration in seconds / 獲取音頻檔案時長（秒）
    
    Args:
        file_path: Path to audio file / 音頻檔案路徑
    
    Returns:
        float: Duration in seconds, 0 if unable to determine / 時長（秒），無法確定時返回 0
    """
    if file_path.endswith(".wav"):
        with wave.open(file_path, 'r') as audio:
            frames = audio.getnframes()
            rate = audio.getframerate()
            duration = frames / float(rate)
            return duration
    elif file_path.endswith(".mp4"):
        command = f"ffmpeg -i \"{file_path}\" 2>&1 | grep 'Duration'"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        duration_str = result.stdout.split(",")[0].split("Duration:")[1].strip()
        h, m, s = map(float, duration_str.split(":"))
        duration = h * 3600 + m * 60 + s
        return duration
    return 0

def coreml_whisper(files, language, update_progress, pause_flag, update_status=None):
    """
    Execute CoreML Whisper transcription / 執行 CoreML Whisper 轉錄
    
    Args:
        files: List of files / 檔案列表
        language: Language code / 語言代碼
        update_progress: Progress update callback / 進度更新回調
        pause_flag: Pause flag / 暫停標誌
        update_status: Status update callback (optional) / 狀態更新回調（可選）
    """
    logger.info(f"開始 CoreML Whisper 轉錄，共 {len(files)} 個檔案，語言: {language}")
    total_duration = sum(get_audio_duration(file) for file in files)
    logger.info(f"總音頻時長: {total_duration:.2f} 秒")
    
    # Initial progress / 初始進度
    update_progress(0)
    if update_status:
        update_status(f"開始轉錄 {len(files)} 個檔案...", "INFO")
    
    for i, file in enumerate(files):
        if pause_flag.is_set():
            logger.warning("任務已暫停")
            if update_status:
                update_status("任務已暫停", "WARNING")
            break
        
        # Calculate progress range for current file / 計算當前檔案的進度範圍
        file_start_progress = (i / len(files)) * 100
        file_end_progress = ((i + 1) / len(files)) * 100
        
        logger.info(f"[{i+1}/{len(files)}] 處理檔案: {os.path.basename(file)}")
        if update_status:
            update_status(f"處理檔案 [{i+1}/{len(files)}]: {os.path.basename(file)}", "INFO")
        update_progress(file_start_progress + 5)  # Start processing, show 5% progress / 開始處理，顯示 5% 進度
        
        if file.endswith(".mp4"):
            audio_file_path = f"{os.path.splitext(file)[0]}.wav"
            convert_mp4_to_wav(file, audio_file_path)
            file = audio_file_path
            update_progress(file_start_progress + 5)  # Conversion complete, show 5% progress / 轉換完成，顯示 5% 進度
        
        # Generate unique output file path (with coreml suffix) / 生成不重複的輸出檔案路徑（使用 coreml 後綴）
        base_path = os.path.splitext(file)[0]
        output_srt_path = get_unique_output_path(base_path, 'coreml')
        
        # 計算轉錄的進度範圍（從 10% 到 95%，保留 5% 給完成）
        transcription_start = file_start_progress + 10
        transcription_end = file_end_progress - 5
        
        # 傳遞進度回調和範圍給轉錄函數
        if update_status:
            update_status(f"正在轉錄 [{i+1}/{len(files)}]...", "INFO")
        generate_srt_with_coreml_whisper(
            file, 
            output_srt_path, 
            language,
            update_progress=update_progress,
            progress_range=(transcription_start, transcription_end)
        )
        
        # 檔案處理完成，更新到該檔案的結束進度
        update_progress(file_end_progress)
        logger.info(f"✓ [{i+1}/{len(files)}] 完成: {os.path.basename(output_srt_path)}")
        if update_status:
            update_status(f"✓ 完成 [{i+1}/{len(files)}]: {os.path.basename(output_srt_path)}", "INFO")
    
    # 確保進度條顯示 100%
    update_progress(100)
    logger.info("CoreML Whisper 轉錄全部完成")
    if update_status:
        update_status(f"✓ 全部完成，共處理 {len(files)} 個檔案", "INFO")

def cpu_whisper(files, language, translate_to, update_progress, pause_flag, update_status=None):
    """
    Execute CPU Whisper transcription / 執行 CPU Whisper 轉錄
    
    Args:
        files: List of files / 檔案列表
        language: Language code / 語言代碼
        translate_to: Target language for translation (unused, kept for backward compatibility) / 翻譯目標語言（未使用，保留向後兼容）
        update_progress: Progress update callback / 進度更新回調
        pause_flag: Pause flag / 暫停標誌
        update_status: Status update callback (optional) / 狀態更新回調（可選）
    """
    logger.info(f"開始 CPU Whisper 轉錄，共 {len(files)} 個檔案，語言: {language}")
    total_duration = sum(get_audio_duration(file) for file in files)
    logger.info(f"總音頻時長: {total_duration:.2f} 秒")
    
    # 初始進度
    update_progress(0)
    if update_status:
        update_status(f"開始轉錄 {len(files)} 個檔案...", "INFO")
    
    for i, file in enumerate(files):
        if pause_flag.is_set():
            logger.warning("任務已暫停")
            if update_status:
                update_status("任務已暫停", "WARNING")
            break
        
        # 計算當前檔案的進度範圍
        file_start_progress = (i / len(files)) * 100
        file_end_progress = ((i + 1) / len(files)) * 100
        
        logger.info(f"[{i+1}/{len(files)}] 處理檔案: {os.path.basename(file)}")
        if update_status:
            update_status(f"處理檔案 [{i+1}/{len(files)}]: {os.path.basename(file)}", "INFO")
        update_progress(file_start_progress + 5)  # 開始處理，顯示 5% 進度
        
        if file.endswith(".mp4"):
            audio_file_path = f"{os.path.splitext(file)[0]}.wav"
            convert_mp4_to_wav(file, audio_file_path)
            file = audio_file_path
            update_progress(file_start_progress + 10)  # 轉換完成，顯示 10% 進度
        
        # 生成不重複的輸出檔案路徑（使用 cpu 後綴）
        base_path = os.path.splitext(file)[0]
        output_srt_path = get_unique_output_path(base_path, 'cpu')
        update_progress(file_start_progress + 15)  # 開始轉錄，顯示 15% 進度
        if update_status:
            update_status(f"正在轉錄 [{i+1}/{len(files)}]...", "INFO")
        
        generate_srt_with_cpu_whisper(file, output_srt_path, language)
        
        # 檔案處理完成，更新到該檔案的結束進度
        update_progress(file_end_progress)
        logger.info(f"✓ [{i+1}/{len(files)}] 完成: {os.path.basename(output_srt_path)}")
        if update_status:
            update_status(f"✓ 完成 [{i+1}/{len(files)}]: {os.path.basename(output_srt_path)}", "INFO")
    
    # 確保進度條顯示 100%
    update_progress(100)
    logger.info("CPU Whisper 轉錄全部完成")
    if update_status:
        update_status(f"✓ 全部完成，共處理 {len(files)} 個檔案", "INFO")

def _sanitize_path_for_whisper(file_path):
    """
    處理包含特殊字元的檔案路徑
    如果路徑包含非 ASCII 字元，複製到臨時目錄使用簡單檔名
    """
    try:
        # 檢查路徑是否包含非 ASCII 字元
        file_path.encode('ascii')
        # 如果成功，路徑是純 ASCII，可以直接使用
        logger.debug(f"檔案路徑為 ASCII，直接使用: {os.path.basename(file_path)}")
        return file_path, None
    except UnicodeEncodeError:
        # 路徑包含非 ASCII 字元，需要處理
        logger.warning(f"檔案路徑包含特殊字元，使用臨時檔案: {os.path.basename(file_path)}")
        
        # 建立臨時檔案
        temp_dir = tempfile.gettempdir()
        file_ext = os.path.splitext(file_path)[1]
        temp_file = os.path.join(temp_dir, f"whisper_input_{os.getpid()}{file_ext}")
        
        # 複製檔案到臨時位置
        logger.debug(f"複製檔案到臨時位置: {temp_file}")
        shutil.copy2(file_path, temp_file)
        
        return temp_file, temp_file  # 返回臨時檔案路徑和清理標記


def generate_srt_with_coreml_whisper(audio_file_path, output_srt_path, language, update_progress=None, progress_range=(0, 100)):
    """
    生成 SRT 字幕檔案（CoreML Whisper）
    
    Args:
        audio_file_path: 音頻檔案路徑
        output_srt_path: 輸出 SRT 檔案路徑
        language: 語言代碼
        update_progress: 進度更新回調函數（可選）
        progress_range: 進度範圍 (start, end)，預設 (0, 100)
    """
    logger.info(f"開始 CoreML Whisper 轉錄: {os.path.basename(audio_file_path)} -> {os.path.basename(output_srt_path)}")
    output_dir = os.path.dirname(output_srt_path)
    # 注意：output_srt_path 已經包含 coreml 後綴，不需要再使用 audio_file_path 的基礎名稱
    output_file_base = os.path.splitext(output_srt_path)[0]
    
    progress_start, progress_end = progress_range
    
    # 使用配置中的路徑
    whisper_cpp_path = config.get_whisper_cpp_path()
    model_path = config.get_whisper_model_path()
    
    logger.debug(f"Whisper.cpp 路徑: {whisper_cpp_path}")
    logger.debug(f"模型路徑: {model_path}")
    
    # 檢查路徑是否存在
    if not os.path.exists(whisper_cpp_path):
        logger.error(f"Whisper.cpp 執行檔不存在: {whisper_cpp_path}")
        raise FileNotFoundError(
            f"Whisper.cpp 執行檔不存在: {whisper_cpp_path}\n"
            f"請設定環境變數 WHISPER_CPP_PATH 或檢查 config.py"
        )
    if not os.path.exists(model_path):
        logger.error(f"模型檔案不存在: {model_path}")
        raise FileNotFoundError(
            f"模型檔案不存在: {model_path}\n"
            f"請設定環境變數 WHISPER_MODEL_PATH 或檢查 config.py"
        )
    
    # 檢查音頻檔案是否存在
    if not os.path.exists(audio_file_path):
        logger.error(f"音頻檔案不存在: {audio_file_path}")
        raise FileNotFoundError(f"音頻檔案不存在: {audio_file_path}")
    
    # 處理特殊字元路徑（如果包含日文等）
    safe_audio_path, temp_file = _sanitize_path_for_whisper(audio_file_path)
    safe_output_base = os.path.join(tempfile.gettempdir(), f"whisper_output_{os.getpid()}") if temp_file else output_file_base
    
    try:
        # whisper-cli 的參數格式：[options] file0 file1 ...
        # 檔案應該直接作為參數，而不是用 -f
        whisper_cmd = [
            whisper_cpp_path,  # 使用配置中的 whisper.cpp 路徑
            '-m', model_path,  # 使用配置中的模型路徑
            '-osrt',  # 輸出為 srt 文件
            '-of', safe_output_base,  # 指定輸出文件基名
            '-l', language,  # 指定語言
            safe_audio_path,  # 音頻檔案直接作為參數（不使用 -f）
        ]
        
        logger.debug(f"執行指令: {' '.join(whisper_cmd)}")
        
        # 更新進度：開始執行
        if update_progress:
            update_progress(progress_start + (progress_end - progress_start) * 0.1)  # 10%
        
        # 執行 whisper.cpp，使用更安全的方式
        # 注意：segmentation fault 無法被 Python 直接捕獲，但我們可以檢查退出碼
        try:
            logger.info("啟動 Whisper.cpp 進程...")
            # 使用 Popen 以便更好地控制進程
            process = subprocess.Popen(
                whisper_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None  # 建立新的進程組
            )
            logger.debug(f"Whisper.cpp 進程已啟動 (PID: {process.pid})")
            
            # 在執行期間模擬進度更新（因為無法從 whisper.cpp 獲取實際進度）
            import threading
            import time
            
            def simulate_progress():
                """模擬進度更新，讓用戶知道程序正在運行"""
                current_progress = progress_start + (progress_end - progress_start) * 0.1
                max_progress = progress_start + (progress_end - progress_start) * 0.9
                step = (max_progress - current_progress) / 60  # 60 次更新
                
                while process.poll() is None:  # 進程還在運行
                    time.sleep(1)  # 每秒更新一次
                    current_progress = min(current_progress + step, max_progress)
                    if update_progress:
                        update_progress(current_progress)
            
            progress_thread = threading.Thread(target=simulate_progress, daemon=True)
            progress_thread.start()
            
            try:
                logger.info("等待 Whisper.cpp 執行完成...")
                stdout, stderr = process.communicate(timeout=3600)  # 1 小時超時
                return_code = process.returncode
                logger.debug(f"Whisper.cpp 執行完成，退出碼: {return_code}")
                if stdout:
                    logger.debug(f"Whisper 輸出: {stdout[:500]}...")
                if stderr:
                    logger.debug(f"Whisper 錯誤輸出: {stderr[:500]}...")
            except subprocess.TimeoutExpired:
                logger.error(f"Whisper 執行超時（超過 1 小時）: {audio_file_path}")
                # 超時，終止進程
                process.kill()
                if hasattr(os, 'setsid'):
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    except:
                        pass
                raise RuntimeError(f"Whisper 執行超時（超過 1 小時）: {audio_file_path}")
            
            # 檢查退出碼
            if return_code != 0:
                logger.error(f"Whisper 執行失敗，退出碼: {return_code}")
                # 非零退出碼可能表示錯誤或崩潰
                error_msg = f"Whisper 執行失敗 (退出碼: {return_code})"
                
                # 檢查是否是 segmentation fault
                # macOS 上通常是 -11 (SIGSEGV)，Linux 上可能是 139
                # 使用 signal.SIGSEGV 的值來檢查（通常是 11）
                is_segfault = (
                    return_code == -11 or 
                    return_code == 139 or 
                    return_code == -signal.SIGSEGV or
                    (return_code < 0 and abs(return_code) == signal.SIGSEGV)
                )
                
                if is_segfault:
                    logger.critical("Whisper 發生 Segmentation Fault（段錯誤）")
                    error_msg = (
                        f"❌ Whisper 發生 Segmentation Fault（段錯誤）\n\n"
                        f"可能原因：\n"
                        f"1. 檔案路徑包含特殊字元（已嘗試處理，但可能仍有問題）\n"
                        f"2. whisper.cpp 執行檔編譯問題或與系統不兼容\n"
                        f"3. 模型檔案損壞或格式不正確\n"
                        f"4. 記憶體不足\n"
                        f"5. whisper.cpp 版本問題\n\n"
                        f"💡 建議解決方案：\n"
                        f"• 使用「CPU 執行」模式（較穩定，功能相同）\n"
                        f"• 檢查 whisper.cpp 是否正確編譯\n"
                        f"• 檢查模型檔案是否完整\n"
                        f"• 嘗試使用較小的模型（如 medium 或 small）"
                    )
                else:
                    logger.error(f"Whisper 執行失敗，退出碼: {return_code}")
                    # 其他錯誤
                    if stderr:
                        logger.error(f"錯誤訊息: {stderr}")
                        error_msg += f"\n\n錯誤訊息:\n{stderr}"
                    if stdout:
                        logger.debug(f"輸出: {stdout[:500]}")
                        error_msg += f"\n\n輸出:\n{stdout[:500]}"
                
                raise RuntimeError(error_msg)
            
            # 成功執行
            logger.info("Whisper.cpp 執行成功")
            
            # 更新進度：執行完成
            if update_progress:
                update_progress(progress_start + (progress_end - progress_start) * 0.95)  # 95%
            
            # 如果使用了臨時檔案，需要將輸出檔案移動到原始位置
            if temp_file:
                temp_srt = f"{safe_output_base}.srt"
                if os.path.exists(temp_srt):
                    logger.debug(f"移動臨時輸出檔案: {temp_srt} -> {output_srt_path}")
                    shutil.move(temp_srt, output_srt_path)
                    logger.info(f"✓ 已將輸出檔案移動到: {output_srt_path}")
                else:
                    logger.error(f"輸出檔案不存在: {temp_srt}")
                    raise RuntimeError(f"輸出檔案不存在: {temp_srt}")
            else:
                # whisper.cpp 會根據 -of 參數生成檔案，但我們已經指定了 output_srt_path
                # 檢查輸出檔案是否存在（可能在不同的位置）
                expected_srt = f"{output_file_base}.srt"
                if os.path.exists(expected_srt) and expected_srt != output_srt_path:
                    # 如果檔案在預期位置但路徑不同，移動到目標位置
                    logger.debug(f"移動輸出檔案: {expected_srt} -> {output_srt_path}")
                    shutil.move(expected_srt, output_srt_path)
                    logger.info(f"✓ 已將輸出檔案移動到: {output_srt_path}")
                elif os.path.exists(output_srt_path):
                    logger.info(f"✓ 輸出檔案已生成: {output_srt_path}")
                else:
                    logger.error(f"輸出檔案不存在: {expected_srt} 或 {output_srt_path}")
                    raise RuntimeError(f"輸出檔案不存在: {expected_srt} 或 {output_srt_path}")
                    
        except subprocess.TimeoutExpired:
            logger.error(f"Whisper 執行超時（超過 1 小時）: {audio_file_path}")
            raise RuntimeError(f"Whisper 執行超時（超過 1 小時）: {audio_file_path}")
        except RuntimeError:
            # 重新拋出 RuntimeError
            raise
        except Exception as e:
            logger.exception(f"執行 Whisper 時發生未預期的錯誤: {e}")
            raise RuntimeError(f"執行 Whisper 時發生錯誤: {e}")
    finally:
        # 清理臨時檔案
        if temp_file and os.path.exists(temp_file):
            try:
                logger.debug(f"清理臨時檔案: {temp_file}")
                os.remove(temp_file)
            except Exception as e:
                logger.warning(f"清理臨時檔案失敗: {e}")

def generate_srt_with_cpu_whisper(audio_file_path, output_srt_path, language):
    logger.info(f"開始 CPU Whisper 轉錄: {os.path.basename(audio_file_path)} -> {os.path.basename(output_srt_path)}")
    output_dir = os.path.dirname(output_srt_path)
    
    # 檢查音頻檔案是否存在
    if not os.path.exists(audio_file_path):
        logger.error(f"音頻檔案不存在: {audio_file_path}")
        raise FileNotFoundError(f"音頻檔案不存在: {audio_file_path}")
    
    # 處理特殊字元路徑（如果包含日文等）
    safe_audio_path, temp_file = _sanitize_path_for_whisper(audio_file_path)
    
    # 如果使用臨時檔案，輸出也需要調整
    if temp_file:
        # 臨時檔案的輸出目錄
        temp_output_dir = tempfile.gettempdir()
        output_file_base = os.path.splitext(os.path.basename(output_srt_path))[0]
        safe_output_srt = os.path.join(temp_output_dir, f"{output_file_base}.srt")
    else:
        safe_output_srt = output_srt_path
        safe_output_dir = output_dir
    
    whisper_cmd = [
        'whisper', safe_audio_path,  # 使用處理過的安全路徑
        '--model', config.CPU_WHISPER_MODEL,  # 使用配置中的模型
        '--output_format', 'srt',  # 輸出格式為 srt
        '--output_dir', temp_output_dir if temp_file else output_dir  # 指定輸出目錄
    ]
    if language != "auto":
        whisper_cmd.extend(['--language', language])  # 指定語言
    
    # 驗證模型名稱（確保不是錯誤的模型名稱）
    model_name = config.CPU_WHISPER_MODEL
    if model_name == 'large-v3-turbo':
        logger.warning(f"檢測到錯誤的模型名稱 'large-v3-turbo'，自動修正為 'turbo'")
        model_name = 'turbo'
        # 更新命令中的模型名稱
        whisper_cmd[whisper_cmd.index('--model') + 1] = model_name
    
    logger.debug(f"執行指令: {' '.join(whisper_cmd)}")
    logger.info(f"使用模型: {model_name}")
    
    # 執行 whisper，即時顯示 log
    try:
        logger.info("啟動 CPU Whisper 進程...")
        # 使用 Popen 以便即時顯示輸出
        process = subprocess.Popen(
            whisper_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # 將 stderr 合併到 stdout
            text=True,
            bufsize=1,  # 行緩衝
            env=os.environ.copy()  # 確保環境變數正確傳遞
        )
        logger.info(f"CPU Whisper 進程已啟動 (PID: {process.pid})")
        
        # 即時讀取並顯示輸出
        output_lines = []
        logger.info("等待 CPU Whisper 執行完成...")
        
        # 使用 threading 來即時讀取輸出
        import threading
        import queue
        import time
        
        output_queue = queue.Queue()
        read_complete = threading.Event()
        
        def read_output():
            """在背景線程中讀取輸出"""
            try:
                for line in process.stdout:
                    line = line.rstrip()
                    if line:  # 忽略空行
                        output_queue.put(line)
                read_complete.set()
            except Exception as e:
                logger.error(f"讀取輸出時發生錯誤: {e}")
                read_complete.set()
        
        reader_thread = threading.Thread(target=read_output, daemon=True)
        reader_thread.start()
        
        # 主線程中即時顯示輸出，並監控超時
        start_time = time.time()
        timeout_seconds = 3600  # 1 小時超時
        
        while True:
            # 檢查超時
            if time.time() - start_time > timeout_seconds:
                logger.error(f"Whisper 執行超時（超過 1 小時）: {audio_file_path}")
                process.kill()
                process.wait()
                raise RuntimeError(f"Whisper 執行超時（超過 1 小時）: {audio_file_path}")
            
            # 檢查進程是否已結束
            if process.poll() is not None:
                # 進程已結束，等待讀取線程完成
                read_complete.wait(timeout=5)
                break
            
            # 嘗試讀取輸出
            try:
                line = output_queue.get(timeout=1)  # 1 秒超時
                logger.info(f"Whisper: {line}")
                output_lines.append(line)
            except queue.Empty:
                continue  # 繼續等待
        
        # 讀取剩餘輸出
        while True:
            try:
                line = output_queue.get_nowait()
                logger.info(f"Whisper: {line}")
                output_lines.append(line)
            except queue.Empty:
                break
        
        # 獲取進程退出碼
        return_code = process.returncode
        logger.info(f"CPU Whisper 執行完成，退出碼: {return_code}")
        
        if return_code != 0:
            error_output = '\n'.join(output_lines)
            raise subprocess.CalledProcessError(return_code, whisper_cmd, output=error_output)
        
        logger.info("CPU Whisper 執行成功")
        
        # 如果使用臨時檔案，需要移動輸出檔案
        if temp_file:
            # whisper 會根據輸入檔案名稱生成輸出檔案
            temp_input_base = os.path.splitext(os.path.basename(safe_audio_path))[0]
            temp_output_file = os.path.join(temp_output_dir, f"{temp_input_base}.srt")
            
            if os.path.exists(temp_output_file):
                # 移動到最終位置
                import shutil
                shutil.move(temp_output_file, output_srt_path)
                logger.info(f"✓ 已將輸出檔案移動到: {output_srt_path}")
            else:
                # 嘗試其他可能的檔案名稱
                expected_srt = safe_output_srt
                if os.path.exists(expected_srt):
                    shutil.move(expected_srt, output_srt_path)
                    logger.info(f"✓ 已將輸出檔案移動到: {output_srt_path}")
                else:
                    logger.error(f"輸出檔案不存在: {temp_output_file} 或 {expected_srt}")
                    raise FileNotFoundError(f"輸出檔案不存在: {temp_output_file}")
        else:
            # 檢查輸出檔案是否存在
            expected_srt = os.path.join(output_dir, os.path.splitext(os.path.basename(audio_file_path))[0] + '.srt')
            if os.path.exists(expected_srt):
                logger.info(f"✓ 輸出檔案已生成: {expected_srt}")
            else:
                logger.warning(f"輸出檔案可能不在預期位置: {expected_srt}")
    except subprocess.TimeoutExpired:
        logger.error(f"Whisper 執行超時（超過 1 小時）: {audio_file_path}")
        raise RuntimeError(f"Whisper 執行超時（超過 1 小時）: {audio_file_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Whisper 執行失敗 (退出碼: {e.returncode})")
        logger.error(f"執行命令: {' '.join(whisper_cmd)}")
        error_msg = f"Whisper 執行失敗 (退出碼: {e.returncode})"
        
        # 顯示完整的錯誤訊息（不截斷）
        if hasattr(e, 'stderr') and e.stderr:
            logger.error(f"錯誤訊息: {e.stderr}")
            error_msg += f"\n錯誤訊息: {e.stderr[:1000]}"  # 顯示更多內容
        if hasattr(e, 'output') and e.output:
            logger.error(f"輸出: {e.output}")
            error_msg += f"\n輸出: {e.output[:1000]}"
        elif hasattr(e, 'stdout') and e.stdout:
            logger.error(f"輸出: {e.stdout}")
            error_msg += f"\n輸出: {e.stdout[:1000]}"
        
        # 特別處理退出碼 2（通常是參數錯誤）
        if e.returncode == 2:
            error_msg += "\n\n可能的原因："
            error_msg += "\n1. 模型名稱不正確（應為: tiny, base, small, medium, large, turbo）"
            error_msg += "\n2. 參數格式不正確"
            error_msg += "\n3. whisper 命令未正確安裝"
            error_msg += "\n\n建議："
            error_msg += "\n- 檢查 whisper 是否正確安裝: pip install -U openai-whisper"
            error_msg += "\n- 檢查模型名稱是否正確"
            error_msg += "\n- 嘗試手動執行命令查看詳細錯誤"
        
        raise RuntimeError(error_msg)
    except Exception as e:
        logger.exception(f"執行 Whisper 時發生未預期的錯誤: {e}")
        raise RuntimeError(f"執行 Whisper 時發生錯誤: {e}")
    finally:
        # 清理臨時檔案
        if temp_file and os.path.exists(safe_audio_path):
            try:
                os.remove(safe_audio_path)
                logger.debug(f"清理臨時檔案: {safe_audio_path}")
            except Exception as e:
                logger.warning(f"清理臨時檔案失敗: {e}")
