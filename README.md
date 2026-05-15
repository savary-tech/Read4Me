# Read4Me 🔊

A local, interactive text-to-speech reader for `.txt` and `.pdf` files.
Just run it, follow the menus, and it reads your file aloud in a natural AI voice.

---

## What it does

- Reads `.txt` and `.pdf` files aloud using high-quality neural voices
- Fully interactive — arrow keys and Enter, no command-line flags to memorise
- Lets you pick your voice, speed, and page range
- **Flow mode** — smooths out awkward mid-sentence pauses from PDF line breaks
- Can play audio live or save it to a `.wav` file

---

## Install

Install Python 3.10+ if you don't have it, then install the dependencies:

```bash
pip install kokoro soundfile sounddevice pypdf edge-tts pyttsx3 numpy misaki espeakng_loader
```

For audio playback with the `edge-tts` engine:

```bash
sudo apt install mpg123
```

Then just run it:

```bash
python3 read4me.py
```

---

## Voices / engines

Read4Me will auto-detect which engines are installed and let you choose at startup.

| Engine | Quality | Internet? |
|--------|---------|-----------|
| **Kokoro** | Best — local neural TTS | No (downloads ~80 MB once) |
| **edge-tts** | Great — Microsoft neural | Yes |
| **pyttsx3** | Basic — system voices | No |

---

## If all else fails

```bash
cd ~/WhereEverTheAppIsInstalled/Read4Me
python3 -m venv venv
source venv/bin/activate
pip install kokoro soundfile sounddevice pypdf edge-tts pyttsx3 numpy misaki espeakng_loader
python read4me.py
```
