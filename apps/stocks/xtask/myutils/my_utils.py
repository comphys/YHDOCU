from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
from pytz import timezone
import requests, math

# number

def round_up(n,decimals=2) :
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

def ceil(n) :
    return math.ceil(n)

def sv(v,s='f') :
    return float(v.replace(',','')) if s=='f' else int(v.replace(',',''))

def sf(v,s='f') :
    temp = v.split('/')
    if s == 'f' : return([float(x) for x in temp])
    else : return([int(x) for x in temp])

# time & date

def now_timestamp() :
    return int(datetime.now().timestamp())

def date_format_change(v,f1,f2) :
    return datetime.strptime(v,f1).strftime(f2)

def timestamp_to_date(ts='now',opt=1) :

    kst = timezone('Asia/Seoul')

    if ts=='now' : ts = int(datetime.now().timestamp())

    if    opt == 1 : t_format = "%Y-%m-%d %H:%M:%S"
    elif  opt == 2 : t_format = "%Y/%m/%d %H:%M:%S"
    elif  opt == 3 : t_format = "%y-%m-%d %H:%M"
    elif  opt == 4 : t_format = "%y%m%d"
    elif  opt == 5 : t_format = "%Y/%m/%d %H:%M"
    elif  opt == 6 : t_format = "%y/%m/%d %H:%M:%S"
    elif  opt == 7 : t_format = "%Y-%m-%d"
    else  : t_format = opt

    return datetime.fromtimestamp(ts,kst).strftime(t_format)


def kor_loc_date(opt) :

    loc = timezone('Asia/Seoul') if opt == 'kor' else timezone('US/Eastern')

    ts = int(datetime.now().timestamp())
    t_format = "%Y-%m-%d %H:%M:%S"
        
    loc_time = datetime.fromtimestamp(ts,loc).strftime(t_format)
    
    return (loc_time)

def dayofdate(theday,delta=0) :
    dow = ('월','화','수','목','금','토','일')
    a = datetime.strptime(theday,'%Y-%m-%d')
    if delta : b = a+timedelta(days=delta) ; return (b.strftime('%Y-%m-%d'),dow[b.weekday()])
    else : return dow[a.weekday()]

def diff_day(day1,day2='') :
    a = datetime.strptime(day1,'%Y-%m-%d')
    b = datetime.now() if not day2 else datetime.strptime(day2,'%Y-%m-%d')
    c = b-a
    return c.days

# social media

def post_slack(key,text,ch='주식'):

    client = WebClient(token=key)
    try:
        response = client.chat_postMessage(channel= ch, text= text)
        assert response["message"]["text"] == text
    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]
        print(f"slack error : {e.response['error']}")


# stock
#nimbus-app > section > section > section > article > div.container > div.table-container.svelte-ewueuo > table > tbody > tr
def get_history(code,minDate) :
    headers = {'User-Agent' : ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36')}
    url = f"https://finance.yahoo.com/quote/{code}/history"
    temp = requests.get(url, headers=headers)
    soup = bs(temp.text,'lxml')
    html = soup.select("#nimbus-app > section > section > section > article > div > div > table > tbody > tr")[0:20]

    today = timestamp_to_date(ts='now',opt=7)
    SH = []

    for trs in html :
        tds = trs.select('td')
        if (len(tds)) < 3 : continue
        tdate = date_format_change(tds[0].text,"%b %d, %Y","%Y-%m-%d")
        if tdate >= today : continue
        if tdate <  minDate : break
        SH.append([tdate,sv(tds[1].text),sv(tds[2].text),sv(tds[3].text),sv(tds[4].text),sv(tds[6].text,'i'),0.0,0,0])

    return(SH[::-1])

def get_usd_krw():
    headers = {'User-Agent' : ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36')}
    url = "https://finance.naver.com/marketindex/?tabSel=exchange"
    temp = requests.get(url, headers=headers)
    soup = bs(temp.text,'lxml')
    html_value = soup.select("#exchangeList > li.on > a.head.usd > div > span.value")[0]
    html_date  = soup.select("#exchangeList > li.on > div > span.time")[0]
    html_date  = html_date.text.replace('.','-')
    return (html_date[:10],sv(html_value.text))

def get_stockdio_price(app_key,symbol,dfrom,dto) :
    url  = f"https://api.stockdio.com/data/financial/prices/v1/GetHistoricalPrices?app-key={app_key}&symbol={symbol}&from={dfrom}&to={dto}"
    temp = requests.get(url).json()
    ohlc = temp['data']['prices']['values']
    
    SH = []
    for row in ohlc :
        tdate = row[0][:10]
        if tdate < dfrom : break
        SH.append([tdate,row[1],row[2],row[3],row[4],row[5],0.0,0,0])

    return SH

def get_alphavantage_price(app_key,symbol,dfrom) :
    url  = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={app_key}"
    temp = requests.get(url).json()

    tmp1 = dict(temp["Time Series (Daily)"])

    if  dfrom in tmp1 :
        tmp2 = list(tmp1[dfrom].values()) #ohlcv
        ohlc = [dfrom,float(tmp2[0]),float(tmp2[1]),float(tmp2[2]),float(tmp2[3]),int(tmp2[4]),0.0,0,0] 
    else : ohlc = None

    return ohlc

def get_tiingo_price(app_key,symbol,dfrom,dto) :
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
    
