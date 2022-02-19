import os,re,pprint,logging,html,json
from werkzeug.datastructures import ImmutableMultiDict

def my_log(logger_name) :

    logger = logging.getLogger(logger_name)

    if len(logger.handlers) > 0 : return logger
    
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s-%(filename)-15s - %(funcName)15s - %(lineno)3s : %(message)s') 

    file_handler = logging.FileHandler('logging.log',encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.propagate = 0
    return logger


def load_control(module_name,myapp):

    module = 'apps.'+ myapp +'.control.'
    if '-' in module_name : 
        folder, classn = module_name.split("-")
        module += folder + '.' + classn   
    else : 
        module += module_name
        classn =  module_name    
    
    classn = classn.capitalize()
    return getattr( __import__('%s' %(module), fromlist=[classn]), classn )


class Control :
    def __init__(self,**V) :
        '''
        모든 컨트롤러의 부모 컨트롤이다. 
        초기 셋팅값, DB연결, POST값의 dict 변환, 로깅 설정이 이루어진다.  
        '''
        self.V = V   # index.py 로 부터 전달받은 초기 파라미터
        self.D = {}  # view에 전달하기 위한 변수 
        
        imd = ImmutableMultiDict(V['_pos'])
        # control에 전달하는 기본 값
        self.CFG = V['_cfg']
        self.log  = my_log('my_logger') # 사용시 self.log.info(...), self.log.debug(...)
        self.info = self.log.info  
        # view에 전달하는 기본 값
        self.D['post'] = imd.to_dict()
        self.D['_skn'] = V['_skn']
        self.D['_bse'] = V['_bse']
        self.D['_mbl'] = V['_mbl']

        try :    self.C = self.CFG['general']
        except : self.C = None
        self.DB = None
        
        self.__parm()
        self.skin_dir = os.path.join(V['_pth'],'apps',V['_app'],'skin')
        self._auto()

    def _auto(self) :
        pass

    def __parm(self) :
        self.parm = []
        self.gets = {}
        if  self.V['_opt'] :
            self.parm = self.V['_opt'].split('/')

            if  self.V['_opt'].find('=') != -1 : 
                for temp in self.parm :
                    pos = temp.find('=')
                    if pos != -1 : self.gets[temp[:pos]] = temp[pos+1:]        
    
    def echo(self,D) :
        if self.DB : self.DB.close()
        if type(D) is str : return D
        if type(D) is dict :
            D['parm'] = self.parm
            D['gets'] = self.gets
            self.D |= D
            return self.D  
        return False

    def json(self,D) :
        return json.dumps(D) 

    def html(self,template) :
        if self.DB : self.DB.close()
        D={'parm':self.parm,'gets':self.gets,'skin':template}
        self.D |= D
        return self.D

    def test(self,Test) :
        '''
        디버깅을 위해서 Test 값의 내용을 확인하고자 할 때 호출한다.  
        '''  
        self.D['skin'] = 'sys_test.html'
        self.D['test'] =  pprint.pformat(Test,indent=2,width=80)
        if self.DB : self.DB.close()
        return self.D  

    def moveto(self,path,short=True) :
        self.D['_redirect'] = '/' + self.V['_app'] + '/' + path if short else '/' + path
        return self.D

    def model(self,module_name):
        if '-' in module_name : 
            folder, classn = module_name.split("-")
            module = 'apps.'+ self.V['_app'] +'.model.' + folder + '.' + classn   
        else : 
            module = 'apps.'+ self.V['_app'] +'.model.' + module_name
            classn =  module_name       
        
        classn = 'M_' + classn

        mod = __import__('%s' %(module), fromlist=[classn])
        return getattr( mod, classn )(self)

    def load_lib(self,module_name):
        module = 'system.lib.' + module_name
        classn =  module_name.upper()      
        
        mod = __import__('%s' %(module), fromlist=[classn])
        return getattr( mod, classn )(self)

    def db(self,dbname) :
        tmp =  self.load_lib('db')
        tmp.con(dbname)
        return tmp

    def load_app_lib(self,module_name):
        module = f"apps.{self.V['_app']}.lib.{module_name}"
        classn =  module_name.upper()      
        
        mod = __import__('%s' %(module), fromlist=[classn])
        return getattr( mod, classn )(self)

    def load_skin(self,opt='list') :
        classn = os.path.splitext(self.D['BCONFIG']['sub_'+ opt ])[0]
        module = f"apps.{self.V['_app']}.skin.board.{self.D['BCONFIG']['skin']}.{opt}.{classn}"
        mod = __import__('%s' %(module), fromlist=[classn])
        return getattr( mod, classn )(self)

    def set_message(self,msg,typ='notice') :
        self.DB.exe(f"UPDATE act_message SET type='{typ}', message='{msg}' WHERE no=1")    

    def get_message(self) :
        msg = self.DB.exe("SELECT * FROM act_message WHERE no=1", many=1, assoc=True)
        if msg['message'] :
            self.D['act_msg'] = f"<script>h_dialog.{msg['type']}('{msg['message']}')</script>"
            self.DB.exe("UPDATE act_message SET type='', message=''")
        else :
            self.D['act_msg'] = ''

    def html_decode(self,html_str) :
        return html.unescape(html_str)
        
    def html_encode(self,html_str,ignoreNewLine=True) :
        if ignoreNewLine : html_str = html_str.replace('\r\n','')
        return html.escape(html_str)

    def html_pretty(self,html_str) :
        html_new = re.sub(r'(<br>)([^\n])',r'\1\n\2',html_str)
        html_new = re.sub(r'<p(.*?)>([^\n])',r'<p\1>\n\2',html_str)
        html_new = re.sub(r'([^\n])<div(.*?)>',r'\1\n<div\2>\n',html_str)
        html_new = re.sub(r'([^\n])(<img|<span|<li)',r'\1\n\2',html_str)
        html_new = re.sub(r'([^\n])(<\/p>)',r'\1\n\2',html_str)
        html_new = re.sub(r'([^\n])(<\/div>)',r'\1\n\2',html_str)
        html_new = html_new.replace('><','>\n<')
        html_new = html_new.replace('class=""','')
        return html_new 

    # related to windows system
    def win_run(self,f_in) :
        #api.ShellExecute(0,'open',f_in,None,None,1)
        os.startfile(f_in)
    
    def open_explorer(self,folder) :
        os.startfile(folder)
# --------------------------------------------------------------------------------------------------------------
class Model :
    def __init__(self,SYS) :
        self.SYS  = SYS
        self.C    = SYS.C
        self.D    = SYS.D
        self.M    = {}
        self.DB   = SYS.DB
        self.info = SYS.info
        self.parm = SYS.parm
        self.gets = SYS.gets
        self.skin_dir = SYS.skin_dir
        self._auto()

    def find_key(self,my_dict:dict,val:str) : # dict 변수에서 값으로 키 찾기
        try : return list(my_dict.keys())[list(my_dict.values()).index(val)]  
        except : return False 

    def _auto(self) :
        pass

class SKIN :
    def __init__(self,SYS) :
        self.SYS  = SYS
        self.D    = SYS.D
        self.DB   = SYS.DB
        self.info = SYS.info
        self._auto()
    
    def _auto(self) :
        pass
