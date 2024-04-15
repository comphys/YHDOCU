import requests
from bs4 import BeautifulSoup as bs
import system.core.my_utils as my

class STOCK :
    
    def __init__(self,SYS) :    
        self.SYS = SYS
        self.headers = {'User-Agent' : ('Mozilla/5.0 (Windows NT 10.0;Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')} 

    def get_history(self,code,minDate) :
        url = f"https://finance.yahoo.com/quote/{code}/history"
        temp = requests.get(url, headers=self.headers)
        soup = bs(temp.text,'lxml')
        html = soup.select("#nimbus-app > section > section > section > article > div.container > div.table-container.svelte-ta1t6m > table > tbody > tr")[0:20]

        today = my.timestamp_to_date(ts='now',opt=7)
        SH = []
   
        for trs in html :
            tds = trs.select('td')
            if (len(tds)) < 3 : continue
            tdate = my.date_format_change(tds[0].text,"%b %d, %Y","%Y-%m-%d")
            if tdate >= today    : continue
            if tdate <  minDate  : break
            SH.append([tdate,my.sv(tds[1].text),my.sv(tds[2].text),my.sv(tds[3].text),my.sv(tds[4].text),my.sv(tds[6].text,'i'),0.0,0,0])
        
        return(SH[::-1])
    
    def get_usd_krw(self):
        url = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD'
        exchange =requests.get(url).json()
        return (exchange[0]['date'],exchange[0]['basePrice'])