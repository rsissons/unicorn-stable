"""Build Unicorn Stable: render every voice line to MP3 (cached) and bake them into the page.

Usage:  python source/build.py
Needs:  pip install edge-tts ; ffmpeg on PATH. Ron picked Microsoft's child voice "Ana" (2026-09-26)
        after the pitched-up Kokoro voice sounded synthetic. ENGINE='kokoro' still works as an offline
        fallback (pip install kokoro-onnx soundfile + source/model/kokoro-v1.0.onnx, voices-v1.0.bin).
Output: unicorn-stable.html (artifact form, no <html>/<head>) and index.html (GitHub Pages form).
"""
import base64, hashlib, json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(HERE, 'unicorn-stable.src.html')
VDIR = os.path.join(HERE, 'voice')
MDIR = os.path.join(HERE, 'model')

# The unicorn's voice: Microsoft's en-US-AnaNeural child voice, as-is (no pitch shifting).
ENGINE, VOICE, SPEED, PITCH = 'edge', 'en-US-AnaNeural', 1.0, 1.0
AFILTER = ((f'rubberband=pitch={PITCH}:formant=shifted,' if PITCH != 1.0 else '') +
           'silenceremove=start_periods=1:start_threshold=-45dB,areverse,'
           'silenceremove=start_periods=1:start_threshold=-45dB,areverse,'
           'loudnorm=I=-16:TP=-1.5:LRA=11')


def lines_from_source(src):
    m = re.search(r'/\*LINES-START\*/(.*?)/\*LINES-END\*/', src, re.S)
    raw = json.loads(m.group(1))
    names = raw.pop('_names')
    out = {}
    for k, v in raw.items():
        if '*' in k:
            for n in names:
                out[k.replace('*', n)] = v.replace('*', n)
        else:
            out[k] = v
    return out


def clip_path(key, text):
    h = hashlib.sha1(f'{ENGINE}|{VOICE}|{SPEED}|{PITCH}|{text}'.encode()).hexdigest()[:10]
    return os.path.join(VDIR, f'{key}.{h}.mp3')


def render(todo):
    with tempfile.TemporaryDirectory() as tmp:
        raw = os.path.join(tmp, 'raw')
        if ENGINE == 'edge':
            import edge_tts
            say = lambda text: edge_tts.Communicate(text, VOICE, rate=f'{round((SPEED - 1) * 100):+d}%').save_sync(raw)
        else:
            import soundfile as sf
            from kokoro_onnx import Kokoro
            kok = Kokoro(os.path.join(MDIR, 'kokoro-v1.0.onnx'), os.path.join(MDIR, 'voices-v1.0.bin'))
            def say(text):
                samples, sr = kok.create(text, voice=VOICE, speed=SPEED, lang='en-us')
                sf.write(raw, samples, sr, format='WAV')
        for i, (key, text, out) in enumerate(todo, 1):
            say(text)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', AFILTER,
                            '-ac', '1', '-ar', '24000', '-b:a', '48k', out], check=True)
            print(f'[{i}/{len(todo)}] {key}: {text}')


def main():
    os.makedirs(VDIR, exist_ok=True)
    src = open(SRC, encoding='utf-8').read()
    lines = lines_from_source(src)
    todo = [(k, t, clip_path(k, t)) for k, t in lines.items() if not os.path.exists(clip_path(k, t))]
    if todo:
        render(todo)
    keep = {os.path.basename(clip_path(k, t)) for k, t in lines.items()}
    for f in os.listdir(VDIR):
        if f not in keep:
            os.remove(os.path.join(VDIR, f))
    vox = {k: base64.b64encode(open(clip_path(k, t), 'rb').read()).decode() for k, t in lines.items()}
    page = re.sub(r'/\*VOX-START\*/.*?/\*VOX-END\*/',
                  lambda _: '/*VOX-START*/' + json.dumps(vox, separators=(',', ':')) + '/*VOX-END*/', src, flags=re.S)
    open(os.path.join(ROOT, 'unicorn-stable.html'), 'w', encoding='utf-8', newline='\n').write(page)
    head = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            '<meta name="apple-mobile-web-app-capable" content="yes">\n</head>\n<body>\n')
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8', newline='\n').write(head + page + '\n</body>\n</html>\n')
    print(f'{len(lines)} clips, page {len(page) / 1e6:.2f} MB')


if __name__ == '__main__':
    sys.exit(main())
