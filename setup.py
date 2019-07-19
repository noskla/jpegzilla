#!/usr/bin/python3
<<<<<<< HEAD
import os
=======
import os, sys
from conf import VER, JZ_ICON_SETUP
>>>>>>> origin/master

try:
    from cx_Freeze import setup, Executable
except ImportError:
    print('You have to install cx_freeze from pip or your distro repository.')


<<<<<<< HEAD
jzexe = Executable('jpegzilla.py', base = ('Win32GUI' if os.name == 'nt' else None))
=======
jzexe = Executable(
        'jpegzilla.py', 
        base = ('Win32GUI' if os.name == 'nt' else None),
        icon = JZ_ICON_SETUP
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

>>>>>>> origin/master

setup(
        
    name = 'Jpegzilla',
<<<<<<< HEAD
    version = '0.9',
    options = {
        'build_exe': {
            'include_files': ['locale/'],
            'packages': ['hurry.filesize', 'glob', 'sys', 'threading', 'shutil', 'platform', 'ntpath', 'subprocess'],
=======
    version = VER,
    options = {
        'build_exe': {
            'include_files': include_files,
            'packages': [
                'glob', 'sys', 'threading', 'shutil',
                'platform', 'ntpath', 'subprocess', 'PIL', 're'
                ],
>>>>>>> origin/master
            'includes': ['tkinter']
            }
        },
    executables = [jzexe]

)
<<<<<<< HEAD


=======
>>>>>>> origin/master
