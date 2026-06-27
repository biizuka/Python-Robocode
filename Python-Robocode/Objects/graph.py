#! /usr/bin/python
# -*- coding: utf-8 -*-

import math
import os
import random
import time

from PyQt6.QtWidgets import QGraphicsScene, QMessageBox, QGraphicsRectItem
from PyQt6.QtGui import QPixmap, QBrush
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF

from robot import Robot
from obstacle import Obstacle
from arena_layouts import (
    GRID_STEP,
    ROBOT_SIZE,
    SPAWN_SAFETY_MARGIN,
    count_free_spawn_positions,
    get_compatible_layout_names,
    get_layout,
    get_layout_names,
)
from battle_rules import describe_battle_rules, normalize_battle_rules


class Graph(QGraphicsScene):

    def __init__(
        self,
        parent,
        width,
        height,
        layout_name=None,
        seed=None,
        required_spawn_positions=1,
        battle_rules=None,
    ):
        QGraphicsScene.__init__(self, parent)
        self.setSceneRect(0, 0, width, height)
        self.Parent = parent

        self.width = width
        self.height = height
        self.obstacles = []
        self.requiredSpawnPositions = required_spawn_positions
        self.battleRules = normalize_battle_rules(battle_rules)

        self.aliveBots = []
        self.deadBots = []
        self.battleEnded = False
        self.lastBattleFinishReason = None
        self.battleStartTime = None
        self.lastDisplayedSecond = None
        self.timeoutTieBreakers = {}

        # A dedicated generator makes the selected layout, spawn positions,
        # and timeout tie-breakers reproducible when the same seed is used.
        if seed is None:
            seed = random.SystemRandom().randrange(0, 2 ** 32)

        self.layoutSeed = seed
        self.randomGenerator = random.Random(seed)
        self.layoutName = self.__selectLayout(layout_name)

        self.setTiles()
        self.setObstacles()
        self.grid = self.getGrid()

        message = "Arena layout: {} | battle seed: {}".format(
            self.layoutName,
            self.layoutSeed,
        )
        print(message)
        print("Battle rules: {}".format(describe_battle_rules(self.battleRules)))
        self.__showStatus(message)

    def AddRobots(self, botList):
        """Create and place all robots in valid arena positions."""
        self.aliveBots = []
        self.deadBots = []
        self.timeoutTieBreakers = {}

        try:
            posList = self.randomGenerator.sample(self.grid, len(botList))

            for bot in botList:
                try:
                    robot = bot(self.sceneRect().size(), self, str(bot))
                    self.aliveBots.append(robot)
                    self.addItem(robot)
                    robot.setPos(posList.pop())

                    # Used only when every other timeout criterion is tied.
                    self.timeoutTieBreakers[id(robot)] = self.randomGenerator.random()

                    self.Parent.addRobotInfo(robot)
                except Exception as error:
                    print("Problem with bot file '{}': {}".format(bot, str(error)))

            try:
                self.Parent.battleMenu.close()
            except AttributeError:
                pass

        except ValueError:
            QMessageBox.about(
                self.Parent,
                "Alert",
                "Too many Bots for the map's size!",
            )

    def advance(self):
        """Advance the scene and enforce time and inactivity rules."""
        if self.battleEnded:
            return

        now = time.monotonic()

        # Start the clock only when the first simulation frame is executed.
        # Loading the arena and creating widgets do not consume battle time.
        if self.battleStartTime is None:
            self.battleStartTime = now
            for robot in self.aliveBots:
                robot.resetActivityTimer(now)
            self.__updateStatus(now, force=True)

        QGraphicsScene.advance(self)

        # A robot death may have finished the battle during scene advancement.
        if self.battleEnded:
            return

        now = time.monotonic()
        elapsed = now - self.battleStartTime
        time_limit = self.battleRules["time_limit_seconds"]

        if time_limit > 0 and elapsed >= time_limit:
            print("Battle time limit reached after {} seconds.".format(time_limit))
            self.battleFinished("time_limit")
            return

        self.__applyInactivityPenalties(now)
        self.__updateStatus(now)

    def __applyInactivityPenalties(self, now):
        timeout = self.battleRules["inactivity_timeout_seconds"]
        if timeout == 0:
            return

        interval = self.battleRules["inactivity_penalty_interval_seconds"]
        damage = self.battleRules["inactivity_damage"]

        for robot in list(self.aliveBots):
            if robot.shouldReceiveInactivityPenalty(now, timeout, interval):
                idle_seconds = robot.getIdleDuration(now)
                robot.applyInactivityPenalty(damage, idle_seconds, now)

    def __updateStatus(self, now, force=False):
        if self.battleStartTime is None:
            return

        elapsed = now - self.battleStartTime
        time_limit = self.battleRules["time_limit_seconds"]

        if time_limit == 0:
            display_second = int(elapsed)
            time_text = "unlimited"
        else:
            remaining = max(0, int(math.ceil(time_limit - elapsed)))
            display_second = remaining
            minutes, seconds = divmod(remaining, 60)
            time_text = "{:02d}:{:02d}".format(minutes, seconds)

        if not force and display_second == self.lastDisplayedSecond:
            return

        self.lastDisplayedSecond = display_second

        inactivity_timeout = self.battleRules["inactivity_timeout_seconds"]
        if inactivity_timeout == 0:
            inactivity_text = "idle penalty off"
        else:
            inactivity_text = "idle {}s / -{} HP".format(
                inactivity_timeout,
                self.battleRules["inactivity_damage"],
            )

        self.__showStatus(
            "Arena: {} | Time left: {} | {}".format(
                self.layoutName,
                time_text,
                inactivity_text,
            )
        )

    def __showStatus(self, message):
        try:
            self.Parent.statusBar().showMessage(message)
            return
        except (AttributeError, RuntimeError):
            pass

        try:
            self.Parent.statusbar.showMessage(message)
        except (AttributeError, RuntimeError):
            pass

    def __rankRemainingRobots(self):
        """Return remaining robots from worst to best for final placement."""
        return sorted(
            self.aliveBots,
            key=lambda robot: (
                robot.getHealth(),
                robot.getKills(),
                -robot.getInactivityPenalties(),
                self.timeoutTieBreakers.get(id(robot), 0.0),
            ),
        )

    def killAllRobots(self):
        """Remove all robots while preserving a deterministic placement."""
        print("kill all robots")

        try:
            for robot in self.__rankRemainingRobots():
                self.deadBots.append(robot)
                self.removeItem(robot)
            self.aliveBots = []
        except Exception:
            pass

    def battleFinished(self, reason="last_robot"):
        """Finish a battle and update tournament statistics."""
        if self.battleEnded:
            return

        self.battleEnded = True
        self.lastBattleFinishReason = reason

        try:
            self.Parent.timer.stop()
        except (AttributeError, RuntimeError):
            pass

        # A normal battle has one survivor. A timeout or manual termination
        # can leave several robots, which are ranked by health, kills, and
        # inactivity penalties.
        for robot in self.__rankRemainingRobots():
            self.deadBots.append(robot)
            try:
                self.removeItem(robot)
            except RuntimeError:
                pass

        self.aliveBots = []

        reason_labels = {
            "last_robot": "last robot standing",
            "time_limit": "time limit reached",
            "terminated": "manually terminated",
        }
        reason_text = reason_labels.get(reason, reason)
        print("battle terminated: {}".format(reason_text))

        total_robots = len(self.deadBots)

        for index, robot in enumerate(self.deadBots):
            place = total_robots - index
            print("N° {}: {}".format(place, robot))

            stats = self.Parent.statisticDico[repr(robot)]

            if place == 1:
                stats.first += 1
            if place == 2:
                stats.second += 1
            if place == 3:
                stats.third += 1

            stats.points += index
            stats.kills += robot.getKills()
            stats.idlePenalties += robot.getInactivityPenalties()

        self.__showStatus("Battle finished: {}".format(reason_text))
        self.Parent.chooseAction()

    def setTiles(self):
        # Background
        brush = QBrush()
        pix = QPixmap(os.getcwd() + "/robotImages/tile.png")
        brush.setTexture(pix)
        brush.setStyle(Qt.BrushStyle.TexturePattern)
        self.setBackgroundBrush(brush)

        # Left wall
        left = QGraphicsRectItem()
        pix = QPixmap(os.getcwd() + "/robotImages/tileVert.png")
        left.setRect(QRectF(0, 0, pix.width(), self.height))
        brush.setTexture(pix)
        brush.setStyle(Qt.BrushStyle.TexturePattern)
        left.setBrush(brush)
        left.name = "left"
        self.addItem(left)

        # Right wall
        right = QGraphicsRectItem()
        right.setRect(self.width - pix.width(), 0, pix.width(), self.height)
        right.setBrush(brush)
        right.name = "right"
        self.addItem(right)

        # Top wall
        top = QGraphicsRectItem()
        pix = QPixmap(os.getcwd() + "/robotImages/tileHori.png")
        top.setRect(QRectF(0, 0, self.width, pix.height()))
        brush.setTexture(pix)
        brush.setStyle(Qt.BrushStyle.TexturePattern)
        top.setBrush(brush)
        top.name = "top"
        self.addItem(top)

        # Bottom wall
        bottom = QGraphicsRectItem()
        bottom.setRect(0, self.height - pix.height(), self.width, pix.height())
        bottom.setBrush(brush)
        bottom.name = "bottom"
        self.addItem(bottom)

    def __selectLayout(self, layout_name):
        available_layouts = get_layout_names()
        compatible_layouts = get_compatible_layout_names(
            self.width,
            self.height,
            self.requiredSpawnPositions,
        )

        if layout_name is None:
            if not compatible_layouts:
                raise ValueError(
                    "No arena layout has enough spawn positions for "
                    "{} robots in a {}x{} arena.".format(
                        self.requiredSpawnPositions,
                        self.width,
                        self.height,
                    )
                )

            return self.randomGenerator.choice(compatible_layouts)

        if layout_name not in available_layouts:
            available = ", ".join(available_layouts)
            raise ValueError(
                "Unknown arena layout '{}'. Available layouts: {}".format(
                    layout_name,
                    available,
                )
            )

        if layout_name not in compatible_layouts:
            free_positions = count_free_spawn_positions(
                layout_name,
                self.width,
                self.height,
            )
            raise ValueError(
                "Arena layout '{}' has {} valid spawn positions, but "
                "the battle requires {}.".format(
                    layout_name,
                    free_positions,
                    self.requiredSpawnPositions,
                )
            )

        return layout_name

    def getLayoutName(self):
        return self.layoutName

    def getLayoutSeed(self):
        return self.layoutSeed

    def setObstacles(self):
        # x, y, width, and height are percentages of the arena.
        layout = get_layout(self.layoutName)

        for obstacle_id, relative_x, relative_y, relative_width, relative_height in layout:
            obstacle = Obstacle(
                obstacle_id,
                self.width * relative_x,
                self.height * relative_y,
                self.width * relative_width,
                self.height * relative_height,
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
        columns = int(self.width / GRID_STEP)
        rows = int(self.height / GRID_STEP)
        positions = []

        for column in range(columns):
            for row in range(rows):
                x = (column + 0.5) * GRID_STEP
                y = (row + 0.5) * GRID_STEP

                spawn_area = QRectF(x, y, ROBOT_SIZE, ROBOT_SIZE).adjusted(
                    -SPAWN_SAFETY_MARGIN,
                    -SPAWN_SAFETY_MARGIN,
                    SPAWN_SAFETY_MARGIN,
                    SPAWN_SAFETY_MARGIN,
                )

                blocked = any(
                    spawn_area.intersects(obstacle.sceneBoundingRect())
                    for obstacle in self.obstacles
                )

                if not blocked:
                    positions.append(QPointF(x, y))

        return positions
