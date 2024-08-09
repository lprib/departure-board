import asyncio
import datetime

from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import *

from departures_widget import RailDepartureWidget
from departure_service import DepartureService
import font


class ScreenManager(QFrame):
    TICK_TIME_MS = 50

    def __init__(
        self,
        screens: list[tuple[RailDepartureWidget, DepartureService]],
        ms_per_screen: int,
    ):
        super().__init__()
        self.setProperty("class", "screen-manager")

        self.ms_per_screen = ms_per_screen
        self.screens = screens

        next_shortcut = QtGui.QShortcut(QtCore.Qt.Key.Key_Space, self)
        next_shortcut.activated.connect(
            lambda: asyncio.ensure_future(self.next_screen(self.stack.currentIndex()))
        )

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        frame = QFrame()
        frame_layout = QGridLayout()
        frame.setLayout(frame_layout)
        frame.setContentsMargins(0, 0, 0, 0)
        frame.setProperty("class", "screen-pad-frame")
        self.stack = QStackedWidget()
        frame_layout.addWidget(self.stack)
        self.stack.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(frame, 0, 0)

        self.time = QLabel("??:??")
        self.time.setProperty("class", "time")
        self.time.setFont(font.make_font(20))
        self.time.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignRight
        )
        frame_layout.addWidget(self.time, 0, 0)

        self.progress = QProgressBar()
        self.progress.setProperty("class", "screen-progress")
        self.progress.setMaximum(self.ms_per_screen)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setContentsMargins(0, 0, 0, 0)
        self.progress.setFixedHeight(4)
        p = QtGui.QPalette()
        p.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor.fromString("#ffffff"))
        self.progress.setPalette(p)
        layout.addWidget(self.progress, 1, 0)

        self.screens = screens

        self.screen_flip_time = 0

        for widget, _ in screens:
            self.stack.addWidget(widget)

        QtCore.QTimer.singleShot(0, lambda: asyncio.ensure_future(self.kick_off()))

        self.tod_timer = QtCore.QTimer()
        self.tod_timer.timeout.connect(
            lambda: asyncio.ensure_future(self.update_time())
        )
        self.tod_timer.start(1000)

    @QtCore.Slot()
    async def kick_off(self):
        for i in range(len(self.screens)):
            await self.update_screen(i)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: asyncio.ensure_future(self.tick()))
        self.timer.start(self.TICK_TIME_MS)

    async def update_screen(self, index: int):
        deps = await self.screens[index][1].get_board_async()
        self.screens[index][0].update_departures(deps)

    @QtCore.Slot()
    async def tick(self):
        self.screen_flip_time += self.TICK_TIME_MS
        self.progress.setValue(self.screen_flip_time)
        self.progress.update()

        if self.screen_flip_time > self.ms_per_screen:
            self.screen_flip_time = 0
            await self.next_screen(self.stack.currentIndex())

    @QtCore.Slot()
    async def next_screen(self, index: int):
        if (index + 1) >= len(self.screens):
            self.stack.setCurrentIndex(0)
        else:
            self.stack.setCurrentIndex(index + 1)

        # now update the upcoming screen
        await self.update_screen((index + 2) % len(self.screens))

    @QtCore.Slot()
    async def update_time(self):
        self.time.setText(datetime.datetime.now().strftime("%d %b %H:%M"))
