#!/usr/bin/python3
import os, sys
from conf import VER, JZ_ICON_SETUP

try:
    from cx_Freeze import setup, Executable
except ImportError:
    print('You have to install cx_Freeze from pip or your distro repository.')


jzexe = Executable(
        'jpegzilla.py', 
        base = ('Win32GUI' if os.name == 'nt' else None),
        icon = JZ_ICON_SETUP
        )

updater = Executable(
        'updater.py',
        base = ('Win32GUI' if os.name == 'nt' else None)
        )

include_files = [
    './locale/',
    './icons/'
]

if os.name == 'nt':

    python_install_dir = sys.exec_prefix

    os.environ['TCL_LIBRARY'] = python_install_dir + '/tcl/tcl8.6'
    os.environ['TK_LIBRARY'] = python_install_dir + '/tcl/tk8.6'

    include_files = include_files + [
        python_install_dir + '/DLLs/tcl86t.dll',
        python_install_dir + '/DLLs/tk86t.dll',
        ]


setup(
        
    name = 'Jpegzilla',
    version = VER,
    options = {
        'build_exe': {
            'include_files': include_files,
            'packages': [
                'glob', 'sys', 'threading', 'shutil', 'requests',
                'platform', 'ntpath', 'subprocess', 'PIL', 're'
                ],
            'includes': ['tkinter', 'idna.idnadata']
            }
        },
    executables = [jzexe, updater]

)
