# #!/bin/bash

# Pink_n_Black - Terminal Customization Script
# Author: [Roy and Leon Daley]

depends:

pip install pyinstaller

pyinstaller --noconfirm --onedir --windowed --add-data "lonhro_facts.json:." "main.py"

# Define Colors for the Installer Output
PINK='\\033[1;35m'
BLACK='\\033[0;30m' # Actually usually dark gray in terminals
NC='\\033[0m' # No Color

echo -e "${PINK}---------------------------------${NC}"
echo -e "${PINK}    Pink_n_Black Installer       ${NC}"
echo -e "${PINK}---------------------------------${NC}"

# 1. Define the target config file (usually .bashrc or .zshrc)
SHELL_CONFIG="$HOME/.bashrc"
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
fi

echo -e "[*] Detected Shell Config: ${SHELL_CONFIG}"

# 2. Create a backup of the user's current config
if [ -f "$SHELL_CONFIG" ]; then
    cp "$SHELL_CONFIG" "${SHELL_CONFIG}.backup_$(date +%F_%T)"
    echo -e "[*] Backup created at ${SHELL_CONFIG}.backup_..."
else
    echo -e "[!] No config file found. Creating one."
    touch "$SHELL_CONFIG"
fi

# 3. Append the Pink_n_Black logic
# You can paste the specific logic from the original script here.
# Below is a standard "Pink and Black" prompt customization.

cat <<EOT >> "$SHELL_CONFIG"


# Pink_n_Black

A lightweight terminal customization script that applies a high-contrast Pink and Black theme to your Bash or Zsh shell.

## Features
- Custom PS1 prompt with Pink identifiers.
- Auto-backups your existing configuration file.
- Works on Linux and macOS.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/lonhro-pi/Pink_n_Black.git
   cd Pink_n_Black

chmod +x install.sh
./install.sh








# --- PINK_N_BLACK THEME END ---
EOT

echo -e "${PINK}[*] Installation Complete!${NC}"
echo -e "Please run: source ${SHELL_CONFIG} OR restart your terminal."
y

```bash
pip install -r requirements.txt
```

Optional components:

- `qtermwidget` (and its system libraries) for a real terminal widget
- `python-vlc` with VLC installed for media playback

## OpenAI API (ChatGPT panel)

Set your API key in the environment before running:

```bash
export OPENAI_API_KEY="you-key"
```

The ChatGPT panel calls the OpenAI Chat Completions API with model `gpt-4o-mini`.

## Running

From the project directory:

```bash
python3 main.py
```

On first run, the app will create a configuration directory at:

- `~/.pinkblack-terminal`




## License

You can choose any license you like; a common choice is MIT. Add a `LICENSE` file if you want to publish this on GitHub.

