# Jpegzilla

Jpegzilla is a simple, cross-platform and lightweight graphical user interface for [MozJPEG](https://github.com/mozilla/mozjpeg) written in Python & Tkinter.

---

## Building and running or installing

### __GNU/Linux__

#### Arch Linux, Antergos, Manjaro

- Update system and install dependencies:  
``sudo pacman -Syu``  
``sudo pacman -S python python-pip python-cx_freeze git``
- Install MozJPEG from AUR or [compile it from source](https://github.com/mozilla/mozjpeg/blob/master/BUILDING.md):
``pacaur -S aur/mozjpeg`` or ``yay mozjpeg``
- Download Jpegzilla from Github:  
For most recent version: ``git clone --single-branch -b master https://github.com/canimar/jpegzilla.git jpegzilla``  
For delayed version: ``git clone --single-branch -b stable https://github.com/canimar/jpegzilla.git jpegzilla``
- Enter the repository directory:
``cd jpegzilla``
- Install all PIP dependencies:
``sudo -H pip install -r requirements.txt``
- Build portable or install:
``python setup.py build`` ``sudo python setup.py install``

The ready binary should be present in the newly created directory.

#### Debian, Ubuntu, Linux Mint, elementaryOS

- Install dependencies:
``sudo apt install python3 python3-pip git zlib1g-dev python3-tk libtcl-8.6 libtk-8.6 python3-tktreectrl``
- [Compile MozJPEG from the source](https://gist.github.com/Kelfitas/f3fb99984698ccd79414c6a29e9f4edd).
- Download Jpegzilla from Github:  
For most recent version: ``git clone --single-branch -b master https://github.com/canimar/jpegzilla.git jpegzilla``  
For delayed version: ``git clone --single-branch -b stable https://github.com/canimar/jpegzilla.git jpegzilla``
- Enter the repository directory:
``cd jpegzilla``
- Install all PIP dependencies:
``sudo -H python3 -m pip install -r requirements.txt``
- Install cx-Freeze:
``sudo -H python3 -m pip install cx-freeze``
- Build portable or install:
``python3 setup.py build`` ``sudo python3 setup.py install``

The ready binary should be present in the newly created directory.

---

### __Windows__

#### Windows 7, 8.1, 10

- [Download and install Python 3](https://www.python.org/downloads/).
- While installing make sure you have checked "Add Python to PATH", "pip" and "tcl/tk and IDLE"
- Download this repository, unzip it and open cmd.exe in it.
- Install Visual Studio:
[Windows 10 - Visual Studio 2017](https://visualstudio.microsoft.com/vs/older-downloads/) / 
[Windows 7, 8.1 - Visual Studio 2015](https://go.microsoft.com/fwlink/?LinkId=532606&clcid=0x409)
- Install all PIP dependencies:
``py -m pip install -r requirements.txt``
- Install cx-Freeze:
``py -m pip install cx_freeze``
- Run the build script:
``py setup.py build``
- [Download the MozJPEG binary](https://mozjpeg.codelove.de/binaries.html) or [compile it for your own](https://github.com/mozilla/mozjpeg/blob/master/BUILDING.md).
- Put the cjpeg.exe and dll libraries into a newly created directory next to jpegzilla.exe

The program is ready to use.

#### Windows XP, Vista

I am not actively testing the functionality on those OS's but
the install prodecure should be the same as above, with the
exception of used software version.  
I am not able to perform tests on this OS's often,
so if I am missing something please file an issue.

Use [version of Python compatible with Windows XP](https://www.python.org/downloads/release/python-343/).
Use [Visual Studio 2012](https://visualstudio.microsoft.com/vs/older-downloads/#visual-studio-2012-family).

---

### __MacOS__

I cannot release an instruction nor the binaries for MacOS for this moment.  
If you're interested in helping me with optimizing this software under MacOS,
please send me an e-mail.
