#!/usr/bin/env python3
"""
tts_reader.py — Interactive Natural-voice Text-to-Speech
"""

import asyncio, curses, os, re, readline, shutil, sys, glob

KOKORO_VOICES = [
    ("af_heart",    "a", "American \u2640  warm, natural \u2b50"),
    ("af_bella",    "a", "American \u2640  expressive, clear"),
    ("af_nicole",   "a", "American \u2640  soft, conversational"),
    ("af_sarah",    "a", "American \u2640  bright, articulate"),
    ("af_sky",      "a", "American \u2640  youthful, energetic"),
    ("am_adam",     "a", "American \u2642  deep, confident"),
    ("am_michael",  "a", "American \u2642  smooth, professional"),
    ("bf_emma",     "b", "British  \u2640  crisp, natural"),
    ("bf_isabella", "b", "British  \u2640  elegant, warm"),
    ("bm_george",   "b", "British  \u2642  authoritative, clear"),
    ("bm_lewis",    "b", "British  \u2642  relaxed, conversational"),
]

EDGE_VOICES = [
    ("en-US-AriaNeural",        "American \u2640  natural, expressive \u2b50"),
    ("en-US-JennyNeural",       "American \u2640  friendly, conversational"),
    ("en-US-MichelleNeural",    "American \u2640  warm, clear"),
    ("en-US-GuyNeural",         "American \u2642  authoritative"),
    ("en-US-ChristopherNeural", "American \u2642  smooth, professional"),
    ("en-US-EricNeural",        "American \u2642  calm, mature"),
    ("en-GB-SoniaNeural",       "British  \u2640  crisp, natural"),
    ("en-GB-LibbyNeural",       "British  \u2640  bright, clear"),
    ("en-GB-RyanNeural",        "British  \u2642  warm, friendly"),
    ("en-AU-NatashaNeural",     "Australian \u2640  clear, natural"),
    ("en-AU-WilliamNeural",     "Australian \u2642  deep, relaxed"),
]

def detect_backends():
    found = []
    for name, mod in [("kokoro", "kokoro"), ("edge", "edge_tts"), ("pyttsx3", "pyttsx3")]:
        try:
            __import__(mod)
            found.append(name)
        except ImportError:
            pass
    return found

def clear():
    os.system("clear")

def hr(w=70):
    print("  " + "\u2500" * w)

def banner():
    clear()
    print()
    print("  \u2554" + "\u2550" * 44 + "\u2557")
    print("  \u2551       \U0001f50a  TTS Reader  \u2014 voice CLI        \u2551")
    print("  \u255a" + "\u2550" * 44 + "\u255d")
    print()

def ask(msg, default=""):
    suffix = f" [{default}]" if default else ""
    try:
        val = input(f"  {msg}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    return val if val else default

def confirm(msg, default=True):
    hint = "Y/n" if default else "y/N"
    ans = ask(f"{msg} ({hint})")
    if not ans:
        return default
    return ans.lower().startswith("y")

def arrow_menu(title, options, default=0):
    C_TITLE = 1; C_SEL = 2; C_DIM = 3

    def _run(stdscr):
        curses.curs_set(0); curses.start_color(); curses.use_default_colors()
        curses.init_pair(C_TITLE, curses.COLOR_CYAN, -1)
        curses.init_pair(C_SEL, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(C_DIM, curses.COLOR_WHITE, -1)
        idx = default; scroll = 0; n = len(options)
        while True:
            stdscr.erase(); h, w = stdscr.getmaxyx(); visible = max(1, h - 7)
            stdscr.addstr(1, 2, title, curses.color_pair(C_TITLE) | curses.A_BOLD)
            stdscr.addstr(2, 2, "\u2191/\u2193 navigate   Enter select   q cancel", curses.color_pair(C_DIM))
            stdscr.addstr(3, 2, "\u2500" * min(w - 4, 68), curses.color_pair(C_DIM))
            if idx < scroll: scroll = idx
            if idx >= scroll + visible: scroll = idx - visible + 1
            for row, i in enumerate(range(scroll, min(scroll + visible, n))):
                label, desc = options[i]; y = 4 + row
                if y >= h - 1: break
                line = f" \u25b6 {label:<22} {desc}"; plain = f"   {label:<22} {desc}"
                try:
                    if i == idx:
                        stdscr.addstr(y, 2, line[:w-4], curses.color_pair(C_SEL) | curses.A_BOLD)
                    else:
                        stdscr.addstr(y, 2, plain[:w-4])
                except curses.error:
                    pass
            if n > visible:
                hint = f"  {scroll+1}\u2013{min(scroll+visible,n)} of {n}"
                try: stdscr.addstr(h - 1, 2, hint, curses.color_pair(C_DIM))
                except curses.error: pass
            stdscr.refresh(); key = stdscr.getch()
            if key in (curses.KEY_UP, ord('k')): idx = (idx - 1) % n
            elif key in (curses.KEY_DOWN, ord('j')): idx = (idx + 1) % n
            elif key == curses.KEY_PPAGE: idx = max(0, idx - visible)
            elif key == curses.KEY_NPAGE: idx = min(n - 1, idx + visible)
            elif key == curses.KEY_HOME: idx = 0
            elif key == curses.KEY_END: idx = n - 1
            elif key in (10, 13, curses.KEY_ENTER): return idx
            elif key in (ord('q'), 27): return -1

    result = curses.wrapper(_run)
    return result if result is not None else -1

def extract_text_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def extract_pdf(path, page_range=None):
    try:
        from pypdf import PdfReader
    except ImportError:
        print("\n  \u2717 pypdf not installed. Run: pip install pypdf"); sys.exit(1)
    reader = PdfReader(path); total = len(reader.pages); start, end = 0, total
    if page_range:
        start = max(0, page_range[0] - 1); end = min(total, page_range[1])
    print(f"  PDF: {total} page(s) total \u2014 reading pages {start+1}\u2013{end}")
    chunks = [reader.pages[i].extract_text() or "" for i in range(start, end)]
    return "\n\n".join(chunks)

def clean_text(raw, flow_mode=False):
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', raw)
    text = re.sub(r'(?m)^\s*\d+\s*$', '', text)
    if flow_mode:
        text = re.sub(r'\n{2,}', '\x00PARA\x00', text)
        text = re.sub(r'\n', ' ', text)
        text = re.sub(r' {2,}', ' ', text)
        text = re.sub(r'\x00PARA\x00', '\n\n', text)
    else:
        text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def pdf_page_count(path):
    try:
        from pypdf import PdfReader
        return len(PdfReader(path).pages)
    except Exception:
        return 0

def kokoro_speak(text, voice_id, lang_code, speed, save_path):
    from kokoro import KPipeline
    print(f"\n  Initialising Kokoro\u2026 (first run downloads ~80 MB model)\n")
    pipeline = KPipeline(lang_code=lang_code, repo_id="hexgrad/Kokoro-82M")
    if save_path:
        import soundfile as sf, numpy as np
        chunks = []
        print("  Generating audio\u2026")
        for r in pipeline(text, voice=voice_id, speed=speed):
            if r.audio is not None:
                a = r.audio.numpy() if hasattr(r.audio, 'numpy') else r.audio
                chunks.append(a)
        combined = np.concatenate(chunks)
        sf.write(save_path, combined, 24000)
        _print_saved(save_path, len(combined), 24000)
    else:
        import sounddevice as sd
        print("  \u25b6  Playing\u2026  (Ctrl+C to stop)\n")
        try:
            for r in pipeline(text, voice=voice_id, speed=speed):
                if r.audio is not None:
                    a = r.audio.numpy() if hasattr(r.audio, 'numpy') else r.audio
                    sd.play(a, samplerate=24000); sd.wait()
        except KeyboardInterrupt:
            sd.stop(); print("\n\n  \u25a0  Stopped.")

def edge_speak(text, voice_id, speed, save_path):
    import edge_tts
    rate_pct = int((speed - 1.0) * 100)
    rate_str = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"
    async def _save():
        print("\n  Generating audio (requires internet)\u2026")
        await edge_tts.Communicate(text, voice_id, rate=rate_str).save(save_path)
        size = os.path.getsize(save_path) / 1_048_576
        print(f"\n  \u2713  Saved \u2192 {save_path}  ({size:.1f} MB)")
    async def _play():
        import tempfile, subprocess
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name
        print("\n  \u25b6  Generating & playing\u2026  (Ctrl+C to stop)\n")
        try:
            await edge_tts.Communicate(text, voice_id, rate=rate_str).save(tmp_path)
            played = False
            for player, args in [("mpg123", ["mpg123", tmp_path]), ("ffplay", ["ffplay", "-nodisp", "-autoexit", tmp_path]), ("mplayer", ["mplayer", tmp_path])]:
                if shutil.which(player):
                    subprocess.run(args, check=True); played = True; break
            if not played:
                print(f"\n  \u26a0  No audio player found.")
                print(f"     Install mpg123:  sudo apt install mpg123")
                print(f"     Audio is at: {tmp_path}"); return
        except KeyboardInterrupt:
            print("\n\n  \u25a0  Stopped.")
        finally:
            if os.path.exists(tmp_path):
                try: os.unlink(tmp_path)
                except Exception: pass
    if save_path: asyncio.run(_save())
    else: asyncio.run(_play())

def pyttsx3_speak(text, voice_id, speed, save_path):
    import pyttsx3
    engine = pyttsx3.init()
    engine.setProperty('rate', int(150 * speed)); engine.setProperty('volume', 1.0)
    if voice_id:
        for v in engine.getProperty('voices'):
            if voice_id.lower() in (v.id or '').lower():
                engine.setProperty('voice', v.id); break
    if save_path:
        engine.save_to_file(text, save_path); engine.runAndWait()
        size = os.path.getsize(save_path) / 1_048_576 if os.path.exists(save_path) else 0
        print(f"\n  \u2713  Saved \u2192 {save_path}  ({size:.1f} MB)")
    else:
        print("\n  \u25b6  Speaking\u2026  (Ctrl+C to stop)\n")
        try:
            engine.say(text); engine.runAndWait()
        except KeyboardInterrupt:
            engine.stop(); print("\n\n  \u25a0  Stopped.")

def _print_saved(path, n_samples, sr):
    dur = n_samples / sr; size = os.path.getsize(path) / 1_048_576
    print(f"\n  \u2713  Saved \u2192 {path}  ({dur:.1f}s, {size:.1f} MB)")

def step_file():
    def path_completer(text, state):
        expanded = os.path.expanduser(text); matches = glob.glob(expanded + "*")
        matches = [m + "/" if os.path.isdir(m) else m for m in matches]
        return matches[state] if state < len(matches) else None
    readline.set_completer_delims(" \t\n"); readline.parse_and_bind("tab: complete")
    readline.set_completer(path_completer)
    while True:
        banner(); print("  Step 1 of 5 \u2014 File"); hr()
        print("  Enter the path to your .txt or .pdf file.")
        print("  Tip: press Tab to auto-complete file paths.\n")
        raw = ask("File path")
        if not raw: continue
        path = os.path.expanduser(raw.strip())
        if not os.path.isfile(path):
            print(f"\n  \u2717  File not found: {path}"); input("  Press Enter to try again\u2026"); continue
        ext = os.path.splitext(path)[1].lower()
        if ext not in (".txt", ".pdf"):
            print(f"\n  \u2717  Unsupported type '{ext}'. Please give a .txt or .pdf file.")
            input("  Press Enter to try again\u2026"); continue
        return path

def step_pages(path):
    total = pdf_page_count(path)
    if total <= 1: return None
    banner(); print("  Step 2 of 5 \u2014 Pages"); hr()
    print(f"  The PDF has {total} page(s).\n")
    options = [("All pages", f"Read all {total} pages"), ("Custom range", "Choose a start and end page")]
    choice = arrow_menu("Page selection", options)
    if choice < 0: sys.exit(0)
    if choice == 0: return None
    banner(); print("  Step 2 of 5 \u2014 Pages"); hr()
    print(f"  PDF has {total} pages.\n")
    while True:
        raw = ask("Page range (e.g.  3-10  or  7)"); parts = raw.split("-")
        try:
            if len(parts) == 1:
                n = int(parts[0]); return (n, n)
            return (int(parts[0]), int(parts[1]))
        except ValueError:
            print("  \u2717  Invalid. Enter something like  3  or  2-8")

def step_backend(available):
    if len(available) == 1: return available[0]
    descriptions = {
        "kokoro":  "Local neural TTS  (best quality, ~80 MB one-time download)",
        "edge":    "Microsoft neural  (great quality, requires internet)",
        "pyttsx3": "System voices     (offline espeak/festival, robotic)",
    }
    banner(); print("  Step 3 of 5 \u2014 Engine"); hr()
    print("  Choose your TTS engine:\n")
    options = [(b, descriptions.get(b, "")) for b in available]
    choice = arrow_menu("TTS Engine", options)
    if choice < 0: sys.exit(0)
    return available[choice]

def step_voice(backend):
    banner(); print("  Step 4 of 5 \u2014 Voice"); hr(); print()
    if backend == "kokoro":
        options = [(v[0], v[2]) for v in KOKORO_VOICES]
        choice = arrow_menu("Kokoro Voice", options)
        if choice < 0: sys.exit(0)
        v = KOKORO_VOICES[choice]; return v[0], v[1]
    elif backend == "edge":
        options = [(v[0], v[1]) for v in EDGE_VOICES]
        choice = arrow_menu("Microsoft Edge Voice", options)
        if choice < 0: sys.exit(0)
        return EDGE_VOICES[choice][0], None
    else:
        import pyttsx3
        engine = pyttsx3.init(); voices = engine.getProperty("voices") or []
        if not voices: return None, None
        options = [(v.id.split(".")[-1][:26], v.name or "") for v in voices]
        choice = arrow_menu("System Voice", options)
        if choice < 0: sys.exit(0)
        return voices[choice].id, None

def step_flow_mode():
    banner(); print("  Line-break handling\n"); hr()
    print("  PDFs often have hard newlines at the end of every visual line,")
    print("  which can cause the voice to pause mid-sentence.\n")
    options = [
        ("Flow mode  \u2605", "Collapse mid-paragraph line breaks \u2014 smooth, natural reading (Recommended for PDFs)"),
        ("Normal",            "Keep all newlines as-is (preserves structure)"),
    ]
    choice = arrow_menu("Line breaks", options)
    if choice < 0: sys.exit(0)
    return choice == 0

def step_speed():
    banner(); print("  Step 5 of 5 \u2014 Speed & Output"); hr(); print()
    speed_options = [
        ("0.75\u00d7", "Slower \u2014 easier to follow"),
        ("0.90\u00d7", "Slightly slower"),
        ("1.00\u00d7", "Normal speed  (recommended)"),
        ("1.15\u00d7", "Slightly faster"),
        ("1.30\u00d7", "Faster"),
        ("1.50\u00d7", "Much faster"),
        ("Custom",     "Enter your own value"),
    ]
    speeds = [0.75, 0.90, 1.00, 1.15, 1.30, 1.50, None]
    choice = arrow_menu("Speed", speed_options, default=2)
    if choice < 0: sys.exit(0)
    if speeds[choice] is not None: return speeds[choice]
    banner(); print("  Custom speed\n")
    while True:
        raw = ask("Speed multiplier (e.g. 1.2)", "1.0")
        try:
            s = float(raw)
            if 0.1 <= s <= 4.0: return s
            print("  \u2717  Enter a value between 0.1 and 4.0")
        except ValueError:
            print("  \u2717  Not a valid number")

def step_output():
    options = [
        ("\u25b6  Play now",     "Stream audio to your speakers immediately"),
        ("\U0001f4be  Save to file", "Write a .wav audio file to disk"),
    ]
    choice = arrow_menu("Output", options)
    if choice < 0: sys.exit(0)
    if choice == 0: return None
    banner(); print("  Save audio file\n")
    while True:
        raw = ask("Output filename", "output.wav")
        if not raw.endswith((".wav", ".mp3")): raw += ".wav"
        out_dir = os.path.dirname(raw) or "."
        if not os.path.isdir(out_dir):
            print(f"  \u2717  Directory not found: {out_dir}"); continue
        return raw

def show_summary(path, backend, voice_id, speed, page_range, save_path, words, est_min, flow_mode):
    banner(); print("  Ready to read\n"); hr()
    print(f"  File    : {os.path.basename(path)}")
    print(f"  Engine  : {backend}")
    print(f"  Voice   : {voice_id or 'system default'}")
    print(f"  Speed   : {speed}\u00d7")
    if page_range:
        print(f"  Pages   : {page_range[0]}\u2013{page_range[1]}")
    flow_str = "on \u2014 soft newlines collapsed" if flow_mode else "off \u2014 newlines preserved"
    print(f"  Flow    : {flow_str}")
    print(f"  Words   : {words:,}  (est. {est_min:.1f} min at {speed}\u00d7 speed)")
    if save_path:
        print(f"  Save to : {save_path}")
    hr(); print()
    if not confirm("Start?", default=True):
        print("\n  Cancelled.\n"); sys.exit(0)

def main():
    available = detect_backends()
    if not available:
        print("\n  \u2717  No TTS backend installed. Install at least one:\n")
        print("     pip install kokoro soundfile sounddevice   # best quality")
        print("     pip install edge-tts                       # Microsoft neural")
        print("     pip install pyttsx3                        # offline fallback\n")
        sys.exit(1)
    banner()
    print("  Welcome! This tool reads .txt and .pdf files aloud")
    print("  using high-quality AI voices.\n")
    print(f"  Detected engines: {', '.join(available)}\n")
    input("  Press Enter to begin\u2026")
    path = step_file()
    ext = os.path.splitext(path)[1].lower()
    page_range = step_pages(path) if ext == ".pdf" else None
    flow_mode = step_flow_mode()
    backend = step_backend(available)
    voice_id, extra = step_voice(backend)
    speed = step_speed()
    save_path = step_output()
    banner(); print("  Extracting text\u2026\n")
    raw = extract_pdf(path, page_range) if ext == ".pdf" else extract_text_file(path)
    text = clean_text(raw, flow_mode=flow_mode)
    if not text:
        print("  \u2717  No readable text found in the file."); sys.exit(1)
    words = len(text.split()); est_min = words / 150 / speed
    show_summary(path, backend, voice_id, speed, page_range, save_path, words, est_min, flow_mode)
    banner()
    print(f"  {os.path.basename(path)}  \u2014  {voice_id or 'system default'}  \u2014  {speed}\u00d7\n")
    if backend == "kokoro": kokoro_speak(text, voice_id, extra, speed, save_path)
    elif backend == "edge": edge_speak(text, voice_id, speed, save_path)
    else: pyttsx3_speak(text, voice_id, speed, save_path)
    print("\n  \u2713  Done.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Interrupted. Goodbye.\n"); sys.exit(0)
