
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
## License

You can choose any license you like; a common choice is MIT. Add a `LICENSE` file if you want to publish this on GitHub.

