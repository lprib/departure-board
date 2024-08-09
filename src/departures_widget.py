from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import *
from PySide6.QtSvgWidgets import *

from departure_service import Departure, DeparturesInfo, DepartureStatus, TransitType
import font


BUS_LOGO = "busses_roundel.svg"
RAIL_LOGO = "National_Rail_logo.svg"


class RailDepartureWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.setProperty("class", "depboard")
        self.setLayout(self.main_layout)
        self.main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        header = QFrame()
        header.setProperty("class", "title-frame")
        header.setContentsMargins(0, 0, 0, 0)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(30)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header.setLayout(header_layout)
        self.main_layout.addWidget(header)

        self.logo = QSvgWidget(RAIL_LOGO)
        self.logo.setMaximumSize(QtCore.QSize(140, 140))
        self.logo.renderer().setAspectRatioMode(
            QtCore.Qt.AspectRatioMode.KeepAspectRatio
        )
        header_layout.addWidget(self.logo)

        self.location_label = QLabel("Fetching data...")
        self.location_label.setProperty("class", "station-name")
        self.location_label.setFont(font.make_font(60))
        header_layout.addWidget(self.location_label)

        self.departures_widgets = []

    def update_departures(self, departures: DeparturesInfo):
        for w in self.departures_widgets:
            self.main_layout.removeWidget(w)
            w.deleteLater()
        self.location_label.setText(departures.location)
        if departures.transit == TransitType.NATIONAL_RAIL:
            self.logo.load(RAIL_LOGO)
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
                no_deps.setFont(font.make_font(20))
                self.departures_widgets = [no_deps]
                self.main_layout.addWidget(no_deps)
        else:
            error = QLabel("Exception: " + departures.failtext)
            error.setProperty("class", "error")
            error.setFont(font.make_font(20))
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

        layout = QHBoxLayout()
        self.setLayout(layout)

        if dep.std is not None:
            std_label = QLabel(dep.std)
            std_label.setFont(font.make_font(50))
            std_label.setProperty("class", "departure-time")
            layout.addWidget(std_label)

        to_label = QLabel(dep.to)
        to_label.setFont(font.make_font(50))
        layout.addWidget(to_label)

        layout.addStretch()

        etd_label = QLabel(dep.etd)
        etd_label.setFont(font.make_font(50))
        layout.addWidget(etd_label)
