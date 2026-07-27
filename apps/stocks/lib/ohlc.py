import system.core.my_utils as my
import requests
from bs4 import BeautifulSoup as bs

class OHLC :

    def __init__(self,SYS) :
        self.SYS   = SYS
        self.info  = SYS.info
        self.D     = SYS.D
        self.DB    = SYS.DB

    def stocks_update(self,cdx,today) :
        cdx = cdx.upper()
        b_date = self.DB.one(f"SELECT max(add0) FROM h_stockHistory_board WHERE add1='{cdx}'")
        
        # # add0 = date / add1 = code / add2 = alias / add4 = open / add5 = high / add6 = low / add7 = volume / add8 = change / add9 = up / add10 = dn
        one = self.DB.oneline(f"SELECT add0,add4,add5,add6,add3,add7,add8,add9,add10 FROM h_stockHistory_board WHERE add0='{b_date}' and add1='{cdx}'")
        the_first_data = [one[0],float(one[1]),float(one[2]),float(one[3]),float(one[4]),int(one[5]),float(one[6]),int(one[7]),int(one[8])]

      
        ohlc = self.get_tiingo_price(cdx,b_date,today)

        if  not ohlc : return False
        
        ohlc[0] = the_first_data
            
        for i in range(1,len(ohlc)) :
            ohlc[i][6]  = round((ohlc[i][4] - ohlc[i-1][4])/ohlc[i-1][4]*100,2) 
            ohlc[i][7]  = ohlc[i-1][7]+1 if ohlc[i][4] >= ohlc[i-1][4] else 0
            ohlc[i][8]  = ohlc[i-1][8]+1 if ohlc[i][4] <  ohlc[i-1][4] else 0
            
        rst3 = ohlc[1:]

        db_keys = "add0,add4,add5,add6,add3,add7,add8,add9,add10,add1,add2,uid,uname,wdate,mdate"
        time_now = my.now_timestamp()
        
        # 환율 업데이트
        krw = self.get_usd_krw()

        if rst3 :
            for row in rst3 :
                row2 = list(row)
                row2 += [cdx,'','comphys','정용훈',time_now,time_now]
                values = str(row2)[1:-1]
                sql = f"INSERT INTO h_stockHistory_board ({db_keys}) VALUES({values})"
                self.DB.exe(sql)

            lday = rst3[-1][0]
            self.DB.exe(f"UPDATE h_stockHistory_board SET add2={krw[1]} WHERE add0='{lday}'")

        return True

    def get_tiingo_price(self,symbol,dfrom,dto) :

        app_key = self.DB.store("tiingo")

        symbol = symbol.lower()
        headers = { 'Content-Type' : 'application/json' }
        url = f"https://api.tiingo.com/tiingo/daily/{symbol}/prices?startDate={dfrom}&endDate={dto}&token={app_key}"
        
        ohlc = requests.get(url,headers).json()
        
        SH = []
        for row in ohlc :
            tdate = row['date'][:10]
            if tdate < dfrom : break
            SH.append([tdate,row['open'],row['high'],row['low'],row['close'],row['volume'],0.0,0,0])

        return SH

    def get_usd_krw(self):
        headers = {'User-Agent' : ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36')}
        url = "https://finance.naver.com/marketindex/?tabSel=exchange"
        temp = requests.get(url, headers=headers)
        soup = bs(temp.text,'lxml')
        html_value = soup.select("#exchangeList > li.on > a.head.usd > div > span.value")[0]
        html_date  = soup.select("#exchangeList > li.on > div > span.time")[0]
        html_date  = html_date.text.replace('.','-')
        return (html_date[:10],my.sv(html_value.text))