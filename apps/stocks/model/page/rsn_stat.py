from system.core.load import Model
import system.core.my_utils as my
import csv

class M_rsn_stat(Model) :

    def view(self) :
        
        # 기본 값
        self.D['종목코드'] = 'SOXL'
        
        self.D['종목코드'] = 'SOXL'
        self.D['투자자금'] = self.DB.parameter('TC010')

        self.D['기회시점'] = self.DB.parameter('TR021')
        self.D['기회회복'] = self.DB.parameter('TR022')
        self.D['안정시점'] = self.DB.parameter('TS021')
        self.D['안정회복'] = self.DB.parameter('TS022')

        self.D['수료적용'] = 'on'
        self.D['세금적용'] = 'off'
        self.D['일밸런싱'] = 'on'
        self.D['이밸런싱'] = 'on'
        self.D['가상손실'] = 'off'
        self.D['기간한정'] = 'off'
        self.D['한정기간'] = '365'

        # 기간 설정(최근 2년간)
        # self.D['end_date'] = my.timestamp_to_date(ts='now',opt=7)
        self.D['종료일자'] = self.DB.one("SELECT max(add0) FROM h_stockHistory_board")
        self.D['통계시작'] = my.dayofdate(self.D['종료일자'],delta=-365*2)[0]

    def action(self) :

        D = {}
        D['투자자금'] = self.D['post']['투자자금']
        D['시작일자'] = self.D['post']['통계시작']
        D['통계시작'] = D['시작일자']
        D['종료일자'] = self.D['post']['종료일자']
        # -------------------
        D['기회시점'] = self.D['post']['기회시점']
        D['기회회복'] = self.D['post']['기회회복']
        D['안정시점'] = self.D['post']['안정시점']
        D['안정회복'] = self.D['post']['안정회복']

        D['수료적용'] = 'off'
        D['세금적용'] = 'off'
        D['일밸런싱'] = 'on'
        D['이밸런싱'] = 'on'
        D['기간한정'] = self.D['post'].get('chk_lmt','off')
        D['한정기간'] = self.D['post']['한정기간']
        
        opt = 'lmt_days' if D['기간한정'] == 'on' else ''
        RST = self.SYS.load_app_lib('rsn')
        RST.D |= D

        RST.do_viewStat(opt)

        fieldnames = ['시작일자','종료일자','경과일자','최종수익','종수익률','최장일수','최장일자','최대손절','최손날자','게임횟수','게임승수','게임패수','게임승률','게임익평','게임손평']
        with open("rsn_stat.csv","w",newline="",encoding="euc-kr") as f :
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(RST.D['SR'])
        
        return self.SYS.echo(RST.D)
        