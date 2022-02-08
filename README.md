# Poom

Yandex.Lyceum PyGame project

First-person Shooter, the main goal of which is to clear the location from zombies.
There are 3 maps. CPU-bound operations have been implemented in Cython, which has significantly increased fps.

In general, it is a mini 3D engine. You can change sprites, textures, sounds and other parameters and get new games.

https://user-images.githubusercontent.com/64976988/153035366-880515ec-1caf-47a9-8c47-831d29cf9faa.mp4

## Installing 💾

You can install source and some precompiled libraries from [here](https://github.com/xDiaym/poom/releases/tag/v1.0.1)

- Choose your platform and version
- Unzip the files
- Put precompiled files into ./poom/pooma
- Play

## Build 🛠️

> On Windows you may need MSVC to compile Cython.
>
> You can load Build Tools from [here](https://docs.microsoft.com/en-us/visualstudio/releases/2022/release-history#release-dates-and-build-numbers)
>
> - Choose *Desktop development with C++*
>
> - 💡 Don't forget to tick *Windows SDK* on installing

```sh
git clone git@github.com:xDiaym/poom.git
cd poom
pip install -r requirements.txt
python setup.py build_ext --inplace
```

## Control 🕹️

|    Key    | Action        |
|:---------:|:--------------|
| `W`       | Move forward  |
| `A`       | Rotate left   |
| `S`       | Move backward |
| `D`       | Rotate right  |
| `<`       | Move left     |
| `>`       | Move right    |
| `<space>` | Shoot         |
