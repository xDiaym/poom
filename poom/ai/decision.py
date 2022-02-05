from math import atan2

from poom.ai.actions import AbstractAction, AStarChaseAction, AttackAction, DieAction
from poom.ai.intelligent import AbstractIntelligent


def make_decision(owner: AbstractIntelligent) -> AbstractAction:
    direction = owner.enemy.position - owner.position
    angle = atan2(direction.y, direction.x)
    owner.rotate_to(angle)

    if owner.get_health() <= 0:
        return DieAction(owner)
    if owner.can_cause_damage():
        return AttackAction(owner, owner.enemy.position)
    # if owner.wall_nearby:
    #     return DiagonalChaseAction(owner)
    return AStarChaseAction(owner)
