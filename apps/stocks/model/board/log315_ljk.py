from system.core.load import Model
import system.core.my_utils as my

class Ajax(Model) :

    
    def dailyCheckUpdate(self) :

        odrday = self.D['post']['odrday']
        option = self.D['post']['option']
        
        if  option == 'RSN'   : key = 'TX070'
        if  option == 'N315'  : key = 'N0710_' + self.D['USER']['uid']
        self.DB.parameter_update(key,odrday)


    def reset_balance(self) :
        
        n_bl = self.D['post']['n_bl']
        LD = self.DB.last_record('h_log315_ljk_board')
        
        # 잔액 및 가치합계 재 설정
        o_mon = my.sv(LD['add5'])
        n_mon = my.sv(n_bl)
        x_mon = f"(증) {n_mon-o_mon:,.2f}" if n_mon > o_mon else f"(감) {o_mon-n_mon:,.2f}"

        LD['add0'] = LD['add18'] = self.DB.last_date("h_stockHistory_board")
        LD['add5'] = LD['add16'] = LD['add19'] = f"{n_mon:.2f}"
        LD['add6'] = ''
        LD['content'] = f"투자금액 변경 (기존) {o_mon:,.2f} > (변경) {n_mon:,.2f}, {x_mon}, (변경시작일) {LD['add0']}" 
        LD['add2'] = 'R' # 새로운 베이스 임을 표시 
        LD['add3'] = LD['add4'] = LD['add13'] = LD['add14'] = LD['add15'] = LD['add17'] = LD['add21'] = '0.00' 
        LD['add20'] = '기초셋팅'
        
        # 새로운 데이타 
        del(LD['no']); del(LD['brother']); del(LD['tle_color']); del(LD['reply']); del(LD['hit'])
        LD['wdate'] = LD['mdate'] = my.now_timestamp()
        qry=self.DB.qry_insert('h_log315_ljk_board',LD)  
        self.DB.exe(qry)

        # 파라미터 업데이트

        return "___OK____"


    def update_log(self) :

        N315 = self.SYS.load_app_lib('n315')
        board = 'h_log315_ljk_board'
        
        ini_data = self.DB.oneline(f"SELECT add18,add19 FROM {board} ORDER BY add0 DESC LIMIT 1")
        ini_date = ini_data[0]
        ini_capt = ini_data[1]
        lday = self.DB.last_date('h_stockHistory_board')
        
        N315.do_tacticLog(ini_date,lday,ini_capt)
        LD = N315.get_simulLog()
        
        LD['uid']   = 'ljk6244'
        LD['uname'] = '이재국'
        LD['wdate'] = LD['mdate'] = my.now_timestamp() 

        LS = self.DB.last_data_one('add1',board) # last season
        
        LD['add1'] = int(LS) + 1 if LD['add2'] == 1 else LS

        # 최종 업데이트 확인날자 기록
        self.DB.parameter_update('N0720',lday)
            
        if  not LD['첫날기록'] or LD['add6'] in('익절매도','손절매도') :   
            del LD['첫날기록']  
            qry=self.DB.qry_insert(board,LD)
            self.DB.exe(qry)

        return self.SYS.json("OK")

            

