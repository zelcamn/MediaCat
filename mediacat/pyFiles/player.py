import sqlite3
from PyQt5 import QtCore, QtMultimedia


# Класс отвечающий за плеер

class Player:
    def __init__(self, backButton, playButton, forwardButton, playlistWidget, loudSlider,
                 positionSlider, radioButton,
                 changeListsAction, trackLabel):

        self.trackLabel = trackLabel
        self.player = QtMultimedia.QMediaPlayer()
        self.backButton = backButton
        self.playButton = playButton
        self.forwardButton = forwardButton
        self.loudSlider = loudSlider
        self.positionSlider = positionSlider
        self.radiobutton = radioButton
        self.changeListsAction = changeListsAction

        # кнопка включения/выключения повтора
        self.radiobutton.toggled.connect(self.repeat_flag)

        # подключение базы данных
        self.con = sqlite3.connect("mediacat/database/mediacatDB.db")
        self.cur = self.con.cursor()

        # флаги включения/выключения медиафайла и повтора
        self.flag = True
        self.repeatflag = False

        # изменение позиций слайдеров пользователем
        self.loudSlider.valueChanged.connect(self.loud_slider)
        self.positionSlider.sliderReleased.connect(self.position_slider)
        self.loudSlider.setRange(0, 100)

        # кнопки включения/выключения медиафайла и выбора соседних медиафайлов
        self.playButton.clicked.connect(self.play_btn)
        self.backButton.clicked.connect(lambda: self.switch_track(-1))
        self.forwardButton.clicked.connect(lambda: self.switch_track(1))

        #  список треков
        self.playlistWidget = playlistWidget
        self.playlistWidget.clicked.connect(self.load_from_a_widget)

        #  изменение позиции слайдера медиафайла и повтора медиафайла
        self.player.durationChanged.connect(self.duration_changed)
        self.player.positionChanged.connect(self.changed_position_slider)
        self.player.stateChanged.connect(self.repeat_track)
        self.player.setVolume(10)

    # кнопка включения/выключения медиафайла
    def play_btn(self):
        if self.flag:
            self.player.pause()
            self.flag = False
            print("trackOFF")
            self.playButton.setText('пуск')
        else:
            self.player.play()
            self.flag = True
            print("trackON")
            self.playButton.setText('пауза')

    # выбор медиафайла из списка
    def load_from_a_widget(self):
        filepath = str(self.choose_track()[0]).split("'")[1]
        print(filepath)
        self.load_track(filepath)

    # запрос на получение пути медиафайла
    def choose_track(self):
        try:
            track = self.playlistWidget.currentItem().text()
            print(track)
            trackpath = self.cur.execute("""SELECT trackPath FROM trackList WHERE trackName=?""", (track,)).fetchall()
            return trackpath
        except BaseException as ve:
            print(ve)

    # кнопки выбора соседних медиафайлов
    def switch_track(self, trackmove):
        # noinspection PyBroadException
        try:
            row = self.playlistWidget.currentRow() + trackmove
            self.playlistWidget.setCurrentRow(row)
            track = self.playlistWidget.currentItem().text()

            nexttrackpath = \
                self.cur.execute("""SELECT trackPath from trackList WHERE trackName=?""", (track,)).fetchone()[0]
            self.load_track(nexttrackpath)
        except BaseException:
            print('track switch error')

    # загрузка медиафайла в плеер
    def load_track(self, filepath):
        try:
            media = QtCore.QUrl.fromLocalFile(filepath)
            content = QtMultimedia.QMediaContent(media)
            self.player.setMedia(content)
            self.player.play()
            self.flag = True

            self.playButton.setText('пауза')
            self.trackLabel.setText(self.playlistWidget.currentItem().text())
        except BaseException as ve:
            print(ve)

    # управление громкостью плеера
    def loud_slider(self, value):
        self.player.setVolume(value)

    # выбор позиции на таймлайне медиафайла
    def position_slider(self):
        value = self.positionSlider.value()
        print(value)
        self.player.setPosition(value)

    # изменение количества позиций слайдера при изменении трека
    def duration_changed(self, tracklength):
        self.positionSlider.setRange(0, tracklength)
        print('duration changed')

    # управление позицией слайдера длины трека
    def changed_position_slider(self, value):
        self.positionSlider.setValue(value)

    # включение/выключение повтора медиафайла
    def repeat_flag(self):
        if self.repeatflag:
            self.repeatflag = False
        else:
            self.repeatflag = True

    # повтор медиафайла
    def repeat_track(self, state):
        if self.repeatflag:
            if state == self.player.StoppedState:
                self.player.stop()
                self.player.play()
                print("repeatON")
        print(self.player.MediaStatus)
