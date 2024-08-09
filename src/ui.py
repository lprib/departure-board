import sys
import logging
from typing import Any
import asyncio

from PySide6 import QtCore, QtWidgets, QtGui
import PySide6.QtAsyncio as QtAsyncio

from departures_widget import RailDepartureWidget
from departure_service import DepartureService
from config import Config

from screen_manager import ScreenManager

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logging.basicConfig(
        filename="log.txt",
        filemode="a",
        format="%(asctime)s %(name)s [%(levelname)s]: %(message)s",
        datefmt="%H:%M:%S",
        level=logging.INFO,
    )

    logging.info("startup")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    conf = Config("config.json")

    app = QtWidgets.QApplication([])

    QtGui.QFontDatabase.addApplicationFont("johnston_underground.ttf")
    QtGui.QFontDatabase.addApplicationFont("johnston_underground_heavy.ttf")

    with open("style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    widget = ScreenManager(
        [(RailDepartureWidget(), s) for s in conf.board_services()],
        conf.ms_per_screen(),
    )
    widget.setFixedSize(1920, 360)
    widget.setProperty("class", "window")
    widget.show()

    QtAsyncio.run()
