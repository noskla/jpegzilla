#!/usr/bin/python3
# -*- config: utf-8 -*-
# Jpegzilla
# A simple, cross-platform and lightweight graphical user interface for MozJPEG.
# https://github.com/canimar/jpegzilla

import os, platform, sys

if (getattr(sys, 'frozen', False)):
    _thisfile = sys.executable
else:
    _thisfile = __file__

_here = os.path.dirname(os.path.abspath(_thisfile.replace('\\', '/')))

OS = platform.system()

# --- Editable content ---

VER = '1.2.0-pre'

JZ_ICON_SETUP = ('icons/icon-96x96.ico' if OS == 'Windows' else 'icons/icon-96x96.gif')
JZ_ICON_TKINTER = (_here + '/icons/icon-96x96.gif')

DEBUG = True
DOCS_URL = 'https://canimar.github.io/jpegzilla/'

SUPPORTED_FORMATS = ['*.jpg', '*.jpeg', '*.tga', '*.png']

# Put full path to directory containing all required libraries and executables
# (make sure to use forward slashes)
# Examples:
#   /home/user/Desktop/mozjpeg/
#   C:/Users/user/Desktop/mozjpeg/
MOZJPEG_PATH_OVERRIDE = '/usr/bin/'

# --- --- --- --- --- ---

TEMPDIR = ((os.getenv('WINDIR').replace('\\', '/') + '/Temp/jpegzilla/') if OS == 'Windows' else '/tmp/jpegzilla/')
if not os.path.exists(TEMPDIR):
    os.mkdir(TEMPDIR)

