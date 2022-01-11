import numpy
from setuptools import setup
from setuptools.extension import Extension

from Cython.Build import cythonize  # isort: skip strange build system bug


def read(filename: str) -> str:
    with open(filename, "r", encoding="utf8") as fp:
        return fp.read()


extensions = [
    Extension(
        name="poom.pooma.ray_march",
        sources=["poom/pooma/ray_march.pyx"],
    ),
    Extension(name="poom.pooma.math", sources=["poom/pooma/math.pyx"]),
]

setup(
    name="poom",
    description=read("README.md"),
    ext_modules=cythonize(extensions, language_level=3),
    include_dirs=numpy.get_include(),
)
