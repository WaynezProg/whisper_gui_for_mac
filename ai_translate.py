from openai import OpenAI
import srt
import datetime
import os
from config import config
from logger import logger


def get_unique_output_path(base_path, suffix):
    """
    生成不重複的輸出檔案路徑
    
    Args:
        base_path: 基礎檔案路徑（不含副檔名）
        suffix: 要添加的後綴（例如 'coreml', 'cpu', '英文'）
    
    Returns:
        str: 不重複的檔案路徑
    """
    # 如果 base_path 包含副檔名，先移除
    if '.' in os.path.basename(base_path):
        base_path_no_ext = os.path.splitext(base_path)[0]
        ext = os.path.splitext(base_path)[1]
        output_dir = os.path.dirname(base_path)
    else:
        base_path_no_ext = base_path
        ext = '.srt'  # 預設為 .srt
        output_dir = os.path.dirname(base_path) if os.path.dirname(base_path) else '.'
    
    # 生成檔案名稱：base_name_suffix.ext
    output_path = os.path.join(output_dir, f"{os.path.basename(base_path_no_ext)}_{suffix}{ext}")
    
    # 如果檔案已存在，添加數字後綴
    counter = 1
    original_output_path = output_path
    while os.path.exists(output_path):
        base_name = os.path.basename(base_path_no_ext)
        output_path = os.path.join(output_dir, f"{base_name}_{suffix}_{counter}{ext}")
        counter += 1
    
    if counter > 1:
        logger.info(f"檔案 {original_output_path} 已存在，使用新名稱: {output_path}")
    
    return output_path

# 使用配置中的 API Key
# 如果沒有設定 API Key，會在調用時報錯
def get_openai_client():
    """取得 OpenAI 客戶端，如果 API Key 未設定則返回 None"""
    api_key = config.get_openai_api_key()
    if not api_key:
        raise ValueError(
            "OpenAI API Key 未設定。\n"
            "請設定環境變數 OPENAI_API_KEY 或在 .env 檔案中設定。\n"
            "詳見 docs/CONFIGURATION.md"
        )
    return OpenAI(api_key=api_key)

def translate_text(text, target_language=None, pause_flag=None):
    logger.info(f"開始翻譯文字，長度: {len(text)} 字元，目標語言: {target_language}")
    # 取得 OpenAI 客戶端
    client = get_openai_client()
    
    # 使用配置中的參數
    max_chunk_size = config.TRANSLATE_CHUNK_SIZE
    chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    logger.debug(f"文字分割為 {len(chunks)} 個區塊")
    translated_chunks = []
    
    # 使用配置中的系統提示詞
    system_prompt = config.TRANSLATE_SYSTEM_PROMPT.format(
        target_language=target_language or '目標語言'
    )
    
    for i, chunk in enumerate(chunks):
        if pause_flag and pause_flag.is_set():
            logger.warning("翻譯已暫停")
            break
        logger.info(f"翻譯區塊 [{i+1}/{len(chunks)}]: {chunk[:60]}...")
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"請幫我翻譯以下內容:\n\n{chunk}"}
            ]
        )
        translated_text = response.choices[0].message.content.strip()
        logger.debug(f"翻譯結果: {translated_text[:100]}...")
        translated_chunks.append(translated_text)
        logger.info(f"✓ 區塊 [{i+1}/{len(chunks)}] 翻譯完成")
    
    result = ' '.join(translated_chunks)
    logger.info(f"文字翻譯完成，結果長度: {len(result)} 字元")
    return result

def translate_srt(input_srt_path, output_srt_path=None, target_language=None, pause_flag=None):
    logger.info(f"開始翻譯 SRT 檔案: {os.path.basename(input_srt_path)}")
    with open(input_srt_path, 'r', encoding='utf-8') as f:
        srt_content = f.read()
        logger.debug(f"已讀取字幕檔案，大小: {len(srt_content)} 字元")

    subtitles = list(srt.parse(srt_content))
    logger.info(f"已解析字幕，共 {len(subtitles)} 條")

    for i, subtitle in enumerate(subtitles):
        if pause_flag and pause_flag.is_set():
            logger.warning("翻譯已暫停")
            break
        logger.info(f"翻譯字幕 [{i+1}/{len(subtitles)}]: {subtitle.content[:50]}...")
        subtitle.content = translate_text(subtitle.content, target_language, pause_flag)
        logger.debug(f"✓ 字幕 {subtitle.index} 翻譯完成")

    translated_srt_content = srt.compose(subtitles)
    logger.debug("已合成翻譯後的字幕")

    if output_srt_path is None or output_srt_path.strip() == "":
        # 使用翻譯語言作為後綴
        language_suffix = target_language or 'translated'
        # 將語言名稱轉換為適合檔案名稱的格式
        language_suffix = language_suffix.replace(' ', '_').replace('/', '_')
        base_path = os.path.splitext(input_srt_path)[0]
        output_srt_path = get_unique_output_path(base_path, language_suffix)
        logger.info(f"未提供輸出檔案路徑，將使用預設路徑：{output_srt_path}")

    # 確保輸出目錄存在
    output_dir = os.path.dirname(output_srt_path) if os.path.dirname(output_srt_path) else '.'
    os.makedirs(output_dir, exist_ok=True)

    with open(output_srt_path, 'w', encoding='utf-8') as f:
        f.write(translated_srt_content)
        logger.info(f"✓ 已寫入翻譯後的字幕檔案: {os.path.basename(output_srt_path)}")
