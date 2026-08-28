# -*- coding: utf-8 -*-

"""Initial battle settings dialog shown before robot selection."""

import os
import pickle

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
)

from battle_rules import DEFAULT_BATTLE_RULES, normalize_battle_rules


class BattleSettings(QDialog):
    """Collect arena and battle-rule settings before selecting robots."""

    def __init__(self, parent=None, initial_configuration=None):
        super().__init__(parent)
        self.window = parent

        self.setWindowTitle("Battle Settings")
        self.setWindowIcon(QIcon(QPixmap("robotImages/smallgrey.png")))
        self.setModal(True)
        self.setMinimumWidth(500)

        configuration = self.__loadInitialConfiguration(initial_configuration)
        battle_rules = normalize_battle_rules(configuration.get("battleRules"))

        main_layout = QVBoxLayout(self)

        introduction = QLabel(
            "Configure the arena and tournament rules. "
            "Robot selection will be shown in the next step.",
            self,
        )
        introduction.setWordWrap(True)
        main_layout.addWidget(introduction)

        arena_group = QGroupBox("Arena and Tournament", self)
        arena_layout = QFormLayout(arena_group)

        size_row = QHBoxLayout()

        self.widthSpinBox = QSpinBox(arena_group)
        self.widthSpinBox.setRange(300, 100000)
        self.widthSpinBox.setSuffix(" px")
        self.widthSpinBox.setValue(int(configuration.get("width", 700)))

        self.heightSpinBox = QSpinBox(arena_group)
        self.heightSpinBox.setRange(300, 100000)
        self.heightSpinBox.setSuffix(" px")
        self.heightSpinBox.setValue(int(configuration.get("height", 500)))

        size_row.addWidget(self.widthSpinBox)
        size_row.addWidget(QLabel("×", arena_group))
        size_row.addWidget(self.heightSpinBox)

        self.battleCountSpinBox = QSpinBox(arena_group)
        self.battleCountSpinBox.setRange(1, 10000)
        self.battleCountSpinBox.setValue(
            int(configuration.get("battleCount", self.__currentBattleCount()))
        )

        arena_layout.addRow("Arena size:", size_row)
        arena_layout.addRow("Number of battles:", self.battleCountSpinBox)
        main_layout.addWidget(arena_group)

        rules_group = QGroupBox("Battle Rules", self)
        rules_layout = QFormLayout(rules_group)

        self.battleDurationSpinBox = QSpinBox(rules_group)
        self.battleDurationSpinBox.setRange(0, 3600)
        self.battleDurationSpinBox.setSuffix(" s")
        self.battleDurationSpinBox.setSpecialValueText("No limit")
        self.battleDurationSpinBox.setValue(
            battle_rules["time_limit_seconds"]
        )

        self.inactivityTimeoutSpinBox = QSpinBox(rules_group)
        self.inactivityTimeoutSpinBox.setRange(0, 600)
        self.inactivityTimeoutSpinBox.setSuffix(" s")
        self.inactivityTimeoutSpinBox.setSpecialValueText("Disabled")
        self.inactivityTimeoutSpinBox.setValue(
            battle_rules["inactivity_timeout_seconds"]
        )

        self.inactivityIntervalSpinBox = QSpinBox(rules_group)
        self.inactivityIntervalSpinBox.setRange(1, 600)
        self.inactivityIntervalSpinBox.setSuffix(" s")
        self.inactivityIntervalSpinBox.setValue(
            battle_rules["inactivity_penalty_interval_seconds"]
        )

        self.inactivityDamageSpinBox = QSpinBox(rules_group)
        self.inactivityDamageSpinBox.setRange(1, 100)
        self.inactivityDamageSpinBox.setSuffix(" HP")
        self.inactivityDamageSpinBox.setValue(
            battle_rules["inactivity_damage"]
        )

        rules_layout.addRow("Battle duration:", self.battleDurationSpinBox)
        rules_layout.addRow("Inactive after:", self.inactivityTimeoutSpinBox)
        rules_layout.addRow("Penalty interval:", self.inactivityIntervalSpinBox)
        rules_layout.addRow("Penalty damage:", self.inactivityDamageSpinBox)

        inactivity_help = QLabel(
            "A robot is active when it moves, rotates, scans, or fires.",
            rules_group,
        )
        inactivity_help.setWordWrap(True)
        inactivity_help.setStyleSheet("color: #666;")
        rules_layout.addRow("", inactivity_help)

        main_layout.addWidget(rules_group)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Ok,
            Qt.Orientation.Horizontal,
            self,
        )
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setText(
            "Next: Select Robots"
        )
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        main_layout.addWidget(self.buttonBox)

        self.inactivityTimeoutSpinBox.valueChanged.connect(
            self.__updateInactivityControls
        )
        self.__updateInactivityControls(self.inactivityTimeoutSpinBox.value())

    def __currentBattleCount(self):
        try:
            return self.window.spinBox_battle_num.value()
        except (AttributeError, RuntimeError):
            return 10

    def __loadInitialConfiguration(self, initial_configuration):
        if initial_configuration:
            return dict(initial_configuration)

        configuration = {
            "width": 700,
            "height": 500,
            "battleCount": self.__currentBattleCount(),
            "battleRules": dict(DEFAULT_BATTLE_RULES),
        }

        arena_path = os.path.join(os.getcwd(), ".datas", "lastArena")
        if not os.path.exists(arena_path):
            return configuration

        try:
            with open(arena_path, "rb") as file:
                previous = pickle.Unpickler(file).load()

            configuration.update({
                "width": previous.get("width", configuration["width"]),
                "height": previous.get("height", configuration["height"]),
                "battleCount": previous.get(
                    "battleCount",
                    configuration["battleCount"],
                ),
                "battleRules": previous.get(
                    "battleRules",
                    configuration["battleRules"],
                ),
            })
        except Exception as error:
            print("Could not load previous battle settings: {}".format(error))

        return configuration

    def __updateInactivityControls(self, timeout):
        enabled = timeout > 0
        self.inactivityIntervalSpinBox.setEnabled(enabled)
        self.inactivityDamageSpinBox.setEnabled(enabled)

    def getConfiguration(self):
        """Return a validated configuration dictionary."""
        return {
            "width": self.widthSpinBox.value(),
            "height": self.heightSpinBox.value(),
            "battleCount": self.battleCountSpinBox.value(),
            "battleRules": normalize_battle_rules({
                "time_limit_seconds": self.battleDurationSpinBox.value(),
                "inactivity_timeout_seconds": self.inactivityTimeoutSpinBox.value(),
                "inactivity_penalty_interval_seconds": self.inactivityIntervalSpinBox.value(),
                "inactivity_damage": self.inactivityDamageSpinBox.value(),
            }),
        }
