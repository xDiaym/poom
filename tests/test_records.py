from datetime import timedelta
from pathlib import Path

import pytest

from poom.records import Record, load_record, save_record, update_record


@pytest.fixture
def record_file(tmp_path: Path) -> Path:
    file = tmp_path / "update_record.json"
    with open(file, "w") as fp:
        fp.write('{"game_time": 42.0, "health": 10}')
    return file


def test_record_merge_best() -> None:
    old = Record(game_time=42, health=10)
    new = Record(game_time=10, health=42)
    old.merge_best(new)
    assert old.game_time == 10
    assert old.health == 42


def test_load_record(record_file: Path) -> None:
    record = load_record(record_file)
    assert record.game_time == 42
    assert record.health == 10


def test_write_record(tmp_path: Path) -> None:
    file = tmp_path / "write_record.json"
    record = Record(game_time=42, health=42)
    save_record(file, record)

    with open(file, "r") as fp:
        content = fp.read()
    assert content == '{"game_time": 42, "health": 42}'


def test_update_record(record_file: Path) -> None:
    new = Record(game_time=10, health=42)

    update_record(record_file, new)

    with open(record_file, "r") as fp:
        content = fp.read()
    assert content == '{"game_time": 10, "health": 42}'
