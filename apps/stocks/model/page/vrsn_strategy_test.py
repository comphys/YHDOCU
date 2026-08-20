from system.core.load import Model
import system.core.my_utils as my

class M_vrsn_strategy_test(Model) :

    def _auto(self) :
        pass

    def view(self) :
        
        # 기본 값

        self.D['전략선택'] = 'vrsn_01'
        self.D['일반자금'] = "100,000"
 
        self.D['수료적용'] = 'off'
        self.D['세금적용'] = 'off'

        # 기간 설정(최근 2년간)
        # self.D['종료일자'] = self.DB.last_date("h_stockHistory_board")
        # self.D['시작일자'] = my.dayofdate(self.D['종료일자'],delta=-365*2)[0]

        self.D['종료일자'] = '2022-12-31'
        self.D['시작일자'] = '2022-01-01'

    def action(self) :

        D = {}

        D['전략선택'] = self.D['post']['전략선택'] ; 
        if not D['전략선택'] : D['전략선택'] = 'vrsn_n01'
        D['일반자금'] = self.D['post']['일반자금']

        D['시작일자'] = self.D['post']['시작일자']
        D['종료일자'] = self.D['post']['종료일자']

        D['수료적용'] = self.D['post'].get('chk_fee','off')
        D['세금적용'] = self.D['post'].get('chk_tax','off')
        
        VB = self.SYS.load_app_lib(D['전략선택'])
        VB.D |= D

        VB.do_viewChart()

        return self.SYS.echo(VB.D)

# ----------------------------------------------------------------------------------------------
# AJAX 
# ----------------------------------------------------------------------------------------------
    