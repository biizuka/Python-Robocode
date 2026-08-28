#! /usr/bin/python
#-*- coding: utf-8 -*-

from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtGui import QColor, QBrush, QPen
from PyQt6.QtCore import QRectF


class Obstacle(QGraphicsRectItem):
    """Solid arena object that can block robots, bullets and radar."""

    def __init__(self, obstacle_id, x, y, width, height,
                 blocks_bullets=True, blocks_radar=True):
        super().__init__(QRectF(x, y, width, height))

        self.obstacle_id = obstacle_id
        self.blocks_bullets = blocks_bullets
        self.blocks_radar = blocks_radar

        self.setBrush(QBrush(QColor(70, 74, 82)))
        self.setPen(QPen(QColor(185, 190, 200), 2))
        self.setZValue(5)
