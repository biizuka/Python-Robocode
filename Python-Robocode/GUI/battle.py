# -*- coding: utf-8 -*-

"""Module implementing the robot-selection dialog."""

import os
import pickle

from PyQt6.QtWidgets import QDialog, QLabel, QMessageBox, QPushButton
from PyQt6.QtCore import pyqtSlot

from robot import Robot
from battle_rules import describe_battle_rules, normalize_battle_rules
from Ui_battle import Ui_Dialog


class Battle(QDialog, Ui_Dialog):
    """Select robots after the arena and battle rules are configured."""

    def __init__(self, parent=None, battle_configuration=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.window = parent
        self.battleConfiguration = self.__normalizeConfiguration(
            battle_configuration
        )

        self.setWindowTitle("Robot Selection")

        # Arena settings are now collected in BattleSettings before this dialog.
        for widget in (
            self.label_3,
            self.label_5,
            self.spinBox,
            self.label_4,
            self.spinBox_2,
            self.label_6,
        ):
            widget.hide()

        self.configurationSummary = QLabel(
            self.__configurationSummaryText(),
            self,
        )
        self.configurationSummary.setWordWrap(True)
        self.configurationSummary.setStyleSheet(
            "QLabel {"
            "  background: #f2f3f5;"
            "  border: 1px solid #c9ccd1;"
            "  border-radius: 4px;"
            "  padding: 8px;"
            "}"
        )
        self.verticalLayout_5.insertWidget(0, self.configurationSummary)

        self.selectAllButton = QPushButton("Select All >>", self)
        self.verticalLayout.insertWidget(1, self.selectAllButton)
        self.selectAllButton.clicked.connect(self.selectAllBots)

        self.pushButton_3.setText("Start Battle")
        self.resize(620, 430)

        botnames = []
        self.listBots = {}
        botFiles = os.listdir(os.getcwd() + "/Robots")

        for botFile in botFiles:
            if not botFile.endswith(".py"):
                continue

            botName = botPath = botFile[:botFile.rfind(".")]
            if botName in botnames:
                continue

            botnames.append(botName)

            try:
                botModule = __import__(botPath)
                for name in dir(botModule):
                    candidate = getattr(botModule, name)
                    if candidate in Robot.__subclasses__():
                        key = str(candidate).replace("<class '", "").replace("'>", "")
                        self.listBots[key] = candidate
                        break
            except Exception as error:
                print("Problem with bot file '{}': {}".format(botFile, str(error)))

        for key in self.listBots.keys():
            self.listWidget.addItem(key)

    def __normalizeConfiguration(self, configuration):
        configuration = dict(configuration or {})

        return {
            "width": int(configuration.get("width", 700)),
            "height": int(configuration.get("height", 500)),
            "battleCount": max(1, int(configuration.get("battleCount", 10))),
            "battleRules": normalize_battle_rules(
                configuration.get("battleRules")
            ),
        }

    def __configurationSummaryText(self):
        return (
            "Arena: {width} × {height} px   |   Battles: {battle_count}\n"
            "Rules: {rules}"
        ).format(
            width=self.battleConfiguration["width"],
            height=self.battleConfiguration["height"],
            battle_count=self.battleConfiguration["battleCount"],
            rules=describe_battle_rules(
                self.battleConfiguration["battleRules"]
            ),
        )

    @pyqtSlot()
    def on_pushButton_clicked(self):
        """Add the currently selected bot."""
        current_item = self.listWidget.currentItem()
        if current_item is not None:
            self.listWidget_2.addItem(current_item.text())

    @pyqtSlot()
    def on_pushButton_2_clicked(self):
        """Remove the currently selected bot."""
        self.listWidget_2.takeItem(self.listWidget_2.currentRow())

    @pyqtSlot()
    def on_pushButton_3_clicked(self):
        """Start the configured tournament."""
        botList = []
        for index in range(self.listWidget_2.count()):
            key = str(self.listWidget_2.item(index).text())
            botList.append(self.listBots[key])

        if not botList:
            QMessageBox.warning(
                self,
                "No robots selected",
                "Select at least one robot before starting the battle.",
            )
            return

        width = self.battleConfiguration["width"]
        height = self.battleConfiguration["height"]
        battle_count = self.battleConfiguration["battleCount"]
        battle_rules = self.battleConfiguration["battleRules"]

        self.window.spinBox_battle_num.setValue(battle_count)
        self.save(width, height, botList, battle_rules, battle_count)
        started = self.window.setUpBattle(width, height, botList, battle_rules)

        if started:
            self.accept()

    def save(self, width, height, botList, battle_rules, battle_count):
        data = {
            "width": width,
            "height": height,
            "battleCount": battle_count,
            "botList": botList,
            "battleRules": normalize_battle_rules(battle_rules),
        }

        data_directory = os.path.join(os.getcwd(), ".datas")
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)

        with open(os.path.join(data_directory, "lastArena"), "wb") as file:
            pickle.Pickler(file).dump(data)

    def selectAllBots(self):
        """Add every bot that is not already selected."""
        selected_bots = {
            self.listWidget_2.item(index).text()
            for index in range(self.listWidget_2.count())
        }

        for index in range(self.listWidget.count()):
            bot_name = self.listWidget.item(index).text()
            if bot_name not in selected_bots:
                self.listWidget_2.addItem(bot_name)