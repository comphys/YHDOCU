from system.core.load import Control

class Winopen(Control) :
    def search(self) :
        
        SearchCata = self.D['post'].get('search_cata','all')
        if self.D['post'] :
            self.D['SearchWord'] = self.D['post']['search_word']
            if self.D['SearchWord'] != "" : 
                self.D['SearchCata'] = self.D['post']['search_cata']

                board_list = self.DB.exe("SELECT bid FROM h_board_config WHERE type != 'page'")
                board_list = [x[0] for x in board_list]

                sql = "SELECT a.no,a.add0,a.brother, b.bid, b.title FROM h_#TABLE#_board as a LEFT JOIN h_board_config as b ON b.bid='#TABLE#' WHERE "

                if self.D['SearchCata'] == 'subject' : 
                    sql2 = sql+"a.add0 LIKE '%" + self.D['SearchWord'] + "%'"
                elif self.D['SearchCata'] == 'content' : 
                    sql2 = sql+"a.content LIKE '%" + self.D['SearchWord'] + "%'"
                else : sql2 = sql+"a.add0 LIKE '%" + self.D['SearchWord'] + "%' OR a.content LIKE '%" + self.D['SearchWord'] + "%'"

                RS=[]
                for board in board_list :
                    sql3 = sql2.replace('#TABLE#',board)
                    rs = self.DB.exe(sql3,assoc=True)
                    RS=RS+rs

                for row in RS :
                    row['add0'] = row['add0'].replace(self.D['SearchWord'],f"<span class='search'>{self.D['SearchWord']}</span>",1)

                self.D['SLIST']=RS


        self.D['cata_s'] = {'subject':'','content':'','all':''}
        self.D['cata_s'][SearchCata] = 'selected'

        return self.html("winopen/search.html")