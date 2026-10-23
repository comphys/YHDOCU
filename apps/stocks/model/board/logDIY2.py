from system.core.load import Model
import system.core.my_utils as my

class Ajax(Model) :
    # Update Log ------------------------------------------------------------------------------------------------------------------------------------------



    def update_log(self) :

        board = 'h_logDIY2_board'
        cday = self.DB.last_date(board)
        lday = self.DB.last_date('h_stockHistory_board')
        if cday >= lday : return 

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

        # 최종 업데이트 확인날자 기록
        self.DB.parameter_update('A0721',lday)

        if  not LD['첫날기록'] or LD['add6'] in('익절매도','손절매도') :   
            del LD['첫날기록']  
            qry=DIY.DB.qry_insert(board,LD)
            DIY.DB.exe(qry)

        return self.SYS.json("OK")

    # -----------------------------------------------------------------------------------------------------------------------------------------------------
    
