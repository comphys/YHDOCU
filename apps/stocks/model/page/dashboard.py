from system.core.load import Model
import system.core.my_utils as ut
class M_dashboard(Model) :

    def view(self) :

        # 조회목록
        self.D['CATEGORY'] = ['분할매수']

        self.D['분할매수'] = {}
 
        self.D['분할매수']['가상계좌'] = ['h_daily_virtual_board','IFB',1,8030]
        self.D['분할매수']['첫째계좌'] = ['h_daily_first_board','IFB',1,5377]
        self.D['분할매수']['둘째계좌'] = ['h_daily_second_board','IFB',1,5200]

        # -------------------------------------------------------------
        # 1 이면 카테고리별 합계에 포함, 0 이면 포함하지 않음(virtual)

        self.D['평가합계'] = {}
        self.D['투자합계'] = {}
        self.D['손익현황'] = {}
        self.D['합수익률'] = {}

        for category in self.D['CATEGORY'] : 
            self.D['평가합계'][category] = 0
            self.D['투자합계'][category] = 0

            for key, val in self.D[category].items() : 
                self.D[category][key] = self.outcome(key,val[0],val[1],val[3]) #key, table, type, init

                if val[2] == 1 :
                    self.D['평가합계'][category] += float(self.D[category][key][1].replace(',',''))
                    self.D['투자합계'][category] += float(self.D[category][key][2].replace(',',''))

        
            self.D['손익현황'][category] = self.D['평가합계'][category] - self.D['투자합계'][category]
            self.D['합수익률'][category] = self.D['손익현황'][category] / self.D['투자합계'][category] * 100
        
            self.D['평가합계'][category] = f"{self.D['평가합계'][category]:,.0f}"
            self.D['투자합계'][category] = f"{self.D['투자합계'][category]:,.0f}"
            self.D['손익현황'][category] = f"<span style='color:#ced8f6'>{self.D['손익현황'][category]:,.2f}</span>"  if self.D['손익현황'][category] < 0 else f"<span style='color:#f6cece'>{self.D['손익현황'][category]:,.2f}</span>"
            self.D['합수익률'][category] = f"<span style='color:#ced8f6'>{self.D['합수익률'][category]:,.1f}%</span>" if self.D['합수익률'][category] < 0 else f"<span style='color:#f6cece'>{self.D['합수익률'][category]:,.1f}%</span>"

        #-----------------------------------------------------------------------------------------------------------------------------
        
        ckday = self.DB.one("SELECT max(add0) FROM h_stockHistory_board")

        self.D['오늘날자']  = ut.timestamp_to_date(opt=7) 
        self.D['오늘요일']  = ut.dayofdate(self.D['오늘날자'])
        self.D['확인날자']  = ckday
        self.D['확인요일']  = ut.dayofdate(ckday)

    def outcome(self,key,tbl,type,init) :
        if type == 'IFB' :
            self.DB.tbl, self.DB.wre = (tbl,"add1='SOXL'")
            start_date, last_date = self.DB.get("min(add0),max(add0)",many=1,assoc=False)

            self.DB.wre = f"add0='{start_date}'"
            기본자산, 추가자산 = self.DB.get("sub7,sub8",many=1,assoc=False) 

            self.DB.wre = f"add0='{last_date}'"
            평가금액, 가용잔액, 추가자본 = self.DB.get("add11,add16,add17",many=1,assoc=False) 

            초기자본 = float(기본자산) + float(추가자산) if not init else float(init)
            최종자본 = float(평가금액) + float(가용잔액) + float(추가자본)
            최종수익 = 최종자본 - 초기자본 
            최종수익률 = (최종수익/초기자본) * 100 

            초기자본 = f"{초기자본:,.0f}"
            최종자본 = f"{최종자본:,.0f}"
            최종수익 = f"<span style='color:#ced8f6'>{최종수익:,.2f}</span>" if 최종수익 < 0 else f"<span style='color:#f6cece'>{최종수익:,.2f}</span>"
            최종수익률 = f"<span style='color:#ced8f6'>{최종수익률:,.1f}%</span>" if 최종수익률 < 0 else f"<span style='color:#f6cece'>{최종수익률:,.1f}%</span>"

        elif type == 'VR' :
            self.DB.tbl, self.DB.wre = (tbl,'')
            start_date, last_date = self.DB.get("min(add0),max(add0)",many=1,assoc=False)

            self.DB.wre = ''
            초기자산 = self.DB.get_one("sum(add1)") if not init else init 

            self.DB.wre = f"add0='{last_date}'"
            현재자산 = self.DB.get_one("add17") 

            초기자본 = float(초기자산) 
            최종자본 = float(현재자산)
            최종수익 = 최종자본 - 초기자본 
            최종수익률 = (최종수익/초기자본) * 100 

            초기자본 = f"{초기자본:,.0f}"
            최종자본 = f"{최종자본:,.0f}"
            최종수익 = f"<span style='color:#ced8f6'>{최종수익:,.2f}</span>" if 최종수익 < 0 else f"<span style='color:#f6cece'>{최종수익:,.2f}</span>"
            최종수익률 = f"<span style='color:#ced8f6'>{최종수익률:,.1f}%</span>" if 최종수익률 < 0 else f"<span style='color:#f6cece'>{최종수익률:,.1f}%</span>"            
        
        out = [key,최종자본,초기자본,최종수익,최종수익률]
        return out
