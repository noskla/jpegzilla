#!/usr/bin/python3

from setuptools import setup

setup(
        name='jpegzilla',
        version=0.5.1,
        description='Lightweight, basic and easy to use MozJPEG frontend made in Tkinter',
        url='https://github.com/fabulouskana/jpegzilla',
        author='Jaroslaw "_kana" C.',
        author_email='kana.rvn@inventati.org',
        license='MPL2',
        scripts=['bin/jpegzilla'],
        packages=['jpegzilla'],
        install_requires=[
            'hurry.filesize'
            ],
        zip_safe=False
)

