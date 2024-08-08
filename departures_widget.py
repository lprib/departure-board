from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import *
from PySide6.QtSvgWidgets import *

from departure_service import Departure, DeparturesInfo, DepartureStatus, TransitType

JOHNSTON_FAMILY = "P22 Johnston Underground"
JOHNSTON_HEAVY_FAMILY = "P22UndergroundW01-Heavy"
JOHNSTON_STYLE = "Regular"


def make_font(size, heavy=False) -> QtGui.QFont:
    font = QtGui.QFontDatabase.font(
        JOHNSTON_FAMILY if not heavy else JOHNSTON_HEAVY_FAMILY, JOHNSTON_STYLE, size
    )
    font.setHintingPreference(QtGui.QFont.HintingPreference.PreferFullHinting)
    return font


class RailDepartureWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.setProperty("class", "depboard")
        self.setLayout(self.main_layout)

        header = QFrame()
        header.setProperty("class", "title-frame")
        header.setContentsMargins(0, 0, 0, 0)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(30)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header.setLayout(header_layout)
        self.main_layout.addWidget(header)
        self.main_layout.addStretch()

        self.logo = QSvgWidget("busses_roundel.svg")
        header_layout.addWidget(self.logo)

        self.location_label = QLabel()
        self.location_label.setProperty("class", "station-name")
        self.location_label.setFont(make_font(60))
        header_layout.addWidget(self.location_label)

        header_layout.addStretch()

        self.time = QLabel("13:01")
        self.time.setProperty("class", "time")
        self.time.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.time.setFont(make_font(30))
        header_layout.addWidget(self.time)

        self.departures_widgets = []

    def update_departures(self, departures: DeparturesInfo):
        for w in self.departures_widgets:
            self.main_layout.removeWidget(w)
        self.location_label.setText(departures.location)
        if departures.transit == TransitType.NATIONAL_RAIL:
            self.logo.load("National_Rail_logo.svg")
        elif departures.transit == TransitType.BUS:
            self.logo.load("busses_roundel.svg")

        self.logo.setMaximumSize(QtCore.QSize(140, 140))
        self.logo.renderer().setAspectRatioMode(
            QtCore.Qt.AspectRatioMode.KeepAspectRatio
        )

        if departures.failtext is None:
            if len(departures.departures) != 0:
                self.departures_widgets = [
                    DepartureTimeWidget(d) for d in departures.departures[:4]
                ]
                for w in self.departures_widgets:
                    self.main_layout.addWidget(w)
            else:
                no_deps = QLabel("No departures found")
                no_deps.setProperty("class", "no-deps")
                no_deps.setFont(make_font(20))
                self.departures_widgets = [no_deps]
                self.main_layout.addWidget(no_deps)
        else:
            error = QLabel("Exception: " + departures.failtext)
            error.setProperty("class", "error")
            error.setFont(make_font(20))
            error.setMaximumWidth(1000)
            self.departures_widgets = [error]
            self.main_layout.addWidget(error)


class DepartureTimeWidget(QFrame):
    def __init__(self, dep: Departure):
        super().__init__()
        self.setProperty("class", "departure-container")
        if dep.status == DepartureStatus.ON_TIME:
            self.setProperty("state", "ontime")
        elif dep.status == DepartureStatus.DELAYED:
            self.setProperty("state", "delayed")
        elif dep.status == DepartureStatus.CANCELLED:
            self.setProperty("state", "cancelled")
        else:
            # ?
            self.setProperty("state", "cancelled")

        font = QtGui.QFontDatabase.font(JOHNSTON_FAMILY, JOHNSTON_STYLE, 50)
        font.setHintingPreference(QtGui.QFont.HintingPreference.PreferFullHinting)

        layout = QHBoxLayout()
        self.setLayout(layout)

        if dep.std is not None:
            std_label = QLabel(dep.std)
            std_label.setFont(font)
            std_label.setProperty("class", "departure-time")
            layout.addWidget(std_label)

        to_label = QLabel(dep.to)
        to_label.setFont(font)
        layout.addWidget(to_label)

        layout.addStretch()

        etd_label = QLabel(dep.etd)
        etd_label.setFont(font)
        layout.addWidget(etd_label)
