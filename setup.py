import numpy
from setuptools import setup
from setuptools.extension import Extension

from Cython.Build import cythonize  # isort: skip strange build system bug


def read(filename: str) -> str:
    with open(filename, "r", encoding="utf8") as fp:
        return fp.read()


pooma = Extension(
    name="pooma",
    sources=["poom/ray_march.pyx", "poom/math.pyx"],
)

setup(
    name="poom",
    description=read("README.md"),
    ext_modules=cythonize(pooma, language_level=3),
    include_dirs=numpy.get_include(),
)
