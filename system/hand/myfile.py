import os

def get_dirs(path,*sub) :
    _dir = os.path.join(path,*sub)
    return [d for d in os.listdir(_dir) if os.path.isdir(os.path.join(_dir, d))]

def get_files(path,*sub,ext=None) :
    _dir = os.path.join(path,*sub)
    if ext :
        ext = '.' + ext
        return [f for f in os.listdir(_dir) if f.endswith(ext) ]
    else :
        return [f for f in os.listdir(_dir) if os.path.isfile(os.path.join(_dir, f))]