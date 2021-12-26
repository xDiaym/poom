from distutils.extension import Extension

import numpy
from Cython.Build import cythonize
from setuptools import setup


def read(filename: str) -> str:
    with open(filename, "r") as fp:
        return fp.read()


extensions = [
    Extension(
        "ray_march",
        ["poom/ray_march.pyx"],
        include_dirs=[numpy.get_include()],
    )
]

setup(
    name="poom",
    description=read("README.md"),
    ext_modules=cythonize(extensions),
)
