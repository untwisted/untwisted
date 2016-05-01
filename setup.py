#! /usr/bin/env python

from distutils.core import setup
setup(name="untwisted",
      version="0.1.0",
      packages=["untwisted", 
                "untwisted.utils",
                "untwisted.plugins"],
      scripts=['quickserv'],
      author="Iury O. G. Figueiredo",
      author_email="ioliveira@id.uff.br",
      url='https://github.com/iogf/untwisted',
      download_url='https://github.com/iogf/untwisted',
      keywords=['asynchronous', 'programming', 'twisted', 'untwisted', 'library', 'framework', 'networking', 'protocols'],
      classifiers=[],
      description="A library for asynchronous programming in python.")














