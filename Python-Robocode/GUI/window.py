# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""

import os
import pickle
import re
import csv
import random
from datetime import datetime
from importlib import reload

from PyQt6.QtWidgets import (
    QMainWindow,
    QGraphicsScene,
    QHeaderView,
    QTableWidgetItem,
    QMessageBox
)
from PyQt6.QtCore import pyqtSlot, QTimer, Qt
from PyQt6.QtGui import QColor, QBrush

from graph import Graph
from Ui_window import Ui_MainWindow
from battle import Battle
from robot import Robot
from RobotInfo import RobotInfo
from statistic import statistic


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.countBattle = 0
        self.timer = QTimer()
        self.competitionStartTime = None

        # Configuração visual da tabela de resultados
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels([
            "Rank",
            "Name",
            "1st",
            "2nd",
            "3rd",
            "Points",
            "Kills"
        ])

        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Esconde a numeração lateral automática da tabela,
        # porque agora teremos a coluna Rank.
        self.tableWidget.verticalHeader().setVisible(False)

        # Mantém a ordem calculada pelo ranking, sem reordenar automaticamente.
        self.tableWidget.setSortingEnabled(False)

        self.tableWidget.hide()

    def createResultItem(self, text, rank=None, align_center=True):
        item = QTableWidgetItem(str(text))

        if align_center:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        if rank == 1:
            # 1º lugar - amarelo claro
            item.setBackground(QBrush(QColor(255, 245, 180)))

        elif rank == 2:
            # 2º lugar - cinza claro
            item.setBackground(QBrush(QColor(225, 225, 225)))

        elif rank == 3:
            # 3º lugar - bronze claro
            item.setBackground(QBrush(QColor(224, 198, 156)))

        return item

    def showStatisticsTable(self):
        self.graphicsView.hide()
        self.tableWidget.show()

        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(self.statisticDico))
        self.tableWidget.setSortingEnabled(False)

        ranking = self.getRanking()

        for i, (key, value) in enumerate(ranking):
            rank = i + 1

            self.tableWidget.setItem(
                i, 0, self.createResultItem(rank, rank)
            )

            self.tableWidget.setItem(
                i, 1, self.createResultItem(key, rank, align_center=False)
            )

            self.tableWidget.setItem(
                i, 2, self.createResultItem(value.first, rank)
            )

            self.tableWidget.setItem(
                i, 3, self.createResultItem(value.second, rank)
            )

            self.tableWidget.setItem(
                i, 4, self.createResultItem(value.third, rank)
            )

            self.tableWidget.setItem(
                i, 5, self.createResultItem(value.points, rank)
            )

            self.tableWidget.setItem(
                i, 6, self.createResultItem(value.kills, rank)
            )

    def reimport_class(self, cls):
        """
        Reload and reimport class "cls".
        """

        mod = __import__(cls.__module__, fromlist=[cls.__name__])
        reload(mod)

        return getattr(mod, cls.__name__)


    @pyqtSlot()
    def on_pushButton_clicked(self):
        """
        Start the last battle
        """
        arenaPath = os.path.join(os.getcwd(), ".datas", "lastArena")
        if os.path.exists(arenaPath):
            with open(arenaPath,  'rb') as file:
                unpickler = pickle.Unpickler(file)
                dico = unpickler.load()
                botList = [self.reimport_class(bot) for bot in dico["botList"]]
                self.setUpBattle(dico["width"], dico["height"], botList)
        else:
            print("No last arena found.")
        


    @pyqtSlot()
    def on_terminateButton_clicked(self):
        """
        Terminate Current Battle
        """
        try:
            self.timer.stop()
            self.scene.killAllRobots()
            self.scene.battleFinished()
        except:
            pass

    def setUpBattle(self, width, height, botList):
        self.tableWidget.clearContents()
        self.tableWidget.hide()
        self.graphicsView.show()

        self.width = width
        self.height = height
        self.botList = botList

        self.statisticDico = {}

        for bot in botList:
            self.statisticDico[self.repres(bot)] = statistic()

        self.competitionStartTime = datetime.now()

        seed_from_environment = os.environ.get("ROBOCODE_ARENA_SEED")
        if seed_from_environment is not None:
            try:
                self.competitionSeed = int(seed_from_environment)
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Invalid arena seed",
                    "ROBOCODE_ARENA_SEED must be an integer.",
                )
                return
        else:
            self.competitionSeed = random.SystemRandom().randrange(0, 2 ** 32)

        self.forcedArenaLayout = os.environ.get("ROBOCODE_ARENA_LAYOUT") or None

        print("Competition arena seed: {}".format(self.competitionSeed))
        if self.forcedArenaLayout is not None:
            print("Forced arena layout: {}".format(self.forcedArenaLayout))

        self.startBattle()

    def startBattle(self):
        try:
            self.timer.stop()
        except:
            pass

        proxima_batalha = self.countBattle + 1
        total_batalhas = self.spinBox_battle_num.value()

        resposta = QMessageBox.question(
            self,
            "Start Battle",
            f"Ready to start?\n\nBattle {proxima_batalha} of {total_batalhas}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if resposta == QMessageBox.StandardButton.No:
            return False

        try:
            self.timer.timeout.disconnect(self.scene.advance)
            del self.timer
            del self.scene
            del self.sceneMenu
        except:
            pass

        self.timer = QTimer()
        self.countBattle += 1

        total_batalhas = self.spinBox_battle_num.value()

        self.setWindowTitle(
            f"Python-Robocode - Battle {self.countBattle} of {total_batalhas}"
        )

        self.statusBar().showMessage(
            f"Battle {self.countBattle} of {total_batalhas}"
        )

        self.sceneMenu = QGraphicsScene()
        self.graphicsView_2.setScene(self.sceneMenu)

        battle_seed = self.competitionSeed + self.countBattle - 1

        try:
            self.scene = Graph(
                self,
                self.width,
                self.height,
                layout_name=self.forcedArenaLayout,
                seed=battle_seed,
                required_spawn_positions=len(self.botList),
            )
        except ValueError as error:
            QMessageBox.critical(self, "Arena configuration error", str(error))
            self.countBattle = 0
            return False

        self.graphicsView.setScene(self.scene)

        self.scene.AddRobots(self.botList)

        self.timer.timeout.connect(self.scene.advance)
        self.timer.start((self.hslider_game_speed.value() ** 2) // 100)

        self.resizeEvent()

        return True
    
    @pyqtSlot(int)
    def on_horizontalSlider_valueChanged(self, value):
        """
        Slot documentation goes here.
        """
        self.timer.setInterval((value**2)//100)
    
    @pyqtSlot()
    def on_actionNew_triggered(self):
        """
        Battle Menu
        """
        self.battleMenu = Battle(self)
        self.battleMenu.show()
    
    @pyqtSlot()
    def on_actionNew_2_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        print("Not Implemented Yet")
    
    @pyqtSlot()
    def on_actionOpen_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        print("Not Implemented Yet")

    def resizeEvent(self, evt=None):
        try:
            self.graphicsView.fitInView(self.scene.sceneRect(), 4)
        except :
            pass

    def addRobotInfo(self, robot):
        self.sceneMenu.setSceneRect(0, 0, 170, 800)
        rb = RobotInfo()
        rb.pushButton.setText(str(robot))
        rb.progressBar.setValue(100)
        rb.robot = robot
        robot.info = rb
        robot.progressBar = rb.progressBar
        robot.icon = rb.toolButton
        robot.icon2 = rb.toolButton_2
        p = self.sceneMenu.addWidget(rb)
        l = (len(self.scene.aliveBots) )
        self.sceneMenu.setSceneRect(0, 0, 170, l*80)
        p.setPos(0, (l -1)*80)


    def chooseAction(self):
        if self.countBattle >= self.spinBox_battle_num.value():
            self.showStatisticsTable()
            self.exportRankingToCSV()

            total_batalhas = self.spinBox_battle_num.value()

            self.setWindowTitle(
                f"Python-Robocode - Tournament finished"
            )

            self.statusBar().showMessage(
                f"Tournament finished - {total_batalhas} battles completed"
            )

            self.countBattle = 0
            self.timer.stop()

        else:
            iniciou = self.startBattle()

            if not iniciou:
                self.showStatisticsTable()
                self.exportRankingToCSV()
                self.countBattle = 0


    def repres(self, bot):
        repres = repr(bot).split(".")
        return repres[1].replace("'>", "")


    def getRanking(self):
        ranking = sorted(
            self.statisticDico.items(),
            key=lambda item: (
                -item[1].points,
                -item[1].first,
                -item[1].second,
                -item[1].third,
                -item[1].kills,
                item[0]
            )
        )

        return ranking

    def exportRankingToCSV(self):
        if self.competitionStartTime is None:
            self.competitionStartTime = datetime.now()

        date_time_text = self.competitionStartTime.strftime("%Y-%m-%d_%H-%M-%S")

        results_folder = os.path.join(os.getcwd(), "results")

        if not os.path.exists(results_folder):
            os.makedirs(results_folder)

        file_name = f"ranking_competition_{date_time_text}.csv"
        file_path = os.path.join(results_folder, file_name)

        ranking = self.getRanking()

        with open(file_path, mode="w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.writer(csv_file, delimiter=";")

            writer.writerow([
                "Rank",
                "Name",
                "1st",
                "2nd",
                "3rd",
                "Points",
                "Kills"
            ])

            for i, (name, value) in enumerate(ranking):
                rank = i + 1

                writer.writerow([
                    rank,
                    name,
                    value.first,
                    value.second,
                    value.third,
                    value.points,
                    value.kills
                ])

        print(f"Ranking CSV generated: {file_path}")

        return file_path
