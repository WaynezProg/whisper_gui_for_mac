# Whisper Transcription and Translation GUI
[![Demo Video](https://img.youtube.com/vi/2BLUM1b18Dg/0.jpg)](https://youtu.be/2BLUM1b18Dg)

> 💡 **Click the image above to watch the full demo video** showing the complete workflow of the application.

**Language**: [English](README.md) | [中文](README_zh.md)

## 📖 Introduction

A Whisper-based speech transcription and translation GUI application for macOS, supporting both **CoreML** and **CPU** modes. Users can add audio files for transcription and translate the results into multiple languages.

### Key Features

- 🎤 **Speech Transcription**: Supports CoreML acceleration (Apple Silicon) and CPU mode
- 🌍 **Multi-language Support**: Automatic language detection or manual specification
- 🔄 **AI Translation**: Translate transcription results using OpenAI API
- 🇯🇵 **Japanese Processing**: Convert Japanese subtitles to Katakana
- 📁 **Batch Processing**: Supports single files, multiple files, or entire folders
- 🎨 **Modern UI**: Built with CustomTkinter, supports dark/light themes

---

## 🚀 Quick Start

### Prerequisites

- **macOS** (macOS 12+ recommended)
- **Python 3.9+** (System Python 3.9.6 recommended)
- **Xcode Command Line Tools** (for compiling whisper.cpp)

### Installation Steps

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd whisper_gui_for_mac
```

#### 2. Create Virtual Environment

```bash
# Use system Python (recommended)
/usr/bin/python3 -m venv venv
source venv/bin/activate

# Or use pyenv Python
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Install System Tools (Required for CoreML)

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install ffmpeg (for audio conversion)
brew install ffmpeg
```

#### 5. Install and Compile whisper.cpp (Required for CoreML Mode)

> **Note**: Skip this step if you only need CPU mode.

##### 5.1 Download whisper.cpp

```bash
# Choose a directory to store whisper.cpp (recommended outside the project)
cd ~
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
```

##### 5.2 Compile with CoreML Support

```bash
# Using Makefile (recommended)
make clean
WHISPER_COREML=1 make -j

# Or using CMake
cmake -B build -DWHISPER_COREML=1
cmake --build build -j --config Release
```

After compilation, the executable will be at:
- Makefile: `./main`
- CMake: `./build/bin/whisper-cli`

##### 5.3 Download Model Files

```bash
# Download GGML model (large-v3 as example)
cd models
bash download-ggml-model.sh large-v3

# Or download manually
# From https://huggingface.co/ggerganov/whisper.cpp download the corresponding .bin file
```

##### 5.4 Generate CoreML Model (Optional but Recommended)

```bash
# In whisper.cpp directory
cd models
bash generate-coreml-model.sh large-v3
```

This will generate CoreML format model files for faster inference.

#### 6. Configure the Application

The project uses `config.py` to manage configuration, supporting environment variables and `.env` files.

**Method 1: Using .env File (Recommended)**

```bash
# Copy example file
cp env.example .env

# Edit .env file and fill in your configuration
nano .env
```

Set in `.env` file:

```env
# OpenAI API Key (required for translation)
OPENAI_API_KEY=sk-your-api-key-here

# Whisper.cpp paths (required for CoreML mode)
WHISPER_CPP_PATH=/Users/yourname/whisper.cpp/build/bin/whisper-cli
WHISPER_MODEL_PATH=/Users/yourname/whisper.cpp/models/ggml-large-v3.bin
```

**Method 2: Using Environment Variables**

```bash
export OPENAI_API_KEY='sk-your-api-key-here'
export WHISPER_CPP_PATH='/Users/yourname/whisper.cpp/build/bin/whisper-cli'
export WHISPER_MODEL_PATH='/Users/yourname/whisper.cpp/models/ggml-large-v3.bin'
```

**Check Configuration**

```bash
python check_config.py
```

**Detailed Configuration Guide**: See [docs/CONFIGURATION.md](docs/CONFIGURATION.md)

---

## 🎯 Usage

### Launching the Application

**Method 1: Double-click (Simplest, Recommended)**
- Double-click the `Whisper_GUI.command` file to launch
- On first run, macOS may prompt for security, allow execution in "System Preferences > Security & Privacy"
- The script will automatically detect `venv` or `.venv` virtual environment

**Method 2: Using Launch Script**
```bash
./run.sh
```

**Method 3: Manual Launch**
```bash
source venv/bin/activate  # or source .venv/bin/activate
python main.py
```

### GUI Features

#### Basic Operations

1. **Add Audio Files**
   - Click "Add" button to select files
   - Click "Add Folder" button to select entire folder
   - Supports `.wav` and `.mp4` formats

2. **Select Language**
   - Choose language from "Language" dropdown
   - Select "auto" for automatic language detection

3. **Execute Transcription**
   - **CoreML Execute**: Use CoreML acceleration (requires whisper.cpp)
   - **CPU Execute**: Use CPU mode (uses openai-whisper)

4. **Translate Results**
   - Click "Translate" button
   - Select target language
   - Requires OpenAI API Key configuration
   - ⚠️ **Important**: AI translation may contain errors. Please review and verify the translation results carefully.

5. **Other Features**
   - **Japanese to Katakana**: Convert Japanese subtitles to Katakana
   - **Pause Task**: Pause currently running task

#### Output File Naming Rules

After transcription completes, files will be generated in the same directory as the audio file:
- **CoreML Mode**: `filename_coreml.srt`
- **CPU Mode**: `filename_cpu.srt`

After translation completes, files will be generated:
- `filename_language.srt` - e.g., `filename_English.srt`, `filename_Chinese.srt`

After Katakana conversion:
- `filename_katakana.srt`

**Note**: If files already exist, a numeric suffix will be automatically added (e.g., `filename_coreml_1.srt`) to avoid overwriting existing files.

---

## ⚙️ Configuration

### Mode Selection

#### CoreML Mode (Recommended for Apple Silicon)

**Advantages**:
- ✅ Uses Apple Neural Engine, fast processing
- ✅ Low power consumption
- ✅ Suitable for long processing sessions

**Requirements**:
- ✅ Need to compile whisper.cpp
- ✅ Need to download model files
- ✅ Need to configure paths

#### CPU Mode

**Advantages**:
- ✅ Easy installation (just `pip install openai-whisper`)
- ✅ No compilation required
- ✅ Cross-platform

**Disadvantages**:
- ❌ Slower processing
- ❌ Higher power consumption

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Tkinter Dependency Issue

**Error**: `ImportError: Library not loaded: libtk8.6.dylib`

**Solution**:
```bash
# Recreate virtual environment using system Python
mv venv venv_backup
/usr/bin/python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. whisper.cpp Not Found

**Error**: `FileNotFoundError: whisper.cpp/main`

**Solution**:
- Check if path in config is correct
- Verify whisper.cpp is compiled
- Verify executable has execute permissions: `chmod +x /path/to/whisper.cpp/build/bin/whisper-cli`

#### 3. Model File Not Found

**Error**: `Error: model file not found`

**Solution**:
- Verify model file path is correct
- Verify model file is downloaded
- Check file permissions

#### 4. CoreML Feature Unavailable

**Error**: macOS version check error

**Solution**:
```bash
# Update coremltools
pip install --upgrade coremltools

# Or temporarily remove (if not needed)
pip uninstall coremltools
```

#### 5. Translation Feature Unavailable

**Error**: OpenAI API error

**Solution**:
- Check if API Key is correctly configured
- Verify network connection
- Check API quota

### Detailed Troubleshooting

For more issues, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## 📚 Documentation

- [Documentation Index](docs/README.md) - Navigation page for all documentation
- [Configuration Guide](docs/CONFIGURATION.md) - Detailed configuration guide
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Common issue solutions
- [Development Documentation](docs/DEVELOPMENT.md) - Development environment setup and project structure
- [Logging System](docs/LOGGING.md) - Logging functionality
- [Known Issues](docs/ISSUES.md) - Technical debt and known issues tracking

---

## 🛠️ Development

### Project Structure

```
whisper_gui_for_mac/
├── main.py              # Application entry point
├── gui.py               # GUI main program (CustomTkinter)
├── actions.py           # Transcription action handlers (CoreML/CPU)
├── ai_translate.py      # AI translation functionality
├── config.py            # Configuration management (environment variables, .env)
├── logger.py            # Logging system
├── check_config.py      # Configuration check tool
├── requirements.txt     # Python dependencies
├── env.example          # Environment variable example
├── run.sh               # Launch script
├── fix.sh               # Troubleshooting script
├── Whisper_GUI.command  # Double-click executable (macOS)
├── docs/                # Documentation directory
│   ├── README.md        # Documentation index
│   ├── CONFIGURATION.md # Configuration guide
│   ├── TROUBLESHOOTING.md # Troubleshooting
│   ├── DEVELOPMENT.md   # Development documentation
│   ├── LOGGING.md       # Logging guide
│   └── ISSUES.md        # Known issues
└── logs/                # Log files directory
```

### Tech Stack

- **GUI Framework**: CustomTkinter 5.2+
- **Python Version**: 3.9+ (System Python recommended)
- **Core Features**:
  - Whisper speech transcription (CoreML / CPU)
  - OpenAI API translation
  - Japanese Katakana conversion

### Development Environment Setup

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

---

## 📝 License

MIT License

---

## 👤 Developer

Created by: Wayne

---

## 🙏 Acknowledgments

- [whisper.cpp](https://github.com/ggerganov/whisper.cpp) - Efficient Whisper implementation
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern GUI framework
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech transcription model

---

## 📞 Support

If you encounter issues or have suggestions:
1. Check [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
2. Review [Known Issues](docs/ISSUES.md)
3. Submit an Issue or Pull Request

---

## 🔄 Changelog

### Latest Version

- ✅ Migrated to CustomTkinter (modern UI)
- ✅ Japanese Katakana conversion feature
- ✅ Improved error handling
- ✅ Complete documentation

---

## ⚠️ Notes

1. **AI Accuracy Warning**: Both speech transcription and AI translation are powered by AI models and may contain errors. Please carefully review and verify all results before using them for important purposes.
2. **API Key Security**: Do not commit API keys to public repositories, use `.env` files for management
3. **Model File Size**: Whisper model files are large (several GB), ensure sufficient storage space
4. **Compilation Time**: Compiling whisper.cpp may take 10-20 minutes
5. **System Requirements**: CoreML mode requires Apple Silicon (M1/M2/M3) or CoreML-capable Mac
6. **External Dependencies**: The application requires users to install and configure `whisper.cpp` and model files separately, these external resources are not packaged with the application

---

## 🎓 Learning Resources

- [Whisper.cpp Official Documentation](https://github.com/ggerganov/whisper.cpp)
- [CustomTkinter Documentation](https://customtkinter.tomschimansky.com/)
- [OpenAI Whisper Documentation](https://github.com/openai/whisper)
