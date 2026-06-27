#! /usr/bin/python
#-*- coding: utf-8 -*-

import time, os, random

from PyQt6.QtWidgets import QGraphicsScene, QMessageBox, QGraphicsRectItem
from PyQt6.QtGui import QPixmap, QColor, QBrush
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF

from robot import Robot
from obstacle import Obstacle
from outPrint import outPrint

class Graph(QGraphicsScene):
    
    def __init__(self,  parent, width,  height):
        QGraphicsScene.__init__(self,  parent)
        self.setSceneRect(0, 0, width, height)
        self.Parent = parent
        
        #self.Parent.graphicsView.centerOn(250, 250)
        self.width = width
        self.height = height
        self.obstacles = []

        self.setTiles()
        self.setObstacles()
        self.grid = self.getGrid()

        
    def AddRobots(self, botList):
        
        """
        """
        self.aliveBots = []
        self.deadBots = []
        try:
            posList = random.sample(self.grid, len(botList))
            for bot in botList:
                try:
                    robot = bot(self.sceneRect().size(), self, str(bot))
                    self.aliveBots.append(robot)
                    self.addItem(robot)
                    robot.setPos(posList.pop())
                    self.Parent.addRobotInfo(robot)
                except Exception as e:
                    print("Problem with bot file '{}': {}".format(bot, str(e)))

            self.Parent.battleMenu.close()
        except ValueError:
            QMessageBox.about(self.Parent, "Alert", "Too many Bots for the map's size!")
        except AttributeError:
            pass

    def killAllRobots(self):
        print("kill all robots")
        try:
            self.aliveBots.sort(key=lambda r: r._Robot__health)
            for r in self.aliveBots:
                self.deadBots.append(r)
                self.removeItem(r)
            self.aliveBots = []
        except:
            pass


    def  battleFinished(self):
        print("battle terminated")
        try:
            self.deadBots.append(self.aliveBots[0])
            self.removeItem(self.aliveBots[0])
        except IndexError:
            pass
        j = len(self.deadBots)
        
        
        for i in range(j):
            print("N° {}:{}".format(j - i, self.deadBots[i]))
            if j-i == 1: #first place
                self.Parent.statisticDico[repr(self.deadBots[i])].first += 1
            if j-i == 2: #2nd place
                self.Parent.statisticDico[repr(self.deadBots[i])].second += 1
            if j-i ==3:#3rd place
                self.Parent.statisticDico[repr(self.deadBots[i])].third += 1
                
            self.Parent.statisticDico[repr(self.deadBots[i])].points += i
            self.Parent.statisticDico[repr(self.deadBots[i])].kills += self.deadBots[i].getKills()
                
        self.Parent.chooseAction()       

                    
    def setTiles(self):
        #background
        brush = QBrush()
        pix = QPixmap(os.getcwd() + "/robotImages/tile.png")
        brush.setTexture(pix)
        brush.setStyle(Qt.BrushStyle.TexturePattern)
        self.setBackgroundBrush(brush)
        
        #wall
        #left
        left = QGraphicsRectItem()
        pix = QPixmap(os.getcwd() + "/robotImages/tileVert.png")
        left.setRect(QRectF(0, 0, pix.width(), self.height))
        brush.setTexture(pix)
        brush.setStyle(Qt.BrushStyle.TexturePattern)
        left.setBrush(brush)
        left.name = 'left'
        self.addItem(left)
        #right
        right = QGraphicsRectItem()
        right.setRect(self.width - pix.width(), 0, pix.width(), self.height)
        right.setBrush(brush)
        right.name = 'right'
        self.addItem(right)
        #top
        top = QGraphicsRectItem()
        pix = QPixmap(os.getcwd() + "/robotImages/tileHori.png")
        top.setRect(QRectF(0, 0, self.width, pix.height()))
        brush.setTexture(pix)
        brush.setStyle(Qt.BrushStyle.TexturePattern)
        top.setBrush(brush)
        top.name = 'top'
        self.addItem(top)
        #bottom
        bottom = QGraphicsRectItem()
        bottom.setRect(0 ,self.height - pix.height() , self.width, pix.height())
        bottom.setBrush(brush)
        bottom.name = 'bottom'
        self.addItem(bottom)
        
    def setObstacles(self):
        # x, y, width and height are percentages of the arena.
        layout = [
            ("central", 0.46, 0.28, 0.08, 0.44),
            ("upper_left", 0.16, 0.18, 0.22, 0.08),
            ("lower_right", 0.62, 0.74, 0.22, 0.08),
        ]

        for obstacle_id, rx, ry, rw, rh in layout:
            obstacle = Obstacle(
                obstacle_id,
                self.width * rx,
                self.height * ry,
                self.width * rw,
                self.height * rh,
            )
            self.obstacles.append(obstacle)
            self.addItem(obstacle)

    def isRadarBlocked(self, start, end):
        sight_line = QLineF(start, end)

        for obstacle in self.obstacles:
            if not obstacle.blocks_radar:
                continue

            rect = obstacle.sceneBoundingRect()
            edges = (
                QLineF(rect.topLeft(), rect.topRight()),
                QLineF(rect.topRight(), rect.bottomRight()),
                QLineF(rect.bottomRight(), rect.bottomLeft()),
                QLineF(rect.bottomLeft(), rect.topLeft()),
            )

            for edge in edges:
                intersection_type, _ = sight_line.intersects(edge)
                if intersection_type == QLineF.IntersectionType.BoundedIntersection:
                    return True

        return False

    def getGrid(self):
        w = int(self.width / 80)
        h = int(self.height / 80)
        positions = []

        robot_size = 60
        safety_margin = 12

        for i in range(w):
            for j in range(h):
                x = (i + 0.5) * 80
                y = (j + 0.5) * 80

                spawn_area = QRectF(x, y, robot_size, robot_size).adjusted(
                    -safety_margin,
                    -safety_margin,
                    safety_margin,
                    safety_margin,
                )

                blocked = any(
                    spawn_area.intersects(obstacle.sceneBoundingRect())
                    for obstacle in self.obstacles
                )

                if not blocked:
                    positions.append(QPointF(x, y))

        return positions
