#!/usr/bin/python3
# Jpegzilla
# A simple, cross-platform and lightweight graphical user interface for MozJPEG.
# https://github.com/fabulouskana/jpegzilla

import sys, ntpath, os, subprocess, threading, json
import hurry.filesize, platform, shutil, glob
import tkinter, tkinter.ttk, tkinter.filedialog

from PIL import Image, ImageTk

FNULL = open(os.devnull, 'w')
OS = platform.system()
VER = '0.6.0'

TEMPDIR = ((os.getenv('WINDIR').replace('\\', '/') + '/Temp/jpegzilla/') if OS == 'Windows' else '/tmp/jpegzilla/')
if not os.path.exists(TEMPDIR):
    os.mkdir(TEMPDIR)

class jpegzilla:

    def __init__(self):

        first_run = False

        # Load locale file.
        locale_path = os.path.dirname(os.path.abspath(__file__).replace('\\', '/')) + '/locale/'

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
                print('Locale with given language code doesn\'t exist. Fallback to en_US...')
                locale_code = 'en_US'

            with open(locale_path + locale_code + '.json', 'r') as f:
                self.locale = json.load(f)
                f.close()
        
        else:

            def set_language(lang, setup_window):

                with open(locale_path + lang + '.json', 'r') as f:
                    self.locale = json.load(f)
                    f.close()

                with open(locale_path + 'locale.txt', 'w') as f:
                    f.write(lang)
                    f.close()

                setup_window.destroy()


            raw_languages_list = os.listdir(locale_path)
            languages_list = []

            for lang in raw_languages_list:
                if lang.endswith('.json'):
                    languages_list.append(lang[:-5])

            first_run_setup = tkinter.Tk()
            first_run_setup.geometry('300x180')
            first_run_setup.title('Jpegzilla - First run setup')
            first_run_setup.resizable(False, False)
            first_run_setup.protocol('WM_DELETE_WINDOW', lambda:sys.exit())
            language = tkinter.StringVar(first_run_setup)
            language.set('Select a language')

            first_run_setup_skip = tkinter.Button(first_run_setup, text='Skip setup (Will use defaults)', command=lambda:set_language('en_US', first_run_setup))
            first_run_setup_done = tkinter.Button(first_run_setup, text='Accept settings', command=lambda:set_language(language.get(), first_run_setup))
            first_run_setup_lang = tkinter.OptionMenu(first_run_setup, language, *languages_list)
            first_run_setup_text = tkinter.Label(first_run_setup, text='Thanks for using Jpegzilla!\nPlease choose a language you wanna use\nor click "SKIP".\n')

            first_run_setup_text.pack()
            first_run_setup_lang.pack()
            first_run_setup_skip.pack(fill='x', side='bottom')
            first_run_setup_done.pack(fill='x', side='bottom')

            first_run_setup.mainloop()

            print('Loaded language: ' + self.locale['locale-name'])



        # Check if Mozjpeg is available.
        if OS == 'Windows':

            win_paths = os.getenv('PATH').split(';')

            if os.path.isfile('./cjpeg.exe') and glob.glob('./libjpeg-*.dll'):
                print(self.locale['mozjpeg-found-local-dir'])
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
                    sys.exit()



        else:

            if not os.path.isfile('/usr/bin/cjpeg') or not os.path.isfile('/bin/cjpeg'):
                print(self.locale['mozjpeg-not-found-error'])
                sys.exit()

        self.bg = '#FEFEFE' # Background color
        self.fg = '#000000' # Foreground color
        self.fgdis = '#555555' # Foreground color of disabled element

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

        for bid, button in self.buttons.items():
            button.place(x=dpos[0], y=dpos[1])
            dpos[0] += 220

        # Parameters/Options

        self.cjpeg_parameters = {
                '-quality': tkinter.IntVar(),
                '-smooth': tkinter.IntVar(),
                '-progressive': tkinter.IntVar(),
                '-greyscale': tkinter.IntVar(),
                '-arithmetic': tkinter.IntVar(),
                '-colorformat': tkinter.StringVar(self.root)
                }

        self.cjpeg_parameters['-colorformat'].set('YUV 4:2:0')

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
                    variable=self.cjpeg_parameters['-arithmetic']
                    ),
                'colorformat': tkinter.OptionMenu(
                    self.root, 
                    self.cjpeg_parameters['-colorformat'], *['YUV 4:2:0', 'YUV 4:2:2', 'YUV 4:4:4', 'RGB']
                    )
                }

        # - Set the defaults
        self.gui_options['progressive'].select()
        self.gui_options['quality'].set(90)

        # - Place items
        self.gui_options['quality'].place(x=10, y=45)
        self.gui_options['smoothing'].place(x=10, y=105)
        self.gui_options['progressive'].place(x=220, y=70)
        self.gui_options['greyscale'].place(x=220, y=90)
        self.gui_options['arithmetic'].place(x=220, y=110)
        self.gui_options['colorformat'].place(x=225, y=130)


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
        self.root.bind('<Shift-E>', lambda x:subprocess.Popen(['start' if OS == 'Windows' else 'xdg-open', 'https://waa.ai/XxXN'], stdout=FNULL, stderr=subprocess.STDOUT))

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
        filename = ntpath.basename(selected_file[2])

        self.preview_window = tkinter.Toplevel(self.root)
        self.preview_window.title(self.locale['image-preview-title'].format(filename))

        # Open in image viewer
        oiiv_button = tkinter.Button(
                self.preview_window,
                width='600',
                text=self.locale['open-in-image-viewer'],
                command=lambda:subprocess.Popen([
                    'start' if OS == 'Windows' else 'xdg-open',
                    TEMPDIR + filename if selected_file[1] == self.locale['status-completed'] else selected_file[2]
                    ])
                )
        oiiv_button.pack()

        self.preview_imgfile = Image.open( TEMPDIR + filename if selected_file[1] == self.locale['status-completed'] else selected_file[2] )

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
            
            filesize = hurry.filesize.size(os.stat(image).st_size)

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

                subprocess.Popen(c, shell=True, stdout=subprocess.PIPE).wait()
                self.file_queue.item(entry, values=( entry_data[0] + ' -> ' + hurry.filesize.size(os.stat(TEMPDIR + img + extension).st_size), self.locale['status-completed'], entry_data[2] ))

            if self.cancel_thread:
                self.cancel_thread = False
                break

        self.buttons['run'].configure(state='normal')
        self.buttons['save'].configure(state='normal')
        self.cancel_button.configure(state='disabled')



if __name__ == '__main__':
    
    try:
        if sys.argv[1].startswith('-'):

            if sys.argv[1] in ['-v', '--version']:
                print(self.locale['version-info'].format(VER))
            elif sys.argv[1] in ['-h', '--help']:
                print(self.locale['help-info'])
            else:
                print(self.locale['unknown-argument'])
    
        else:
            raise IndexError

    except IndexError:
        jz = jpegzilla()

