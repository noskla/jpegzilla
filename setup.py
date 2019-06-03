#!/usr/bin/python3
import os

try:
    from cx_Freeze import setup, Executable
except ImportError:
    print('You have to install cx_freeze from pip or your distro repository.')


jzexe = Executable('jpegzilla.py', base = ('Win32GUI' if os.name == 'nt' else None))

setup(
        
    name = 'Jpegzilla',
    version = '0.9',
    options = {
        'build_exe': {
            'include_files': ['locale/'],
            'packages': ['hurry.filesize', 'glob', 'sys', 'threading', 'shutil', 'platform', 'ntpath', 'subprocess'],
            'includes': ['tkinter']
            }
        },
    executables = [jzexe]

)


