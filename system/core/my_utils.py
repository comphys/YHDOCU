import os, datetime, re

# 파일조작 관련 함수 
def file_split(filename) :
    '''
    filename을 입력으로 [경로, 파일명, 확장자]를 리턴함
    '''
    return (os.path.dirname(filename),os.path.basename(filename),os.path.splitext(filename)[1][1:])

def file_ctime(filename,opt=1) : #파일 생성시각
    ctime = os.path.getctime(filename)
    return timestamp_to_date(ctime,opt=1)

def file_mtime(filename,opt=1) : #파일 수정시각
    mtime = os.path.getmtime(filename)
    return timestamp_to_date(mtime,opt=1)

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

def delete_foler(fx) :
    try:
        os.rmdir(fx)
        return True
    except :
        return False

def rename_file(fx1, fx2) :
    return os.rename(fx1, fx2)

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

# time & date
def now_timestamp() :
    return int(datetime.datetime.now().timestamp())

def timestamp_to_date(ts='now',opt=1) :
    '''
    timestamp는 1970-01-01 00:00:00 를 기준으로 경과한 시간(한국은 +9시간)
    '''
    if ts=='now' : ts = int(datetime.datetime.now().timestamp())

    if    opt == 1 : t_format = "%Y-%m-%d %H:%M:%S"
    elif  opt == 2 : t_format = "%Y/%m/%d %H:%M:%S"
    elif  opt == 3 : t_format = "%y-%m-%d %H:%M"  
    elif  opt == 4 : t_format = "%y%m%d"   
    elif  opt == 5 : t_format = "%Y/%m/%d %H:%M" 
    elif  opt == 6 : t_format = "%y/%m/%d %H:%M:%S" 
    else  : t_format = opt 

    return datetime.datetime.fromtimestamp(ts).strftime(t_format)

def rg_ex(op,txt) :
    if op is 'mobile' : see = re.compile('010-\d{3,4}-\d{4}') 
    return  True if see.match(txt) else False 