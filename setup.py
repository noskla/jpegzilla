#!/usr/bin/python3
import os

try:
    from cx_Freeze import setup, Executable
except ImportError:
    print('You have to install cx_freeze from pip or your distro repository.')


jzexe = Executable(
        'jpegzilla.py', 
        base = ('Win32GUI' if os.name == 'nt' else None),
        icon = None
        )

if os.name == 'nt':

    python_install_dir = sys.exec_prefix

    os.environ['TCL_LIBRARY'] = python_install_dir + '/tcl/tcl8.6'
    os.environ['TK_LIBRARY'] = python_install_dir + '/tcl/tk8.6'

    include_files = [python_install_dir + '/DLLs/tcl86t.dll', python_install_dir + '/DLLs/tk86t.dll', './locale/']

else:

    include_files = ['./locale/']


setup(
        
    name = 'Jpegzilla',
    version = '0.99',
    options = {
        'build_exe': {
            'include_files': include_files,
            'packages': [
                'hurry.filesize', 'glob', 'sys',
                'threading','shutil', 'platform',
                'ntpath', 'subprocess', 'PIL'
                ],
            'includes': ['tkinter']
            }
        },
    executables = [jzexe]

)


