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

    # -------------------------------------------------------
    # respond to form submit, prefix rpd_, rpd means respond
    # -------------------------------------------------------

    def rpd_viewChart(self) :
        D = {}
        D['종목코드'] = self.D['post']['종목코드']
        D['일반자금'] = self.D['post']['일반자금']
        D['기회자금'] = self.D['post']['기회자금']
        D['안정자금'] = self.D['post']['안정자금']
        D['생활자금'] = self.D['post']['생활자금']

        D['시작일자'] = self.D['post']['시작일자']
        D['종료일자'] = self.D['post']['종료일자']
        # -------------------
        D['기회시점'] = self.D['post']['기회시점']
        D['기회회복'] = self.D['post']['기회회복']
        D['안정시점'] = self.D['post']['안정시점']
        D['안정회복'] = self.D['post']['안정회복']
        D['생활시점'] = self.D['post']['생활시점']
        D['생활회복'] = self.D['post']['생활회복']

        D['수료적용'] = self.D['post'].get('chk_fee','off')
        D['세금적용'] = self.D['post'].get('chk_tax','off')
        D['일밸런싱'] = self.D['post'].get('chk_brs','off')
        D['이밸런싱'] = self.D['post'].get('chk_rs_','off')
        D['일반상황'] = self.D['post'].get('chk_von','off')
        D['가상손실'] = self.D['post'].get('chk_chx','off')
        D['랜덤종가'] = self.D['post'].get('chk_rnd','off')
        
        RST = self.load_app_lib('rst')
        RST.D |= D

        RST.do_viewChart()

        RST.D['skin'] = f"{self.skin}/{self.D['bid']}.html"
        return self.echo(RST.D)
    
    def rpd_rsnview(self) :
        D = {}
        D['기회자금'] = self.D['post']['기회자금']
        D['안정자금'] = self.D['post']['안정자금']
        D['생활자금'] = self.D['post']['생활자금']
        D['투자자금'] = self.D['post']['투자자금']

        D['시작일자'] = self.D['post']['시작일자']
        D['종료일자'] = self.D['post']['종료일자']
        # -------------------
        D['기회시점'] = self.D['post']['기회시점']
        D['기회회복'] = self.D['post']['기회회복']
        D['안정시점'] = self.D['post']['안정시점']
        D['안정회복'] = self.D['post']['안정회복']

        D['수료적용'] = self.D['post'].get('chk_fee','off')
        D['세금적용'] = self.D['post'].get('chk_tax','off')
        D['일밸런싱'] = self.D['post'].get('chk_brs','off')
        D['이밸런싱'] = self.D['post'].get('chk_rs_','off')
        D['일반상황'] = self.D['post'].get('chk_von','off')
        D['가상손실'] = self.D['post'].get('chk_chx','off')
        
        RST = self.load_app_lib('rsn')
        RST.D |= D

        RST.do_viewChart()

        RST.D['skin'] = f"{self.skin}/{self.D['bid']}.html"
        return self.echo(RST.D)
    
    def rpd_viewStat(self) :
        D = {}
        D['종목코드'] = self.D['post']['종목코드']
        D['일반자금'] = self.D['post']['일반자금']
        D['기회자금'] = self.D['post']['기회자금']
        D['안정자금'] = self.D['post']['안정자금']
        D['생활자금'] = self.D['post']['생활자금']

        D['시작일자'] = self.D['post']['통계시작']
        D['통계시작'] = D['시작일자']
        D['종료일자'] = self.D['post']['종료일자']
        # -------------------
        D['기회시점'] = self.D['post']['기회시점']
        D['기회회복'] = self.D['post']['기회회복']
        D['안정시점'] = self.D['post']['안정시점']
        D['안정회복'] = self.D['post']['안정회복']
        D['생활시점'] = self.D['post']['생활시점']
        D['생활회복'] = self.D['post']['생활회복']

        D['수료적용'] = self.D['post'].get('chk_fee','off')
        D['세금적용'] = self.D['post'].get('chk_tax','off')
        D['일밸런싱'] = self.D['post'].get('chk_brs','off')
        D['이밸런싱'] = self.D['post'].get('chk_rs_','off')

        RST = self.load_app_lib('rst')
        RST.D |= D

        RST.do_viewStat()
        RST.D['skin'] = f"{self.skin}/{self.D['bid']}.html"
        
        return self.echo(RST.D)
    
    def rpd_rsnStat(self) :
        D = {}
        D['기회자금'] = self.D['post']['기회자금']
        D['안정자금'] = self.D['post']['안정자금']
        D['생활자금'] = self.D['post']['생활자금']

        D['시작일자'] = self.D['post']['통계시작']
        D['통계시작'] = D['시작일자']
        D['종료일자'] = self.D['post']['종료일자']
        # -------------------
        D['기회시점'] = self.D['post']['기회시점']
        D['기회회복'] = self.D['post']['기회회복']
        D['안정시점'] = self.D['post']['안정시점']
        D['안정회복'] = self.D['post']['안정회복']

        D['수료적용'] = self.D['post'].get('chk_fee','off')
        D['세금적용'] = self.D['post'].get('chk_tax','off')
        D['일밸런싱'] = self.D['post'].get('chk_brs','off')
        D['이밸런싱'] = self.D['post'].get('chk_rs_','off')

        RST = self.load_app_lib('rsn')
        RST.D |= D

        RST.do_viewStat()
        RST.D['skin'] = f"{self.skin}/{self.D['bid']}.html"
        
        return self.echo(RST.D)

    def rpd_baseChart(self) :
        D = {}
        D['종목코드'] = self.D['post']['종목코드']
        D['일반자금'] = self.D['post']['일반자금']

        D['시작일자'] = self.D['post']['시작일자']
        D['종료일자'] = self.D['post']['종료일자']

        D['수료적용'] = self.D['post'].get('chk_fee','off')
        D['세금적용'] = self.D['post'].get('chk_tax','off')
        D['가상손실'] = self.D['post'].get('chk_chx','off')
        
        VB = self.load_app_lib('vtactic')
        VB.D |= D

        VB.do_viewChart()

        VB.D['skin'] = f"{self.skin}/{self.D['bid']}.html"
        return self.echo(VB.D)
    
    def rpd_testChart(self) :
        D = {}
        D['종목코드'] = self.D['post']['종목코드']
        D['일반자금'] = self.D['post']['일반자금']

        D['시작일자'] = self.D['post']['시작일자']
        D['종료일자'] = self.D['post']['종료일자']

        D['수료적용'] = self.D['post'].get('chk_fee','off')
        D['세금적용'] = self.D['post'].get('chk_tax','off')
        
        VB = self.load_app_lib('n310')
        VB.D |= D

        VB.do_viewChart()

        VB.D['skin'] = f"{self.skin}/{self.D['bid']}.html"
        return self.echo(VB.D)
    
    def rpd_generalTestChart(self) :
        D = {}
        D['종목코드'] = 'SOXL'
        D['전략선택'] = self.D['post']['전략선택']
        D['일반자금'] = self.D['post']['일반자금']

        D['시작일자'] = self.D['post']['시작일자']
        D['종료일자'] = self.D['post']['종료일자']

        D['수료적용'] = self.D['post'].get('chk_fee','off')
        
        VB = self.load_app_lib('getest')
        VB.D |= D

        VB.do_viewChart()

        VB.D['skin'] = f"{self.skin}/{self.D['bid']}.html"
        return self.echo(VB.D)
    
    def rpd_N310Chart(self) :
        D = {}
        D['종목코드'] = self.D['post']['종목코드']
        D['일반자금'] = self.D['post']['일반자금']

        D['시작일자'] = self.D['post']['시작일자']
        D['종료일자'] = self.D['post']['종료일자']

        D['수료적용'] = self.D['post'].get('chk_fee','off')
        D['세금적용'] = self.D['post'].get('chk_tax','off')
        
        VB = self.load_app_lib('n310')
        VB.D |= D

        VB.do_viewChart()

        VB.D['skin'] = f"{self.skin}/{self.D['bid']}.html"
        return self.echo(VB.D)