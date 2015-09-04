#! /usr/bin/env python

from distutils.core import setup

try:
   from distutils.command.build_py import build_py_2to3 \
        as build_py
except ImportError:
   from distutils.command.build_py import build_py

setup(name="untwisted",
      version="0.1",
      packages=["untwisted", 
                "untwisted.utils"],
      author="Iury O. G. Figueiredo",
      author_email="ioliveira@id.uff.br",
      cmdclass = {'build_py': build_py}
)
