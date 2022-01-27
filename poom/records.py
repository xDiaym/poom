import json
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any, Optional


@dataclass
class Record:
    game_time: float  # UNIX delta time
    health: float

    def merge_best(self, other: "Record") -> None:
        self.game_time = min(self.game_time, other.game_time)
        self.health = max(self.health, other.health)


class JsonRecordEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Record):
            return {
                "game_time": o.game_time,  # Time in s
                "health": o.health,
            }
        return super().default(o)


def has_record(path: Path) -> bool:
    return path.exists()


def load_record(path: Path) -> Optional[Record]:
    if not has_record(path):
        return None
    with open(path, "r") as fp:
        raw_record = json.load(fp)
    return Record(
        game_time=float(raw_record["game_time"]),
        health=float(raw_record["health"]),
    )


def save_record(path: Path, record: Record) -> None:
    with open(path, "w") as fp:
        json.dump(record, fp, cls=JsonRecordEncoder)


def update_record(path: Path, new_record: Record) -> None:
    if has_record(path):  # TODO: TypeGuard
        old_record = load_record(path)
        assert old_record, "Old record can't be None here."
        new_record.merge_best(old_record)
    save_record(path, new_record)
