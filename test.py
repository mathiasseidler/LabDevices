from enthought.traits.api import HasTraits, Str, Instance, Array, Button, Any, Enum, Int, Event,Trait, Callable
import numpy as np

import numpy as np
from enthought.traits.api import HasTraits, Array, Int, Str, NO_COMPARE
from enthought.traits.ui.api \
    import View, Item

class ArrayEditorTest ( HasTraits ):
    flag=Int(0)
    str=Str('')
    arr = Array(np.int, (3,3), comparison_mode=NO_COMPARE)

    def _flag_changed(self):
        self.str+='changed\n'
        self.arr[0,0]+=1
        self.arr = self.arr
        print self.arr

    view = View(Item('flag', style='custom',label='Flag'),
                Item('str', style='custom', label='Str'),
                Item('arr', style='custom', show_label=False,),
                )


if __name__ == '__main__':
    ArrayEditorTest().configure_traits() 

    
    
