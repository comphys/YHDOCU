from system.core.load import Model
import system.core.my_utils as my

class Ajax(Model) :
    # Update Log ------------------------------------------------------------------------------------------------------------------------------------------



    def update_log(self) :

        board = 'h_logDIY_board'
        lday = self.DB.last_date('h_stockHistory_board')
        DIY = self.SYS.load_app_lib('diy')

        ini_data = self.DB.oneline(f"SELECT add18,add19,add1 FROM {board} ORDER BY add0 DESC LIMIT 1")
        ini_date = ini_data[0]
        ini_capt = f"{my.sv(ini_data[1]):,.2f}"
        season   = ini_data[2]
        
        DIY.do_tacticLog(ini_date,lday,ini_capt)
        LD = DIY.get_simulLog()
        
        LD['uid']   = 'comphys'
        LD['uname'] = '정용훈'
        LD['wdate'] = LD['mdate'] = my.now_timestamp() 

        LD['add1'] = int(season) + 1 if LD['add2'] == 1 else season
            
        if  not LD['첫날기록'] or LD['add6'] in('익절매도','손절매도') :   
            del LD['첫날기록']  
            qry=DIY.DB.qry_insert(board,LD)
            DIY.DB.exe(qry)
            return self.SYS.json("OK")
       


    # -----------------------------------------------------------------------------------------------------------------------------------------------------
    
    def dailyCheckUpdate(self) :

        odrday = self.D['post']['odrday']
        option = self.D['post']['option']
        
        if  option == 'DIY'  : key = 'A0710'

        self.DB.parameter_update(key,odrday)


    def reset_balance(self) :
        
        n_bl = self.D['post']['n_bl']
        LD = self.DB.last_record('h_logDIY_board')
        CD = self.DB.last_record('h_stockHistory_board')
        ST = self.DB.parameters_dict('매매전략/DIY')
        
        # 잔액 및 가치합계 재 설정
        o_mon = my.sv(LD['add5'])
        n_mon = my.sv(n_bl)
        a_mon = my.sv(ST['A0702'])
        b_mon = n_mon + a_mon
        x_mon = f"(증) {n_mon-o_mon:,.2f}" if n_mon > o_mon else f"(감) {o_mon-n_mon:,.2f}"

        당일종가 = float(CD['add3'])
        당일연속 = int(CD['add10'])
        진입일자 = ST['A0202']
        진입가치 = ST['A0203']
        분할배분 = my.sf(ST['A0101'])
        배분금액 = int( b_mon * 분할배분[0])
        매수예가 = round( 당일종가-0.01, 2) if 당일연속 >= 진입일자-1 else round( 당일종가 * 진입가치,2)    
        매수예정 = int( 배분금액/ 매수예가 )         

        LD['add0'] = LD['add18'] = CD['add0'] # 진행일자 및 초기일자 변경
        LD['add5'] = LD['add16'] = LD['add19'] = f"{n_mon:.2f}"
        LD['add6'] = '' # 진행상황
        LD['content'] = f"투자금액 변경 (기존) {o_mon:,.2f} > (변경) {n_mon:,.2f}, {x_mon}, (변경시작일) {LD['add0']}" 
        LD['add2'] = 'R' # 새로운 베이스 임을 표시 
        LD['add3'] = LD['add4'] = LD['add13'] = LD['add14'] = LD['add15'] = LD['add17'] = LD['add21'] = '0.00' 
        LD['add20'] = '기초셋팅'
        LD['add17'] = 배분금액
        LD['add19'] = f"{b_mon:.2f}" #초기금액
        LD['add22'] = 매수예정
        LD['add23'] = f"{매수예가:.2f}"
        
        # 새로운 데이타 
        del(LD['no']); del(LD['brother']); del(LD['tle_color']); del(LD['reply']); del(LD['hit'])
        LD['wdate'] = LD['mdate'] = my.now_timestamp()
        qry=self.DB.qry_insert('h_logDIY_board',LD)  
        self.DB.exe(qry)

        # 파라미터 업데이트

        return "___OK____"
    
