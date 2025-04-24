from system.core.load import Control
from flask import session

class Rsn_ajax(Control) :

    def _auto(self) :
        
        self.DB = self.db('stocks')
    
    def log_rsn(self) :
        
        RSN = self.load_app_lib('rsn')
        
        PD = {} # post data

        PD['기회자금'] = self.D['post']['기회자금']
        PD['안정자금'] = self.D['post']['안정자금']
        PD['생활자금'] = self.D['post']['생활자금']

        PD['시작일자'] = self.D['post']['시작일자']
        PD['종료일자'] = self.D['post']['종료일자']
        PD['기회시점'] = self.D['post']['기회시점']
        PD['기회회복'] = self.D['post']['기회회복']
        PD['안정시점'] = self.D['post']['안정시점']
        PD['안정회복'] = self.D['post']['안정회복']        
        
        PD['수료적용'] = 'on' if self.D['post']['수료적용'] == 'true' else 'off'
        PD['세금적용'] = 'on' if self.D['post']['세금적용'] == 'true' else 'off'
        PD['일밸런싱'] = 'on' if self.D['post']['일밸런싱'] == 'true' else 'off'
        PD['이밸런싱'] = 'on' if self.D['post']['이밸런싱'] == 'true' else 'off'
        PD['가상손실'] = 'on' if self.D['post']['가상손실'] == 'true' else 'off'
        
        key = self.D['post']['적용전략']
            
        RSN.D |= PD
        RSN.get_simResult(PD['시작일자'],PD['종료일자'])
        DC = RSN.get_simulLog(key)
        
        return self.json(DC)
            
        