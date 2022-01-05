import numpy
from Cython.Build import cythonize
from setuptools import setup


def read(filename: str) -> str:
    with open(filename, "r") as fp:
        return fp.read()


setup(
    name="poom",
    description=read("README.md"),
    ext_modules=cythonize("poom/ray_march.pyx", language_level="3"),
    include_dirs=numpy.get_include(),
)
