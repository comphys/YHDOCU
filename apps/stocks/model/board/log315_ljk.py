from system.core.load import Model
import system.core.my_utils as my

class Ajax(Model) :

    
    def dailyCheckUpdate(self) :

        odrday = self.D['post']['odrday']
        option = self.D['post']['option']
        
        if  option == 'RSN'   : key = 'TX070'
        if  option == 'N315'  : key = 'N0710_' + self.D['USER']['uid']
        if  option == 'LUCKY' : key = 'L0500'
        self.DB.parameter_update(key,odrday)



