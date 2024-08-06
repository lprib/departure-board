import sys
import random
from typing import Any
from PySide6 import QtCore, QtWidgets, QtGui

from departures_widget import RailDepartureWidget
from ldbws_api import RailDepartureService
from tfl_api import TflStopPointService
from departure_service import DepartureService
from config import Config

import asyncio


class ScreenManager(QtWidgets.QStackedWidget):
    def __init__(
        self,
        screens: list[tuple[RailDepartureWidget, DepartureService]],
    ):
        super().__init__()

        self.screens = screens

        next_shortcut = QtGui.QShortcut(QtCore.Qt.Key.Key_Space, self)
        next_shortcut.activated.connect(self.next_screen)

        for widget, service in screens:
            widget.update_departures(service.get_board_sync())
            self.addWidget(widget)

    @QtCore.Slot()
    def next_screen(self):
        idx = self.currentIndex()
        idx += 1
        if idx >= len(self.screens):
            self.setCurrentIndex(0)
        else:
            self.setCurrentIndex(idx)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    conf = Config("config.json")

    app = QtWidgets.QApplication([])

    QtGui.QFontDatabase.addApplicationFont("johnston_underground.ttf")
    QtGui.QFontDatabase.addApplicationFont("johnston_underground_heavy.ttf")

    with open("style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    widget = ScreenManager([(RailDepartureWidget(), s) for s in conf.board_services()])
    # widget.resize(1920, 360)
    widget.setFixedSize(1920, 360)
    widget.setProperty("class", "window")
    widget.show()

    sys.exit(app.exec())
