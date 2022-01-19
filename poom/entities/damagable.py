"""Interface for everything with health."""
from abc import ABC, abstractmethod


# ??? Can be protocol?
class Damagable(ABC):
    """Interface for evrything, that has health."""

    @abstractmethod
    def take_damge(self, damage: float) -> None:
        """Decrease health.

        :param damage: damage by which health is reduced
        """
