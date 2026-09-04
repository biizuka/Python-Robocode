#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Obstacle layouts used by the battle arena.

All coordinates are relative to the arena size and use the format:
    (obstacle_id, x, y, width, height)

The values must remain between 0.0 and 1.0.
"""


GRID_STEP = 80
ROBOT_SIZE = 60
SPAWN_SAFETY_MARGIN = 12


ARENA_LAYOUTS = {
    # Baseline map. It is also a safe fallback for very small arenas.
    "open_field": [],

    "classic": [
        ("central", 0.46, 0.28, 0.08, 0.44),
        ("upper_left", 0.16, 0.18, 0.22, 0.08),
        ("lower_right", 0.62, 0.74, 0.22, 0.08),
    ],

    "crossroads": [
        ("north_gate", 0.47, 0.12, 0.06, 0.28),
        ("south_gate", 0.47, 0.60, 0.06, 0.28),
        ("west_gate", 0.12, 0.47, 0.28, 0.06),
        ("east_gate", 0.60, 0.47, 0.28, 0.06),
    ],

    "four_pillars": [
        ("north_west", 0.20, 0.20, 0.12, 0.16),
        ("north_east", 0.68, 0.20, 0.12, 0.16),
        ("south_west", 0.20, 0.64, 0.12, 0.16),
        ("south_east", 0.68, 0.64, 0.12, 0.16),
    ],

    "corridors": [
        ("west_wall", 0.27, 0.16, 0.07, 0.56),
        ("east_wall", 0.66, 0.28, 0.07, 0.56),
        ("middle_cover", 0.43, 0.45, 0.14, 0.08),
    ],

    "fortress": [
        ("fortress_north", 0.35, 0.32, 0.30, 0.06),
        ("fortress_south", 0.35, 0.62, 0.30, 0.06),
        ("fortress_west", 0.35, 0.38, 0.06, 0.18),
        ("fortress_east", 0.59, 0.44, 0.06, 0.18),
    ],

    # Two long pieces of cover create three major movement lanes.
    "twin_towers": [
        ("west_tower", 0.28, 0.24, 0.09, 0.52),
        ("east_tower", 0.63, 0.24, 0.09, 0.52),
    ],

    # The center is open, but the north and south routes are divided.
    "split_gate": [
        ("north_divider", 0.47, 0.08, 0.06, 0.30),
        ("south_divider", 0.47, 0.62, 0.06, 0.30),
        ("west_cover", 0.15, 0.45, 0.18, 0.08),
        ("east_cover", 0.67, 0.47, 0.18, 0.08),
    ],

    # Alternating barriers require repeated changes of direction.
    "zigzag": [
        ("upper_barrier", 0.10, 0.20, 0.48, 0.07),
        ("middle_barrier", 0.42, 0.46, 0.48, 0.07),
        ("lower_barrier", 0.10, 0.72, 0.48, 0.07),
    ],

    # Small independent covers keep long lines of sight between them.
    "islands": [
        ("north_west_island", 0.15, 0.18, 0.11, 0.13),
        ("north_east_island", 0.74, 0.18, 0.11, 0.13),
        ("central_island", 0.44, 0.43, 0.12, 0.14),
        ("south_west_island", 0.15, 0.69, 0.11, 0.13),
        ("south_east_island", 0.74, 0.69, 0.11, 0.13),
    ],

    # Two side bunkers provide protected areas without closing the center.
    "side_bunkers": [
        ("left_back", 0.16, 0.28, 0.06, 0.44),
        ("left_top", 0.22, 0.28, 0.16, 0.06),
        ("left_bottom", 0.22, 0.66, 0.16, 0.06),
        ("right_back", 0.78, 0.28, 0.06, 0.44),
        ("right_top", 0.62, 0.28, 0.16, 0.06),
        ("right_bottom", 0.62, 0.66, 0.16, 0.06),
    ],

    # Long firing lanes alternate between the left and right sides.
    "sniper_lanes": [
        ("lane_one", 0.08, 0.24, 0.34, 0.06),
        ("lane_two", 0.58, 0.42, 0.34, 0.06),
        ("lane_three", 0.08, 0.60, 0.34, 0.06),
        ("lane_four", 0.58, 0.78, 0.34, 0.06),
    ],

    # Five blocks form a diamond-shaped sequence of hiding positions.
    "diamond_cover": [
        ("diamond_north", 0.45, 0.16, 0.10, 0.12),
        ("diamond_west", 0.24, 0.44, 0.10, 0.12),
        ("diamond_center", 0.45, 0.44, 0.10, 0.12),
        ("diamond_east", 0.66, 0.44, 0.10, 0.12),
        ("diamond_south", 0.45, 0.72, 0.10, 0.12),
    ],

    # A compact spiral creates a protected path toward the center.
    "spiral": [
        ("spiral_top", 0.28, 0.25, 0.44, 0.06),
        ("spiral_right", 0.66, 0.31, 0.06, 0.38),
        ("spiral_bottom", 0.38, 0.63, 0.28, 0.06),
        ("spiral_left", 0.32, 0.43, 0.06, 0.20),
        ("spiral_core", 0.44, 0.43, 0.16, 0.06),
    ],

    # Four pieces of cover point toward an open central combat area.
    "open_wings": [
        ("west_wing", 0.16, 0.35, 0.22, 0.08),
        ("east_wing", 0.62, 0.57, 0.22, 0.08),
        ("north_wing", 0.46, 0.16, 0.08, 0.18),
        ("south_wing", 0.46, 0.66, 0.08, 0.18),
    ],

    # Several horizontal bridges create alternating gaps and ambush points.
    "three_bridges": [
        ("north_west_bridge", 0.12, 0.24, 0.28, 0.06),
        ("north_east_bridge", 0.60, 0.24, 0.28, 0.06),
        ("central_bridge", 0.35, 0.47, 0.30, 0.06),
        ("south_west_bridge", 0.12, 0.70, 0.28, 0.06),
        ("south_east_bridge", 0.60, 0.70, 0.28, 0.06),
    ],
}


def get_layout_names():
    """Return the available layout names in a stable order."""
    return tuple(ARENA_LAYOUTS.keys())


def get_layout(layout_name):
    """Return a copy of a layout to prevent accidental modification."""
    try:
        return list(ARENA_LAYOUTS[layout_name])
    except KeyError as error:
        available = ", ".join(get_layout_names())
        raise ValueError(
            "Unknown arena layout '{}'. Available layouts: {}".format(
                layout_name,
                available,
            )
        ) from error


def _rectangles_intersect(first, second):
    """Return whether two rectangles overlap."""
    first_x, first_y, first_width, first_height = first
    second_x, second_y, second_width, second_height = second

    return (
        first_x < second_x + second_width
        and first_x + first_width > second_x
        and first_y < second_y + second_height
        and first_y + first_height > second_y
    )


def count_free_spawn_positions(layout_name, arena_width, arena_height):
    """Count valid robot spawn positions for an arena and layout."""
    obstacles = [
        (
            arena_width * relative_x,
            arena_height * relative_y,
            arena_width * relative_width,
            arena_height * relative_height,
        )
        for (
            _obstacle_id,
            relative_x,
            relative_y,
            relative_width,
            relative_height,
        ) in get_layout(layout_name)
    ]

    free_positions = 0
    columns = int(arena_width / GRID_STEP)
    rows = int(arena_height / GRID_STEP)

    for column in range(columns):
        for row in range(rows):
            x = (column + 0.5) * GRID_STEP
            y = (row + 0.5) * GRID_STEP

            spawn_area = (
                x - SPAWN_SAFETY_MARGIN,
                y - SPAWN_SAFETY_MARGIN,
                ROBOT_SIZE + 2 * SPAWN_SAFETY_MARGIN,
                ROBOT_SIZE + 2 * SPAWN_SAFETY_MARGIN,
            )

            if not any(
                _rectangles_intersect(spawn_area, obstacle)
                for obstacle in obstacles
            ):
                free_positions += 1

    return free_positions


def get_compatible_layout_names(
    arena_width,
    arena_height,
    required_spawn_positions=1,
):
    """Return layouts with enough valid positions for all robots."""
    return tuple(
        layout_name
        for layout_name in get_layout_names()
        if count_free_spawn_positions(
            layout_name,
            arena_width,
            arena_height,
        ) >= required_spawn_positions
    )
