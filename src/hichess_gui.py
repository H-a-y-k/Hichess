import PySide2.QtWidgets as QtWidgets
from hichess.hichess import BoardWidget


class HiChessGui(QtWidgets.QMainWindow):
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
        chessBoard = BoardWidget(flipped=False)
        informationWidget = QtWidgets.QWidget()

        gameSceneLayout = QtWidgets.QHBoxLayout()
        gameSceneLayout.addWidget(chessBoard)
        gameSceneLayout.addWidget(informationWidget)
        gameSceneLayout.setContentsMargins(0, 0, 0, 0)
        gameSceneWidget.setLayout(gameSceneLayout)

        self.scene.addWidget(gameSceneWidget)
     
    def playOffline(self):
        self.scene.setCurrentIndex(1)
