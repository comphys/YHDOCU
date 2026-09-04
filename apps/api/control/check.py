from system.core.load import Control
import jwt #Pyjwt

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

    def validate(func) :
        def wrapper(self) :
            sec_key  = '정용훈은정유진을사랑해'
            try :
                jwt.decode(self.I['_aut'],sec_key,algorithms=['HS256'])
            except jwt.InvalidTokenError :
                return {'Err':1,'Emsg':'Wrong token'}
            return func(self)
        return wrapper


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

    @ validate
    def check_rsndiy(self) :
        cd = {}
        cd['rsn'] = self.DB.parameter('TX070')
        cd['diy'] = self.DB.parameter('A0710')
        self.info(self.I['_aut'])
        return cd
