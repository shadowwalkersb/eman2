from eman2_gui import emimagemx
import inspect

def test_classes_init():
    objs = []
    for d in inspect.getmembers(emimagemx):
        obj = getattr(emimagemx, d[0])
        if inspect.isclass(obj) and obj.__module__ == 'eman2_gui.emimagemx':
            print(d, obj.__module__)
            objs.append(obj())
    
    print objs
