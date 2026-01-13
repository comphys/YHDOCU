from system.core.load import Model
import system.core.my_utils as my

class Ajax(Model) :

    
    def dailyCheckUpdate(self) :

        odrday = self.D['post']['odrday']
        option = self.D['post']['option']
        
        if  option == 'RSN'   : key = 'TX070'
        if  option == 'N315'  : key = 'N0710_' + self.D['USER']['uid']
        if  option == 'LUCKY' : key = 'L0500'
        self.DB.parameter_update(key,odrday)


    def reset_balance(self) :
        
        n_bl = self.D['post']['n_bl']
        LD = self.DB.last_record('h_log315_board')
        
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
        self.DB.parameter_update(f"N0701_{self.D['USER']['uid']}",LD['add0'])
        return "___OK____"
