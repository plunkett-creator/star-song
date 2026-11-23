# Star Song

Night-sky pieces that play themselves, for iPhone and iPad, Android, and the web.
Wandering Stars is free; the other seven pieces are unlocked by one purchase (`starsong.bundle`).

Start with **SETUP-GUIDE.md**.

| Folder | What's in it |
|---|---|
| `Web/` | The collection screen (`index.html`), the eight pieces (`pieces/<id>/`), fonts, the 3D engine for The Orrery, the privacy page, and `pieces.js`, which lists the pieces and holds the store links. The iPhone app, the Android app and the website all use this one folder. |
| `Web/shared/host.js` | Shared by every piece: the Collection button, pausing sound in the background, and the website's one-minute tastes of the paid pieces. |
| `ios/` | The iPhone/iPad app (Swift): full-screen pages, sound with the silent switch on, screen kept awake, in-app purchase (`Store.swift`). |
| `android/` | The Android app (Kotlin): full-screen pages, screen kept awake, Google Play Billing (`Store.kt`). |
| `.github/workflows/` | The cloud builds: website, iPhone, Android. |
| `tools/build_pieces.py` | How the original artifact pages were turned into app pieces: offline fonts, one look each, no recording, endless play. |

Each piece uses one look: Constellations (Clear night), Cymatics (Slate), The Nursery of Stars (Gilt), Star Trails (Clear), Ground Tracks (Phosphor), Deep Field Receiver (Inferno), The Orrery (a new night plate, formerly Figure Eight), Wandering Stars.

Fonts are under the SIL Open Font License (`Web/fonts/OFL-*.txt`); three.js is under the MIT licence (`Web/vendor/three-LICENSE.txt`).
