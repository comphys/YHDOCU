from system.core.load import Model
import system.core.my_utils as my
# import requests

class Ajax(Model) :
    # Update Log ------------------------------------------------------------------------------------------------------------------------------------------



    def update_log(self,theday=None) :
        # 직접 호출
        day = theday
        # Ajax 호출
        if (self.D.get('post',None)) : day = self.D['post'].get('day',theday)
   
        board = 'h_logDIV_board'
        cday = self.DB.last_date(board)
        lday = self.DB.last_date('h_stockHistory_board')
        if not day and cday >= lday : return 

        DIV = self.SYS.load_app_lib('div')
        if day : lday = day

        ini_data = self.DB.oneline(f"SELECT add18,add19,add1 FROM {board} ORDER BY add0 DESC LIMIT 1")
        ini_date = ini_data[0]
        ini_capt = f"{my.sv(ini_data[1]):,.2f}"
        season   = ini_data[2]

        DIV.do_tacticLog(ini_date,lday,ini_capt)
        LD = DIV.get_simulLog()

        LD['uid']   = 'comphys'
        LD['uname'] = '정용훈'
        LD['wdate'] = LD['mdate'] = my.now_timestamp() 

        LD['add1'] = int(season) + 1 if LD['add2'] == 1 else season

        # 최종 업데이트 확인날자 기록
        self.DB.parameter_update('V0721',lday)

        if  not LD['첫날기록'] or LD['add6'] in('익절매도','손절매도') :   
            del LD['첫날기록']  
            qry=DIV.DB.qry_insert(board,LD)
            DIV.DB.exe(qry)

        return self.SYS.json("OK")

    # -----------------------------------------------------------------------------------------------------------------------------------------------------
    
    def dailyCheckUpdate(self) :

        odrday = self.D['post']['odrday']
        option = self.D['post']['option']
        
        if  option == 'DIV'  : key = 'V0710'

        self.DB.parameter_update(key,odrday)

        # 서버 업데이트 
        # if  self.D['_lcl'] :
        #     api_token = self.DB.store('api_token')
        #     host = "https://comphys.pythonanywhere.com/api/check/check_diy"
        #     headers = {'Content-Type':'application/json;charset=UTF-8','Authorization':api_token}
        #     data = {"diy_check":odrday}
        #     requests.post(host,headers=headers,json=data)


    def reset_balance(self) :
        
        n_bl = self.D['post']['n_bl']
        LD = self.DB.last_record('h_logDIV_board')
        CD = self.DB.last_record('h_stockHistory_board')
        ST = self.DB.parameters_dict('매매전략/DIV')
        
        # 잔액 및 가치합계 재 설정
        o_mon = my.sv(LD['add5'])
        n_mon = my.sv(n_bl)
        a_mon = my.sv(ST['A0702'])
        b_mon = n_mon + a_mon
        x_mon = f"(증) {n_mon-o_mon:,.2f}" if n_mon > o_mon else f"(감) {o_mon-n_mon:,.2f}"


        분할배분 = my.sf(ST['A0101'])
        배분금액 = int( b_mon * 분할배분[0])
    

        LD['add0'] = LD['add18'] = CD['add0'] # 진행일자 및 초기일자 변경
        LD['add5'] = LD['add16'] = LD['add19'] = f"{n_mon:.2f}"
        LD['add6'] = '' # 진행상황
        LD['content'] = f"투자금액 변경 (기존) {o_mon:,.2f} > (변경) {n_mon:,.2f}, {x_mon}, (변경시작일) {LD['add0']}" 
        LD['add2'] = 'R' # 새로운 베이스 임을 표시 
        LD['add3'] = LD['add4'] = LD['add13'] = LD['add14'] = LD['add15'] = LD['add17'] = LD['add21'] = '0.00' 
        LD['add20'] = '기초셋팅'
        LD['add17'] = 배분금액
        LD['add19'] = f"{b_mon:.2f}" #초기금액
        LD['add22'] = '0'
        LD['add23'] = '0.00'
        LD['add24'] = '0.00'
        LD['add25'] = '0.00'

        # 새로운 데이타 
        del(LD['no']); del(LD['brother']); del(LD['tle_color']); del(LD['reply']); del(LD['hit'])
        LD['wdate'] = LD['mdate'] = my.now_timestamp()
        qry=self.DB.qry_insert('h_logDIV_board',LD)  
        self.DB.exe(qry)

        # 파라미터 업데이트

        return "___OK____"


    def get_current_price(self) :
        opt = self.D['post'].get('opt',None)
        MR = self.SYS.load_app_lib('meritz')
        rst = MR.get_current_price()
        if rst :
            if opt == 'krwusd':
                    rst['환율'] = float(rst['환율'])
                    return self.SYS.json(rst)
            else : 
                if rst :
                    rst['현재가'] = f"{float(rst['현재가격']):.2f}"
                    return self.SYS.json(rst)
        else : return self.SYS.json("error::token_issue")
        
