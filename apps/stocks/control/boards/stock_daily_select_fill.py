from system.core.load import Control
from datetime import datetime
import time,json

class Stock_daily_select_fill(Control) :
    
    def getit(self) :
        self.DB = self.db('stocks')
        code = self.D['post']['code']

        self.DB.tbl, self.DB.wre = ('h_daily_trading_board',f"add1='{code}'")
        today,strategy = self.DB.get('max(add0),add20',assoc=False,many=1)
        now = int(time.mktime(datetime.strptime(today,'%Y-%m-%d').timetuple()))
        tomorrow = datetime.fromtimestamp(now+3600*24).strftime('%Y-%m-%d')

        self.DB.tbl,self.DB.wre = ('h_stock_strategy_board',f"add0='{strategy}'")
        base = self.DB.get_one('add1')
        tmp = {'a':tomorrow,'b':strategy,'c':base}
        return json.dumps(tmp)