from system.core.load import Model
import system.core.my_utils as ut
class M_dashboard(Model) :

    def view(self) :

        # 조회목록
        LC = ['현재시즌','전체시즌']

        self.D['현재시즌'] = {}
        self.D['전체시즌'] = {}

        self.D['현재시즌']['첫째상황'] = ['h_daily_first_board','IFB',1,5377]
        self.D['현재시즌']['둘째상황'] = ['h_daily_second_board','IFB',1,5200]
        self.D['현재시즌']['SX_VR'] = ['h_myCLD_board','VR',1,0]
        self.D['현재시즌']['TQ_VR'] = ['h_myOLT_board','VR',1,0]

        self.D['전체시즌']['가상상황'] = ['h_daily_virtual_board','IFB',1,0]
        self.D['전체시즌']['첫째상황'] = ['h_daily_first_board','IFB',1,0]
        self.D['전체시즌']['둘째상황'] = ['h_daily_second_board','IFB',1,0]
        self.D['전체시즌']['SX_VR'] = ['h_myCLD_board','VR',1,0]
        self.D['전체시즌']['TQ_VR'] = ['h_myOLT_board','VR',1,0]
        # -------------------------------------------------------------

        for category in LC : 
            self.D[category]['평가합계'] = 0
            self.D[category]['투자합계'] = 0

            for key, val in self.D[category].items() : 
                self.D[category][key] = self.outcome(key,val[0],val[1],val[3])
                if val[2] == 1 :
                    self.D[category]['평가합계'] += float(self.D[category][key][1].replace(',',''))
                    self.D[category]['투자합계'] += float(self.D[category][key][2].replace(',',''))

        
            self.D[category]['손익현황'] = self.D[category]['평가합계'] - self.D[category]['투자합계']
            self.D[category]['합수익률'] = self.D[category]['손익현황'] / self.D[category]['투자합계'] * 100
        
            self.D[category]['평가합계'] = f"{self.D[category]['평가합계']:,.0f}"
            self.D[category]['투자합계'] = f"{self.D[category]['투자합계']:,.0f}"
            self.D[category]['손익현황'] = f"<span style='color:#ced8f6'>{self.D[category]['손익현황']:,.2f}</span>"  if self.D[category]['손익현황'] < 0 else f"<span style='color:#f6cece'>{self.D[category]['손익현황']:,.2f}</span>"
            self.D[category]['합수익률'] = f"<span style='color:#ced8f6'>{self.D[category]['합수익률']:,.1f}%</span>" if self.D[category]['합수익률'] < 0 else f"<span style='color:#f6cece'>{self.D[category]['합수익률']:,.1f}%</span>"

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
