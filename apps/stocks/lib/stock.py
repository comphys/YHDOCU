import requests
from bs4 import BeautifulSoup as bs
import system.core.my_utils as my

class STOCK :
    
    def __init__(self,SYS) :    
        self.SYS = SYS
        self.headers = {'User-Agent' : ('Mozilla/5.0 (Windows NT 10.0;Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36')} 

    
    def get_usd_krw():
        headers = {'User-Agent' : ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36')}
        url = "https://finance.naver.com/marketindex/?tabSel=exchange"
        temp = requests.get(url, headers=headers)
        soup = bs(temp.text,'lxml')
        html_value = soup.select("#exchangeList > li.on > a.head.usd > div > span.value")[0]
        html_date  = soup.select("#exchangeList > li.on > div > span.time")[0]
        html_date  = html_date.text.replace('.','-')
        return (html_date[:10],my.sv(html_value.text))
    

    def get_tiingo_price(self,app_key,symbol,dfrom,dto) :
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