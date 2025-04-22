from system.core.load import Control

class Rsn_ajax(Control) :
    
    def back(self) :
        sday  = self.D['post']['sday']
        eday  = self.D['post']['eday']
        rmon  = self.D['post']['rmon']
        
        
        rst = {'info':"피드백이 정상적으로 작동중입니다", 'sday':sday, 'eday':eday, 'add3':rmon}
        return self.json(rst)
        