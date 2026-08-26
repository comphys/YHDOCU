from system.core.load import Control
import system.core.my_utils as my
# import jwt #Pyjwt

class Check(Control) : 

    def _auto(self) :
        self.DB = self.db('stocks')

    # def is_valid_token(self) :
    #     s_key = self.DB.store('secret_key')
    #     try :
    #         jwt.decode(self.D['auth'],s_key,algorithms=['HS256'])
    #         return True
    #     except jwt.InvalidTokenError :
    #         return False

    def ip_check(self) :

        KW = self.load_app_lib('kiwoom')
        rst = KW.get_current_price('SOXL')
        return rst

    def check_rsn(self) :
        date = self.D['post']['rsn_check']
        self.DB.parameter_update('TX070',date)
        return "OK"

    def check_diy(self) :
        date = self.D['post']['diy_check']
        self.DB.parameter_update('A0710',date)
        return "OK"

    def check_rsndiy(self) :
        rsn = self.DB.parameter('TX070')
        diy = self.DB.parameter('A0710')
        return {'rsn':rsn,'diy':diy}
