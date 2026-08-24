from system.core.load import Model
import system.core.my_utils as my
import csv

class M_diy_stat(Model) :

    def view(self) :
        
        # 기본 값
        
        self.D['전략선택'] = 'DIY'
        self.D['일반자금'] = '100,000'


        self.D['수료적용'] = 'off'
        self.D['세금적용'] = 'off'
        self.D['기간한정'] = 'off'
        self.D['한정기간'] = '365'
        self.D['파일출력'] = 'off'

        # 기간 설정(최근 2년간)
        # self.D['end_date'] = my.timestamp_to_date(ts='now',opt=7)
        self.D['종료일자'] = self.DB.one("SELECT max(add0) FROM h_stockHistory_board")
        self.D['통계시작'] = my.dayofdate(self.D['종료일자'],delta=-365*2)[0]

    def action(self) :

        D = {}
        D['일반자금'] = self.D['post']['일반자금']
        D['시작일자'] = self.D['post']['통계시작']
        D['통계시작'] = D['시작일자']
        D['종료일자'] = self.D['post']['종료일자']
        # -------------------

        D['수료적용'] = 'off'
        D['세금적용'] = 'off'

        D['기간한정'] = self.D['post'].get('chk_lmt','off')
        D['파일출력'] = self.D['post'].get('chk_csv','off')
        D['한정기간'] = self.D['post']['한정기간']
        
        opt = 'lmt_days' if D['기간한정'] == 'on' else ''
        DIY = self.SYS.load_app_lib('diy')
        DIY.D |= D

        DIY.do_viewStat(opt)

        if D['파일출력'] == 'on' :
            fieldnames = ['진시일자','종료일자','경과일자','최종수익','종수익률','최장일수','최장일자','최대손절','최손날자','진최하락','최하일자','게임횟수','게임승수','게임패수','게임승률','게임익평','게임손평']
            with open("diy_stat.csv","w",newline="",encoding="euc-kr") as f :
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(DIY.D['SR'])
        
        return self.SYS.echo(DIY.D)
        