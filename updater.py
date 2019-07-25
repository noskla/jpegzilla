#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Jpegzilla
# A simple, cross-platform and lightweight graphical user interface for MozJPEG.
# https://github.com/canimar/jpegzilla

from conf import VER, _thisfile, _here, JZ_ICON_TKINTER, OS, TEMPDIR

import threading, tkinter, tkinter.ttk, json, sys, requests, zipfile, os, shutil

VER = '1.0.0'
locale_path = _here + '/locale/'

try:

    with open(locale_path + 'locale.txt', 'r') as f:
        locale_code = f.read().rstrip('\n')
        if not locale_code: raise FileNotFoundError
        f.close()

    with open(locale_path + locale_code + '.json', 'r') as f:
        global LOCALE
        LOCALE = json.load(f)
        f.close()

except FileNotFoundError:
    sys.exit()


root = tkinter.Tk()
root.geometry('300x130')
root.title(LOCALE['updater-title'])
root.resizable(False, False)

icon = tkinter.PhotoImage(file=JZ_ICON_TKINTER)
root.tk.call('wm', 'iconphoto', root._w, icon)

label = tkinter.Label(root, text=LOCALE['updater-initializing'])
label.pack(pady='20')

bar = tkinter.ttk.Progressbar(root, orient='horizontal', length=300, mode='indeterminate')
bar.pack()
bar.start()

def check_for_updates(current_version, label):
    
    response = requests.get('https://api.github.com/repos/canimar/jpegzilla/releases')
    if not response.status_code == 200:
        return [False, str(response.status_code) + ' ' + response.status_text]
    
    newest_version_str = response.json()[0]['tag_name']
    is_pre_release = ('-pre' in newest_version_str)

    if is_pre_release:
        newest_version_str = newest_version_str[:-4]

    git_major  = int(newest_version_str.split('.')[0])
    git_middle = int(newest_version_str.split('.')[1])
    git_minor  = int(newest_version_str.split('.')[2])


    local_is_pre_release = ('-pre' in current_version)
    if local_is_pre_release:
        current_version = current_version[:-4]

    loc_major  = int(current_version.split('.')[0])
    loc_middle = int(current_version.split('.')[1])
    loc_minor  = int(current_version.split('.')[2])

    
    if not git_major > loc_major:
        if not git_middle > loc_middle:
            if not git_minor > loc_minor:
                return [False, 'No updates available.']

    label.configure(text=LOCALE['updater-downloading'])
    x86_64 = (sys.maxsize > 2**32)
    system = OS.lower()
    download_options = response.json()[0]['assets']

    for option in download_options:

        current_option_information = option['name'].split('-')

        if current_option_information[2] == system:

            build_arch = current_option_information[3][:-4]
            if (x86_64 and (build_arch == 'x86_64')) or (not x86_64 and (build_arch == 'x86')):
                
                download_url = option['browser_download_url']
                break

    return [True, download_url]


def install_update(url):

    local_filename = url.split('/')[-1]

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(TEMPDIR + local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)

    if os.path.exists(TEMPDIR + 'newver/'):
        shutil.rmtree(TEMPDIR + 'newver/')

    with zipfile.ZipFile(TEMPDIR + local_filename, 'r') as zip_ref:
        zip_ref.extractall(TEMPDIR + 'newver/')

    os.remove(TEMPDIR + local_filename)

    updater_name = ('updater.exe' if OS == 'Windows' else 'updater')

    try:
        os.remove(TEMPDIR + 'newver/jpegzilla/' + updater_name)
    except FileNotFoundError:
        pass

    for f in os.listdir(TEMPDIR + 'newver/jpegzilla/'):
        if os.path.isdir(f):
            if not os.path.isdir(_here + f):
                os.mkdir(_here + f)
            for sf in os.listdir(f):
                shutil.move(TEMPDIR + f + '/' + sf, _here + '/' + f)
        else:
            shutil.move(TEMPDIR + f, _here)


def update(version, label, bar):

    label.configure(text=LOCALE['updater-checking'])
    result = check_for_updates(version, label)
    if not result[0]:
        label.configure(text=LOCALE['updater-end-before'].format(reason=result[1]))
    else:
        label.configure(text=LOCALE['updater-installing'])
        install_update(result[1])
    label.configure(text=LOCALE['updater-done'])
    bar.stop()


background_thread = threading.Thread(target=update, args=[VER, label, bar], name='Update')
background_thread.start()

root.mainloop()

