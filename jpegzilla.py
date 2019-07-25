#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Jpegzilla
# A simple, cross-platform and lightweight graphical user interface for MozJPEG.
# https://github.com/canimar/jpegzilla

import sys, ntpath, os, subprocess, threading, json
import math, platform, shutil, glob, re
import tkinter, tkinter.ttk, tkinter.filedialog

import webbrowser

from tkinter import messagebox
from PIL import Image, ImageTk

from conf import (TEMPDIR, JZ_ICON_TKINTER, VER, OS, _here,
DOCS_URL, DEBUG, SUPPORTED_FORMATS, MOZJPEG_PATH_OVERRIDE,
_thisfile, _iscompiled)

class jpegzilla:

    def __init__(self):

        # Colors
        self.bg = '#FEFEFE' # Background color
        self.fg = '#000000' # Foreground color
        self.fgdis = '#555555' # Foreground color of disabled element

        self.debug = DEBUG
        self.mozjpeg_path = ''

        first_run = False

        locale_path = _here + '/locale/'

        # Load locale file.

        self.print_debug('Loading locales...')
        try:
            with open(locale_path + 'locale.txt', 'r') as f:
                locale_code = f.read().rstrip('\n')
                if not locale_code:
                    first_run = True
                f.close()

        except FileNotFoundError:
            first_run = True


        if not first_run:

            if not os.path.isfile(locale_path + locale_code + '.json'):
                print('Locale with given language code doesn\'t exist. Fallback to English...')
                locale_code = 'English'

            with open(locale_path + locale_code + '.json', 'r') as f:
                self.locale = json.load(f)
                f.close()
        
        else:

            def set_settings(lang, setup_window):

                if lang == 'Select a language':
                    return

                with open(locale_path + lang + '.json', 'r') as f:
                    self.locale = json.load(f)
                    f.close()

                with open(locale_path + 'locale.txt', 'w') as f:
                    f.write(lang)
                    f.close()
                
                setup_window.destroy()


            raw_languages_list = sorted(os.listdir(locale_path))
            languages_list = []

            for lang in raw_languages_list:
                if lang.endswith('.json'):
                    languages_list.append(lang[:-5])

            first_run_setup = tkinter.Tk()
            first_run_setup.geometry('300x180')
            first_run_setup.title('Jpegzilla - First run setup')
            first_run_setup.resizable(False, False)
            self._icon = tkinter.PhotoImage(file=JZ_ICON_TKINTER)
            first_run_setup.tk.call('wm', 'iconphoto', first_run_setup._w, self._icon)
            first_run_setup.configure(bg=self.bg)
            first_run_setup.protocol('WM_DELETE_WINDOW', lambda:sys.exit())

            language = tkinter.StringVar(first_run_setup)
            language.set('Select a language')

            first_run_setup_skip = tkinter.Button(
                    first_run_setup,
                    text='Skip setup (Will use defaults)',
                    relief='flat',
                    bg=self.bg,
                    fg=self.fg,
                    command=lambda:set_settings('English', first_run_setup)
                    )
            first_run_setup_done = tkinter.Button(
                    first_run_setup,
                    text='Accept settings',
                    relief='flat',
                    bg=self.bg,
                    fg=self.fg,
                    command=lambda:set_settings(language.get(), first_run_setup)
                    )
            # pylint gives here an no-value-for-parameter error, ignore it
            first_run_setup_lang = tkinter.OptionMenu(first_run_setup, language, *languages_list)
            first_run_setup_text = tkinter.Label(
                    first_run_setup,
                    bg=self.bg,
                    fg=self.fg,
                    text='Thanks for using Jpegzilla!\nPlease choose a language you wanna use\nor click "SKIP".\n'
                    )

            first_run_setup_text.pack()
            first_run_setup_lang.pack()
            first_run_setup_skip.pack(fill='x', side='bottom')
            first_run_setup_done.pack(fill='x', side='bottom')

            first_run_setup.mainloop()


        self.cancel_thread = False

        # Test MozJPEG
        if not MOZJPEG_PATH_OVERRIDE:

            if OS == 'Windows':
                path_env = os.getenv('PATH').split(';')
                required_files = ['cjpeg.exe', 'libjpeg-*.dll', 'jpegtran.exe']
                counter = 0

                self.print_debug('Searching in local directory...')
                for file in required_files:
                    counter = 0

                    if glob.glob(file):

                        self.print_debug(f"Found {file} in local directory.")

                        if counter >= len(required_files): 
                            self.mozjpeg_path = _here
                            break
                        else:
                            counter += 1


                if not counter >= len(required_files):
                    self.print_debug('Missing files in local directory, trying to find in PATH')

                    for path in path_env:

                        # Replace Windows backslashes with forward slashes.
                        path = path.replace('\\', '/')
                            
                        # Add last slash if it's missing.
                        path += ( '/' if path[-1:] == '' else '' )

                        for file in required_files:
                                
                            counter = 0
                            if os.path.isfile(path + file):
                                counter += 1
                                self.print_debug(f"Found {file} in PATH.")
                                
                            if counter >= len(required_files): 
                                self.mozjpeg_path = path
                                break

                        if not counter >= len(required_files):
                            messagebox.showerror(
                                self.locale['title-error'],
                                self.locale['mozjpeg-file-missing-error']
                            )
                            sys.exit()

            else: # Linux

                self.print_debug('Searching for MozJPEG')

                possible_paths = [
                    '/opt/mozjpeg/', '/opt/mozjpeg/bin/', '/opt/libmozjpeg/bin/',
                    '/usr/local/bin/', '/usr/bin/'
                ]

                required_binaries = ['cjpeg', 'jpegtran']

                while not self.mozjpeg_path:

                    for path in possible_paths:
                        counter = 0

                        for binary in required_binaries:
                            if os.path.isfile(path + binary):
                                counter += 1

                        if counter >= len(required_binaries):
                            self.print_debug(f"Found MozJPEG binaries in {path}")
                            self.mozjpeg_path = path
                            break

                    if len(required_binaries) > counter:
                        messagebox.showerror(self.locale['title'], self.locale['mozjpeg-file-missing-error'])
                        sys.exit()
                    

        else: # MOZJPEG_PATH_OVERRIDE

            self.print_warning("Running with MOZJPEG_PATH_OVERRIDE, make sure files are inside specified directory.")
            self.mozjpeg_path = MOZJPEG_PATH_OVERRIDE

        # Create root window.
        self.root = tkinter.Tk()
        self.root.geometry('780x550')
        self.root.title(self.locale['window-title'])
        self.root.resizable(False, False)
        self.root.configure(background=self.bg)
        self._icon = tkinter.PhotoImage(file=JZ_ICON_TKINTER)
        self.root.tk.call('wm', 'iconphoto', self.root._w, self._icon)

        # Menu bar
        def about():
            about_window = tkinter.Toplevel(self.root)
            about_window.wm_title(self.locale['about-title'])
            about_window.geometry('300x340')

            program_name = tkinter.Label(about_window,

                text='Jpegzilla ' + VER + '\n' +
                    self.locale['about-credit'].format(
                        author = 'Jarosław "_kana" C.',
                        dependencies = 'MozJPEG, libjpeg-turbo,\nPython Imaging Library & cx_Freeze\n'
                    )

                )

            program_name.pack(side="top", fill="both", expand=True)

        def reset():
            os.remove(_here + '/locale/locale.txt')
            self.root.destroy()
            self.__init__()

        def update():

            self.print_debug('Running updater...')

            if _iscompiled:
                command = ['./updater']

            else:
                if OS == 'Windows':
                    command = ['py', 'updater.py']
                else:
                    command = ['python3', 'updater.py']

            subprocess.Popen(command)
            sys.exit()

        self.menubar = tkinter.Menu(self.root)

        menubar_file_cascade = tkinter.Menu(self.menubar, tearoff=0)
        menubar_file_cascade.add_command(label=self.locale['menu-import'], command=lambda:self.select_files())

        menubar_tools_cascade = tkinter.Menu(self.menubar, tearoff=0)
        menubar_tools_cascade.add_command(label=self.locale['menu-reset'], command=lambda:reset())
        menubar_tools_cascade.add_command(label=self.locale['menu-updater'], command=lambda:update())

        menubar_help_cascade = tkinter.Menu(self.menubar, tearoff=0)
        menubar_help_cascade.add_command(label=self.locale['menu-about'], command=lambda:about())
        menubar_help_cascade.add_command(label=self.locale['menu-website'], command=lambda:webbrowser.open_new(DOCS_URL))

        self.menubar.add_cascade(label=self.locale['menu-file'], menu=menubar_file_cascade)
        self.menubar.add_cascade(label=self.locale['menu-tools'], menu=menubar_tools_cascade)
        self.menubar.add_cascade(label=self.locale['menu-help'], menu=menubar_help_cascade)

        self.root.configure(menu=self.menubar)

        # Primary buttons

        self.buttons = {
                    'run': tkinter.Button(
                        self.root, 
                        text=self.locale['run-button'], 
                        state='disabled', 
                        bg=self.bg, 
                        fg=self.fg, 
                        bd=0, 
                        disabledforeground=self.fgdis, 
                        highlightbackground=self.bg, 
                        highlightthickness=0, 
                        relief='flat', 
                        overrelief='flat',
                        font='Arial 10 bold',
                        command=lambda:self.run()
                        ),
                    'save': tkinter.Button(
                        self.root, 
                        text=self.locale['save-button'], 
                        state='disabled', 
                        bg=self.bg, 
                        fg=self.fg, 
                        bd=0, 
                        disabledforeground=self.fgdis, 
                        highlightbackground=self.bg, 
                        highlightthickness=0, 
                        relief='flat', 
                        overrelief='flat',
                        font='Arial 10 bold',
                        command=lambda:self.save_all()
                        ),
                    'import': tkinter.Button(
                        self.root, 
                        text=self.locale['import-button'], 
                        background=self.bg, 
                        fg=self.fg, 
                        bd=0, 
                        disabledforeground=self.fgdis, 
                        highlightbackground=self.bg, 
                        highlightthickness=0, 
                        relief='flat', 
                        overrelief='flat',
                        font='Arial 10 bold',
                        command=lambda:self.select_files()
                        )
                }

        dpos = [35, 10] # x, y

        for _, button in self.buttons.items():
            button.place(x=dpos[0], y=dpos[1])
            dpos[0] += 210

        # Parameters/Options

        self.cjpeg_parameters = {
                '-quality': tkinter.IntVar(),
                '-smooth': tkinter.IntVar(),
                '-progressive': tkinter.IntVar(),
                '-greyscale': tkinter.IntVar(),
                '-arithmetic': tkinter.IntVar(),
                '-colorformat': tkinter.StringVar(self.root),
                '-optimize': tkinter.IntVar(),
                '-baseline': tkinter.IntVar(),
                '-notrellis': tkinter.IntVar()
                }

        self.jpegtran_parameters = {
            '-rotate': tkinter.StringVar(self.root, value='0\N{DEGREE SIGN}'),
            '-transpose': tkinter.IntVar(),
            '-transverse': tkinter.IntVar(),
            '-trim': tkinter.IntVar(),
            '-crop': tkinter.StringVar(self.root)
        }

        self.cjpeg_parameters['-colorformat'].set('YUV 4:2:0')


        def switch_checked(parameter, parameter_group):

            if parameter_group == 'cjpeg':
                if self.cjpeg_parameters[parameter].get() or self.gui_options[parameter[1:]]['state'] == 'normal':
                    self.cjpeg_parameters[parameter].set(0)
                    self.gui_options[parameter[1:]].configure(state='disabled')
                else:
                    self.gui_options[parameter[1:]].configure(state='normal')

            elif parameter_group == 'jpegtran':
                if self.jpegtran_parameters[parameter].get() or self.gui_options[parameter[1:]]['state'] == 'normal':
                    self.jpegtran_parameters[parameter].set(0)
                    self.gui_options[parameter[1:]].configure(state='disabled')
                else:
                    self.gui_options[parameter[1:]].configure(state='normal')


        self.gui_options = {
                'quality': tkinter.Scale(
                    self.root, label=self.locale['image-quality'], orient='horizontal', length='200', 
                    bg=self.bg, fg=self.fg, 
                    bd=0, 
                    highlightbackground=self.bg, 
                    highlightthickness=0, 
                    relief='flat', 
                    variable=self.cjpeg_parameters['-quality']
                    ),
                'smoothing': tkinter.Scale(
                    self.root, label=self.locale['smoothing'], orient='horizontal', length='200', 
                    bg=self.bg, fg=self.fg, 
                    bd=0, 
                    highlightbackground=self.bg, 
                    highlightthickness=0, 
                    relief='flat', 
                    variable=self.cjpeg_parameters['-smooth']
                    ),
                'progressive': tkinter.Checkbutton(
                    self.root, text=self.locale['progressive'],
                    bg=self.bg, fg=self.fg,
                    bd=0, 
                    highlightbackground=self.bg, 
                    highlightthickness=0, 
                    relief='flat', 
                    variable=self.cjpeg_parameters['-progressive']
                    ),
                'greyscale': tkinter.Checkbutton(
                    self.root, text=self.locale['greyscale'], 
                    bg=self.bg, fg=self.fg,
                    bd=0, 
                    highlightbackground=self.bg, 
                    highlightthickness=0, 
                    relief='flat', 
                    variable=self.cjpeg_parameters['-greyscale']
                    ),
                'arithmetic': tkinter.Checkbutton(
                    self.root, text=self.locale['arithmetic'], 
                    bg=self.bg, fg=self.fg,
                    bd=0, 
                    highlightbackground=self.bg, 
                    highlightthickness=0, 
                    relief='flat', 
                    variable=self.cjpeg_parameters['-arithmetic'],
                    command=lambda:switch_checked('-optimize', 'cjpeg')
                    ),
                'colorformat': tkinter.OptionMenu(
                    self.root, 
                    self.cjpeg_parameters['-colorformat'], *['YUV 4:2:0', 'YUV 4:2:2', 'YUV 4:4:4', 'RGB']
                    ),
                'optimize': tkinter.Checkbutton(
                    self.root, text=self.locale['optimize'],
                    bg=self.bg, fg=self.fg,
                    bd=0,
                    highlightbackground=self.bg,
                    highlightthickness=0,
                    relief='flat',
                    variable=self.cjpeg_parameters['-optimize'],
                    ),
                 'baseline': tkinter.Checkbutton(
                    self.root, text=self.locale['baseline'],
                    bg=self.bg, fg=self.fg,
                    bd=0,
                    highlightbackground=self.bg,
                    highlightthickness=0,
                    relief='flat',
                    variable=self.cjpeg_parameters['-baseline'],
                    command=lambda:switch_checked('-progressive', 'cjpeg')
                    ),
                 'notrellis': tkinter.Checkbutton(
                    self.root, text=self.locale['notrellis'],
                    bg=self.bg, fg=self.fg,
                    bd=0,
                    highlightbackground=self.fg,
                    highlightthickness=0,
                    relief='flat',
                    variable=self.cjpeg_parameters['-notrellis']
                    ),

                 'rotate': tkinter.OptionMenu(
                    self.root,
                    self.jpegtran_parameters['-rotate'],
                    *['0\N{DEGREE SIGN}', '90\N{DEGREE SIGN}', '180\N{DEGREE SIGN}', '270\N{DEGREE SIGN}']
                 ),
                 'transpose': tkinter.Checkbutton(
                    self.root, text=self.locale['transpose'],
                    bg=self.bg, fg=self.fg,
                    bd=0,
                    highlightbackground=self.fg,
                    highlightthickness=0,
                    relief='flat',
                    variable=self.jpegtran_parameters['-transpose'],
                    command=lambda:switch_checked('-transverse', 'jpegtran')
                 ),
                 'transverse': tkinter.Checkbutton(
                    self.root, text=self.locale['transverse'],
                    bg=self.bg, fg=self.fg,
                    bd=0,
                    highlightbackground=self.fg,
                    highlightthickness=0,
                    relief='flat',
                    variable=self.jpegtran_parameters['-transverse'],
                    command=lambda:switch_checked('-transpose', 'jpegtran')
                 ),
                 'trim': tkinter.Checkbutton(
                    self.root, text=self.locale['trim'],
                    bg=self.bg, fg=self.fg,
                    bd=0,
                    highlightbackground=self.fg,
                    highlightthickness=0,
                    relief='flat',
                    variable=self.jpegtran_parameters['-trim']
                 ),
                 'crop': tkinter.Entry(
                    self.root,
                    width='24',
                    bg='#8E8E8E', fg='#FFFFFF',
                    bd=0,
                    highlightbackground=self.fg,
                    highlightthickness=0,
                    relief='flat',
                    textvariable=self.jpegtran_parameters['-crop'],
                 ),
                }

        # - Labels
        rotate_label = tkinter.Label(self.root, bg=self.bg, fg=self.fg, text=self.locale['rotate'])
        crop_label = tkinter.Label(self.root, bg=self.bg, fg=self.fg, text=self.locale['crop'])

        # - Set the defaults
        self.gui_options['progressive'].select()
        self.gui_options['quality'].set(75)
        self.gui_options['optimize'].select()

        # - Place items
        self.gui_options['quality'].place(x=10, y=45)
        self.gui_options['smoothing'].place(x=10, y=105)
        self.gui_options['progressive'].place(x=220, y=70)
        self.gui_options['greyscale'].place(x=220, y=90)
        self.gui_options['arithmetic'].place(x=220, y=110)
        self.gui_options['colorformat'].place(x=225, y=130)
        self.gui_options['optimize'].place(x=400, y=70)
        self.gui_options['baseline'].place(x=400, y=90)
        self.gui_options['notrellis'].place(x=400, y=125)

        rotate_label.place(x=13, y=170)
        self.gui_options['rotate'].place(x=15, y=190)
        self.gui_options['transpose'].place(x=10, y=225)
        self.gui_options['transverse'].place(x=10, y=245)
        self.gui_options['trim'].place(x=170, y=180)
        crop_label.place(x=183, y=205)
        self.gui_options['crop'].place(x=185, y=240)

        # Queue/List

        self.queue = tkinter.Frame(self.root, bg=self.bg)
        self.queue.pack(side='bottom')

        self.file_queue_rmdone = tkinter.Button(
                self.queue,
                text=self.locale['clear-all-button'], 
                bg=self.bg, 
                fg=self.fg, 
                bd=0, 
                disabledforeground=self.fgdis, 
                highlightbackground=self.bg, 
                highlightthickness=0, 
                relief='flat', 
                overrelief='flat',
                font='Arial 9 bold',
                command=lambda:self.clean()
                )
        self.file_queue_rmdone.pack(side='top', anchor='e')

        self.cancel_button = tkinter.Button(
                self.queue,
                text=self.locale['cancel-button'],
                state='disabled',
                bg=self.bg,
                fg=self.fg,
                bd=0,
                disabledforeground=self.fgdis,
                highlightbackground=self.bg,
                highlightthickness=0,
                relief='flat',
                overrelief='flat',
                font='Arial 9 bold',
                command=lambda:self.cancel()
                )
        self.cancel_button.pack(side='top', anchor='e')

        self.queue_label = tkinter.Label(self.queue, bg=self.bg, fg=self.fg, text=self.locale['loaded-files'].format('0'))
        self.queue_label.pack(side='top', anchor='w')

        self.file_queue = tkinter.ttk.Treeview(self.queue, selectmode='browse')
        self.file_queue['columns'] = ('size', 'status', 'loc')
        self.file_queue.heading('#0', text=self.locale['treeview-filename'])
        self.file_queue.column('#0', width=345, stretch='no')
        self.file_queue.heading('size', text=self.locale['treeview-size'])
        self.file_queue.column('size', width=245, stretch='no')
        self.file_queue.heading('status', text=self.locale['treeview-status'])
        self.file_queue.column('status', width=195, stretch='no')
        self.file_queue.heading('loc')
        self.file_queue.column('loc', width=0, stretch='no')
        self.file_queue.pack(side='left')

        self.file_queue_vsb = tkinter.ttk.Scrollbar(self.queue, orient='vertical', command=self.file_queue.yview)
        self.file_queue_vsb.pack(side='right', fill='y')

        self.file_queue.configure(yscrollcommand=self.file_queue_vsb.set)

        self.file_queue.bind('<Delete>', lambda x:self.remove_files())
        self.file_queue.bind('<Return>', lambda x:self.show_preview())
        self.file_queue.bind('<Double-Button-1>', lambda x:self.show_preview())

        self.root.mainloop()


    def print_debug(self, message):

        if not self.debug:
            return

        prefix = ( "\033[35m[DEBUG]\033[0m " if (not OS == 'Windows') else '[DEBUG] ' )
        print(prefix + message)
        
    def print_warning(self, message):

        prefix = ( "\033[33m[WARNING]\033[0m " if (not OS == 'Windows') else '[WARNING] ' )
        print(prefix + message)

    def print_error(self, message):

        prefix = ( "\033[31m[WARNING]\033[0m " if (not OS == 'Windows') else '[WARNING] ' )
        print(prefix + message)


    def remove_files(self):

        selected_files = self.file_queue.selection()
        for image in selected_files:
            self.file_queue.delete(image)

        self.queue_label.configure(text=self.locale['loaded-files'].format(
            str(len(
                self.file_queue.get_children()
                ))
            ))
        if not len(self.file_queue.get_children()):
            self.buttons['run'].config(state='disabled')


    def show_preview(self):
    
        selected_file = self.file_queue.item(self.file_queue.selection())['values']
        try:
            file_name = ntpath.basename(selected_file[2])
        except IndexError:
            return

        # 'status'
        if selected_file[1] == self.locale['status-error']:
            return

        self.preview_window = tkinter.Toplevel(self.root)
        self.preview_window.title(self.locale['image-preview-title'].format(filename=file_name))

        location = ((TEMPDIR + file_name) if (selected_file[1] == self.locale['status-completed']) else selected_file[2])

        if OS == 'Windows':
            command = ['start', location.replace('/', "\\")]
        else:
            command = ['xdg-open', location]

        oiiv_button = tkinter.Button(
                self.preview_window,
                width='600',
                text=self.locale['open-in-image-viewer'],
                command=lambda:subprocess.Popen(command, shell=(OS == 'Windows'))
                )
        oiiv_button.pack()

        self.preview_imgfile = Image.open( TEMPDIR + file_name if selected_file[1] == self.locale['status-completed'] else selected_file[2] )

        required_width = 800
        wpercent = (required_width / float(self.preview_imgfile.size[0]) )
        hsize = int( (float(self.preview_imgfile.size[1]) * float(wpercent)) )
        self.preview_imgfile = self.preview_imgfile.resize((required_width, hsize), Image.ANTIALIAS)

        self.preview_image = ImageTk.PhotoImage(self.preview_imgfile)

        self.preview = tkinter.Label(self.preview_window, image=self.preview_image)
        self.preview.image = self.preview_image
        self.preview.pack(fill='both', expand='yes')

    def clean(self):

        all_files = self.file_queue.get_children()
        for image in all_files:
            self.file_queue.delete(image)

        self.queue_label.configure(text=self.locale['loaded-files'].format('0'))
        self.buttons['run'].configure(state='disabled')
        self.buttons['save'].configure(state='disabled')

    def save_all(self):

        location = tkinter.filedialog.askdirectory(title=self.locale['save-all-title'], initialdir='~')

        compressed_images = self.file_queue.get_children()

        for image in compressed_images:
            child_data = self.file_queue.item(image)['values']
            filename = ntpath.basename(child_data[2])
            if child_data[1] == self.locale['status-completed']:
                shutil.move(TEMPDIR + filename, location + '/' + filename)


    def select_files(self):

        filenames = tkinter.filedialog.askopenfilenames(
                    initialdir='~',
                    title=self.locale['select-files-title'],
                    filetypes=(
                        (self.locale['select-filetypes']['compatible-formats'], SUPPORTED_FORMATS),
                        (self.locale['select-filetypes']['all-files'], '*.*')
                    )
                )
        self.filenames = self.root.tk.splitlist(filenames)

        files_already_imported = {}
        ids_already_imported = self.file_queue.get_children()
        for node in ids_already_imported:
            files_already_imported[self.file_queue.item(node)['text']] = self.file_queue.item(node)['values'][1]


        for image in self.filenames:
 
            basename = ntpath.basename(image)

            if (not basename in files_already_imported.keys()) or (not files_already_imported[basename] == self.locale['status-new']):
                filesize = self.convert_size(os.stat(image).st_size)

                self.file_queue.insert('', 'end', text=basename, values=(
                         filesize, self.locale['status-new'], image
                    ))
            
            else:
                messagebox.showerror(self.locale['title-error'], self.locale['import-same-file'].format(filename=basename))

        if self.filenames:
            self.buttons['run'].config(state='normal')

        self.queue_label.configure(text=self.locale['loaded-files'].format(str(len(self.file_queue.get_children()))))

    def run(self):

        self.compress_thread = threading.Thread(target=self.compress)
        self.compress_thread.start()

    def cancel(self):
        self.cancel_thread = True

    def compress(self):

        # Disable buttons
        self.buttons['run'].configure(state='disabled')
        self.cancel_button.configure(state='normal')

        # Prepare commands
        commands = {
            'cjpeg'   : "'{mozjpeg_path}cjpeg'{is_targa} {parameters} -outfile \"{temporary_filename}\" \"{original_filename}\"",
            'jpegtran': "'{mozjpeg_path}jpegtran' {parameters} -outfile \"{new_filename}\" \"{temporary_filename}\""
        }

        non_checkbutton_parameters = [
            '-quality', '-smooth', '-colorformat', '-rotate', '-crop'
        ]

        # Construct parameters for cjpeg command.
        selected_cjpeg_parameters = ''
        colorformat_replacement = {
            'RGB': '-rgb',
            'YUV 4:2:0': '-sample 2x2',
            'YUV 2:2:2': '-sample 2x1',
            'YUV 4:4:4': '-sample 1x1'
        }

        for parameter, value in self.cjpeg_parameters.items():
            value = value.get()

            if parameter in non_checkbutton_parameters:
                selected_cjpeg_parameters += (
                    f" {parameter} {value}" if not parameter == '-colorformat' 
                    else f" {colorformat_replacement[value]}"
                    )

            else:
                if value: # If checked.
                    selected_cjpeg_parameters += f" {parameter}"

        # Remove first space
        selected_cjpeg_parameters = selected_cjpeg_parameters[1:]

        self.print_debug(f"Using cjpeg parameters: \"{selected_cjpeg_parameters}\" ")

        # Construct parameters for jpegtran command
        selected_jpegtran_parameters = ''

        for parameter, value in self.jpegtran_parameters.items():
            value = value.get()

            if parameter == '-rotate':
                # If rotate parameter is unchanged, don't apply it to the final command.
                if value == u'0\N{DEGREE SIGN}':
                    parameter = ''
                else:
                    # Remove the degree character
                    value = value[:-1]

            elif parameter == '-crop':
                # \d+ - digits of unlimited length
                # x - just "x", \+ - just "+"
                reg_match = re.fullmatch(r'^\d+x\d+\+\d+\+\d+$', value)
                if reg_match == None:
                    self.print_debug(f"Wrong crop syntax or empty value. '-crop {value}'")
                    parameter = value = ''

            if parameter in non_checkbutton_parameters:
                selected_jpegtran_parameters += f" {parameter} {value}"
            else:
                if value: # If checked.
                    selected_jpegtran_parameters += f" {parameter}"

        # Remove first space
        selected_jpegtran_parameters = selected_jpegtran_parameters[1:]

        self.print_debug(f"Using jpegtran parameters: \"{selected_jpegtran_parameters}\" ")

        # Prepare to loop through files
        files_to_compress = self.file_queue.get_children()

        def change_status(target, target_information, status_id, size=None, path=None):

            self.file_queue.item(target, values=( 
                (target_information['file_size'] if size == None else size),
                self.locale[status_id],
                (target_information['path'] if path == None else path)
             ))

        for target in files_to_compress:

            self.print_debug(f"Loop currently operating on {target}.")
            target_information = self.file_queue.item(target)['values']
            target_information = {
                'file_size': target_information[0],
                'status': target_information[1],
                'path': target_information[2]
            }

            change_status(target, target_information, 'status-preparing')
            self.print_debug('Target information:\n' + ', '.join( target_information.values() ))

            path, extension = os.path.splitext(target_information['path'])
            filename = path.split('/')[ len(path.split('/')) - 1 ]

            unacceptable_statuses = [
                self.locale['status-completed'],
                self.locale['status-error'],
                self.locale['status-preparing'],
                self.locale['status-import_again']
                ]

            if target_information['status'] in unacceptable_statuses:
                change_status(target, target_information, 'status-import_again')
                continue

            # Create a new file name.
            def generate_filename():
                temporary_filename = ( TEMPDIR + filename )
                counter = 1

                while os.path.isfile(temporary_filename):
                    counter += 1
                    temporary_filename = ( TEMPDIR + filename + str(counter) )

                return temporary_filename + '.jpg'

            temporary_filename = generate_filename()

            # Convert PNG to TGA
            def png_to_tga(filename):
                self.print_debug(f"Converting {filename} to TGA")
                tga_filename = generate_filename()[:-4] + '.tga'
                im = Image.open(filename); im.save(tga_filename)
                return tga_filename

            if extension == '.png':
                change_status(target, target_information, 'status-converting')
                target_information['path'] = png_to_tga(target_information['path'])
                extension = '.tga'

            change_status(target, target_information, 'status-running')

            # Create full commands and execute them.
            cjpeg_command = commands['cjpeg'].format(
                mozjpeg_path = self.mozjpeg_path,
                is_targa = ' -targa' if extension == '.tga' else '',
                parameters = selected_cjpeg_parameters,
                temporary_filename = temporary_filename,
                original_filename = target_information['path']
            )

            if selected_jpegtran_parameters:
                # Generate a new file name.
                new_filename = generate_filename()

                jpegtran_command = commands['jpegtran'].format(
                    mozjpeg_path = self.mozjpeg_path,
                    parameters = selected_jpegtran_parameters,
                    new_filename = new_filename,
                    temporary_filename = temporary_filename
                )


            self.print_debug(f"Executing cjpeg command: {cjpeg_command}")
            subprocess.Popen(cjpeg_command, shell=True, stdout=subprocess.PIPE).wait()

            if selected_jpegtran_parameters:
                self.print_debug(f"Executing jpegtran command: {jpegtran_command}")
                subprocess.Popen(jpegtran_command, shell=True, stdout=subprocess.PIPE).wait()
                compressed_file = new_filename
            else:
                compressed_file = temporary_filename
            
            new_size = self.convert_size( os.stat(compressed_file).st_size )
            status   = ('status-completed' if not new_size == '0B' else 'status-error')

            change_status(
                target, target_information, status,
                size = ( f"{target_information['file_size']} -> {new_size}" ),
                path = compressed_file
                )

            if self.cancel_thread:
                self.cancel_thread = False
                break

        self.buttons['run'].configure(state='normal')
        self.buttons['save'].configure(state='normal')
        self.cancel_button.configure(state='disabled')


    def convert_size(self, size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

if __name__ == '__main__':
    
    try:
        if sys.argv[1].startswith('-'):

            if sys.argv[1] in ['-v', '--version']:

                print("Jpegzilla {}\nhttps://github.com/canimar/jpegzilla".format(VER))

            elif sys.argv[1] in ['-h', '--help']:

                print("Run program by just typing \"jpegzilla\" or by running script without any arguments.")
                print("      -v, --version  - Display version information.")

            else:

                print("Unknown argument. Type --help for more information.")

            sys.exit()

    except IndexError:
        pass

    jz = jpegzilla()
