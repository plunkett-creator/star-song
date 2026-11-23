"""Turns the original artifact pages (src/) into the app/website pieces (Web/pieces/<id>/index.html).
Each piece: offline fonts, the shared host script, one fixed look, recording removed, endless play."""
import re, sys, os

SRC = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/src'
OUT = sys.argv[2] if len(sys.argv) > 2 else '/home/claude/ss/Web/pieces'

HEAD = ('<link rel="stylesheet" href="../../fonts/fonts.css">\n'
        '<script src="../../pieces.js"></script>\n<script src="../../shared/host.js"></script>\n')


def rep(s, a, b, count=1, name=''):
    n = s.count(a)
    if n != count:
        raise SystemExit(f'[{name}] expected {count} of: {a[:90]!r}, found {n}')
    return s.replace(a, b)


def sub(s, pat, b, name='', flags=0, count=1):
    s2, n = re.subn(pat, b, s, flags=flags)
    if n != count:
        raise SystemExit(f'[{name}] pattern {pat[:80]!r} matched {n}, expected {count}')
    return s2


def common(s, name, home):
    # Google Fonts -> bundled fonts; shared host first in <head>
    s = re.sub(r'\s*<link rel="preconnect"[^>]*>', '', s)
    s = sub(s, r'<link (?:href="https://fonts\.googleapis\.com/css2\?[^"]+" rel="stylesheet"|rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^"]+")>', HEAD.strip(), name)
    # full-screen layout under the notch / home indicator
    s = sub(s, r'<meta name="viewport" content="[^"]*">',
            '<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">', name)
    s = sub(s, r'<html lang="en">', f'<html lang="en" data-home="{home}">', name)
    # no text selection / call-outs / tap flashes in the apps
    s = rep(s, '</style>', 'html,body{-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;-webkit-tap-highlight-color:transparent}\n'
            'html.in-app #fs{display:none!important}\n</style>', name=name)
    return s


def glide_engine(s, name, mood_load):
    """Star Trails, Ground Tracks, Deep Field Receiver: drop the look switcher and the saved look."""
    s = sub(s, r'\n\s*<div class="seg" role="group" aria-label="[^"]+" id="moods">.*?</div>\n\s*<span class="sep"></span>', '', name, re.S)
    s = rep(s, mood_load, '', name=name)
    return s


def build(pid, src, fn):
    s = open(os.path.join(SRC, src)).read()
    s = fn(s, pid)
    os.makedirs(os.path.join(OUT, pid), exist_ok=True)
    open(os.path.join(OUT, pid, 'index.html'), 'w').write(s)
    print('built', pid, len(s))


def star_trails(s, n):
    s = common(s, n, 'tc')
    return glide_engine(s, n, 'if(NIGHTS[s.night])night=s.night;')


def ground_tracks(s, n):
    s = common(s, n, 'tc')
    s = rep(s, '</style>', 'html{--ss-top:36px}\n</style>', name=n)
    return glide_engine(s, n, 'if(SCREENS[s.scr])scr=s.scr;')


def deep_field(s, n):
    s = common(s, n, 'tc')
    s = rep(s, '</style>', 'html{--ss-top:36px}\n</style>', name=n)
    return glide_engine(s, n, 'if(MAPS[s.map])map=s.map;')


def nursery(s, n):
    s = common(s, n, 'tl')
    s = rep(s, "let themeName='night';try{const s=localStorage.getItem('nn-plate');if(THEMES[s])themeName=s;}catch(e){}", "let themeName='gilt';", name=n)
    s = rep(s, "try{localStorage.setItem('nn-plate',name);}catch(e){}", '', name=n)
    s = sub(s, r'\n\s*<div class="seg" role="group" aria-label="Plate" id="plates">.*?</div>\n\s*<span class="sep"></span>', '', n, re.S)
    s = rep(s, '<title>Nebula Nursery</title>', '<title>The Nursery of Stars</title>', name=n)
    return s


def session_piece(s, n, mood, title, home):
    """Constellations and Cymatics: one mood, long pieces that roll straight on into a new one, no recording."""
    s = common(s, n, home)
    s = sub(s, r"let moodKey = MOODS\[load\('mood', '[a-z]+'\)\] \? load\('mood', '[a-z]+'\) : '[a-z]+';", f"let moodKey = '{mood}';", n)
    s = sub(s, r"let lenKey = LENGTHS\[load\('len', 'full'\)\] \? load\('len', 'full'\) : 'full';", "let lenKey = 'long';", n)
    s = sub(s, r"let frameKey = FRAMES\[load\('frame', 'fill'\)\] \? load\('frame', 'fill'\) : 'fill';", "let frameKey = 'fill';", n)
    # menu: keep the title, the words and Listen / New ...; hide mood, length, frame and Record
    for lab in ('Mood', 'Length', 'Frame'):   # the first of each is in the start menu (the others are in the recording card)
        tag = '<div class="grp"><span class="lab">' + lab + '</span>'
        if tag not in s: raise SystemExit(f'[{n}] no {lab} group')
        s = s.replace(tag, '<div class="grp" hidden><span class="lab">' + lab + '</span>', 1)
    # bar: hide frame and record buttons (kept in the page so the script still finds them)
    s = rep(s, '</style>', '#frameBtn,#recBar,#recOpen,#recCard,#doneCard{display:none!important}\n</style>', name=n)
    # endless: when a piece reaches its end, a new one begins
    s = sub(s, r"else \{ state = 'ended'; ui\(\); \}", "else { autoNext(); }", n)
    s = rep(s, 'function startPiece() {', 'function autoNext() { seed = (Math.random() * 4294967296) >>> 0; if (typeof buildSky === "function") { buildSky(seed); rebuildStatic(); } recompose(); startPiece(); }\nfunction startPiece() {', name=n)
    return s


def constellations(s, n):
    return session_piece(s, n, 'clear', 'Constellations', 'tr')


def cymatics(s, n):
    s = session_piece(s, n, 'slate', 'Cymatics', 'tl')
    s = rep(s, '</style>', '@media (min-width:700px){html{--ss-top:96px}}\n</style>', name=n)
    return s


def orrery(s, n):
    s = common(s, n, 'tl')
    s = rep(s, '<title>Figure Eight</title>', '<title>The Orrery</title>', name=n)
    # local 3D engine
    s = rep(s, '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>', '<script src="../../vendor/three.min.js"></script>', name=n)
    s = rep(s, '<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>', '<script src="../../vendor/OrbitControls.js"></script>', name=n)
    # night plate: navy card, gold-cream ink, deep disc
    s = rep(s, ':root{color-scheme:light;--card:#ece2cb;--ink:#2b2620;--disc:#232428;--chalk:#f2ede2;--table:#3a332c}',
            ':root{color-scheme:dark;--card:#0f1a3a;--ink:#ead9ac;--disc:#060b1d;--chalk:#f2ede2;--table:rgba(227,193,112,.55)}', name=n)
    s = rep(s, 'background:#2f2a25;color:var(--ink)', 'background:#050b1d;color:var(--ink)', name=n)
    s = rep(s, 'background-image:radial-gradient(ellipse at 50% 45%,rgba(255,250,235,.55),rgba(255,250,235,0) 60%),radial-gradient(ellipse at 50% 50%,rgba(0,0,0,0) 62%,rgba(120,90,40,.16) 100%);',
            'background-image:radial-gradient(ellipse at 50% 42%,rgba(40,70,150,.45),rgba(40,70,150,0) 62%),radial-gradient(ellipse at 50% 50%,rgba(0,0,0,0) 60%,rgba(0,0,0,.35) 100%);border:1px solid rgba(227,193,112,.5);outline:1px solid rgba(227,193,112,.35);outline-offset:-10px;', name=n)
    s = rep(s, 'box-shadow:inset 0 0 0 1px rgba(0,0,0,.4),0 1px 0 rgba(255,255,255,.4)}', 'box-shadow:inset 0 0 0 1px rgba(0,0,0,.4),0 0 0 2px rgba(227,193,112,.6)}', name=n)
    s = rep(s, 'h1{position:absolute;left:0;right:0;top:22px;margin:0;', 'h1{position:absolute;left:0;right:0;top:22px;margin:0;color:#e3c170;', name=n)
    s = rep(s, 'border:1px solid #b9a988;box-shadow:0 6px 24px rgba(0,0,0,.4)', 'border:1px solid rgba(227,193,112,.55);box-shadow:0 6px 24px rgba(0,0,0,.5)', name=n)
    s = rep(s, '.bar button:hover{background:rgba(43,38,32,.07)}', '@media (hover:hover){.bar button:hover{background:rgba(227,193,112,.1)}}', name=n)
    s = rep(s, '.bar input[type=range]{width:80px;accent-color:#6b4a1f}', '.bar input[type=range]{width:80px;accent-color:#e3c170}', name=n)
    s = rep(s, 'outline:2px solid #8a5a1c', 'outline:2px solid #e3c170', name=n)
    s = rep(s, '.sep{width:1px;height:24px;background:#b9a988;', '.sep{width:1px;height:24px;background:rgba(227,193,112,.45);', name=n)
    s = rep(s, '.bar{position:fixed;left:50%;bottom:10px;', '.bar{position:fixed;left:50%;bottom:calc(10px + env(safe-area-inset-bottom,0px));', name=n)
    s = rep(s, "const DISC = 0x232428, CHALK = 0xf2ede2;", "const DISC = 0x060b1d, CHALK = 0xf2ede2;", name=n)
    s = rep(s, 'stroke="#232428" stroke-width="30"', 'stroke="#060b1d" stroke-width="30"', name=n)
    s = rep(s, 'scale = Math.min((innerWidth - 16) / PW, (innerHeight - 16 - barH) / PH);',
            'scale = Math.min((innerWidth - 16) / PW, (innerHeight - 16 - barH - 44) / PH);', name=n)
    s = rep(s, "const x = (innerWidth - PW*scale)/2, y = Math.max(8, (innerHeight - barH - PH*scale)/2);",
            "const x = (innerWidth - PW*scale)/2, y = Math.max(52, (innerHeight - barH - PH*scale)/2 + 22);", name=n)
    # the plate's name
    s = rep(s, '<h1 id="title">TRIPLE SOLAR SYSTEM,</h1>', '<h1 id="title">THE ORRERY,</h1>', name=n)
    s = rep(s, '<p class="sub" id="sub1">DISPLAYING THE PLANETS WITH THEIR LOOPED ORBITS ABOUT THREE SUNS.</p>',
            '<p class="sub" id="sub1">A TRIPLE SOLAR SYSTEM, WITH THE PLANETS IN THEIR LOOPED ORBITS.</p>', name=n)
    s = rep(s, "$('title').textContent = `${KIND[n]} SOLAR SYSTEM,`;\n  $('sub1').textContent = looping ? `DISPLAYING THE PLANETS WITH THEIR LOOPED ORBITS",
            "$('sub1').textContent = `A ${KIND[n]} SOLAR SYSTEM, ` + (looping ? `WITH THE PLANETS IN THEIR LOOPED ORBITS", name=n)
    s = rep(s, ": `DISPLAYING THE PLANETS WITH THEIR FIGURE-OF-EIGHT ORBITS${n > 2 ? ' ABOUT EACH PAIR OF SUNS' : ''}.`;",
            ": `WITH THE PLANETS IN FIGURE-OF-EIGHT ORBITS${n > 2 ? ' ABOUT EACH PAIR OF SUNS' : ''}.`);", name=n)
    s = rep(s, '<div class="hint" id="hint">Double-click to show controls</div>',
            '<div class="hint" id="hint">Double-tap to show the controls</div>\n'
            '<div id="tapSound" style="position:fixed;left:50%;bottom:calc(84px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);z-index:5;'
            'background:#e3c170;color:#060d22;padding:8px 18px 9px;border-radius:2px;font:15px/1.2 \'Old Standard TT\',Georgia,serif;letter-spacing:.04em;'
            'pointer-events:none;transition:opacity .5s;white-space:nowrap">Tap anywhere to start the sound</div>', name=n)
    # sound comes on with the first tap anywhere, like the other pieces
    s = rep(s, "$('bBells').onclick", "(function(){let done=false;const go=e=>{if(done)return;if(e&&e.target&&e.target.closest&&e.target.closest('#bSound'))return;done=true;"
            "const t=$('tapSound');if(t)t.style.opacity=0;if(!soundOn)$('bSound').click();};"
            "addEventListener('pointerup',go,true);addEventListener('keydown',go,true);"
            "$('bSound').addEventListener('click',()=>{done=true;const t=$('tapSound');if(t)t.style.opacity=0;});})();\n$('bBells').onclick", name=n)
    return s


def wandering(s, n):
    # already app-ready; move the shared scripts into <head> and set the button corner
    s = rep(s, '<script src="../../pieces.js"></script>\n<script src="../../shared/host.js"></script>\n</body>', '</body>', name=n)
    s = rep(s, '<title>Wandering Stars</title>', '<title>Wandering Stars</title>\n<script src="../../pieces.js"></script>\n<script src="../../shared/host.js"></script>', name=n)
    s = rep(s, '<html lang="en">', '<html lang="en" data-home="bl">', name=n)
    return s


if __name__ == '__main__':
    build('star-trails', 'star-trails.html', star_trails)
    build('ground-tracks', 'ground-tracks.html', ground_tracks)
    build('deep-field-receiver', 'deep-field-receiver.html', deep_field)
    build('nursery-of-stars', 'nebula-nursery.html', nursery)
    build('constellations', 'constellations.html', constellations)
    build('cymatics', 'cymatics.html', cymatics)
    build('the-orrery', 'figure-eight.html', orrery)
    build('wandering-stars', 'wandering-stars.html', wandering)
