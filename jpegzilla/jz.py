#!/usr/bin/python3

import sys, ntpath, os, subprocess, threading, hurry.filesize, platform, shutil
import tkinter, tkinter.ttk, tkinter.filedialog
from PIL import Image, ImageTk

FNULL = open(os.devnull, 'w')
OS = platform.system()
VER = '0.4'

TEMPDIR = ((os.getenv('WINDIR') + '/tmp/jpegzilla/') if OS == 'Windows' else '/tmp/jpegzilla/')
if not os.path.exists(TEMPDIR):
    os.mkdir(TEMPDIR)

class jpegzilla:

    def __init__(self):

        # Create root window.
        self.root = tkinter.Tk()
        self.root.geometry('600x450')
        self.root.title("JpegZilla - A MozJPEG frontend.")
        self.root.resizable(False, False)

        # Primary buttons

        self.buttons = {
                    'run':    tkinter.Button(self.root, text='Compress', state='disabled', command=lambda:self.run()),
                    'save':   tkinter.Button(self.root, text='Save as...', state='disabled', command=lambda:self.save_all()),
                    'import': tkinter.Button(self.root, text='Import items', command=lambda:self.select_files()),
                }

        dpos = [35, 10] # x, y

        for bid, button in self.buttons.items():
            button.place(x=dpos[0], y=dpos[1])
            dpos[0] += 213

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
                'quality': tkinter.Scale(self.root, label='Image quality', orient='horizontal', length='200', variable=self.cjpeg_parameters['-quality']),
                'smoothing': tkinter.Scale(self.root, label='Smoothing', orient='horizontal', length='200', variable=self.cjpeg_parameters['-smooth']),
                'progressive': tkinter.Checkbutton(self.root, text='Progressive', variable=self.cjpeg_parameters['-progressive']),
                'greyscale': tkinter.Checkbutton(self.root, text='Greyscale', variable=self.cjpeg_parameters['-greyscale']),
                'arithmetic': tkinter.Checkbutton(self.root, text='Use arithmetic coding', variable=self.cjpeg_parameters['-arithmetic']),
                'colorformat': tkinter.OptionMenu(self.root, self.cjpeg_parameters['-colorformat'], *['YUV 4:2:0', 'YUV 4:2:2', 'YUV 4:4:4', 'RGB'])
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

        self.queue = tkinter.ttk.Frame(self.root)
        self.queue.pack(side='bottom')

        self.file_queue_rmdone = tkinter.Button(self.queue, text='Clear all saved', command=lambda:self.clean_completed())
        self.file_queue_rmdone.pack(side='top', anchor='e')

        self.queue_label = tkinter.Label(self.queue, text='Loaded files: 0')
        self.queue_label.pack(side='top', anchor='w')

        self.file_queue = tkinter.ttk.Treeview(self.queue, selectmode='browse')
        self.file_queue['columns'] = ('size', 'status', 'loc')
        self.file_queue.heading('#0', text='Filename')
        self.file_queue.column('#0', width=245, stretch='no')
        self.file_queue.heading('size', text='Size')
        self.file_queue.column('size', width=145, stretch='no')
        self.file_queue.heading('status', text='Status')
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

        self.queue_label.configure(text='Loaded files: {}'.format(str(len(self.file_queue.get_children()))))
        if not len(self.file_queue.get_children()):
            self.buttons['run'].config(state='disabled')


    def show_preview(self):
    
        selected_file = self.file_queue.item(self.file_queue.selection())['values']
        filename = ntpath.basename(selected_file[2])

        self.preview_window = tkinter.Toplevel(self.root)
        self.preview_window.title('Image preview: ' + filename)

        # Open in image viewer
        oiiv_button = tkinter.Button(
                self.preview_window,
                width='600',
                text='Open in default Image viewer',
                command=lambda:subprocess.Popen([
                    'start' if OS == 'Windows' else 'xdg-open',
                    TEMPDIR + filename if selected_file[1] == 'Completed' else selected_file[2]
                    ])
                )
        oiiv_button.pack()

        self.preview_imgfile = Image.open( TEMPDIR + filename if selected_file[1] == 'Completed' else selected_file[2] )

        required_width = 800
        wpercent = (required_width / float(self.preview_imgfile.size[0]) )
        hsize = int( (float(self.preview_imgfile.size[1]) * float(wpercent)) )
        self.preview_imgfile = self.preview_imgfile.resize((required_width, hsize), Image.ANTIALIAS)

        self.preview_image = ImageTk.PhotoImage(self.preview_imgfile)

        self.preview = tkinter.Label(self.preview_window, image=self.preview_image)
        self.preview.image = self.preview_image
        self.preview.pack(fill='both', expand='yes')

    def clean_completed(self):

        all_files = self.file_queue.get_children()
        for image in all_files:
            imginfo = self.file_queue.item(image)['values']
            if (imginfo[1] == 'Completed'):
                self.file_queue.delete(image)

    def save_all(self):

        location = tkinter.filedialog.askdirectory(title='Select directory to save compressed files', initialdir='~')

        compressed_images = self.file_queue.get_children()

        for image in compressed_images:
            child_data = self.file_queue.item(image)['values']
            filename = ntpath.basename(child_data[2])
            if child_data[1] == 'Completed':
                print('Moving: ' + TEMPDIR + filename + ' --> ' + location + '/' + filename)
                shutil.move(TEMPDIR + filename, location + '/' + filename)


    def select_files(self):

        filenames = tkinter.filedialog.askopenfilenames(
                    initialdir='~',
                    title='Select files to import',
                    filetypes=(
                        ('Compatible formats', ['*.jpeg', '*.jpg', '*.png', '*.tga', '*.bmp']),
                        ('All files', '*.*')
                    )
                )
        self.filenames = self.root.tk.splitlist(filenames)
    
        for image in self.filenames:
            
            filesize = hurry.filesize.size(os.stat(image).st_size)

            self.file_queue.insert('', 'end', text=ntpath.basename(image), values=(
                     filesize, 'New', image
                ))

        if self.filenames:
            self.buttons['run'].config(state='normal')

        self.queue_label.configure(text='Loaded files: {}'.format(str(len(self.file_queue.get_children()))))

    def run(self):

        self.compress_thread = threading.Thread(target=self.compress)
        self.compress_thread.start()

    def compress(self):

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

            if entry_data[1] == 'Completed':
                pass
            
            else:

                self.file_queue.item(entry, values=( entry_data[0], 'Running...', entry_data[2] ))

                c = (command.format(filename=(TEMPDIR + img + extension), targa=('-targa' if extension == '.tga' else '')) + ' ' + entry_data[2])

                subprocess.Popen(c, shell=True, stdout=subprocess.PIPE).wait()
                self.file_queue.item(entry, values=( entry_data[0] + ' -> ' + hurry.filesize.size(os.stat(TEMPDIR + img + extension).st_size), 'Completed', entry_data[2] ))

        self.buttons['save'].configure(state='normal')



if __name__ == '__main__':
    
    try:
        if sys.argv[1].startswith('-'):

            if sys.argv[1] in ['-v', '--version']:
                print('Jpegzilla ' + VER + '\nhttps://github.com/fabulouskana/jpegzilla')
            elif sys.argv[1] in ['-h', '--help']:
                print('Run program by typing "jpegzilla" or running script without any arguments.')
                print('     -v, --version  - Display version information')
            else:
                print('Unknown argument. Type --help for more information.')
    
        else:
            raise IndexError

    except IndexError:
        jz = jpegzilla()

