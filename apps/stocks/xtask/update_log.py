import myutils.my_utils as my
from lib_rst import update_Log

# 실행순서 : update_logj.py  >  update_log.py 

today = my.kor_loc_date('US/Eastern')[0:10]
weekd = my.dayofdate(today)
RST = update_Log('rst')

ck_holiday = RST.DB.exe(f"SELECT description FROM parameters WHERE val='{today}' AND cat='미국증시휴장일'")
is_holiday = ck_holiday[0][0] if ck_holiday else ''

skip = (weekd in ['토','일']) or is_holiday

if  skip :
    pass

else :
    RST.do_tacticsLog(today)
    DV = RST.get_tacticLog(today,'V')
    DR = RST.get_tacticLog(today,'R')
    DS = RST.get_tacticLog(today,'S')
    DT = RST.get_tacticLog(today,'T')

    RST.nextStep()
    NV = RST.get_nextStrategyLog('V')
    NR = RST.get_nextStrategyLog('R')
    NS = RST.get_nextStrategyLog('S')
    NT = RST.get_nextStrategyLog('T')

    DV |= NV; DV.update({k:'' for k,v in DV.items() if v == None})
    DR |= NR; DR.update({k:'' for k,v in DR.items() if v == None})
    DS |= NS; DS.update({k:'' for k,v in DS.items() if v == None})
    DT |= NT; DT.update({k:'' for k,v in DT.items() if v == None})

    del DV['Update']
    del DR['Update']
    qry=RST.DB.qry_insert(RST.M['일반보드'],DV); RST.DB.exe(qry)
    qry=RST.DB.qry_insert(RST.M['기회보드'],DR); RST.DB.exe(qry)

    isDsUpdate = DS['Update']; del DS['Update']
    isDtUpdate = DT['Update']; del DT['Update']

    if  isDsUpdate :
        preDate = RST.DB.one(f"SELECT max(add0) FROM {RST.M['안정보드']}")
        qry=RST.DB.qry_update(RST.M['안정보드'],DS,f"add0='{preDate}'")
        RST.DB.exe(qry)
    else :
        qry=RST.DB.qry_insert(RST.M['안정보드'],DS)
        RST.DB.exe(qry)
    
    if  isDtUpdate :
        preDate = RST.DB.one(f"SELECT max(add0) FROM {RST.M['생활보드']}")
        qry=RST.DB.qry_update(RST.M['생활보드'],DT,f"add0='{preDate}'")
        RST.DB.exe(qry)
    else :
        qry=RST.DB.qry_insert(RST.M['생활보드'],DT)
        RST.DB.exe(qry)

    RST.send_message(f"{today}일 VRST-O 업데이트 완료")
    
    # 자산현황 업데이트
    # 초기값 설정
    init_capital = 36734.2
    jyh = 0.30
    jyw = 0.35
    jhj = 0.35
    
    AD = {}
    AD['add0'] = DR['add0']

    preDate = RST.DB.one(f"SELECT max(add0) FROM h_my_Asset_board WHERE add0 < '{AD['add0']}'")
    LD = RST.DB.one(f"SELECT add18 FROM h_my_Asset_board WHERE add0='{preDate}'")
    LD = my.sv(LD)
 
    AD['add18'] = float(DR['add6']) + float(DS['add6']) + float(DT['add6']) # 현매수금 
    
    AD['add1'] = DR['add0'][:4]
    AD['add2'] = DR['add0'][5:7]
    AD['add3'] = '수익실현' if DR['sub29'] == '전량매도' else '매수진행'
    AD['add4'] = DR['add14']
    
    AD['add5'] = int(DR['add9'])  + int(DS['add9'])  + int(DT['add9'])
    AD['add6'] = float(DR['add15']) + float(DS['add15']) + float(DT['add15']) # 가치

    AD['add7'] = float(DR['add18']) + float(DS['add18']) + float(DT['add18']) # 현재손익
    AD['add7'] = round(AD['add7'],2)
    
    AD['add8'] = round(AD['add7']/LD * 100,2) if AD['add3'] == '수익실현' else round(AD['add7']/AD['add18'] * 100,2) 
    AD['add9'] = float(DR['add3']) + float(DS['add3'])  + float(DT['add3']) # 현금 
    
    AD['add10'] = AD['add6'] + AD['add9']
    AD['add11'] = round(AD['add10'] - init_capital,2) # 누적수익
    AD['add12'] = round(AD['add11']/init_capital * 100,2)
    AD['add13'] = float(RST.DB.one(f"SELECT usd_krw FROM usd_krw ORDER BY rowid DESC LIMIT 1"))

    AD['add14'] = int(AD['add10'] * AD['add13'])
    AD['add15'] = int(AD['add14'] * jyh)
    AD['add16'] = int(AD['add14'] * jyw)
    AD['add17'] = int(AD['add14'] * jhj)
    
    AD['uid']   = 'comphys'
    AD['uname'] = '정용훈'
    AD['wdate'] = AD['mdate'] = my.now_timestamp() 
    qry=RST.DB.qry_insert('h_my_Asset_board',AD); RST.DB.exe(qry)
    