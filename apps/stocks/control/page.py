from system.core.load import Control
from flask import session
import system.core.my_utils as my

class Page(Control) : 


    def _auto(self) :
        self.DB = self.db('stocks')

        if 'N_NO' in session :
            self.D['USER'] = self.DB.exe(f"SELECT * FROM h_user_list WHERE no={session['N_NO']}",many=1,assoc=True)
            self.D['bid']     = self.parm[0] 
            self.D['BCONFIG'] = self.DB.exe(f"SELECT * FROM h_board_config WHERE bid='{self.D['bid']}'",many=1,assoc=True)
            
            if self.D['BCONFIG']['width'] : self.D['xwidth'] = self.D['BCONFIG']['width']
            else : self.D['xwidth'] = '384px' if self.D['_mbl'] else '815px'
             
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

    # ----------------------------------------------------
    # For back_testing
    # ----------------------------------------------------

    def backtest(self) :
        self.M = {}
        
        self.D['code']          = self.D['post']['code']
        self.D['strategy']      = self.D['post']['strategy']
        self.D['capital']       = self.D['post']['capital']
        self.D['addition']      = self.D['post']['addition']
        self.D['start_date']    = self.D['post']['start_date']
        self.D['end_date']      = self.D['post']['end_date']
        # -------------------
        self.D['chanceCapital'] = self.D['post'].get('chanceCapital','36,000')
        self.D['chancePoint']   = self.D['post'].get('chancePoint','-2.2')
        self.D['stablePoint']   = self.D['post'].get('stablePoint','-10.0')

        self.DB.tbl, self.DB.wre = ('h_stock_strategy_board',f"add0='{self.D['strategy']}'")
        s_code = self.DB.get_one('add1')
        M = self.model('backtest-backtest_'+s_code)
        M.view()
        M.get_start()
        M.test_it()
        D={'skin':f"{self.skin}/{self.D['bid']}_{self.D['strategy']}.html"}
        return self.echo(D)

    def overall_test(self) :
        self.M = {}
        
        self.D['종목코드'] = self.D['post']['종목코드']
        self.D['일반자금'] = self.D['post']['일반자금']
        self.D['기회자금'] = self.D['post']['기회자금']
        self.D['안정자금'] = self.D['post']['안정자금']

        self.D['시작일자'] = self.D['post']['시작일자']
        self.D['종료일자'] = self.D['post']['종료일자']
        # -------------------
        self.D['기회시점'] = self.D['post']['기회시점']
        self.D['안정시점'] = self.D['post']['안정시점']

        M = self.model('backtest-backtest_OVERALL')
        M.get_start()
        M.test_it()
        D={'skin':f"{self.skin}/{self.D['bid']}.html"}
        return self.echo(D)



    def get_ohlc(self) :
        code = self.gets['code']
        date = self.gets['date']
        self.DB.tbl, self.DB.wre = ('h_stockHistory_board',f"add1='{code}' and add0='{date}'")
        ohlc = self.DB.get_line("add4,add5,add6,add3,add8,add9,add10")
        # day_change = (float(ohlc['add5']) - float(ohlc['add4'])) / float(ohlc['add4']) * 100
        change = float(ohlc['add8'])*100
        output  = "<div id='stock_prices' style='width:430px;height:80px;padding:10px;background-color:#1d1f24;color:#e1e1e1;border:2px solid slategray;' ondblclick=\"h_dialog.close('OHLC_DAY')\">"
        output += "<table class='table' style='text-align:center'><tr><th>시가</th><th>고가</th><th>저가</th><th>종가</th><th>변동</th><th>상승</th><th>하락</th></tr><tr>"
        output += f"<td>{ohlc['add4']}</td>"
        output += f"<td style='color:#F6CECE'>{ohlc['add5']}</td>"
        # output += f"<td>{day_change:.1f}</td>"
        output += f"<td style='color:#CED8F6'>{ohlc['add6']}</td>"
        output += f"<td style='color:#F5F6CE'>{ohlc['add3']}</td>"
        output += f"<td>{change:.1f}%</td>"
        output += f"<td>{ohlc['add9']}</td>"
        output += f"<td>{ohlc['add10']}</td>"
        output += "</tr></table></div>"
        return self.echo(output)

    # ----------------------------------------------------
    # For engtutor
    # ----------------------------------------------------
