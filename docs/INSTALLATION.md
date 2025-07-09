# Installation Guide

## System Requirements

- **Python 3.8+** (for source installation)
- **2GB RAM minimum** (4GB recommended)
- **Microphone** (built-in or external)
- **500MB disk space** (for models)

## Installation Methods

### Option 1: Pre-built Binaries (Recommended)

1. Go to the [Releases page](https://github.com/yourusername/LoudMouth/releases)
2. Download the appropriate file for your system:
   - **Windows**: `LoudMouth-Windows.exe`
   - **macOS**: `LoudMouth-macOS`
   - **Linux**: `LoudMouth-Linux`
3. Run the executable

### Option 2: From Source

#### Windows
```bash
# Clone the repository
git clone https://github.com/yourusername/LoudMouth.git
cd LoudMouth

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

#### macOS
```bash
# Install audio dependencies
brew install portaudio

# Clone and install
git clone https://github.com/yourusername/LoudMouth.git
cd LoudMouth
pip install -r requirements.txt

# Run the application
python main.py
```

#### Linux (Ubuntu/Debian)
```bash
# Install audio dependencies
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio

# Clone and install
git clone https://github.com/yourusername/LoudMouth.git
cd LoudMouth
pip install -r requirements.txt

# Run the application
python main.py
```

## First Run

1. **Model Download**: On first run, you'll need to download Whisper models
2. **Settings**: Configure your preferred hotkey and audio device
3. **Test**: Hold your hotkey and speak to test the system

## Troubleshooting

### Common Issues

**Import Error (Windows)**
```bash
pip install pywin32
```

**Audio Issues (Linux)**
```bash
# Try alternative audio backend
sudo apt-get install libasound2-dev
```

**Permission Issues (macOS)**
- Go to System Preferences → Security & Privacy → Microphone
- Grant permission to Terminal/Python

### Getting Help

- Check the [Issues page](https://github.com/yourusername/LoudMouth/issues)
- Join our [Discussions](https://github.com/yourusername/LoudMouth/discussions)
- Read the [Troubleshooting Guide](TROUBLESHOOTING.md) 