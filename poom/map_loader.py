from pathlib import Path

from poom.map import Map


class MapLoader:
    def __init__(self, root: Path) -> None:
        self._root = root

    def load(self, number: int) -> Map:
        path = self._root / str(number) / "map.txt"
        with open(path) as fp:
            content = fp.read()
        return Map(content.split("\n"))
