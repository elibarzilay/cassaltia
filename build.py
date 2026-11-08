"""Builds Cassaltia: Cascadia Code with its weight axis extended past Bold.

Cassaltia's Regular is a heavy Cascadia Code, and its Bold continues the straight line from
Cascadia's Regular master through its Bold master.  Windows Terminal always draws bold text at
weight 700, so a font whose 700 is heavier than a usual Bold gives a heavy base font with a
heavier bold.

Usage: ./build [--regular WEIGHT] [--bold WEIGHT]

Weights are CSS-style, as in Cascadia Code: --regular and --bold set the weights cut as the
Regular and the Bold.  The `build` wrapper holds their defaults, and a later option replaces an
earlier one.  Each cut comes in upright and italic, from Cascadia's two designspaces, and in six
families named like Cascadia's with "Cassaltia" in place of "Cascadia": Cassaltia Code and
Cassaltia Mono (without ligatures), each also as PL (with Powerline glyphs) and NF (with Nerd
Font glyphs).  Cascadia's own build.py supplies the feature files, the Powerline and Nerd Font
glyphs, and the font metadata.

The `build` wrapper runs this from Cascadia's clone in cascadia/.  Each run starts with an empty
out/ next to it, and puts the fonts there as <family>-<style>.ttf (e.g.,
CassaltiaMonoNF-BoldItalic.ttf) with a .woff2 of each for web pages, and Cassaltia.ttc, a
collection of all 24 fonts for installing in one go.
"""

import argparse
import functools
import importlib.util
import shutil
from pathlib import Path

import fontTools.designspaceLib as dsl
import ufo2ft
import ufo2ft.instantiator as instantiator
from fontTools.ttLib import TTFont
from fontTools.ttLib.ttCollection import TTCollection
from fontTools.varLib import models

# Cascadia's build.py, in the current directory
spec = importlib.util.spec_from_file_location("cascadia", "build.py")
cascadia = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cascadia)

NAME = "Cassaltia"
MAKER = "Eli Barzilay"
CREDIT = f"{MAKER} <eli@barzilay.org>"
OUT = Path("../out")
WEIGHT_CLASS = {"Regular": 400, "Bold": 700}

# ufo2ft's instantiator clamps locations to the masters; make it extrapolate past them
normalize = models.normalizeLocation
instantiator.Instantiator.normalize = lambda self, location: normalize(
    location, self.axis_bounds, extrapolate=True)
models.VariationModel = functools.partial(models.VariationModel, extrapolate=True)

parser = argparse.ArgumentParser(prog="build")
parser.add_argument("--regular", type=int, required=True)
parser.add_argument("--bold", type=int, required=True)
args = parser.parse_args()
if args.bold <= args.regular:
    parser.error(f"--bold {args.bold} must be above --regular {args.regular}")

cuts = [("Regular", args.regular), ("Bold", args.bold)]


def build(family, designspace, suffix, styles):
    """Builds the cuts of `family` from one of Cascadia's designspaces, and returns their .ttf
    files.  `styles` maps each cut's role ("Regular" or "Bold") to its style name, and the repo's
    build.py chooses the feature files and the Nerd Font glyphs by the family name plus
    `suffix`."""
    ds = dsl.DesignSpaceDocument.fromfile(f"sources/{designspace}")
    axis = next(a for a in ds.axes if a.tag == "wght")
    (i1, o1), (i2, o2) = sorted(axis.map)[-2:]

    def design(weight):
        """Returns the design location of a CSS weight: the axis map's, extending its last
        segment past the axis maximum."""
        return (axis.map_forward(weight) if weight <= axis.maximum
                else o2 + (weight - i2) * (o2 - o1) / (i2 - i1))

    # Rules that swap in heavy glyph shapes up to the heaviest master apply beyond it too
    for rule in ds.rules:
        for conditions in rule.conditionSets:
            for c in conditions:
                if c["name"] == axis.name and c.get("maximum") == o2:
                    c["maximum"] = None
    ds.instances = [
        dsl.InstanceDescriptor(
            name=f"{family} {styles[role]}", familyName=family, styleName=styles[role],
            styleMapFamilyName=family, styleMapStyleName=styles[role].lower(),
            location={axis.name: design(weight)})
        for role, weight in cuts]
    cascadia.prepare_fonts(ds, family + suffix)
    generator = instantiator.Instantiator.from_designspace(ds)
    files = []
    for (role, weight), instance in zip(cuts, ds.instances):
        print(f"[{family}] {styles[role]} at weight {weight} (design {design(weight):g})")
        font = generator.generate_instance(instance)
        font.info.openTypeOS2WeightClass = WEIGHT_CLASS[role]
        # Credits: Cascadia's copyright line stays, as the OFL requires
        font.info.copyright += f" {NAME} changes © 2026 {CREDIT}."
        font.info.openTypeNameDescription = (
            f"Cascadia Code with its weight axis extended past Bold, by {CREDIT}.")
        font.info.openTypeNameManufacturer = MAKER
        font.info.openTypeNameManufacturerURL = "https://barzilay.org"
        ttf =OUT / f"{family.replace(' ', '')}-{styles[role].replace(' ', '')}.ttf"
        ufo2ft.compileTTF(font, removeOverlaps=True, overlapsBackend="pathops").save(ttf)
        cascadia.to_woff2(ttf, ttf.with_suffix(".woff2"))
        files.append(ttf)
    return files


if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
built = [build(family, *slant)
         for family in [f"{NAME} {kind}{glyphs}"
                        for kind in ["Code", "Mono"] for glyphs in ["", " PL", " NF"]]
         for slant in [("CascadiaCode_variable.designspace", "",
                        {"Regular": "Regular", "Bold": "Bold"}),
                       ("CascadiaCode_variable_italic.designspace", " Italic",
                        {"Regular": "Italic", "Bold": "Bold Italic"})]]
collection = TTCollection()
collection.fonts = [TTFont(ttf) for files in built for ttf in files]
collection.save(OUT / f"{NAME}.ttc", shareTables=True)
print(f"[{NAME}] {OUT}/{NAME}.ttc")
