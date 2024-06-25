from openai import OpenAI
import srt
import datetime
import os

client = OpenAI(
  api_key='sk-proj-JV7YYtXnJA5dXfYA76cyT3BlbkFJWO7pKRAYrM7NGETuj8hh',
)

def translate_text(text, target_language=None, pause_flag=None):
    max_chunk_size = 500  # 設定每段文字的最大字數
    chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    translated_chunks = []
    
    for chunk in chunks:
        if pause_flag and pause_flag.is_set():
            print("翻譯已暫停。")
            break
        response = client.chat.completions.create(
            model="gpt-4o",
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            messages=[
                {"role": "system", "content": f"你是一個翻譯專家，幫我翻譯成{target_language}，禁止使用簡體中文。結果要語句通順且好懂的翻譯結果。只需要輸出翻譯結果"},
                {"role": "user", "content": f"請幫我翻譯以下內容:\n\n{chunk}"}
            ]
        )
        print(response.choices[0].message.content)
        print(f"正在翻譯：{chunk[:60]}...")  # 印出正在翻譯的部分內容
        translated_chunks.append(response.choices[0].message.content.strip())
    
    return ' '.join(translated_chunks)

def translate_srt(input_srt_path, output_srt_path=None, target_language=None, pause_flag=None):
    with open(input_srt_path, 'r', encoding='utf-8') as f:
        srt_content = f.read()
        print("已讀取字幕檔案。")

    subtitles = list(srt.parse(srt_content))
    print("正在解析字幕。")

    for subtitle in subtitles:
        if pause_flag and pause_flag.is_set():
            print("翻譯已暫停。")
            break
        subtitle.content = translate_text(subtitle.content, target_language, pause_flag)
        print(f"已翻譯字幕：{subtitle.index}")

    translated_srt_content = srt.compose(subtitles)
    print("已合成翻譯後的字幕。")

    if output_srt_path is None or output_srt_path.strip() == "":
        output_srt_path = input_srt_path.replace('.srt', '_translated.srt')
        print(f"未提供輸出檔案路徑，將使用預設路徑：{output_srt_path}")

    # 確保輸出目錄存在
    os.makedirs(os.path.dirname(output_srt_path), exist_ok=True)

    with open(output_srt_path, 'w', encoding='utf-8') as f:
        f.write(translated_srt_content)
        print("已寫入翻譯後的字幕檔案。")
