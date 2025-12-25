# Pink and Black Terminal

A pink-on-black Qt desktop terminal app with:

- **Embedded terminal** (QTermWidget if available, otherwise a simple pty-backed terminal)
- **ChatGPT panel** (uses the OpenAI API)
- **GitHub repo search**
- **VLC-based media controls** (optional, via `python-vlc`)
- **System info panel** (CPU, RAM, kernel)
- **Lonhro facts** panel

The main window uses a **split view** layout:

- **Left**: Terminal
- **Right**: Tabs for ChatGPT, GitHub, Media, System, Lonhro

## Requirements

Python 3.9+ recommended.

Install dependencies:

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
{
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

