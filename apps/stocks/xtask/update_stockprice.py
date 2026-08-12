from myutils.DB import DB
import requests
import myutils.my_utils as my
from datetime import datetime, timezone

class SU :
    def __init__(self) :
        self.DB = DB('stocks')
        self.skey = self.DB.store("slack_key")
        self.tkey = self.DB.store("tiingo")

    def send_message(self,message) :
        if self.DB.system == "Linux" : my.post_slack(self.skey,message)
        else : print(message)

    def stocks_update(self,cdx,today) :

        cdx = cdx.upper()
          
        # # add0 = date / add1 = code / add2 = alias / add4 = open / add5 = high / add6 = low / add7 = volume / add8 = change / add9 = up / add10 = dn
        one = self.DB.oneline(f"SELECT add0,add4,add5,add6,add3,add7,add8,add9,add10 FROM h_stockHistory_board WHERE add1='{cdx}' ORDER BY add0 DESC LIMIT 1")
        the_first_data = [one[0],float(one[1]),float(one[2]),float(one[3]),float(one[4]),int(one[5]),float(one[6]),int(one[7]),int(one[8])]

        # 주가 가져오기
        get_data = self.get_tiingo_price(cdx,today)
        if not get_data :  get_data = self.fetch_yahoo_chart_data(cdx,today)
        # 환율 가져오기
        krw = self.get_naver_fx_rate(today)
        if not krw : krw = self.fetch_yahoo_chart_data("KRW=X",today)[0][4]

        ohlc = []
        ohlc.append(the_first_data)
        ohlc.append(get_data)

        if  not ohlc[1] : return self.send_message("No data updated")
                  
        ohlc[1][6]  = round((ohlc[1][4] - ohlc[0][4])/ohlc[0][4]*100,2) 
        ohlc[1][7]  = ohlc[0][7]+1 if ohlc[1][4] >= ohlc[0][4] else 0
        ohlc[1][8]  = ohlc[0][8]+1 if ohlc[1][4] <  ohlc[0][4] else 0
            
        db_keys = "add0,add4,add5,add6,add3,add7,add8,add9,add10,add1,add2,uid,uname,wdate,mdate"
        time_now = my.now_timestamp()

        row = ohlc[1] + [cdx,krw,'comphys','정용훈',time_now,time_now]
        values = str(row)[1:-1]

        sql = f"INSERT INTO h_stockHistory_board ({db_keys}) VALUES({values})"
        self.DB.exe(sql)

        self.send_message(f"{today}일 주가&환율 업데이트")

    def get_tiingo_price(self,symbol,today) :

        app_key = self.DB.store("tiingo")

        symbol = symbol.lower()
        headers = { 'Content-Type' : 'application/json' }
        url = f"https://api.tiingo.com/tiingo/daily/{symbol}/prices?startDate={today}&endDate={today}&token={app_key}"
        
        row = requests.get(url,headers).json()[0]

        return [today,row['open'],row['high'],row['low'],row['close'],row['volume'],0.0,0,0]

    def get_naver_fx_rate(self,target_date):

        # 1. 네이버 일별 환율 시세 API (pageSize를 늘려 과거 데이터 확보)
        url = "https://api.stock.naver.com/marketindex/exchange/FX_USDKRW/prices?pageSize=10&page=1"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        res = requests.get(url, headers=headers)
        data = res.json()
        
        # 2. API 응답 데이터 중 입력한 날짜와 일치하는 항목 찾기
        for item in data:
            if item['localTradedAt'] == target_date:
                return my.sv(item['closePrice'])
            
        return ''
      
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


    def stock_holiday(self,today) :
        
        weekd = my.dayofdate(today)

        if weekd in ['토','일'] : return f"{weekd}요일 : Good morning !"
        chk = self.DB.one(f"SELECT description FROM parameters WHERE val='{today}' AND cat='미국증시휴장일'")

        return "Today is a holiday !" if chk else None

# --------------------------------------------------------------------------------------------------
A = SU()
today = my.kor_loc_date('US/Eastern')[0:10]
skip = A.stock_holiday(today)

if  skip : 
    A.send_message(skip)

else :
    A.stocks_update('soxl',today)

