#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Jpegzilla
# A simple, cross-platform and lightweight graphical user interface for MozJPEG.
# https://github.com/fabulouskana/jpegzilla

import sys, ntpath, os, subprocess, threading, json
import math, platform, shutil, glob
import tkinter, tkinter.ttk, tkinter.filedialog

from tkinter import messagebox
from PIL import Image, ImageTk

FNULL = open(os.devnull, 'w')
OS = platform.system()
VER = '1.0'

TEMPDIR = ((os.getenv('WINDIR').replace('\\', '/') + '/Temp/jpegzilla/') if OS == 'Windows' else '/tmp/jpegzilla/')
if not os.path.exists(TEMPDIR):
    os.mkdir(TEMPDIR)

class jpegzilla:

    def __init__(self):

        # Colors
        self.bg = '#FEFEFE' # Background color
        self.fg = '#000000' # Foreground color
        self.fgdis = '#555555' # Foreground color of disabled element

        self.debug = False

        first_run = False

        # Get current file.
        if (getattr(sys, 'frozen', False)):
            _thisfile = sys.executable
        else:
            _thisfile = __file__

        # Get important dir paths.
        locale_path = os.path.dirname(os.path.abspath(_thisfile).replace('\\', '/')) + '/locale/'

        # Load locale file.

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

            def set_language(lang, setup_window):

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
                    command=lambda:set_language('English', first_run_setup)
                    )
            first_run_setup_done = tkinter.Button(
                    first_run_setup,
                    text='Accept settings',
                    relief='flat',
                    bg=self.bg,
                    fg=self.fg,
                    command=lambda:set_language(language.get(), first_run_setup)
                    )
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

        # Check if Mozjpeg is available.
        if OS == 'Windows':

            win_paths = os.getenv('PATH').split(';')

            if os.path.isfile('./cjpeg.exe'):
                print(self.locale['mozjpeg-found-local-dir'])
                if not glob.glob('./libjpeg-*.dll'):
                    messagebox.showerror(self.locale['title-error'], self.locale['mozjpeg-dll-missing-error'])
                pass

            elif os.path.isfile('./jpegzilla-mozjpeg_in_path'):
                pass

            else:

                print(self.locale['mozjpeg-search-in-path'])
                mozjpeg_found = False

                for path in win_paths:
                    if os.path.isfile(path.replace('\\', '/') + ('/' if path[-1:] == '' else '') + 'cjpeg.exe' ):
                        print(self.locale['mozjpeg-found-path'].format(path=path))
                        mozjpeg_found = True
                        f = open('./jpegzilla-mozjpeg_in_path', 'w')
                        f.write(path)
                        f.close()
                        break

                if not mozjpeg_found:
                    print(self.locale['mozjpeg-not-found-error'])
                    messagebox.showerror(self.locale['title-error'], self.locale['mozjpeg-not-found-error'])
                    sys.exit()



        else:

            if not os.path.isfile('/usr/bin/cjpeg') and not os.path.isfile('/opt/mozjpeg/cjpeg'):
                print(self.locale['mozjpeg-not-found-error'])
                messagebox.showerror(self.locale['title-error'], self.locale['mozjpeg-not-found-error'])
                sys.exit()

        self.cancel_thread = False

        # Create root window.
        self.root = tkinter.Tk()
        self.root.geometry('600x450')
        self.root.title(self.locale['window-title'])
        self.root.resizable(False, False)
        self.root.configure(background=self.bg)

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
                        ),
                }

        dpos = [35, 10] # x, y

        for _, button in self.buttons.items():
            button.place(x=dpos[0], y=dpos[1])
            dpos[0] += 220

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

        self.cjpeg_parameters['-colorformat'].set('YUV 4:2:0')
        def uncheck_progressive():
            if self.cjpeg_parameters['-progressive'].get() or self.gui_options['progressive']['state'] == 'normal':
                self.cjpeg_parameters['-progressive'].set(0)
                self.gui_options['progressive'].configure(state='disabled')
            else:
                self.gui_options['progressive'].configure(state='normal')

        def uncheck_optimize():
            if self.cjpeg_parameters['-optimize'].get() or self.gui_options['optimize']['state'] == 'normal':
                self.cjpeg_parameters['-optimize'].set(0)
                self.gui_options['optimize'].configure(state='disabled')
            else:
                self.gui_options['optimize'].configure(state='normal')

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
                    command=lambda:uncheck_optimize()
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
                    command=lambda:uncheck_progressive()
                    ),
                 'notrellis': tkinter.Checkbutton(
                    self.root, text=self.locale['notrellis'],
                    bg=self.bg, fg=self.fg,
                    bd=0,
                    highlightbackground=self.fg,
                    highlightthickness=0,
                    relief='flat',
                    variable=self.cjpeg_parameters['-notrellis']
                    )
                }

        # - Set the defaults
        self.gui_options['progressive'].select()
        self.gui_options['quality'].set(90)
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
        self.file_queue.column('#0', width=245, stretch='no')
        self.file_queue.heading('size', text=self.locale['treeview-size'])
        self.file_queue.column('size', width=145, stretch='no')
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

        self.preview_window = tkinter.Toplevel(self.root)
        self.preview_window.title(self.locale['image-preview-title'].format(filename=file_name))

        # Open in image viewer
        oiiv_button = tkinter.Button(
                self.preview_window,
                width='600',
                text=self.locale['open-in-image-viewer'],
                command=lambda:subprocess.Popen([
                    'start' if OS == 'Windows' else 'xdg-open',
                    TEMPDIR + file_name if selected_file[1] == self.locale['status-completed'] else selected_file[2]
                    ], stdout=FNULL, stderr=subprocess.STDOUT)
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
                        (self.locale['select-filetypes']['compatible-formats'], ['*.jpeg', '*.jpg', '*.tga']),
                        (self.locale['select-filetypes']['all-files'], '*.*')
                    )
                )
        self.filenames = self.root.tk.splitlist(filenames)


        for image in self.filenames:
            
            filesize = self.convert_size(os.stat(image).st_size)

            self.file_queue.insert('', 'end', text=ntpath.basename(image), values=(
                     filesize, self.locale['status-new'], image
                ))

        if self.filenames:
            self.buttons['run'].config(state='normal')

        self.queue_label.configure(text=self.locale['loaded-files'].format(str(len(self.file_queue.get_children()))))

    def run(self):

        self.compress_thread = threading.Thread(target=self.compress)
        self.compress_thread.start()

    def cancel(self):
        self.cancel_thread = True

    def compress(self):

        self.buttons['run'].configure(state='disabled')
        self.cancel_button.configure(state='normal')

        command = "cjpeg {targa} -outfile {filename}"

        for parameter, value in self.cjpeg_parameters.items():
            value = value.get()
            if not parameter in ['-quality', '-smooth', '-colorformat']:
                if value:
                    command += (' {0} {1}'.format(parameter, ('' if value in [0, 1] else value)))

            elif parameter == '-colorformat':
                if value == 'RGB':
                    command += '-rgb'
                elif value == 'YUV 4:2:0':
                    command += '-sample 2x2'
                elif value == 'YUV 4:2:2':
                    command += '-sample 2x1'
                elif value == 'YUV 4:4:4':
                    command += '-sample 1x1'

            else:
                command += ' {0} {1}'.format(parameter, value)

        files_to_compress = self.file_queue.get_children()

        for entry in files_to_compress:

            entry_data = self.file_queue.item(entry)['values']
            img, extension = os.path.splitext(entry_data[2])
            img = img.split('/')[len(img.split('/')) - 1]

            if entry_data[1] == self.locale['status-completed']:
                pass
            
            else:

                self.file_queue.item(entry, values=( entry_data[0], self.locale['status-running'], entry_data[2] ))

                c = (command.format(filename=(TEMPDIR + img + extension), targa=('-targa' if extension == '.tga' else '')) + ' ' + entry_data[2])

                if self.debug:
                    print(c)

                subprocess.Popen(c, shell=True, stdout=subprocess.PIPE).wait()
                self.file_queue.item(entry, values=( entry_data[0] + ' -> ' + self.convert_size(os.stat(TEMPDIR + img + extension).st_size), self.locale['status-completed'], entry_data[2] ))

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

                print("Jpegzilla {}\nhttps://github.com/fabulouskana/jpegzilla".format(VER))

            elif sys.argv[1] in ['-h', '--help']:

                print("Run program by just typing \"jpegzilla\" or by running script without any arguments.")
                print("      -v, --version  - Display version information.")

            else:

                print("Unknown argument. Type --help for more information.")

            sys.exit()

        else:
            raise IndexError

    except IndexError:
        pass

    jz = jpegzilla()
