from system.core.load import Control
import json

class Stocks(Control) : 

  
    def _auto(self) :
        self.DB = self.db('stocks')


    def autoinput(self) :

        update = {}
        update['msg'] = "안녕하세요"
        update['aaa'] = 1
        update['bbb'] = 2
        update['ccc'] = 3
        update['ddd'] = 4
        update['eee'] = 5

        return self.echo(json.dumps(update))