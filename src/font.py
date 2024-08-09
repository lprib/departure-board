from PySide6 import QtGui

JOHNSTON_FAMILY = "P22 Johnston Underground"
JOHNSTON_HEAVY_FAMILY = "P22UndergroundW01-Heavy"
JOHNSTON_STYLE = "Regular"


def make_font(size, heavy=False) -> QtGui.QFont:
    font = QtGui.QFontDatabase.font(
        JOHNSTON_FAMILY if not heavy else JOHNSTON_HEAVY_FAMILY, JOHNSTON_STYLE, size
    )
    font.setHintingPreference(QtGui.QFont.HintingPreference.PreferFullHinting)
    return font
