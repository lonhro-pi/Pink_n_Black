
# Pink_n_Black

A stylish pink-on-black Qt desktop terminal application with:

- Embedded terminal (QTermWidget if available, otherwise a reliable PTY fallback)
- ChatGPT panel (powered by OpenAI API – requires your own API key)
- GitHub repository search
- Media player controls (using QtMultimedia)
- System information panel (CPU, RAM, kernel version)
- Random Lonhro racing facts panel

The layout uses a clean split view:

**Left side** → Terminal  
**Right side** → Tabbed panels (ChatGPT, GitHub, Media, System, Lonhro)

## Requirements

- Debian-based Linux distribution (Ubuntu, Debian, Linux Mint, Pop!_OS, etc.)
- Python 3.9 or newer
- PySide6 (Qt6 Python bindings)
- Internet connection (for ChatGPT and GitHub features)

## Installation

```bash
# Clone the repository
git clone https://github.com/lonhro-pi/Pink_n_Black.git
cd Pink_n_Black

# Make the installer executable
chmod +x install.sh

# Run the installer
./install.sh

# Activate the virtual environment
source venv/bin/activate

# Set your OpenAI API key (required for ChatGPT panel)
export OPENAI_API_KEY="sk-..."

# Launch the application
python main.py

alias pinknblack='source ~/Pink_n_Black/venv/bin/activate && python ~/Pink_n_Black/main.py'

Features
•  Terminal — Full-featured when QTermWidget is installed; otherwise a solid PTY-based fallback
•  ChatGPT — Talk to GPT-4o-mini (or change the model in code)
•  GitHub Search — Quickly find popular repositories
•  Media Player — Play audio/video files using QtMultimedia (no VLC dependency)
•  System Info — Real-time CPU usage, RAM, core count, kernel version
•  Lonhro Facts — Random fun facts about the legendary racehorse Lonhro
Notes & Credits
A huge thank you to Roy and Little Leon Daley — your support, encouragement, ideas and belief in this project meant everything. This terminal would not have reached this point without you both. Thank you from the bottom of my heart

Then just type pinknblack whenever you want to start it.

## License

You can choose any license you like; a common choice is MIT. Add a `LICENSE` file if you want to publish this on GitHub.

