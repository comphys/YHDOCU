import system.core.my_utils as my
import requests
from datetime import datetime, timezone
# from bs4 import BeautifulSoup as bs

class OHLC :

    def __init__(self,SYS) :
        self.SYS   = SYS
        self.info  = SYS.info
        self.D     = SYS.D
        self.DB    = SYS.DB

    def stocks_update(self,cdx,today) :

        cdx = cdx.upper()
          
        # # add0 = date / add1 = code / add2 = alias / add4 = open / add5 = high / add6 = low / add7 = volume / add8 = change / add9 = up / add10 = dn
        one = self.DB.oneline(f"SELECT add0,add4,add5,add6,add3,add7,add8,add9,add10 FROM h_stockHistory_board WHERE add1='{cdx}' ORDER BY add0 DESC LIMIT 1")
        the_first_data = [one[0],float(one[1]),float(one[2]),float(one[3]),float(one[4]),int(one[5]),float(one[6]),int(one[7]),int(one[8])]

        ohlc = []
        ohlc.append(the_first_data)
        ohlc.append(self.get_tiingo_price(cdx,today))

        if  not ohlc[1] : return False
                  
        ohlc[1][6]  = round((ohlc[1][4] - ohlc[0][4])/ohlc[0][4]*100,2) 
        ohlc[1][7]  = ohlc[0][7]+1 if ohlc[1][4] >= ohlc[0][4] else 0
        ohlc[1][8]  = ohlc[0][8]+1 if ohlc[1][4] <  ohlc[0][4] else 0
            
        # 환율 업데이트
        krw = self.fetch_yahoo_chart_data("KRW=X",today)[0][4]

        db_keys = "add0,add4,add5,add6,add3,add7,add8,add9,add10,add1,add2,uid,uname,wdate,mdate"
        time_now = my.now_timestamp()

        row = ohlc[1] + [cdx,krw,'comphys','정용훈',time_now,time_now]
        values = str(row)[1:-1]

        sql = f"INSERT INTO h_stockHistory_board ({db_keys}) VALUES({values})"
        self.DB.exe(sql)

        return True

    def get_tiingo_price(self,symbol,today) :

        app_key = self.DB.store("tiingo")

        symbol = symbol.lower()
        headers = { 'Content-Type' : 'application/json' }
        url = f"https://api.tiingo.com/tiingo/daily/{symbol}/prices?startDate={today}&endDate={today}&token={app_key}"
        
        row = requests.get(url,headers).json()[0]

        return [today,row['open'],row['high'],row['low'],row['close'],row['volume'],0.0,0,0]

    # def get_usd_krw(self):
    #     headers = {'User-Agent' : ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36')}
    #     url = "https://finance.naver.com/marketindex/?tabSel=exchange"
    #     temp = requests.get(url, headers=headers)
    #     soup = bs(temp.text,'lxml')
    #     html_value = soup.select("#exchangeList > li.on > a.head.usd > div > span.value")[0]
    #     html_date  = soup.select("#exchangeList > li.on > div > span.time")[0]
    #     html_date  = html_date.text.replace('.','-')
    #     return (html_date[:10],my.sv(html_value.text))


    # --------------------------------------------------------------------------------------------------------------------------------------------------------
    # yahoo에서 데이타 가져오기 krwx = fetch_yahoo_chart_data("KRW=X",'2026-08-09')
    # --------------------------------------------------------------------------------------------------------------------------------------------------------

    def fetch_yahoo_chart_data(self,ticker, target_date_str):

        target_dt = datetime.strptime(target_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        period1 = int(target_dt.timestamp())
        period2 = period1 + 86400  # 24시간 추가
        
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        params  = { "period1": period1, "period2": period2, "interval": "1d" }
        headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            result = data['chart']['result'][0]
            timestamps = result.get('timestamp', [])
            
            if not timestamps:
                return None
                
            indicators = result['indicators']['quote'][0]
            return [[target_date_str,round(indicators['open'][0],2),round(indicators['high'][0],2),round(indicators['low'][0],2),round(indicators['close'][0],2),round(indicators['volume'][0],2),0.0,0.0]]

        except Exception as e:
            return None
