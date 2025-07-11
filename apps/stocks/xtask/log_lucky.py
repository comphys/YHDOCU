import myutils.my_utils as my
from lib_rsn   import update_Log
from lib_lucky import update_lucky

today = my.kor_loc_date('US/Eastern')[0:10]
weekd = my.dayofdate(today)
RSN = update_Log()
LUC = update_lucky()

ck_holiday = LUC.DB.exe(f"SELECT description FROM parameters WHERE val='{today}' AND cat='미국증시휴장일'")
is_holiday = ck_holiday[0][0] if ck_holiday else ''

skip = (weekd in ['토','일']) or is_holiday

if  skip :
    pass

else :

    wait = int(LUC.DB.parameter('L0200'))
    RSN.do_luckyLog(today)
    DV = RSN.get_luckyLog()
     
    LUC.DB.parameter_update('L0202',DV['기록일자']) 
    거래일자 = LUC.next_stock_day(DV['기록일자'])[0]

    if not float(DV['진입가격']) : LUC.DB.parameter_update('L0500',거래일자)
    
    if  not wait : 
        
        if  DV['감시시작'] :
            LUC.DB.parameter_update('L0200',DV['기록시즌'])
            LUC.DB.parameter_update('L0201',DV['진입가격'])
            LUC.send_message(f"{today}일 LUCKY 초기셋팅 완료")

        else : 
            LUC.send_message(f"{today}일 LUCKY 모드 진행 대기")
        
    else :

        LUC.M['당일종가'] = DV['당일종가']
        LUC.M['전일종가'] = DV['전일종가']
        LUC.M['매수가격'] = my.sv(LUC.DB.parameter('L0201'))
        LUC.M['매도예가'] = DV['매도예가']
        
        LUC.DB.parameter_update('L0201',DV['진입가격'])

        LUC.today_check()
        
        D = LUC.output()
        
        if  D :         
            D['uid']   = 'comphys'
            D['uname'] = '정용훈'
            D['wdate'] = D['mdate'] = my.now_timestamp() 

            D['add0']  = DV['기록일자']
            D['add1']  = DV['기록시즌']
            D['add2']  = DV['기록날수']
            D['add3']  = DV['당일종가']
            D['add4']  = DV['종가변동']

            qry=LUC.DB.qry_insert('h_log_lucky_board',D)
            LUC.DB.exe(qry)
            LUC.send_message(f"{today}일 매매일지 작성완료")

            if not float(D['add20']) : LUC.DB.parameter_update('L0500',거래일자)

        else :
            LUC.send_message(f"{today}일 LUCKY 매매 대기중입니다")

        if  DV['진행종료'] : 
            LUC.DB.parameter_update('L0200','0')
            LUC.DB.parameter_update('L0201','0')


        
    
    
    
       