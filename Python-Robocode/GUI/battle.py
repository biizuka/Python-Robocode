# -*- coding: utf-8 -*-

"""
Module implementing Battle.
"""

import os
import pickle

from PyQt6.QtWidgets import QDialog, QPushButton
from PyQt6.QtCore import pyqtSlot

from robot import Robot
from Ui_battle import Ui_Dialog

class Battle(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.selectAllButton = QPushButton("Select All >>", self)
        self.verticalLayout.insertWidget(1, self.selectAllButton)
        self.selectAllButton.clicked.connect(self.selectAllBots)

        self.window = parent
        botnames = []
        self.listBots = {}
        botFiles = os.listdir(os.getcwd() + "/Robots")
        for botFile in botFiles:
            if botFile.endswith('.py'):
                botName = botPath =  botFile[:botFile.rfind('.')]
                if botName not in botnames:
                    botnames.append(botName)
                    try:
                        botModule =  __import__(botPath)
                        for name in dir(botModule):
                            if getattr(botModule,  name) in Robot.__subclasses__():
                                someBot = getattr(botModule, name)
                                bot = someBot
                                self.listBots[str(bot).replace("<class '","").replace("'>", "")] = bot
                                break
                    except Exception as e:
                        print("Problem with bot file '{}': {}".format(botFile, str(e)))

                        
        for key in self.listBots.keys():
            self.listWidget.addItem(key)
    
    @pyqtSlot()
    def on_pushButton_clicked(self):
        """
        Add Bot
        """
    
        self.listWidget_2.addItem(self.listWidget.currentItem().text())
 
    
    @pyqtSlot()
    def on_pushButton_2_clicked(self):
        """
        Remove Bot
        """
        item = self.listWidget_2.takeItem(self.listWidget_2.currentRow())
        item = None
    
    @pyqtSlot()
    def on_pushButton_3_clicked(self):
        """
        Start
        """
        width = self.spinBox.value()
        height = self.spinBox_2.value()
        botList = []
        for i in range(self.listWidget_2.count()):

            key = str(self.listWidget_2.item(i).text())
            botList.append(self.listBots[key])
            
        self.save(width, height, botList)
        self.window.setUpBattle(width, height, botList)

        
        
    def save(self, width, height, botList):
        dico = {}
        dico["width"] = width
        dico["height"] = height
        dico["botList"] = botList

        if not os.path.exists(os.getcwd() + "/.datas/"):
            os.makedirs(os.getcwd() + "/.datas/")
        
        with open(os.getcwd() + "/.datas/lastArena",  'wb') as file:
            pickler = pickle.Pickler(file)
            pickler.dump(dico)
        file.close()


    def selectAllBots(self):
        selected_bots = set()

        for i in range(self.listWidget_2.count()):
            selected_bots.add(self.listWidget_2.item(i).text())

        for i in range(self.listWidget.count()):
            bot_name = self.listWidget.item(i).text()

            if bot_name not in selected_bots:
                self.listWidget_2.addItem(bot_name)
       


