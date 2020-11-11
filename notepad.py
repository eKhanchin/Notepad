#!/usr/bin/env python3

import os
import sys
import subprocess
from tkinter import filedialog
from tkinter import Label
from tkinter import Menu
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import StringVar
from tkinter import Tk
from tkinter import Toplevel
from tkinter import ttk


class Notepad:
    '''A simple notepad application'''

    def __init__(self, master):
        '''
        Parameters
        ----------
            master : object
                tkinter root window object
        '''

        self.master = master
        self.master.title('Untitled - Notepad')
        self.master.geometry('800x600+500+400')
        self.master.protocol("WM_DELETE_WINDOW", self.exit_app)

        self._current_file_path = None

        # Menu bar fields
        menubar = Menu(self.master)

        # File menu
        self.create_file_menu_fields(menubar)

        # Edit menu
        self.create_edit_menu_fields(menubar)

        # Tools menu
        self.create_tools_menu_fields(menubar)

        # Help menu
        self.create_help_menu_fields(menubar)

        # Adds menu bar to the GUI
        self.master.config(menu=menubar)

        # Text fields
        self._text = scrolledtext.ScrolledText(self.master, undo=True,\
            background='white')
        self._text.place(x=0, y=0, relwidth=1, relheight=1)
        self._text.bind('<<Selection>>', self.selection_event_handler)
        self._text.bind('<Control-x>', self.cut_text)
        self._text.bind('<Control-c>', self.copy_text)
        self._text.bind('<Control-v>', self.paste_text)
        self._text.bind('<Control-a>', self.select_all)

        # When path is given as an argument
        if len(sys.argv) > 1 and sys.argv[1] and os.path.isfile(sys.argv[1]):
            self.open_file(file_path=sys.argv[1])

    def create_file_menu_fields(self, menubar):
        '''Creates "file" menu fields.
        
        Parameters
        ----------
            menubar : object
                tkinter menu object
        '''

        filemenu = Menu(menubar, tearoff=0)
        
        filemenu.add_command(label='New', command=self.new_file)
        filemenu.entryconfig('New', accelerator='Ctrl+N')
        self.master.bind('<Control-n>', self.new_file)

        filemenu.add_command(label='Open', command=self.open_file)
        filemenu.entryconfig('Open', accelerator='Ctrl+O')
        self.master.bind('<Control-o>', self.open_file)

        filemenu.add_command(label='Save', command=self.save_file)
        filemenu.entryconfig('Save', accelerator='Ctrl+S')
        self.master.bind('<Control-s>', self.save_file)

        filemenu.add_command(label='Save As', command=self.save_as_file)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.exit_app)

        menubar.add_cascade(label='File', menu=filemenu)
    
    def create_edit_menu_fields(self, menubar):
        '''Creates "edit" menu fields.
        
        Parameters
        ----------
            menubar : object
                tkinter menu object
        '''

        self._editmenu = Menu(menubar, tearoff=0)

        self._editmenu.add_command(label='Cut', command=self.cut_text)
        self._editmenu.entryconfig('Cut', accelerator='Ctrl+X')

        self._editmenu.add_command(label='Copy', command=self.copy_text)
        self._editmenu.entryconfig('Copy', accelerator='Ctrl+C')

        self._editmenu.add_command(label='Paste', command=self.paste_text)
        self._editmenu.entryconfig('Paste', accelerator='Ctrl+V')

        self._editmenu.add_command(label='Delete', command=self.delete_text)

        menubar.add_cascade(label='Edit', menu=self._editmenu)

        self.disable_edit_labels()
    
    def create_tools_menu_fields(self, menubar):
        '''Creates "tools" menu fields.
        
        Parameters
        ----------
            menubar : object
                tkinter menu object
        '''

        toolsmenu = Menu(menubar, tearoff=0)
        toolsmenu.add_command(label='Finder', command=self.open_finder)
        toolsmenu.entryconfig('Finder', accelerator='Ctrl+F')
        self.master.bind('<Control-f>', self.open_finder)

        menubar.add_cascade(label='Tools', menu=toolsmenu)
    
    def create_help_menu_fields(self, menubar):
        '''Creates "help" menu fields.
        
        Parameters
        ----------
            menubar : object
                tkinter menu object
        '''

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label='About notepad', command=self.view_about)

        menubar.add_cascade(label='Help', menu=helpmenu)

    def new_file(self, event=None):
        '''Clears text field to be blank.
        
        Parameters
        ----------
            event : object
                A bind key event
        '''

        # Suggests to save a file if changes were made
        self.check_changes_in_text()
        
        self._text.delete('1.0', 'end')
        self._current_file_path = None
        self.master.title('Untitled - Notepad')
        self._text.edit_modified(0)

    def open_file(self, event=None, file_path=None):
        '''Opens selected by user file.
        
        Parameters
        ----------
            event : object
                A bind key event
            file_path : string
                File\'s path to open
        '''

        # Suggests to save a file if changes were made
        self.check_changes_in_text()

        if not file_path:
            # Asks user to select which file to open
            file_path = filedialog.askopenfilename(filetypes=\
                (('Text files', '*.txt'), ('All files', '*.*')))
        if file_path:
            file_handler = open(file_path, 'r')
            if file_handler:
                text_read = file_handler.read()
                file_handler.close()
                self._text.delete('1.0', 'end')
                self._text.insert('1.0', text_read)
                self.change_title(file_path)
                self._current_file_path = file_path
                self._text.edit_modified(0)

    def save_file(self, event=None):
        '''Saves current text to it\'s file.
        
        Parameters
        ----------
            event : object
                A bind key event
        '''

        if self._current_file_path:
            # When existing file is open, save is made without asking for path again
            file_handler = open(self._current_file_path, 'w')  
            if file_handler:
                text_to_save = str(self._text.get('1.0', 'end'))
                file_handler.write(text_to_save)
                file_handler.close()
                self.change_title(self._current_file_path)
                self._text.edit_modified(0)
        else:
            # When this is a new file, never saved, asks a user for a path
            self.save_as_file()
    
    def save_as_file(self):
        '''Saves current text to a selected file'''

        # Gets file path from a user
        file_path = filedialog.asksaveasfilename(defaultextension='.txt',\
             filetypes=(('Text files', '*.txt'), ('All files', '*.*')))
        if file_path:
            # When file path was selected, calls save function on that path
            self._current_file_path = file_path
            self.save_file()
    
    def exit_app(self):
        '''Closes the application'''

        self.check_changes_in_text()
        self.master.quit()
        
    def change_title(self, file_path):
        '''Changes application\'s title when the file with the current
        text exists.
        
        Parameters
        ----------
            file_path : string
                File\'s path
        '''

        file_name = os.path.basename(file_path)
        self.master.title(file_name + ' - Notepad')
    
    def check_changes_in_text(self):
        '''Checks whether the text in the text field has been modified'''

        if self._text.edit_modified():
            # When text was modified
            reply = messagebox.askyesno('Save changes',\
                'The file has been modified.\nDo you want to save the changes?')
            if reply:
                self.save_file()

    def enable_edit_labels(self):
        '''Enables "edit" menu labels when text is selected'''

        # Enables Cut, Copy, Paste and Delete labels
        self._editmenu.entryconfig('Cut', state='normal')
        self._editmenu.entryconfig('Copy', state='normal')
        self._editmenu.entryconfig('Delete', state='normal')

        if self.master.clipboard_get():
            self._editmenu.entryconfig('Paste', state='normal')
    
    def disable_edit_labels(self):
        '''Disables "edit" menu labels when text is not selected'''

        # Disables Cut, Copy, Paste and Delete labels
        self._editmenu.entryconfig('Cut', state='disabled')
        self._editmenu.entryconfig('Copy', state='disabled')
        self._editmenu.entryconfig('Delete', state='disabled')

        if not self.master.clipboard_get():
            self._editmenu.entryconfig('Paste', state='disabled')
    
    def selection_event_handler(self, event):
        '''Handles event when a text is selected/deselected.
        
        Parameters
        ----------
            event : object
                A selection bind event
        '''

        if self._text.tag_ranges('sel'):
            # There is selection
            self.enable_edit_labels()
        else:
            self.disable_edit_labels()
    
    def cut_text(self, event=None):
        '''Cuts selected text.
        
        Parameters
        ----------
            event : object
                A bind key event
        '''

        self.copy_text()
        self.delete_text()

        return 'break'
    
    def copy_text(self, event=None):
        '''Copies selected text to the clipboard.
        
        Parameters
        ----------
            event : object
                A bind key event
        '''

        self.master.clipboard_clear()
        text_to_copy = self._text.get('sel.first', 'sel.last')
        self.master.clipboard_append(text_to_copy)

        return 'break'
    
    def paste_text(self, event=None):
        '''Pastes a text from the clipboard.
        
        Parameters
        ----------
            event : object
                A bind key event
        '''
        
        text_to_paste = self.master.clipboard_get()
        self._text.insert('insert', text_to_paste)

        return 'break'
    
    def delete_text(self):
        '''Deletes selected text'''

        self._text.delete('sel.first', 'sel.last')
        self.disable_edit_labels()

        return 'break'

    def view_about(self):
        '''Opens a new window with description of the application'''
        
        about_window = Toplevel(self.master)
        about_window.wm_title('Notepad - About Notepad')
        about_window.resizable(False, False)

        self.define_window_geometry(about_window, 500, 105)

        Label(about_window, justify='left', text='\n'\
            + 'This application is a basic version of Windows 10 Notepad, and '\
            + 'can be run on Unix.'\
            + '\nWritten in Python3 as a personal project.'\
            + '\n\nMade by Eugeny Khanchin =]').pack(ipady=10)

    def select_all(self, event=None):
        '''Selects all text inside the text widget.
        
        Parameters
        ----------
            event : object
                A bind key event
        '''
        
        self._text.tag_add('sel', 1.0, 'end')

        return 'break'
    
    def open_finder(self, event=None):
        '''Creates and opens a finder window that allows to find a text
        inside the text widget.
        
        Parameters
        ----------
            event : object
                A bind key event
        '''

        finder_window = Toplevel(self.master)
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
           command=lambda: finder_window.destroy())
        finder_window._cancel_button.place(x=197, y=60, width=60)

    def find_text(self, finder_window):
        '''Finds text inside the text widget.
        
        Parameters
        ----------
            finder_window : object
                tkinter toplevel window object
        '''

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
                # Recreates again the generator when it's exhausted
                finder_window._generator = self.find_next_generator(text)
                messagebox.showinfo('Finder Info', 'No more matchings!')
                finder_window.lift()
                finder_window.focus_force()
            else:
                # Select the matching word in the Text widget
                self._text.tag_remove('sel', '1.0', 'end')
                self._text.tag_add('sel', pos, f'{pos} + {countVar}c')
                self._text.see(pos)
                
    def find_next_generator(self, text):
        '''Gets a generator that creates an iter list of indexes of a
        matched text.
        
        Parameters
        ----------
            text : string
                Text to be found
        '''

        start = '1.0'
        countVar = StringVar()
        pos = self._text.search(text, start, stopindex='end', count=countVar)
        while pos:
            yield (pos, countVar.get())
            start = f'{pos} + {countVar.get()}c'
            pos = self._text.search(text, start, stopindex='end', count=countVar)

    def define_window_geometry(self, window, width, height):
        '''Defines given window\'s geometry.
        
        Parameters
        ----------
            window : object
                tkinter window object
            width : integer
                Window\'s width
            height : integer
                Window\'s height
        '''

        x = self.master.winfo_x()
        y = self.master.winfo_y()
        x += 10
        y += 10
        window.geometry(f'{width}x{height}+{x}+{y}')


def main():
    root = Tk()
    app = Notepad(root)
    root.mainloop()


if __name__ == '__main__':
    main()