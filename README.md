Pink_n_Black/
│
├── install.sh          # The main script users run to apply the theme/settings
├── README.md           # Instructions on how to use it
├── LICENSE             # (Optional) Open source license
└── configs/            # Folder containing the actual config files
    ├── .bashrc_custom  # The custom bash settings
    └── colors.conf     # The color definitions


# #!/bin/bash

# Pink_n_Black - Terminal Customization Script
# Author: [Your Name]

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


### How to use this to fix your script:

1.  Copy the `install.sh` code above.
2.  Look at the original code you have. Find the lines that actually change the colors or the prompt (look for `PS1=`, `export`, or hex color codes).
3.  Paste those specific lines into the section of `install.sh` that says `# 3. Append the Pink_n_Black logic`.
4.  Upload these files to your GitHub repository.

If you can paste the specific error you were getting with the original script, or paste the raw code here (if it's short), I can debug the specific syntax error for you.





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

## VS Code Debugging

Recommended `.vscode/launch.json` configuration (already included):

```json
CB de l{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Run Pink and Black Terminal",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/main.py",
      "console": "integratedTerminal",
      "justMyCode": true
    }
  ]
}
```

Open the folder in VS Code and use **Run and Debug → Run Pink and Black Terminal**.

## License

You can choose any license you like; a common choice is MIT. Add a `LICENSE` file if you want to publish this on GitHub.

