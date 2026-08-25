from system.core.load import Control
import system.core.my_utils as my
# import jwt #Pyjwt

class Check(Control) : 

    def _auto(self) :
        self.DB = self.db('stocks')
    # def _auto(self) :
    #     self.DB = self.db('stocks')

    # def is_valid_token(self) :
    #     s_key = self.DB.store('secret_key')
    #     try :
    #         jwt.decode(self.D['auth'],s_key,algorithms=['HS256'])
    #         return True
    #     except jwt.InvalidTokenError :
    #         return False

    # def rsn_check(self):

    #     if  self.is_valid_token() :
    #         self.DB.parameter_update('TX070',self.D['post']['date'])
    #         return self.D['post']['date']
    #     else :
    #         return "유효하지 않거나 위변조된 토큰입니다"

    def ip_check(self) :

        KW = self.load_app_lib('kiwoom')
        rst = KW.get_current_price('SOXL')
        return rst

    def check_rsn(self) :
        date = self.D['post']['rsn_check']
        self.DB.parameter_update('TX070',date)
        return "OK"