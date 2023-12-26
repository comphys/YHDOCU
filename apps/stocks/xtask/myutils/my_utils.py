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

def dayofdate(theday,delta=0) :
    dow = ('월','화','수','목','금','토','일')
    a = datetime.strptime(theday,'%Y-%m-%d')
    if delta : b = a+timedelta(days=delta) ; return (b.strftime('%Y-%m-%d'),dow[b.weekday()])
    else : return dow[a.weekday()]

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

def get_history(code,minDate) :
    headers = {'User-Agent' : ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36')}
    url = f"https://finance.yahoo.com/quote/{code}/history?p={code}"
    temp = requests.get(url, headers=headers)
    soup = bs(temp.text,'lxml')
    html = soup.select("#Col1-1-HistoricalDataTable-Proxy>section>div>table>tbody>tr")[0:20]

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
    url = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD'
    exchange =requests.get(url).json()
    return (exchange[0]['date'],exchange[0]['basePrice'])
