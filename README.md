# Cassaltia

Salted Cascadia Code: normally bold, bold means **BOLD**!

Most fonts treat bold like salt: plain text is bland, and a pinch of bold adds
taste. This one is for people who like their food salty, and their salty food
saltier: Cassaltia's normal weight is what other fonts call Bold, and its Bold
is a medical hazard.

Why? Because being able to read my code from across the hall is a feature, and
I still want bold text to stand out.


## The technical reason

Windows Terminal draws bold text at weight 700, whatever weight you configure
for the font: its renderer asks for `DWRITE_FONT_WEIGHT_BOLD`, period. Cascadia
Code stops at 700, so with a heavy base weight there is nothing heavier left
for bold, and bold text looks like everything else. Information you never see
is information thrown away. Without it, you never know when your agent is
shouting something, and that's just rude.

Cassaltia fixes this by moving the scale. Its Regular is Cascadia at weight
600, nearly as heavy as Cascadia's own Bold, and its Bold is Cascadia at weight
900, well past anything Microsoft ships. When a terminal asks for 700, it gets
900, and bold stands out the way it should.


## The families

Every Cascadia family has a Cassaltia twin. Replace "Cascadia" with
"Cassaltia" in a font name and you have the right one, with no table of names
to remember:

| Cascadia          | Cassaltia          | Ligatures | Powerline | Nerd Font |
| ----------------- | ------------------ | :-------: | :-------: | :-------: |
| Cascadia Code     | Cassaltia Code     |    yes    |           |           |
| Cascadia Code PL  | Cassaltia Code PL  |    yes    |    yes    |           |
| Cascadia Code NF  | Cassaltia Code NF  |    yes    |    yes    |    yes    |
| Cascadia Mono     | Cassaltia Mono     |           |           |           |
| Cascadia Mono PL  | Cassaltia Mono PL  |           |    yes    |           |
| Cascadia Mono NF  | Cassaltia Mono NF  |           |    yes    |    yes    |

Each family has Regular, Bold, Italic, and Bold Italic. Metrics are Cascadia's
own (2048 units, 1200 wide, same line height), so anything sized for Cascadia
fits Cassaltia.


## Building

    ./build [--regular WEIGHT] [--bold WEIGHT] [--version VERSION]

- The default weights sit at the top of `build`, which is where you tweak your
  salt level. Next to them is the version: bump it whenever you change a
  weight. The options override all three for one run. The fonts' version
  string shows them after Cascadia's own version, as in
  `Version 2407.024; Cassaltia 1.1 (600/900)`.
- The build works on Cascadia's own repo, in `cascadia/`: it makes a shallow
  clone of [microsoft/cascadia-code][cascadia] when it's missing, and pulls it
  on every run.
- The only tool needed is [uv][uv]; the script installs it in `~/.local/bin`
  if it's missing. Everything Python runs in uv's cache, from Cascadia's
  pinned `requirements.txt`, so nothing gets installed anywhere else.
- It runs from anywhere, through symlinks too.
- Each run starts with an empty `out/` and fills it with a `.ttf` and a
  `.woff2` for each of the 24 fonts, plus `Cassaltia.ttc`, a collection of all
  of them for installing in one go.
- It takes a few minutes, mostly for merging in the Nerd Font glyphs.

How the salt gets in: Cascadia's sources have three masters, ExtraLight,
Regular, and Bold. Weights up to 700 interpolate between them as usual, and
heavier weights continue the straight line from Regular through Bold. The
script reuses Cascadia's `build.py` for the feature files, the Powerline and
Nerd Font glyphs, and the metadata, and patches ufo2ft's instantiator to
extrapolate instead of clamping. The few glyphs that switch to alternate shapes
in heavy weights (`$` among them) keep their heavy shapes past the masters.


## Installing

Install `Cassaltia.ttc`. That's it.

Then replace "Cascadia" with "Cassaltia" in your configs. If you're like me,
you'll also drop the bold weight you had Cascadia set to: Cassaltia's normal
weight is already there.


## Tasting

`preview.html` shows Cassaltia Code from the `.woff2` files, with `**bold**`
and `*italic*` markup in an editable sample. Browsers refuse fonts on `file:`
pages, so serve it from this directory:

    python3 -m http.server 8123

and open <http://localhost:8123/preview.html>.


## Contrast is salt too

The same goes for colors. There's a whole school of "polite" themes: lightish
gray text on a slightly darker gray, everything muted, nothing too loud.
Designers look at it, go "ooh, subtle", and take a deep, satisfied whiff of
their own exhaust.

It isn't subtle, it's hard to read. My monitor can show white on near black,
and more contrast is easier to read, so why should I sacrifice luminance on the
altar of pastel feelings?

The numbers, as WCAG contrast ratios: 1:1 is invisible, 21:1 is white on
black, and 4.5:1 is the accessibility minimum for normal text.

| Theme            | Text   | Comments |
| ---------------- | -----: | -------: |
| Solarized Dark   |  4.7:1 |    2.8:1 |
| One Dark         |  6.6:1 |    2.3:1 |
| Nord             |  9.2:1 |    2.4:1 |
| Dracula          | 13.4:1 |    3.0:1 |
| Salt (#FFF/#101) | 20.4:1 |          |

"WCAG is a hoax invented by Big Eyesight!"

Look at the comments column: the text where someone explains the hard part is
the dimmest thing on the screen, below the accessibility minimum in every one
of them. This Church of Grayscale is madness. A screen is a device for
information transfer; I shouldn't have to highlight your text to read it.

Salt your colors too. Your eyes will thank you. If they go :shrug:, wait a
couple of decades; they'll thank you then.


## Warts

1. Uses Python.

2. The build adds `setuptools<82` to the environment: Cascadia's pinned
   fontTools needs `fs`, which imports `pkg_resources`, which setuptools 82
   removed. It prints a deprecation warning on every run. The pin and the
   warning both go away when Cascadia updates its fontTools pin.


## License

SIL Open Font License 1.1, like Cascadia. "Cascadia Code" is Microsoft's
Reserved Font Name, which this does not use. Microsoft's copyright stays in
every font; the changes are "©" Eli Barzilay <eli@barzilay.org>.

[cascadia]: https://github.com/microsoft/cascadia-code
[uv]: https://docs.astral.sh/uv/
