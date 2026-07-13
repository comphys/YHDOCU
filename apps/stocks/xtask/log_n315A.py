import myutils.my_utils as my
from lib_diy import update_DIY


today = my.kor_loc_date('US/Eastern')[0:10]
weekd = my.dayofdate(today)
DIY = update_DIY()

ck_holiday = DIY.DB.exe(f"SELECT description FROM parameters WHERE val='{today}' AND cat='미국증시휴장일'")
is_holiday = ck_holiday[0][0] if ck_holiday else ''

skip = (weekd in ['토','일']) or is_holiday

if  skip :
    pass

else :
    
    ini_data = DIY.DB.oneline("SELECT add18,add19 FROM h_log315_board ORDER BY add0 DESC LIMIT 1")
    ini_date = ini_data[0]
    ini_capt = f"{my.sv(ini_data[1]):,.2f}"
    
    DIY.do_tacticLog(ini_date,today,ini_capt)
    LD = DIY.get_simulLog()
    
    LD['uid']   = 'comphys'
    LD['uname'] = '정용훈'
    LD['wdate'] = LD['mdate'] = my.now_timestamp() 

    LS = DIY.DB.last_data_one('add1','h_log315_board') # last season
    
    LD['add1'] = int(LS) + 1 if LD['add2'] == 1 else LS
        
    if  not LD['첫날기록'] or LD['add6'] in('익절매도','손절매도') :   
        del LD['첫날기록']  
        qry=DIY.DB.qry_insert('h_log315_board',LD)
        DIY.DB.exe(qry)
        DIY.send_message(f"{today}일 N315 업데이트 완료")
        
    else :
        DIY.send_message(f"{today}일 N315 변동사항 없음")
         