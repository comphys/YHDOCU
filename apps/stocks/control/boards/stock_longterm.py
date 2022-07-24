from system.core.load import Control

class Stock_longterm(Control) :

    def _auto(self) :
        self.DB = self.db('stocks')
        self.tbl = self.parm[0]

    def autoinput(self) :
        update = {}
        pick_day = self.D['post']['add0']

        self.DB.tbl, self.DB.wre = (self.tbl, f"add0 < '{pick_day}'")
        old_date = self.DB.get_one("max(add0)")
        self.DB.wre = f"add0='{old_date}'"
        old_data = self.DB.get_line("add0,add3,add7,add13,sub1,sub2,sub3,sub4,sub5,sub6,sub7,add19")

        self.DB.clear()

        self.DB.tbl, self.DB.wre = ('h_stockHistory_board',f"add0 <= '{pick_day}'")
        on_day = self.DB.get_one("max(add0)")
        self.DB.wre = f"add0='{on_day}' and add1='{old_data['sub6']}'"; update['add8'] = self.DB.get_one('add3')
        self.DB.wre = f"add0='{on_day}' and add1='{old_data['sub7']}'"; update['add14'] = self.DB.get_one('add3')
        
        update['add0'] = old_data['add0']
        update['add3'] = f"{int(old_data['add3']):,}"
        update['add7'] = old_data['add7']
        update['add13'] = old_data['add13']
        update['add19'] = old_data['add19']

        update['sub1'] = f"{int(old_data['sub1']):,}"
        update['sub2'] = old_data['sub2']
        update['sub3'] = old_data['sub3']
        update['sub4'] = old_data['sub4']
        update['sub5'] = old_data['sub5']
        update['sub6'] = old_data['sub6']
        update['sub7'] = old_data['sub7']

        return self.json(update)

    def autoinput2(self) :
        update = {}
        pick_day = self.D['post']['add0']

        self.DB.tbl, self.DB.wre = (self.tbl, f"add0 < '{pick_day}'")
        old_date = self.DB.get_one("max(add0)")
        self.DB.wre = f"add0='{old_date}'"
        old_data = self.DB.get_line("add0,add3,add7,add13,sub2,sub3,sub4,sub5,sub6,sub7,add19,sub12,sub14,sub15,sub16,sub17,sub18,sub19,sub20,sub21,sub22,sub23,sub24")

        self.DB.clear()

        self.DB.tbl, self.DB.wre = ('h_stockHistory_board',f"add0 <= '{pick_day}'")
        on_day = self.DB.get_one("max(add0)")
        self.DB.wre = f"add0='{on_day}'   and add1='{old_data['sub6']}'"; update['add8']  = self.DB.get_one('add3')
        self.DB.wre = f"add0='{on_day}'   and add1='{old_data['sub7']}'"; update['add14'] = self.DB.get_one('add3') 

        base_code = {'SOXL':'SOXX','TQQQ':'QQQ'}
        self.DB.wre = f"add0='{on_day}'   and add1='{base_code[old_data['sub7']]}'" 
        base_value = float(self.DB.get_one('add3'))
          
        update['add0'] = old_data['add0']
        update['add3'] = f"{int(old_data['add3']):,}"
        update['add7'] = old_data['add7']
        update['add13'] = old_data['add13']
        update['add19'] = old_data['add19']

        update['sub1']  = f"{base_value:,}"
        update['sub2']  = old_data['sub2']
        update['sub3']  = old_data['sub3']
        update['sub4']  = old_data['sub4']
        update['sub5']  = old_data['sub5']
        update['sub6']  = old_data['sub6']
        update['sub7']  = old_data['sub7']
        update['sub12'] = old_data['sub12']
        update['sub14'] = old_data['sub14']
        update['sub15'] = old_data['sub15']
        update['sub16'] = old_data['sub16']
        update['sub17'] = old_data['sub17']
        update['sub18'] = old_data['sub18']
        update['sub19'] = old_data['sub19']
        update['sub20'] = old_data['sub20']
        update['sub21'] = old_data['sub21']
        update['sub22'] = old_data['sub22']
        update['sub23'] = old_data['sub23']
        update['sub24'] = old_data['sub24']


        return self.json(update)

