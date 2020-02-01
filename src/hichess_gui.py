# -*- coding: utf-8 -*-
#
# This file is part of the HiChess project.
# Copyright (C) 2019-2020 Haik Sargsian <haiksargsian6@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import PySide2.QtWidgets as QtWidgets
import hichess.hichess


class HichessGui(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.scene = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.scene)
        self.setupMainMenuScene()
        self.setupGameScene()

    def setupMainMenuScene(self):
        menuScene = QtWidgets.QWidget()
        playOfflineButton = QtWidgets.QPushButton("Play Offline")
        playOnlineButton = QtWidgets.QPushButton("Play Online")
        exitButton = QtWidgets.QPushButton("Exit")

        playOfflineButton.clicked.connect(self.playOffline)
        exitButton.clicked.connect(self.close)

        menuSceneLayout = QtWidgets.QVBoxLayout()
        menuSceneLayout.addWidget(playOfflineButton)
        menuSceneLayout.addWidget(playOnlineButton)
        menuSceneLayout.addWidget(exitButton)
        menuScene.setLayout(menuSceneLayout)
         
        self.scene.addWidget(menuScene)
    
    def setupGameScene(self):
        gameSceneWidget = QtWidgets.QWidget()
        chessBoard = hichess.hichess.BoardWidget(flipped=False)

        informationWidget = QtWidgets.QWidget()

        gameSceneLayout = QtWidgets.QHBoxLayout()
        gameSceneLayout.addWidget(chessBoard)
        gameSceneLayout.addWidget(informationWidget)
        gameSceneLayout.setContentsMargins(0, 0, 0, 0)
        gameSceneWidget.setLayout(gameSceneLayout)

        self.scene.addWidget(gameSceneWidget)
     
    def playOffline(self):
        self.scene.setCurrentIndex(1)
