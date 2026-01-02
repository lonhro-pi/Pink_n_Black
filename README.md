# #!/bin/bash

# Pink_n_Black 
# Author: [Roy and Leon Daley]

depends:

pip install pyinstaller

pyinstaller --noconfirm --onedir --windowed --add-data "lonhro_facts.json:." "main.py"




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

