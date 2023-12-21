from system.core.load import Control
import system.core.my_utils as my

class Vrs_guide(Control) : 

    def _auto(self) :
        self.DB = self.db('stocks')
        self.bid   = self.parm[0]
        self.board = 'h_'+self.bid+'_board'
    
# -----------------------------------------------------------------------------------------------------------------------
# Initiate  STABILITY TACTIC
# -----------------------------------------------------------------------------------------------------------------------

    def initiate_Stactic(self) :
        theDay  = self.D['post']['theDay']
        Balance = my.sv(self.D['post']['Balance'])

        self.B = {}
        self.M = {}

        HD = self.DB.line(f"SELECT add3,add8,add9,add10 FROM h_stockHistory_board WHERE add0='{theDay}'")
        GD = self.DB.line(f"SELECT add6,add9,sub2,sub7,sub12,sub19,sub20,sub29 FROM h_INVEST_board WHERE add0='{theDay}'")
        
        self.B['add0']  = theDay
        self.B['add1']  = '0.00';     self.B['add2']  = '0.00';      self.B['add3']  = Balance;      self.B['add4']  = '100'
        self.B['add11'] = '0.00';     self.B['add12'] = '0.00';      self.B['add5']  = 0;          self.B['add8'] = '0.00'
        self.B['add14'] = HD['add3']; self.B['add15'] = '0.00';      self.B['add9']  = 0;          self.B['add16']= '0.00'
        self.B['add7']  = '0.0000';   self.B['sub15'] = '0.00';      self.B['sub14'] = '0.00'; self.B['add6'] = '0.00'
        self.B['sub5']  = HD['add9']; self.B['sub6']  = HD['add10']; self.B['sub28'] = round(my.sv(HD['add8']) * 100,1); self.B['add18'] = '0.00'
        
        
        # 경과일수 GD의 데이타는 오늘의 자료임, 가이드가 진행 중일 때 초기화 시키는 것을 전제로 함
        일매수금 = int(int(Balance*2/3)/22)
        bprice = self.DB.one(f"SELECT add14 FROM h_INVEST_board WHERE sub12='0' and add0 < '{theDay}' ORDER BY add0 DESC LIMIT 1")
        기초수량 = my.ceil(일매수금/float(bprice)) 
        
        찬스수량 = 0
        day_count = min(int(GD['sub12'])+1,6)
        for i in range(0,day_count) : 찬스수량 += my.ceil(기초수량 *(i*1.25 + 1))
        cp05 = self.take_chance(-5.0 ,int(GD['add9']),int(GD['sub2']),float(GD['add6']))
        cp10 = self.take_chance(-10.0,int(GD['add9']),int(GD['sub2']),float(GD['add6']))
        찬스가격 = cp05 if float(GD['sub7']) else cp10
        찬스가격 = min(float(GD['sub19']),찬스가격)
        bprice = self.DB.one(f"SELECT add14 FROM h_INVEST_board WHERE sub12='0' and add0 < '{theDay}' ORDER BY add0 DESC LIMIT 1")
        기초수량 = my.ceil(일매수금/float(bprice)); self.B['sub18'] = 기초수량
        
        self.B['sub1']  = 1; self.B['sub4'] = 일매수금; self.B['sub2'] = 찬스수량;  self.B['sub3'] = 0
        self.B['sub12'] = int(GD['sub12']);   self.B['sub18'] = 기초수량; self.B['sub19'] = 찬스가격; self.B['sub20'] = GD['sub20']
        self.B['add17'] = Balance;  self.B['sub25'] = Balance; self.B['sub26'] = '0.00'; self.B['sub11'] = '0.00'
        self.B['sub29'] = GD['sub29']; self.B['sub30'] = '0.00';  self.B['sub31'] = '0.00';  self.B['sub7'] = GD['sub7']
        
        return self.json(self.B) 
    
    def take_chance(self,p,H,n,A) :
        if H == 0 : return 0
        N = H + n
        k = N / (1+p/100)
        return round(A/(k-n),2)
            
    