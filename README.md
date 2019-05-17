# Jpegzilla
Jpegzilla is a simple, cross-platform and lightweight graphical user interface for [MozJPEG](https://github.com/mozilla/mozjpeg) written in Python & Tkinter.

## Installation

#### GNU/Linux

###### Arch Linux / Manjaro
---
```bash
# Update your system first.
sudo pacman -Syu
# Install required dependencies.
sudo pacman -S python-pip git
# Install MozJPEG from AUR (this may differ depending what software you use, you can also compile it for your own)
yay mozjpeg # or pacaur -S aur/mozjpeg or yaourt mozjpeg
# Download and install Jpegzilla.
git clone https://github.com/fabulouskana/jpegzilla
sudo -H pip install ./jpegzilla
# Done.
```

###### Debian / Ubuntu
---
```bash
# Install required dependencies.
sudo apt install python3-pip git cmake autoconf automake libtool nasm make pkg-config -y
# Download and compile MozJPEG
git clone https://github.com/mozilla/mozjpeg.git
cd mozjpeg
autoreconf -fiv
mkdir build && cd build
sh ../configure
sudo make install
sudo ln -s /opt/mozjpeg/bin/jpegtran /usr/local/bin/mozjpeg
# Download and install Jpegzilla.
git clone https://github.com/fabulouskana/jpegzilla
sudo -H pip install ./jpegzilla
```
#### Windows

###### Windows 7 and above
---
- [Download and install Python](https://www.python.org/downloads/).
- While installing make sure you have checked "Add Python to PATH", "pip" and "tcl/tk and IDLE"
- Download this repository, open cmd.exe in it and go back one time (``cd ..``).
- Install Jpegzilla: ``python -m pip install ./jpegzilla``
- [Download the MozJPEG binary](https://mozjpeg.codelove.de/binaries.html) or [compile it for your own](https://github.com/mozilla/mozjpeg).
- Put the cjpeg.exe and all required dll libraries in new empty directory.
- Add that directory to PATH. [How to add things to PATH?](https://stackoverflow.com/questions/44272416/how-to-add-a-folder-to-path-environment-variable-in-windows-10-with-screensho)
- You should be able to run Jpegzilla with ``python -m jpegzilla``.

###### Windows XP
---
The same as above, but you have to use [older version of Python](https://www.python.org/downloads/release/python-343/).


