# Read4Me (Read for Me) 🔊

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
Still failing? Are you running python 3.13+ by chance? If you are getting an error where kokoro or spacy refuses to install, try with Python 3.11.
```
sudo apt update

sudo apt install -y \
build-essential \
zlib1g-dev \
libncurses5-dev \
libgdbm-dev \
libnss3-dev \
libssl-dev \
libreadline-dev \
libffi-dev \
libsqlite3-dev \
libbz2-dev \
liblzma-dev \
wget curl llvm tk-dev xz-utils cargo rustc

cd /tmp

wget https://www.python.org/ftp/python/3.11.13/Python-3.11.13.tgz

tar -xvf Python-3.11.13.tgz

cd Python-3.11.13

./configure --enable-optimizations

make -j$(nproc)

sudo make altinstall

#the 2 lines below are to avoid /temp running out of storage space, you can skip it if you know what you are doing.

mkdir -p ~/bigtemp

echo 'export TMPDIR=$HOME/bigtemp' >> ~/.bashrc

#reboot your machine

source ~/.bashrc

python3.11 -m venv ~/kokoro-env

source ~/kokoro-env/bin/activate

pip install --upgrade pip setuptools wheel

pip install --no-cache-dir kokoro
```
Did the above steps solve your problem? If so, in the future, you may need to open the app using the steps below
```
python3.11 -m venv kokoro-env
source kokoro-env/bin/activate
pip install --upgrade pip setuptools wheel
python -c "import kokoro"
pip install --no-cache-dir kokoro
pip install soundfile sounddevice pypdf numpy misaki espeakng_loader
python read4me.py
```
