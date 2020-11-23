from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtGui
from PyQt5 import uic
from mediacat.pyFiles.player import Player  #
from mediacat.pyFiles.playlistList import PlaylistList  #


class main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('mediacat/ui/main.ui', self)  # выбор дизайна приложения
        self.setWindowTitle('Mediacat')  # выбор названия приложения
        self.setWindowIcon(QtGui.QIcon('mediacat/ui/uiDesign/playButton/playButtonBig.png'))  # выбор дизайна иконки

        self.player = Player(self.backButton, self.playButton,
                             self.forwardButton, self.listWidget,
                             self.loudSlider,
                             self.positionSlider, self.repeatButton,
                             self.actionchange_lists_1, self.trackName)  # обьект - плеер

        self.playlistlist = PlaylistList(self.listWidget, self.listWidget_2,
                                         self.actionplaylist_2, self.actiontrack_2,
                                         self.actionupdate_1, self.actionchange_lists_1,
                                         self.actiontrackdelete, self.actionplaylistdelete,
                                         'mediacat/dataBase/mediacatDB.db')  # обьект - плейлисты
