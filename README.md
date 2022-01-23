# poom

Like doom, but in python

Шутер от 1 лица, главная цель которого зачистить локацию от противников.
Особенность проекта - наличие зеркал, которые отражают как окружение, так и снаряды.
Поддерживается мультиплеер.

FPS, the main goal of which is to clear the location from opponents.
A feature of the project is the presence of mirrors that reflect both the environment and the projectiles.
Multiplayer is supported.

## Build

```console
git clone git@github.com:xDiaym/poom.git
cd poom
pip install -r requirements.txt
python setup.py build_ext --inplace
```

## Control
|    Key    | Action        |
|:---------:|:--------------|
| `W`       | Move forward  |
| `A`       | Rotate left   |
| `S`       | Mova backward |
| `D`       | Rotate right  |
| `<`       | Move left     |
| `>`       | Move right    |
| `<space>` | Shoot         |
