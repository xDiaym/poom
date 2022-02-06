from math import atan2

from poom.ai.actions import (
    AbstractAction,
    AStarChaseAction,
    AttackAction,
    DiagonalChaseAction,
    DieAction,
)
from poom.ai.intelligent import AbstractIntelligent


def make_decision(owner: AbstractIntelligent) -> AbstractAction:
    direction = owner.enemy.position - owner.position
    angle = atan2(direction.y, direction.x)
    owner.rotate_to(angle)
    owner.whether_shoot = not owner.whether_shoot
    if owner.get_health() <= 0:
        return DieAction(owner)
    elif owner.can_cause_damage() and (owner.whether_shoot or owner.player_nearby):
        return AttackAction(owner, owner.enemy.position)
    elif not owner.wall_nearby:
        return DiagonalChaseAction(owner)
    return AStarChaseAction(owner)
