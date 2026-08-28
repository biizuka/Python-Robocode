#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Battle rule defaults and validation helpers."""


DEFAULT_BATTLE_RULES = {
    # Zero disables the battle time limit.
    "time_limit_seconds": 180,

    # Zero disables inactivity penalties.
    "inactivity_timeout_seconds": 15,

    # After the first inactivity penalty, apply another one at this interval.
    "inactivity_penalty_interval_seconds": 5,

    # Health removed on each inactivity penalty.
    "inactivity_damage": 2,
}


def _as_non_negative_integer(value, key):
    try:
        result = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError("Battle rule '{}' must be an integer.".format(key)) from error

    if result < 0:
        raise ValueError("Battle rule '{}' cannot be negative.".format(key))

    return result


def normalize_battle_rules(rules=None):
    """Return a validated battle-rule dictionary with all required keys."""
    normalized = dict(DEFAULT_BATTLE_RULES)

    if rules:
        for key in DEFAULT_BATTLE_RULES:
            if key in rules:
                normalized[key] = _as_non_negative_integer(rules[key], key)

    if (
        normalized["inactivity_timeout_seconds"] > 0
        and normalized["inactivity_penalty_interval_seconds"] == 0
    ):
        raise ValueError(
            "The inactivity penalty interval must be greater than zero "
            "when inactivity penalties are enabled."
        )

    return normalized


def describe_battle_rules(rules):
    """Return a compact human-readable rule description."""
    rules = normalize_battle_rules(rules)

    if rules["time_limit_seconds"] == 0:
        duration_text = "no time limit"
    else:
        duration_text = "{} s time limit".format(rules["time_limit_seconds"])

    if rules["inactivity_timeout_seconds"] == 0:
        inactivity_text = "inactivity penalty disabled"
    else:
        inactivity_text = (
            "inactivity after {} s: -{} HP every {} s"
        ).format(
            rules["inactivity_timeout_seconds"],
            rules["inactivity_damage"],
            rules["inactivity_penalty_interval_seconds"],
        )

    return "{} | {}".format(duration_text, inactivity_text)
