import sys,platform
import subprocess
from slack_sdk import WebClient
from datetime import datetime
from zoneinfo import ZoneInfo

_sysos = platform.system()
_mac_addr = {'Windows':'BCFCE7C9911F','Linux':'A475B980D0CA','Android':'A475B980D0CA'}
_rootpath = {'Windows':'/YHDOCU/','Linux':'/home/comphys/YHDOCU/','Android':'/data/data/com.termux/files/home/YHDOCU/'}
sys.path.append(_rootpath[_sysos])

class Control :

    def __init__(self) :
        self.D = {}
        self.I = {}
        self.I['_app'] = 'stocks'
        self.I['_dev'] = _sysos
        self.I['_rth'] = _rootpath[_sysos]
        self.I['_mac'] = _mac_addr[_sysos]
        self.DB = None
        self.info = None
        self.parm = None
        self.gets = None
        self.skin_dir = None
        self._auto()
        self.title=''

    def _auto(self) :
        pass

    def json(self,D) :
        return D 

    def model(self,module_name):
        if '-' in module_name : 
            folder, classn = module_name.split("-")
            module = 'apps.'+ self.I['_app'] +'.model.' + folder + '.' + classn   
        else : 
            module = 'apps.'+ self.I['_app'] +'.model.' + module_name
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
        tmp.con(dbname,self.I['_rth'])
        return tmp

    def load_app_lib(self,module_name):
        module = f"apps.{self.I['_app']}.lib.{module_name}"
        classn =  module_name.upper()      
        
        mod = __import__('%s' %(module), fromlist=[classn])
        return getattr( mod, classn )(self)

    
    def load_pajax(self,module_name,method_name):
        module = f"apps.{self.I['_app']}.model.page.{module_name}"
        classn =  'Ajax'  
        
        mod = __import__('%s' %(module), fromlist=[classn])
        ins = getattr( mod, classn )(self)
        return getattr( ins, method_name)
    
    def load_bajax(self,module_name,method_name):
        module = f"apps.{self.I['_app']}.model.board.{module_name}"
        classn =  'Ajax'  
        
        mod = __import__('%s' %(module), fromlist=[classn])
        ins = getattr( mod, classn )(self)
        return getattr( ins, method_name)
    
    def lprint(self,data) :
        if isinstance(data,list) :
            for d in data : print(d)
        else : print(data)

    def send_message(self,message) :
        if self.I['_dev'] == 'Android' :
            subprocess.run(["termux-notification","--title",self.title,"--content",message])
        elif self.I['_dev'] == 'Windows' :
            print(self.title,message)
        else :  
            client = WebClient(token=self.skey)
            client.chat_postMessage(channel= '주식', text= message)

    # Android 의 termux-api 를 통해 문자메세지를 보낸다.(사전권한 획득 필요, 안드로이드에서만 동작)
    def send_sms(phone_number='01027208737',message="") :
        subprocess.run(['termux-sms-send','-n',phone_number,message])

    def log(self,str) :
        hour_now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")  
        with open(self.I['_rth']+"logs/xtask.log","a",encoding="utf-8") as f:
            f.write(f"<span class='who-time'>{hour_now} :</span> {str}\n")
# --------------------------------------------------------------------------------------------------------------
class Model :
    def __init__(self,SYS) :
        self.SYS  = SYS
        self.D    = SYS.D
        self.M    = {}
        self.DB   = SYS.DB
        self._auto()

    def _auto(self) :
        pass
