class Control :
    def __init__(self) :
        self.D = {}
        self.C = {}
        self.I = {}
        self.I['_app'] = 'stocks'
        self.DB = None
        self.info = None
        self.parm = None
        self.gets = None
        self.skin_dir = None
        self._auto()

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

    def db(self,dbname,path='') :
        tmp =  self.load_lib('db')
        tmp.con(dbname,path)
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
