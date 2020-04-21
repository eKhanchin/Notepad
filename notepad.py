#!/usr/intel/bin/python3 -w

'''
This is a simple notepad application made as a personal project.
'''

import sys
import os

from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import messagebox


class Notepad:
    def __init__(self, master):
        self._master = master
        self._master.title('Untitled - Notepad')
        self._master.geometry('800x600+500+400')
        self._master.protocol("WM_DELETE_WINDOW", self.exit_app)

        self._current_file_path = None

        # Menu bar fields
        menubar = Menu(self._master)

        # File menu
        filemenu = Menu(menubar, tearoff=0)

        filemenu.add_command(label='New', command=self.new_file)
        filemenu.entryconfig('New', accelerator='Ctrl+N')
        self._master.bind('<Control-n>', self.new_file)

        filemenu.add_command(label='Open', command=self.open_file)
        filemenu.entryconfig('Open', accelerator='Ctrl+O')
        self._master.bind('<Control-o>', self.open_file)

        filemenu.add_command(label='Save', command=self.save_file)
        filemenu.entryconfig('Save', accelerator='Ctrl+S')
        self._master.bind('<Control-s>', self.save_file)

        filemenu.add_command(label='Save As', command=self.save_as_file)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.exit_app)

        menubar.add_cascade(label='File', menu=filemenu)

        # Edit menu
        self._editmenu = Menu(menubar, tearoff=0)
        self._editmenu.add_command(label='Cut', command=self.cut_text)
        self._editmenu.add_command(label='Copy', command=self.copy_text)
        self._editmenu.add_command(label='Paste', command=self.paste_text)
        self._editmenu.add_command(label='Delete', command=self.delete_text)
        menubar.add_cascade(label='Edit', menu=self._editmenu)

        self.disable_edit_labels()

        # Tools menu
        toolsmenu = Menu(menubar, tearoff=0)
        toolsmenu.add_command(label='Finder', command=self.open_finder)
        toolsmenu.entryconfig('Finder', accelerator='Ctrl+F')
        self._master.bind('<Control-f>', self.open_finder)

        menubar.add_cascade(label='Tools', menu=toolsmenu)  

        # Help menu
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label='About notepad', command=self.view_about)
        menubar.add_cascade(label='Help', menu=helpmenu)

        # Adds menu bar to the GUI
        self._master.config(menu=menubar)

        # Text fields
        self._text = scrolledtext.ScrolledText(self._master, wrap=None)
        self._text.place(x=0, y=0, relwidth=1, relheight=1)
        self._text.bind('<<Selection>>', self.selection_event_handler)

        # Additional bind keys
        self._master.bind('<Control-a>', self.select_all)

        # When path is given as an argument
        if len(sys.argv) > 1 and sys.argv[1] and os.path.isfile(sys.argv[1]):
            self.open_file(file_path=sys.argv[1])

    # File tab functions
    def new_file(self, event=None):
        self.check_changes_in_text()
        
        self._text.delete('1.0', END)
        self._current_file_path = None
        self._master.title('Untitled - Notepad')
        self._text.edit_modified(0)

    def open_file(self, event=None, file_path=None):
        self.check_changes_in_text()

        if not file_path:
            # Asks user to select file to open
            file_path = filedialog.askopenfilename(filetypes=(('Text files', '*.txt'),\
                ('All files', '*.*')))
        if file_path:
            file_handler = open(file_path, 'r')
            if file_handler:
                text_read = file_handler.read()
                file_handler.close()
                self._text.delete('1.0', END)
                self._text.insert('1.0', text_read)
                self.change_title(file_path)
                self._current_file_path = file_path
                self._text.edit_modified(0)

    def save_file(self, event=None):
        if self._current_file_path:
            # When existing file is open, save is made without asking for path again
            file_handler = open(self._current_file_path, 'w')  
            if file_handler:
                text_to_save = str(self._text.get('1.0', END))
                file_handler.write(text_to_save)
                file_handler.close()
                self.change_title(self._current_file_path)
                self._text.edit_modified(0)
        else:
            # When this is a new file, never saved, asks user for a path
            self.save_as_file()
    
    def save_as_file(self):
        # Gets file path from user
        file_path = filedialog.asksaveasfilename(defaultextension='.txt',\
             filetypes=(('Text files', '*.txt'), ('All files', '*.*')))
        if file_path:
            # When file path was selected, calls save function on that path
            self._current_file_path = file_path
            self.save_file()
    
    def exit_app(self):
        self.check_changes_in_text()
        self._master.quit()
        
    def change_title(self, file_path):
        # Changes app's title when file with the current text exists
        file_name = os.path.basename(file_path)
        self._master.title(file_name + ' - Notepad')
    
    def check_changes_in_text(self):
        if self._text.edit_modified():
            # When text was modified
            reply = messagebox.askyesno('Save changes', 'The file has been modified.\nDo you want to save the changes?')
            if reply:
                self.save_file()
    # File tab functions - end

    # Edit tab functions
    def enable_edit_labels(self):
        # Enables Cut, Copy, Paste and Delete labels when text is selected
        self._editmenu.entryconfig('Cut', state='normal')
        self._editmenu.entryconfig('Copy', state='normal')
        self._editmenu.entryconfig('Delete', state='normal')

        if self._master.clipboard_get():
            self._editmenu.entryconfig('Paste', state='normal')
    
    def disable_edit_labels(self):
        # Disables Cut, Copy, Paste and Delete labels when text is not selected
        self._editmenu.entryconfig('Cut', state='disabled')
        self._editmenu.entryconfig('Copy', state='disabled')
        self._editmenu.entryconfig('Delete', state='disabled')

        if not self._master.clipboard_get():
            self._editmenu.entryconfig('Paste', state='disabled')
    
    def selection_event_handler(self, event):
        # Handles text selection event
        if self._text.tag_ranges(SEL):
            self.enable_edit_labels()
        else:
            self.disable_edit_labels()
    
    def cut_text(self, event=None):
        # Cuts selected text
        self.copy_text()
        self.delete_text()
    
    def copy_text(self, event=None):
        # Copies selected text to clipboard
        text_to_copy = self._text.get(SEL_FIRST, SEL_LAST)
        self._master.clipboard_clear()
        self._master.clipboard_append(text_to_copy)
    
    def paste_text(self, event=None):
        # Pastes text from clipboard
        text_to_paste = self._master.clipboard_get()
        self._text.insert(INSERT, text_to_paste)
    
    def delete_text(self, event=None):
        # Deletes selected text
        self._text.delete(SEL_FIRST, SEL_LAST)
        self.disable_edit_labels()
    # Edit tab functions - end

    # Help tab functions
    def view_about(self):
        # Opens new window with description about this app
        about_window = Toplevel(self._master)
        about_window.wm_title('Notepad - About Notepad')

        self.define_window_geometry(about_window, 500, 150)

        Label(about_window, text='\n'\
            + 'This application is a basic version of Windows 10 Notepad, and can be run on Unix.'\
            + '\nWritten in Python3 as a personal project.'\
            + '\n\n Made by Eugeny Khanchin =]').pack(ipady=20)
    # Help tab functions - end

    def select_all(self, event=None):
        # Selects all text inside Text widget
        self._text.tag_add('sel', 1.0, 'end')
    
    # Tools tab functions
    def open_finder(self, event=None):
        # Creates and opens the Finder window
        finder_window = Toplevel(self._master)
        finder_window.wm_title('Notepad - Finder')
        self.define_window_geometry(finder_window, 374, 115)
        finder_window.takefocus = True

        finder_window._current_text = None

        Label(finder_window, text='Text to find:').place(x=10, y=10)

        finder_window._finder_entry = ttk.Entry(finder_window, width=50)
        finder_window._finder_entry.place(x=10, y=30)

        finder_window._find_button = ttk.Button(finder_window, text='Find',\
           command=lambda: self.find_text(finder_window))
        finder_window._find_button.place(x=117, y=60, width=60)

        finder_window._cancel_button = ttk.Button(finder_window, text='Cancel',\
           command=lambda: self.cancel_sub_window(finder_window))
        finder_window._cancel_button.place(x=197, y=60, width=60)

    def find_text(self, finder_window):
        text = finder_window._finder_entry.get()
        if text != finder_window._current_text:
            # When given text is different from the previous search
            finder_window._generator = self.find_next_generator(text)
            finder_window._current_text = text

        if finder_window._generator:
            try:
                # Gets next value from the generator
                (pos, countVar) = next(finder_window._generator)
            except:
                # When generator is exhausted, it is recreated again
                finder_window._generator = self.find_next_generator(text)
                messagebox.showinfo('Finder Info', 'No more matchings!')
                finder_window.lift()
                finder_window.focus_force()
            else:
                # Select the matching word in the Text widget
                self._text.tag_remove('sel', '1.0', 'end')
                self._text.tag_add('sel', pos, f'{pos} + {countVar}c')
                self._text.see(pos)
                
    def find_next_generator(self, text, start="1.0"):
        # A generator that creates a iter list of indexes of a matched text
        countVar = StringVar()
        pos = self._text.search(text, start, stopindex="end", count=countVar)
        while pos:
            yield (pos, countVar.get())
            start = f'{pos} + {countVar.get()}c'
            pos = self._text.search(text, start, stopindex="end", count=countVar)
    # Tools tab functions - end

    def define_window_geometry(self, window, width, height):
        # Defines geometry of the given sub window
        x = self._master.winfo_x()
        y = self._master.winfo_y()
        x += 10
        y += 10
        window.geometry(f'{width}x{height}+{x}+{y}')

    def cancel_sub_window(self, window):
        window.destroy()


def main():
    root = Tk()
    app = Notepad(root)
    root.mainloop()


if __name__ == '__main__':
    main()