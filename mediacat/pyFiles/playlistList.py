import sqlite3
from PyQt5 import QtCore
from PyQt5.QtWidgets import QFileDialog
import os


class PlaylistList:
    def __init__(self, trackWidget, playlistWidget, playlistAddAction,
                 trackAddAction, updateAction, changeListsAction, deleteTrackAction, deletePlaylistAction, db):

        self.trackWidget = trackWidget
        self.playlistWidget = playlistWidget
        self.playlistAddAction = playlistAddAction
        self.trackAddAction = trackAddAction
        self.updateAction = updateAction
        self.changeListsAction = changeListsAction
        self.deleteTrackAction = deleteTrackAction
        self.deletePlaylistAction = deletePlaylistAction
        self.filesformats = ['mp3', 'wav', 'aiff', 'au', 'wma', 'snd']

        # подключение базы данных
        self.con = sqlite3.connect(db)
        self.cur = self.con.cursor()

        self.playlistWidget.clicked.connect(self.update_tracks)

        # кнопки взаимодействия с функциями
        self.playlistAddAction.triggered.connect(self.add_playlist)
        self.trackAddAction.triggered.connect(self.add_track)
        self.updateAction.triggered.connect(self.update_tracks)
        self.updateAction.triggered.connect(self.update_playlists)
        self.changeListsAction.triggered.connect(self.change_lists)
        self.deleteTrackAction.triggered.connect(self.delete_track)
        self.deletePlaylistAction.triggered.connect(self.delete_playlist)

        self.update_playlists()
        self.update_ids()

    # добавление плейлиста в медиатеку
    def add_playlist(self):

        idplaylist = int(self.cur.execute("""SELECT id FROM playlistList""").fetchall()[-1][0])
        idtrack = len(self.cur.execute("""SELECT id FROM Tracklist""").fetchall())
        print(idplaylist, idtrack)

        try:
            direction = QFileDialog.getExistingDirectory(None, "Select Directory", QtCore.QDir.currentPath())
            files = os.listdir(direction)
            playliststats = [int(idplaylist) + 1, direction.split('/')[-1], str(direction)]
            print(playliststats)

            try:
                self.cur.execute("""INSERT INTO playlistList VALUES(?, ?, ?)""", playliststats)
                for file in files:
                    for fileformat in self.filesformats:
                        if fileformat in file:
                            trackstats = [int(idtrack + 1), str(file), str(direction + '/' + file),
                                          int(idplaylist) + 1]
                            self.cur.execute("""INSERT INTO trackList VALUES(?, ?, ?, ?)""", trackstats)
                            idtrack += 1
                            print(file)
                self.update_playlists()

            except sqlite3.Error:
                print("Failed to insert new data into data base")
        except WindowsError as error:
            print(error)
            print("invalid Direction")

        self.con.commit()

    # добавление трека в выбранный плейлист
    def add_track(self):
        try:
            id_track = len(self.cur.execute("""SELECT id FROM Tracklist""").fetchall())
            if self.playlistWidget.currentItem() is None:
                return print('No playlist selected')

            currentplaylist = self.cur.execute("""SELECT id FROM playlistList WHERE playlistName=?""",
                                               (str(self.playlistWidget.currentItem().text()),)).fetchone()

            direction = QFileDialog.getOpenFileName(None, "Select mp3 File", '')
            trackstats = [id_track + 1, str(direction[0].split('/')[-1]), direction[0], currentplaylist[0]]
            print(trackstats)

            for fileformat in self.filesformats:
                if fileformat in str(direction[0].split('/')[-1]):
                    self.cur.execute("""INSERT INTO trackList VALUES(?, ?, ?, ?)""", trackstats)

            self.con.commit()
            self.update_tracks()
        except BaseException as ve:
            print(ve)

    # обновление списка плейлистов
    def update_playlists(self):
        self.playlistWidget.clear()
        playlists = self.cur.execute("""SELECT playlistName From playlistList """).fetchall()
        for playlist in playlists:
            self.playlistWidget.addItem(str(playlist).split("'")[1])
            print(playlist)

    # обновление списка треков
    def update_tracks(self):
        # noinspection PyBroadException
        try:
            self.trackWidget.clear()
            currentplaylist = self.playlistWidget.currentItem().text()
            tracks = self.cur.execute("""SELECT trackName FROM trackList WHERE playlistID=
                                     ( SELECT id FROM playlistList WHERE playlistName=?)""",
                                      (currentplaylist,)).fetchall()
            for track in tracks:
                self.trackWidget.addItem(str(track).split("'")[1])
                print(track)
        except BaseException:
            print('update tracks error')

    # обмен положениями списков на экране
    def change_lists(self):
        trackwidgetgeometry = self.trackWidget.geometry()
        playlistgeometry = self.playlistWidget.geometry()
        self.trackWidget.setGeometry(playlistgeometry)
        self.playlistWidget.setGeometry(trackwidgetgeometry)

    # удаление медиафайла
    def delete_track(self):
        try:
            track = self.trackWidget.currentItem().text()
            self.cur.execute("""DELETE FROM Tracklist WHERE trackName=?""", (track, ))
            self.con.commit()
            self.update_ids()
            self.update_tracks()
        except BaseException as ve:
            print(ve)

    # удаление плейлиста
    def delete_playlist(self):
        try:
            playlist = self.playlistWidget.currentItem().text()
            idplaylist = self.cur.execute("""SELECT id FROM playlistList WHERE playlistName=?""",
                                          (playlist, )).fetchone()
            self.cur.execute("""DELETE FROM TrackList WHERE playlistID=?""", idplaylist)
            self.cur.execute("""DELETE FROM playlistList WHERE id=?""", idplaylist)
            self.con.commit()
            self.update_ids()
            self.update_playlists()
            self.update_tracks()
        except BaseException as ve:
            print(ve)

    # обновление идентификатора у медиафайлов
    def update_ids(self):
        try:
            finallist = []
            lists = self.cur.execute("""SELECT * FROM TrackList""").fetchall()
            count = 1
            print(lists)
            for index in range(len(lists)):
                finallist.append(list(lists[index]))
                finallist[index][0] = count
                count += 1
            self.cur.execute("""DELETE FROM TrackList""")
            print(finallist)
            for element in finallist:
                self.cur.execute("""INSERT INTO TrackList VALUES(?, ?, ?, ?)""", element)

        except BaseException as ve:
            print(ve)
