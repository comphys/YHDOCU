import os, datetime 

def file_split(filename) :
    '''
    filename을 입력으로 [경로, 파일명, 확장자]를 리턴함
    '''
    return [os.path.dirname(filename),os.path.basename(filename),os.path.splitext(filename)[1][1:]]


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
    else  : t_format = opt 

    return datetime.datetime.fromtimestamp(ts).strftime(t_format)
