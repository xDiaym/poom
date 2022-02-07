from copy import copy
from functools import cache, wraps
from pathlib import Path
from typing import Callable, ParamSpec, TypeVar

import pygame as pg

from poom.animated import Animation, Clonable
from poom.settings import ROOT

RetT = TypeVar("RetT", bound=Clonable)
PS = ParamSpec("PS")


def clone(fn: Callable[PS, RetT]) -> Callable[PS, RetT]:
    """Clone result of function.

    :param fn: function
    :return: wrapped function
    """

    @wraps(fn)
    def wrapper(*args: PS.args, **kwargs: PS.kwargs) -> RetT:
        return fn(*args, **kwargs).clone()

    return wrapper


class LazyAnimationLoader:
    def __init__(self, path: Path) -> None:
        self._path = path

    @clone
    @cache
    def get(self, name: str, speed: float, scale: float = 1) -> Animation:
        return Animation.from_dir(self._path / name, speed, scale)


class LazySoundLoader:
    def __init__(self, path) -> None:
        self._path = path

    @cache
    def get(self, name: str) -> pg.mixer.Sound:
        return pg.mixer.Sound(self._path / name)


class Resources:
    def __init__(self, root: Path) -> None:
        self._animation = LazyAnimationLoader(root / "sprites")
        self._sound = LazySoundLoader(root / "sounds")

    @property
    def animation(self) -> LazyAnimationLoader:
        return self._animation

    @property
    def sound(self) -> LazySoundLoader:
        return self._sound


R = Resources(ROOT / "assets")  # noqa WPS111: shortcut for resources
