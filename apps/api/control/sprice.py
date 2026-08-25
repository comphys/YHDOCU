from system.core.load import Control


class Sprice(Control) : 

    def _auto(self) :
        self.DB = self.db('stocks')

    def get_current_price(self) :

        KW = self.load_app_lib('kiwoom')
        rst = KW.get_current_price('SOXL')
        return rst

