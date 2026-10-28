from system.core.load import Model
import system.core.my_utils as my
import time

#
# RSN ( Revolution, Stable, New Trust ) Strategy 
#
class M_myhts(Model) :

    def view(self) :

        closeP = self.DB.exe("SELECT add0,add3 FROM h_stockHistory_board ORDER BY add0 DESC LIMIT 60")
        closeP.reverse()

        self.D['cls_d'] = []
        self.D['cls_p'] = []
        for c in closeP :
            self.D['cls_d'].append(c[0][5:])
            self.D['cls_p'].append(c[1])

        if self.SYS.I['_dev'] in ['Windows','Android'] : 

            if    self.SYS.I['_dev'] == 'Windows'  :  rootpath = '/YHDOCU'; macaddress = 'BCFCE7C9911F'
            elif  self.SYS.I['_dev'] ==  'Android' :  rootpath = '/data/data/com.termux/files/home/YHDOCU'; macaddress = 'A475B980D0CA'
            API = self.SYS.load_app_lib('meritz')
            API.root = rootpath
            API.maca = macaddress
            oddday = API.get_market_date()
            self.D['기준날자'] = oddday[0:4]+'-'+oddday[4:6]+'-'+oddday[6:8]

            self.D['balance'] = []
            # self.D['balance'] = [
            #     {'달러예수금': '0.00', '평가환율': '1324.3000', '원화환산': '0', '원화예수금': '0', '통합달러': '0.00', '통합원화': '0'},
            #     {'달러예수금': '0.00', '평가환율': '1324.3000', '원화환산': '0', '원화예수금': '0', '통합달러': '0.00', '통합원화': '0'},
            #     {'달러예수금': '0.00', '평가환율': '1324.3000', '원화환산': '0', '원화예수금': '4197633', '통합달러': '3169.70', '통합원화': '4197633'},
            #     {'달러예수금': '746.970', '평가환율': '1324.3000', '원화환산': '989212', '원화예수금': '10665.653', '통합달러': '8800.77', '통합원화': '11654865'}
            #     ]

            for x in ['01','02','03','lth'] :
                API.change_account(x)
                rst = API.get_money_balance()
                self.D['balance'].append(rst)
                time.sleep(0.2)

            for B in self.D['balance'] :
                B['달러예수금'] = f"{float(B['달러예수금']):,.2f}"
                B['평가환율']   = f"{float(B['평가환율']):,.2f}"
                B['원화환산']   = f"{float(B['원화환산']):,.0f}"
                B['원화예수금'] = f"{float(B['원화예수금']):,.0f}"
                B['통합달러']   = f"{float(B['통합달러']):,.2f}"
                B['통합원화']   = f"{float(B['통합원화']):,.0f}"



    def action(self) :
        pass

# ----------------------------------------------------------------------------------------------
# AJAX 
# ----------------------------------------------------------------------------------------------
class Ajax(Model) :

    def reserved(self) :

        if self.SYS.I['_dev'] in ['Windows','Android'] : 

            if    self.SYS.I['_dev'] == 'Windows'  :  rootpath = '/YHDOCU'; macaddress = 'BCFCE7C9911F'
            elif  self.SYS.I['_dev'] ==  'Android' :  rootpath = '/data/data/com.termux/files/home/YHDOCU'; macaddress = 'A475B980D0CA'
            API = self.SYS.load_app_lib('meritz')
            API.root = rootpath
            API.maca = macaddress        

            odday = API.get_market_date()
            opt = self.D['post']['opt']
            API.change_account(opt)
            rst = API.get_reserved_order(odday,code='2')
            return self.SYS.json(rst)
        
        else :
            return None
        
    def account(self) :
        
        if self.SYS.I['_dev'] in ['Windows','Android'] :
            
            if    self.SYS.I['_dev'] == 'Windows'  :  rootpath = '/YHDOCU'; macaddress = 'BCFCE7C9911F'
            elif  self.SYS.I['_dev'] ==  'Android' :  rootpath = '/data/data/com.termux/files/home/YHDOCU'; macaddress = 'A475B980D0CA'
            API = self.SYS.load_app_lib('meritz')
            API.root = rootpath
            API.maca = macaddress  

            opt = self.D['post']['opt']
            API.change_account(opt)
            rst = API.get_account_balance()
            return self.SYS.json(rst)
        
        else :
            return None

    def orders_today(self) :
        
        if self.SYS.I['_dev'] in ['Windows','Android'] :
            
            if    self.SYS.I['_dev'] == 'Windows'  :  rootpath = '/YHDOCU'; macaddress = 'BCFCE7C9911F'
            elif  self.SYS.I['_dev'] ==  'Android' :  rootpath = '/data/data/com.termux/files/home/YHDOCU'; macaddress = 'A475B980D0CA'
            API = self.SYS.load_app_lib('meritz')
            API.root = rootpath
            API.maca = macaddress  

            opt = self.D['post']['opt']
            API.change_account(opt)
            rst = API.get_orders_today('2','0')
            return self.SYS.json(rst)
        
        else :
            return None

    def real_cancel(self) :
        
        if self.SYS.I['_dev'] in ['Windows','Android'] :
            
            if    self.SYS.I['_dev'] == 'Windows'  :  rootpath = '/YHDOCU'; macaddress = 'BCFCE7C9911F'
            elif  self.SYS.I['_dev'] ==  'Android' :  rootpath = '/data/data/com.termux/files/home/YHDOCU'; macaddress = 'A475B980D0CA'
            API = self.SYS.load_app_lib('meritz')
            API.root = rootpath
            API.maca = macaddress  

            acc    = self.D['post']['a']
            date   = self.D['post']['d']
            ordnum = self.D['post']['n']
            qty    = self.D['post']['q']
            code   = self.D['post']['c']
            API.change_account(acc)
            API.do_real_cancel(date,ordnum,qty,code=code)
            time.sleep(1)
            return self.SYS.json("OK")

    def real_sell(self) :
        
        if self.SYS.I['_dev'] in ['Windows','Android'] :
            
            if    self.SYS.I['_dev'] == 'Windows'  :  rootpath = '/YHDOCU'; macaddress = 'BCFCE7C9911F'
            elif  self.SYS.I['_dev'] ==  'Android' :  rootpath = '/data/data/com.termux/files/home/YHDOCU'; macaddress = 'A475B980D0CA'
            API = self.SYS.load_app_lib('meritz')
            API.root = rootpath
            API.maca = macaddress  

            acc    = self.D['post']['acc']
            qty   = self.D['post']['qty']
            price = self.D['post']['price']
            API.change_account(acc)
            API.do_real_sell(qty,price,code='32',ccode='7') 
            time.sleep(1)
            return self.SYS.json("OK")

    def get_current_price(self) :

        if self.SYS.I['_dev'] in ['Windows','Android'] :
            DB = self.SYS.load_app_lib('dbopen')
            rst = DB.get_current_price('SOXL',mk='FA')
            if rst :
                rst['현재가'] = abs(float(rst['현재가']))
                rst['현재가'] = f"{rst['현재가']:.2f}"
                return self.SYS.json(rst)
            else : return self.SYS.json("error::token_issue")
        

        