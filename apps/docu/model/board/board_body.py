from system.core.load import Model
import system.core.my_utils as ut

class M_board_body(Model) :

    def body_main(self) :
        self.D['Brother'] = int(self.gets.get('brother','0'))
        self.D['No'] = self.gets['no']

        qry = f"UPDATE h_{self.D['bid']}_board SET hit = hit +1 WHERE no = {self.D['No']}"
        self.DB.exe(qry)
        qry = f"SELECT * FROM h_{self.D['bid']}_board WHERE no = {self.D['No']}"
        BODY = self.DB.exe(qry,many=1,assoc=True)

        self.D['wdate'] = ut.timestamp_to_date(BODY['wdate'])
        self.D['mdate'] = ut.timestamp_to_date(BODY['mdate'])
        self.D['content'] = self.SYS.html_decode(BODY['content'])
        self.D['S_title'] = self.D['EXTITLE']['add0']
        self.D['BODY'] = BODY

        self.D['subject']  = BODY['add0']
        self.D['cur_time'] = ut.timestamp_to_date('now',6)

        # reply
        if self.D['BCONFIG']['type'] == 'yhboard' :
            qry = f"SELECT * FROM h_{self.D['bid']}_reply WHERE parent={self.D['No']} ORDER BY wdate"
            REPLY = self.DB.exe(qry,assoc=True)
            for rp in REPLY :
                rp['wdate'] = ut.timestamp_to_date(rp['wdate'],5)

            self.D['REPLY'] = REPLY

        if self.D['Brother'] :
            qry = f"SELECT no,add0,uname,wdate,mdate,hit,brother,reply FROM h_{self.D['bid']}_board WHERE "
            if self.D['Brother'] <0 : 
                qry += f"brother={self.D['No']} OR no={self.D['No']}" 
            else :
                qry += f"no={self.D['Brother']} OR brother={self.D['Brother']}" 
            qry += " ORDER BY wdate"
            self.D['APPEND'] = self.DB.exe(qry,assoc=True) 
            
            for ap in self.D['APPEND'] :
                ap['wdate'] = ut.timestamp_to_date(ap['wdate'],5)
                ap['mdate'] = ut.timestamp_to_date(ap['mdate'],5)
            
            self.D['Ano'] = int(self.D['No'])



