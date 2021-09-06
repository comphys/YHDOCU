import datetime,html,requests
from bs4 import BeautifulSoup

# page_scrap table :  id / url / content / wdate / mdate
class SCRAP :

    def __init__(self,SYS) :    
        self.SYS = SYS
        self.info = SYS.info
        self.DB2 = SYS.db('scrap')
        self.select = None
        self.html_text = None
        self.table = 'page_scrap'
        self.url=''
        self.selector='body'
        self.id=''
        self.interval = 60

    def get(self) :
        if not self.id : return "조회 ID가 누락되었습니다"
        qry = f"SELECT mdate FROM {self.table} WHERE id='{self.id}'"

        cnt = self.DB2.cnt(qry)
 
        if cnt == 0 : self.db_put('in')
        else : 
            rst = self.DB2.line(qry)
            itv = int(datetime.datetime.now().timestamp()) - rst['mdate']
            if itv > self.interval : self.db_put('up')

        qry = f"SELECT content FROM {self.table} WHERE id='{self.id}'"
        html_soup = self.DB2.one(qry)
        txt =  self.SYS.html_decode(html_soup)
        return BeautifulSoup(txt,'lxml')

    def encode(self,htx) :
        return self.SYS.html_encode(str(htx))

    def html_simple(self,html_str) :
        html_str = html_str.replace('\r\n','')
        html_str = html_str.replace('\t','')
        html_str = html_str.replace('\n','')
        return html_str

    def db_put(self,op) :
        if not self.id : return
        temp = requests.get(self.url)
        temp = self.html_simple(temp.text)
        soup = BeautifulSoup(temp,'lxml')
        
        html_text = soup.select_one(self.selector) if self.selector else soup
        html_dbin = html.escape(str(html_text))

        if op == 'in' :
            db_in = {}
            db_in['id'] = self.id 
            db_in['url'] = self.url
            db_in['content'] = html_dbin
            db_in['wdate'] = int(datetime.datetime.now().timestamp())
            db_in['mdate'] = db_in['wdate']
            qry = self.DB2.qry_insert(self.table,db_in)
            self.DB2.exe(qry)
        
        else :
            db_up = {}
            db_up['content'] = html_dbin
            db_up['mdate'] = int(datetime.datetime.now().timestamp())
            con = f"id='{self.id}'"
            qry = self.DB2.qry_update(self.table,db_up,con)
            self.DB2.exe(qry)