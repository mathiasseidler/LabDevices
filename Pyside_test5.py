"""File dialog demo.

This demonstration shows how a program can use the FileDialog from the
enthought.pyface package to open files, and how to maintain a "current"
file, including whether or not the data being edited has been saved or
not.

This demonstration program only looks at the first line of any file that it
opens.  The "Save" function will overwrite the file with a single line that
contains the value shown in the editor.  (Don't "Load" any important
file with this program, because you will lose everything in that file if
you then hit the "Save" button accidentally!) 
"""

import os

from enthought.traits.api import HasTraits, Str, Bool, Button
from enthought.traits.ui.api import Handler, View, Item, UItem, HGroup
from enthought.pyface.api import FileDialog, OK, confirm, YES


class FooHandler(Handler):
    """Handler for the Foo class.
    This handler will
    (1) listen for changes to the 'filename' Trait of the object and
        update the window title when it changes; and
    (2) intercept request to close the window, and if the data is not saved,
        ask the user for confirmation.
    """

    def object_filename_changed(self, info):
        filename = info.object.filename
        if filename is "":
            filename = "<no file>"
        info.ui.title = "Editing: " + filename

    def close(self, info, isok):
        # Return True to indicate that it is OK to close the window.
        if not info.object.saved:
            response = confirm(info.ui.control,
                            "Value is not saved.  Are you sure you want to exit?")
            return response == YES
        else:
            return True
        

class Foo(HasTraits):

    value = Str

    saved = Bool(True)

    filedir = Str
    filename = Str

    save_button = Button("Save")
    save_as_button = Button("Save as")
    load_button = Button("Load")

    # Wildcard pattern to be used in file dialogs.
    file_wildcard = Str("Text file (*.txt)|*.txt|Data file (*.dat)|*.dat|All files|*")

    view = View(Item('value'),
                HGroup(
                    UItem('save_button', enabled_when='not saved and filename is not ""'),
                    UItem('save_as_button'),
                    UItem('load_button'),
                ),
                resizable=True,
                width=240,
                handler=FooHandler(),
                title="File Dialog Demo")
    
    #-----------------------------------------------
    # Trait change handlers
    #-----------------------------------------------

    def _value_changed(self):
        self.saved = False

    def _save_button_fired(self):
        self._save_to_file()
        
    def _save_as_button_fired(self):
        dialog = FileDialog(action="save as", wildcard=self.file_wildcard)
        dialog.open()
        if dialog.return_code == OK:
            self.filedir = dialog.directory
            self.filename = dialog.filename
            self._save_to_file()

    def _load_button_fired(self):
        dialog = FileDialog(action="open", wildcard=self.file_wildcard)
        dialog.open()
        if dialog.return_code == OK:
            f = open(dialog.path, 'r')
            data = f.readline()
            if data.endswith('\n'):
                data = data[:-1]
            self.value = data
            self.filedir = dialog.directory
            self.filename = dialog.filename
            self.saved = True

    #-----------------------------------------------
    # Private API
    #-----------------------------------------------

    def _save_to_file(self):
        """Save `self.value` to the file `self.filedir`+`self.filename`."""
        path = os.path.join(self.filedir, self.filename)
        f = open(path, 'w')
        f.write(self.value + '\n')
        f.close()
        self.saved = True


if __name__ == "__main__":
    f = Foo()
    f.configure_traits()