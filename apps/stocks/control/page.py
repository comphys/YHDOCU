from system.core.load import Control
from flask import session

class Page(Control) : 


    def _auto(self) :
        self.DB = self.db('stocks')

        if 'N_NO' in session :
            self.D['USER'] = self.DB.exe(f"SELECT * FROM h_user_list WHERE no={session['N_NO']}",many=1,assoc=True)
            self.D['bid']     = self.parm[0] 
            self.D['BCONFIG'] = self.DB.exe(f"SELECT * FROM h_board_config WHERE bid='{self.D['bid']}'",many=1,assoc=True)
            self.D['xwidth'] = self.D['BCONFIG']['width'] if self.D['BCONFIG']['width'] else '815px'

            self.skin = 'page/'+self.D['BCONFIG']['skin']
            self.D['DOCU_ROOT'] = self.C['DOCU_ROOT']

            qry = f"SELECT section FROM h_board_config WHERE acc_sect <={self.D['USER']['level']} GROUP BY section ORDER BY sposition"
            self.D['MENU_SECTION'] = self.DB.exe(qry)
            
            for val in self.D['MENU_SECTION'] :
                qry = f"SELECT title,bid,type FROM h_board_config WHERE section='{val[0]}' AND acc_board <= {self.D['USER']['level']} ORDER BY bposition"
                self.D[val[0]] = self.DB.exe(qry,assoc=True)
                for temp in self.D[val[0]] :
                    if      temp['type'] == 'yhboard' : temp['bid'] = 'board/list/'+temp['bid']
                    elif    temp['type'] == 'yhtable' : temp['bid'] = 'board/list/'+temp['bid']
                    elif    temp['type'] == 'page'    : temp['bid'] =  'page/view/'+temp['bid']

    def view(self) :
        if not 'N_NO' in session : return self.moveto('board/login')
        M = self.model('page-'+self.D['bid'])
        M.view()
        D={'skin':f"{self.skin}/{self.D['bid']}.html"}
        
        return self.echo(D)

    def backtest(self) :
        self.M = {}
        
        self.D['code']       = self.D['post']['code']
        self.D['strategy']   = self.D['post']['strategy']
        self.D['capital']    = self.D['post']['capital']
        self.D['addition']   = self.D['post']['addition']
        self.D['start_date'] = self.D['post']['start_date']
        self.D['end_date']   = self.D['post']['end_date']
        self.D['progress']   = self.D['post']['progress']

        self.DB.tbl, self.DB.wre = ('h_stock_strategy_board',f"add0='{self.D['strategy']}'")
        s_code = self.DB.get_one('add1')
        
        M = self.model('backtest-backtest_'+s_code)
        M.view()
        M.get_start()
        D={'skin':f"{self.skin}/{self.D['bid']}.html"}
        return self.echo(D)

    def dashboard(self) :
        D={'skin':f"{self.skin}/{self.D['bid']}.html"}
        return self.echo(D)        

    def test_if(self) :

        self.D['progress']   = self.gets['progress']

        self.D['code']       = 'SOXL'
        self.D['strategy']   = 'DNA_SECOND'
        self.D['capital']    = '20,000'
        self.D['addition']   = '2,000'
        self.D['start_date'] = self.gets['date']

        M = self.model('backtest-backtest_ifthisday')

        M.get_start()

        output  = "<div id='stock_tips' style='width:260px;height:180px;padding:10px;background-color:#1d1f24;color:#e1e1e1;border:2px solid #f6cece;' ondblclick=\"h_dialog.close('TEST_IF')\">"
        output += f"시작일 = {self.D['s_day']} 진행률 {self.D['progress']} %<br>"
        output += f"종료일 = {self.D['e_day']} <br>"
        output += f"소요일 = {self.D['days_span']}일 <br>"
        output += "=======================<br>"
        output += f"총씨드 = {self.D['s_capital']:,} <br>"
        output += f"최종액 = {self.D['e_capital']:,.2f} <br>"
        output += f"수익률 = {self.D['profit_rate']:,.2f} % <br>"
        output += "</div>"
        return self.echo(output)

    def test_theday(self) :

        self.D['code']       = 'SOXL'
        self.D['strategy']   = 'DNA 2022'
        self.D['capital']    = '20,000'
        self.D['addition']   = '2,000'
        self.D['start_date'] = self.gets['date']

        M = self.model('backtest-backtest_theday')
        M.get_start()

        sty1 ="style='text-align:center;width:100px'"
        sty2 ="style='text-align:center;width:80px'"
        sty3 ="style='text-align:right;width:80px;padding-right:10px'"
        sty4 ="style='text-align:right;width:100px;padding-right:10px'"
        sty5 ="style='color:#CED8F6'"
        sty6 ="style='color:#F6CECE'"

        output  = "<div id='stock_tips' style='width:200px;height:180px;padding:10px;background-color:#1d1f24;color:#e1e1e1;border:2px solid #F7F8E0;' ondblclick=\"h_dialog.close('TEST_IF')\">"
        output += f"시작일 = {self.D['s_day']} <br>"
        output += f"종료일 = {self.D['e_day']} <br>"
        output += f"소요일 = {self.D['days_span']}일 <br>"
        output += "==============<br>"
        output += f"총씨드 = {self.D['s_capital']} <br>"
        output += f"최종액 = {self.D['e_capital']:,.2f} <br>"
        output += f"수익률 = {self.D['profit_rate']:,.2f} % <br>"
        output += "</div>"
        return self.echo(output)