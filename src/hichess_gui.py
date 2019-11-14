from PySide2.QtWidgets import QMainWindow, QStackedWidget
from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from PySide2.QtCore import Qt
from hichess.hichess import BoardWidget

class HiChessGui(QMainWindow):
    def __init__(self):
        super().__init__()

        self.scene = QStackedWidget()
        self.setCentralWidget(self.scene)
        self.setupMainMenuScene()
        self.setupGameScene()

    def setupMainMenuScene(self):
        menuScene = QWidget()
        playOfflineButton = QPushButton("Play Offline")
        playOnlineButton = QPushButton("Play Online")
        exitButton = QPushButton("Exit")

        playOfflineButton.clicked.connect(self.playOffline)
        exitButton.clicked.connect(self.close)

        menuSceneLayout = QVBoxLayout()
        menuSceneLayout.addWidget(playOfflineButton)
        menuSceneLayout.addWidget(playOnlineButton)
        menuSceneLayout.addWidget(exitButton)
        menuScene.setLayout(menuSceneLayout)
         
        self.scene.addWidget(menuScene)
    
    def setupGameScene(self):
        gameSceneWidget = QWidget()
        chessBoard = BoardWidget(flipped = False)
        informationWidget = QWidget()

        gameSceneLayout = QHBoxLayout()
        gameSceneLayout.addWidget(chessBoard)
        gameSceneLayout.addWidget(informationWidget)
        gameSceneLayout.setContentsMargins(0, 0, 0, 0)
        gameSceneWidget.setLayout(gameSceneLayout)

        self.scene.addWidget(gameSceneWidget)
     
    def playOffline(self):
        self.scene.setCurrentIndex(1)