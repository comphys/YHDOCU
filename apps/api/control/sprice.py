from system.core.load import Control


class Sprice(Control) : 

    def _auto(self) :
        self.DB = self.db('stocks')

    def get_current_price(self) :

        KW = self.load_app_lib('kiwoom')
        rst = KW.get_current_price('SOXL')
        return rst

    def get_token(self) :

        token = self.D['post']['token']
        token_date = self.D['post']['token_date']

        self.DB.store('kiwoom_token',token)
        self.DB.store('kiwoom_token_date',token_date)

        return '___OK___'

    def send_token(self) :

        tk = {}
        tk['token'] = self.DB.store('kiwoom_token')
        tk['token_date'] = self.DB.store('kiwoom_token_date')

        return tk