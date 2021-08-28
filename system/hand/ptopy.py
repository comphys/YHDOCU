
def my_findkey(my_dict:dict,val) : # dict 변수에서 값으로 키 찾기
    try : return list(my_dict.keys())[list(my_dict.values()).index(val)]  
    except : return False 

# 변수의 이름을 받아, 변수가 정의되어 있으면 그 값 또는 None(비어있을경우), 정의되어 있지 않을 경우는 False
def my_isset(a:str,default=False) :
    if a in globals() : 
        if globals().get(a) : return globals().get(a)
        else : return None
    else : return default
