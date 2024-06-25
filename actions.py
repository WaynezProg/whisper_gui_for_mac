import os
import subprocess
import wave

def convert_mp4_to_wav(video_file_path, audio_file_path):
    extract_audio_cmd = ['ffmpeg', '-y', '-i', video_file_path, '-acodec', 'pcm_s16le', '-ar', '16000', audio_file_path]
    subprocess.run(extract_audio_cmd, check=True)

def get_audio_duration(file_path):
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

def coreml_whisper(files, language, update_progress, pause_flag):
    total_duration = sum(get_audio_duration(file) for file in files)
    for i, file in enumerate(files):
        if pause_flag.is_set():
            break
        if file.endswith(".mp4"):
            audio_file_path = f"{os.path.splitext(file)[0]}.wav"
            convert_mp4_to_wav(file, audio_file_path)
            file = audio_file_path
        output_srt_path = f"{os.path.splitext(file)[0]}.srt"
        generate_srt_with_coreml_whisper(file, output_srt_path, language)
        progress = ((i + 1) / len(files)) * 100
        update_progress(progress)

def cpu_whisper(files, language, translate_to, update_progress, pause_flag):
    total_duration = sum(get_audio_duration(file) for file in files)
    for i, file in enumerate(files):
        if pause_flag.is_set():
            break
        if file.endswith(".mp4"):
            audio_file_path = f"{os.path.splitext(file)[0]}.wav"
            convert_mp4_to_wav(file, audio_file_path)
            file = audio_file_path
        output_srt_path = f"{os.path.splitext(file)[0]}.srt"
        generate_srt_with_cpu_whisper(file, output_srt_path, language)
        progress = ((i + 1) / len(files)) * 100
        update_progress(progress)

def generate_srt_with_coreml_whisper(audio_file_path, output_srt_path, language):
    output_dir = os.path.dirname(output_srt_path)
    output_file_base = os.path.splitext(audio_file_path)[0]
    whisper_cmd = [
        '/Users/waynetu/thrid_party_repo/whisper.cpp/main',  # 使用 whisper.cpp 的二進制文件
        '-m', '/Users/waynetu/thrid_party_repo/whisper.cpp/models/ggml-large-v3.bin',  # 指定模型文件
        '-f', audio_file_path,  # 指定音頻文件
        '-osrt',  # 輸出為 srt 文件
        '-of', output_file_base,  # 指定輸出文件基名
        '-l', language,  # 指定語言
    ]
    subprocess.run(whisper_cmd, check=True)

def generate_srt_with_cpu_whisper(audio_file_path, output_srt_path, language):
    output_dir = os.path.dirname(output_srt_path)
    whisper_cmd = [
        'whisper', audio_file_path,  # 使用 whisper 的二進制文件
        '--model', 'large-v3',  # 指定模型
        '--output_format', 'srt',  # 輸出格式為 srt
        '--output_dir', output_dir  # 指定輸出目錄
    ]
    if language != "auto":
        whisper_cmd.extend(['--language', language])  # 指定語言
    subprocess.run(whisper_cmd, check=True)
