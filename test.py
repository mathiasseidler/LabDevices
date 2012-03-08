# key_bindings.py -- Example of a code editor with a
#                    key bindings editor

from enthought.traits.api \
    import Button, Code, HasPrivateTraits, Str
from enthought.traits.ui.api \
    import View, Item, Group, Handler, CodeEditor
from enthought.traits.ui.key_bindings \
    import KeyBinding, KeyBindings

key_bindings = KeyBindings(
    KeyBinding( binding1    = 'Ctrl-s',
                description = 'Save to a file',
                method_name = 'save_file' ),
    KeyBinding( binding1    = 'Ctrl-r',
                description = 'Run script',
                method_name = 'run_script' ),
    KeyBinding( binding1    = 'Ctrl-k',
                description = 'Edit key bindings',
                method_name = 'edit_bindings' )
)

# Traits UI Handler class for bound methods
class CodeHandler ( Handler ):

    def save_file ( self, info ):
        info.object.status = "save file"

    def run_script ( self, info ):
        info.object.status = "run script"

    def edit_bindings ( self, info ):
        info.object.status = "edit bindings"
        key_bindings.edit_traits()

class KBCodeExample ( HasPrivateTraits ):

    code   = Code
    status = Str
    kb    = Button(label='Edit Key Bindings')

    view = View( Group (
                 Item( 'code',
                       style     = 'custom',
                       resizable = True ),
                 Item('status', style='readonly'),
                 'kb',
                 orientation = 'vertical',
                 show_labels = False,
                 ),
               id = 'KBCodeExample',
               key_bindings = key_bindings,
               title = 'Code Editor With Key Bindings',
               resizable = True,

               handler   = CodeHandler() )

    def _kb_fired( self, event ):
        key_bindings.edit_traits()


if __name__ == '__main__':
    KBCodeExample().configure_traits()