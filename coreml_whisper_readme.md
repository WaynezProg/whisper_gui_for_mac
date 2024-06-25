
# Whisper.cpp 操作說明

## 前置條件

確保已經完成以下步驟：

1. 安裝必要的 Python 依賴：
    ```bash
    pip install ane_transformers
    pip install openai-whisper
    pip install coremltools
    ```
2. 安裝 Xcode 和命令行工具：
    ```bash
    xcode-select --install
    ```

3. 生成 Core ML 模型（以 `large-v3` 模型為例）：
    ```bash
    ./models/generate-coreml-model.sh large-v3
    ```

4. 構建 `whisper.cpp` 支援 Core ML：
    使用 Makefile：
    ```bash
    make clean
    WHISPER_COREML=1 make -j
    ```

    使用 CMake：
    ```bash
    cmake -B build -DWHISPER_COREML=1
    cmake --build build -j --config Release
    ```

## 使用 Whisper.cpp 進行語音轉錄

### 自動檢測語言

運行以下命令來自動檢測語言：
```bash
./main -m models/ggml-large-v3.bin -f samples/your_audio_file.wav --detect-language
```

### 自動檢測語言並轉錄

運行以下命令來自動檢測語言並進行轉錄：
```bash
./main -m models/ggml-large-v3.bin -f samples/your_audio_file.wav --detect-language --language auto
```

### 指定語言進行轉錄

如果你知道語音的語言，可以使用 `-l` 或 `--language` 參數來指定語言：
```bash
./main -m models/ggml-large-v3.bin -f samples/your_audio_file.wav -l zh
```

### 將結果輸出到文件

你可以將結果輸出到文本文件中：
```bash
./main -m models/ggml-large-v3.bin -f samples/your_audio_file.wav -l zh --output-txt --output-file output
```

### 完整的示例

以下是自動檢測語言並將結果輸出到文件的完整命令：
```bash
./main -m models/ggml-large-v3.bin -f samples/your_audio_file.wav --detect-language --language auto --output-txt --output-file output
```

### 檢查輸出結果

運行命令後，檢查輸出結果，確認它正確地識別和轉錄了語音。

## 可用參數列表

使用 `./main -h` 查看所有可用的參數和選項：
```bash
./main -h
```

### 參數詳解

```
usage: ./main [options] file0.wav file1.wav ...

options:
  -h,        --help              [default] show this help message and exit
  -t N,      --threads N         [4      ] number of threads to use during computation
  -p N,      --processors N      [1      ] number of processors to use during computation
  -ot N,     --offset-t N        [0      ] time offset in milliseconds
  -on N,     --offset-n N        [0      ] segment index offset
  -d  N,     --duration N        [0      ] duration of audio to process in milliseconds
  -mc N,     --max-context N     [-1     ] maximum number of text context tokens to store
  -ml N,     --max-len N         [0      ] maximum segment length in characters
  -sow,      --split-on-word     [false  ] split on word rather than on token
  -bo N,     --best-of N         [5      ] number of best candidates to keep
  -bs N,     --beam-size N       [5      ] beam size for beam search
  -ac N,     --audio-ctx N       [0      ] audio context size (0 - all)
  -wt N,     --word-thold N      [0.01   ] word timestamp probability threshold
  -et N,     --entropy-thold N   [2.40   ] entropy threshold for decoder fail
  -lpt N,    --logprob-thold N   [-1.00  ] log probability threshold for decoder fail
  -tp,       --temperature N     [0.00   ] The sampling temperature, between 0 and 1
  -tpi,      --temperature-inc N [0.20   ] The increment of temperature, between 0 and 1
  -debug,    --debug-mode        [false  ] enable debug mode (eg. dump log_mel)
  -tr,       --translate         [false  ] translate from source language to english
  -di,       --diarize           [false  ] stereo audio diarization
  -tdrz,     --tinydiarize       [false  ] enable tinydiarize (requires a tdrz model)
  -nf,       --no-fallback       [false  ] do not use temperature fallback while decoding
  -otxt,     --output-txt        [false  ] output result in a text file
  -ovtt,     --output-vtt        [false  ] output result in a vtt file
  -osrt,     --output-srt        [false  ] output result in a srt file
  -olrc,     --output-lrc        [false  ] output result in a lrc file
  -owts,     --output-words      [false  ] output script for generating karaoke video
  -fp,       --font-path         [/System/Library/Fonts/Supplemental/Courier New Bold.ttf] path to a monospace font for karaoke video
  -ocsv,     --output-csv        [false  ] output result in a CSV file
  -oj,       --output-json       [false  ] output result in a JSON file
  -ojf,      --output-json-full  [false  ] include more information in the JSON file
  -of FNAME, --output-file FNAME [       ] output file path (without file extension)
  -np,       --no-prints         [false  ] do not print anything other than the results
  -ps,       --print-special     [false  ] print special tokens
  -pc,       --print-colors      [false  ] print colors
  -pp,       --print-progress    [false  ] print progress
  -nt,       --no-timestamps     [false  ] do not print timestamps
  -l LANG,   --language LANG     [en     ] spoken language ('auto' for auto-detect)
  -dl,       --detect-language   [false  ] exit after automatically detecting language
             --prompt PROMPT     [       ] initial prompt (max n_text_ctx/2 tokens)
  -m FNAME,  --model FNAME       [models/ggml-base.en.bin] model path
  -f FNAME,  --file FNAME        [       ] input WAV file path
  -oved D,   --ov-e-device DNAME [CPU    ] the OpenVINO device used for encode inference
  -dtw MODEL --dtw MODEL         [       ] compute token-level timestamps
  -ls,       --log-score         [false  ] log best decoder scores of tokens
  -ng,       --no-gpu            [false  ] disable GPU
  -fa,       --flash-attn        [false  ] flash attention
  --suppress-regex REGEX         [       ] regular expression matching tokens to suppress
  --grammar GRAMMAR              [       ] GBNF grammar to guide decoding
  --grammar-rule RULE            [       ] top-level GBNF grammar rule name
  --grammar-penalty N            [100.0  ] scales down logits of nongrammar tokens
```
