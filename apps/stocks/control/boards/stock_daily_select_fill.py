from system.core.load import Control
from datetime import datetime,timedelta
import json

class Stock_daily_select_fill(Control) :
    
    def getit(self) :
        self.DB = self.db('stocks')
        code = self.D['post']['code']
            
        self.DB.tbl, self.DB.wre = (self.parm[0],f"add1='{code}' and add19='시즌진행'")
        today,strategy = self.DB.get('max(add0),add20',assoc=False,many=1)
        
        datetime_today = datetime.strptime(today,'%Y-%m-%d')
        
        if   datetime_today.weekday() == 4 : day_plus = 3
        elif datetime_today.weekday() == 5 : day_plus = 2
        else  : day_plus = 1

        temp = datetime_today + timedelta(days=day_plus)

        tomorrow = temp.strftime('%Y-%m-%d')

        self.DB.tbl,self.DB.wre = ('h_stock_strategy_board',f"add0='{strategy}'")
        base = self.DB.get_one('add1')
        tmp = {'a':tomorrow,'b':strategy,'c':base}
        return json.dumps(tmp)
    
    def getit2(self) :
        self.DB = self.db('stocks')
        strategy = self.D['post']['strategy']

        self.DB.tbl,self.DB.wre = ('h_stock_strategy_board',f"add0='{strategy}'")
        base = self.DB.get_one('add1')
        return base
