from system.core.load import Model

class M_board_write(Model) :

    def write_main(self) :
        self.D['Brother']  = int(self.gets.get('brother','0')) 
        self.D['Form_act'] = self.D['_bse'] + 'boards-action/save/' + self.D['bid']
        self.D['BODY']     = None

        if  self.D['Brother'] > 0 :
            qry = f"SELECT add0 FROM h_{self.D['bid']}_board WHERE no={self.D['Brother']}"
            self.D['B_title'] = self.DB.one(qry)
            self.D['MustCheck'] = ["'add0'","'추가 타이틀'"]
        
        if self.D['Mode'] == 'modify' :
            self.D['No'] = self.gets.get('no')
            self.D['Form_act'] = self.D['_bse'] + 'boards-action/modify/' + self.D['bid'] + '/no=' + self.D['No']
            qry = f"SELECT * FROM h_{self.D['bid']}_board WHERE no={self.D['No']}"
            self.D['BODY'] = self.DB.line(qry)
            self.D['BODY']['content'] = self.SYS.html_decode(self.D['BODY']['content'])
                   
        SKIN = self.SYS.load_skin("write")
        SKIN.write()