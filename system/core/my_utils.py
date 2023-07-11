import os, re 
import shutil,math
from datetime import datetime, timedelta
from pytz import timezone

# number

def round_up(n,decimals=2) :
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

def ceil(n) :
    return math.ceil(n)

def sv(v,s='f') :
    return float(v.replace(',','')) if s=='f' else int(v.replace(',',''))

# 파일조작 관련 함수 
def file_split(filename) :
    '''
    filename을 입력으로 [경로, 파일명, 확장자]를 리턴함
    '''
    return (os.path.dirname(filename),os.path.basename(filename),os.path.splitext(filename)[1][1:])

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

def get_file_names(path) :
    _dir = os.path.join(path)
    temp = [f for f in os.listdir(_dir) if os.path.isfile(os.path.join(_dir, f))]
    return [os.path.splitext(f)[0] for f in temp]

def file_ctime(filename,opt=1) : #파일 생성시각
    ctime = os.path.getctime(filename) ; return timestamp_to_date(ctime,opt=1)

def file_mtime(filename,opt=1) : #파일 수정시각
    mtime = os.path.getmtime(filename) ; return timestamp_to_date(mtime,opt=1)

def file_size(filename) :
    return os.path.getsize(filename)

def makedir(directory) :
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
            return True
    except OSError:
        return False

def checkdir(fdir,d=True) :
    if d : 
        if os.path.isdir(fdir) : return True
        else : return False
    else :
        if os.path.isfile(fdir) : return True
        else : return False

def makefile(fname) :
    if os.path.isfile(fname) : return False
    f = open(fname,"w")
    f.close()
    return True

def delete_file(fx) :
    os.remove(fx) 

def clear_folder(fx) :
    for file in os.scandir(fx) :
        os.remove(file.path)

def delete_foler(fx) :
    try:
        os.rmdir(fx)
        return True
    except :
        return False

def rename_file(fx1, fx2) :
    return os.rename(fx1, fx2)

def copy_file(src, tgt) :
    shutil.copy(src,tgt)

def move_file(src, tgt) :
    shutil.move(src,tgt)

# string
def dequote(s):
    """
    If a string has single or double quotes around it, remove them.
    Make sure the pair of quotes match.
    If a matching pair of quotes is not found, return the string unchanged.
    """
    if (s[0] == s[-1]) and s.startswith(("'", '"')):
        return s[1:-1]
    return s

def rg_ex(op,txt) :
    if op == 'mobile' : see = re.compile('010-\d{3,4}-\d{4}') 
    return  True if see.match(txt) else False 


# time & date
def now_timestamp() :
    return int(datetime.now().timestamp())

def timestamp_to_date(ts='now',opt=1) :

    kst = timezone('Asia/Seoul')

    if ts=='now' : ts = int(datetime.now().timestamp())

    if    opt == 1 : t_format = "%Y-%m-%d %H:%M:%S"
    elif  opt == 2 : t_format = "%Y/%m/%d %H:%M:%S"
    elif  opt == 3 : t_format = "%y-%m-%d %H:%M"  
    elif  opt == 4 : t_format = "%y%m%d"   
    elif  opt == 5 : t_format = "%Y/%m/%d %H:%M" 
    elif  opt == 6 : t_format = "%y/%m/%d %H:%M:%S" 
    elif  opt == 7 : t_format = "%Y-%m-%d"
    else  : t_format = opt 

    return datetime.fromtimestamp(ts,kst).strftime(t_format)

def date_format_change(v,f1,f2) :
    return datetime.strptime(v,f1).strftime(f2)

def dayofdate(theday,delta=0) :
    dow = ('월','화','수','목','금','토','일')
    a = datetime.strptime(theday,'%Y-%m-%d')
    if delta : b = a+timedelta(days=delta) ; return (b.strftime('%Y-%m-%d'),dow[b.weekday()])
    else : return dow[a.weekday()]

def diff_day(day1,day2='') :
    a = datetime.strptime(day1,'%Y-%m-%d')
    b = datetime.now() if not day2 else datetime.strptime(day2,'%Y-%m-%d')
    c = b-a
    return c.days 
