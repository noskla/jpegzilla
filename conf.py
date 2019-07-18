#!/usr/bin/python3
# -*- config: utf-8 -*-
# Jpegzilla
# A simple, cross-platform and lightweight graphical user interface for MozJPEG.
# https://github.com/canimar/jpegzilla

import os, platform

FNULL = open(os.devnull, 'w')
OS = platform.system()
VER = '1.1.0-pre2'
JZ_ICON = 'icons/icon-96x96.gif'

DEBUG = False
DOCS_URL = 'https://canimar.github.io/jpegzilla/'

TEMPDIR = ((os.getenv('WINDIR').replace('\\', '/') + '/Temp/jpegzilla/') if OS == 'Windows' else '/tmp/jpegzilla/')
if not os.path.exists(TEMPDIR):
    os.mkdir(TEMPDIR)

