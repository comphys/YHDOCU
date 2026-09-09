from system.core.load import Control
import jwt 
class Sprice(Control) : 

    def _auto(self) :
        self.DB = self.db('stocks')

    def validate(func) :
        def wrapper(self) :
            sec_key  = self.DB.store('api_key')
            try :
                jwt.decode(self.I['_aut'],sec_key,algorithms=['HS256'])
            except jwt.InvalidTokenError :
                return {'Err':1,'Emsg':'Wrong token'}
            return func(self)
        return wrapper

    @validate
    def get_current_price(self) :

        KW = self.load_app_lib('kiwoom')
        rst = KW.get_current_price('SOXL')
        return rst

    @validate
    def new_token(self) :

        token = self.D['post']['token']
        token_date = self.D['post']['token_date']

        self.DB.store('dbapi_token',token)
        self.DB.store('dbapi_time',token_date)

        return '___OK___'

    @validate
    def old_token(self) :

        tk = {}
        tk['token'] = self.DB.store('dbapi_token')
        tk['token_date'] = self.DB.store('dbapi_time')

        return tk