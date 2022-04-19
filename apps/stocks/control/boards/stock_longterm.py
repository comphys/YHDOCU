from system.core.load import Control

class Stock_longterm(Control) :

    def _auto(self) :
        self.DB = self.db('stocks')
        self.tbl = self.parm[0]

    def autoinput(self) :
        update = {}
        self.DB.tbl,self.DB.wre = ('h_stockHistory_board',f"add0 <= '{self.D['post']['add0']}'")
        old_date = self.DB.get_one("max(add0)")
        
        self.DB.wre = f"add0='{old_date}' and add1='JEPI'"; update['add8'] = self.DB.get_one('add3')
        self.DB.wre = f"add0='{old_date}' and add1='TQQQ'"; update['add14'] = self.DB.get_one('add3')

        self.DB.tbl,self.DB.wre = (self.tbl,f"add0='{old_date}'")
        old_data = self.DB.get_line("add0,add3,add7,add13")

        update['add0'] = old_data['add0']
        update['add3'] = f"{int(old_data['add3']):,}"
        update['add7'] = old_data['add7']
        update['add13'] = old_data['add13']

        return self.json(update)

