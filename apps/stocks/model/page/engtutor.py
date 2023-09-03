from system.core.load import Model
import system.core.my_utils as my

class M_engtutor(Model) :

    def view(self) :
        self.D['오늘날자']  = my.timestamp_to_date(opt=7) 
        self.D['오늘요일']  = my.dayofdate(self.D['오늘날자'])
        self.D['오픈키'] = self.DB.store('openai_key')
