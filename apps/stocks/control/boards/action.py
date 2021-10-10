from system.core.load import Control
import system.core.my_utils as ut

class Action(Control) : 

    def _auto(self) :
        self.DB = self.db('stocks')
        self.bid   = self.parm[0]
        self.board = 'h_'+self.bid+'_board'
        self.page  = self.gets.get('page','1') 
        self.DB.tbl, self.DB.wre = ("h_board_config",f"bid='{self.bid}'")
        self.BCONFIG = self.DB.get("*",many=1,assoc=True)
  
    def save(self) :
        # h_{bid}_board : [no,brother,add0,uid,uname,content,reply,hit,wdate,mdate,add1~add15]
        
        # 저장 시 [정수 및 실수] 형식은 형태를 수정하여 저장한다. 
        USE_KEY = []
        for i in range(16) :
            key = f'add{i}' 
            if self.BCONFIG[key] :  USE_KEY.append(key)        

        SAVE = self.D['post']

        if SAVE['mode'] == 'add_body' :
            no = int(self.gets.get('no',0))
            origin = int(SAVE['brother']) if int(SAVE['brother']) > 0 else no
            qry = f"UPDATE {self.board} SET brother = brother-1 WHERE no={origin}"
            self.DB.exe(qry)
            SAVE['brother'] = no

 
        SAVE['wdate']   = ut.now_timestamp()
        SAVE['mdate']   = SAVE['wdate']
        SAVE['content'] = self.html_encode(SAVE['content'])
        SAVE.pop('mode')
       
        qry = self.DB.qry_insert(self.board,SAVE)
        self.DB.exe(qry)

        if self.bid == 'daily_trading' :
            self.DB.tbl,self.DB.wre = ('h_daily_trading_board',f"add1='{SAVE['add1']}' and add2='{SAVE['add2']}'")
            self.save_chart(self.DB.get_one('no'))
        
        return self.moveto('board/list/'+self.bid+'/page='+self.page+'/csh=on')

    def delete(self) :
        no      = self.gets['no']
        bid     = self.parm[0]
        page    = self.gets['page']
        
        board_type = self.DB.one(f"SELECT type FROM h_board_config WHERE bid='{bid}'")
        
        if board_type == 'yhboard' :
            qry =   f"SELECT brother FROM h_{bid}_board WHERE no={no}"
            brother = self.DB.one(qry)

            if brother < 0 : self.echo("추가글이 존재합니다")
            if brother > 0 : self.DB.exe(f"UPDATE h_{bid}_board SET brother = brother + 1 WHERE no={brother}")

            qry = f"DELETE FROM h_{bid}_reply WHERE parent={no}"
            self.DB.exe(qry)
        
        qry = f"DELETE FROM h_{bid}_board WHERE no={no}"
        self.DB.exe(qry)

        return self.moveto(f"board/list/{bid}/page={page}")

    def modify(self) :
        # h_{bid}_board : [no,brother,add0,uid,uname,content,reply,hit,wdate,mdate,add1~add15]
        brother = self.D['post'].get('brother',0)
        tbl     = 'h_'+self.parm[0]+'_board'
        no      = self.gets['no']

        con     = f"no={no}"
        # 업데이트 항목 외에는 pop 시킨다.
        self.D['post'].pop('mode')
        self.D['post'].pop('uid')
        self.D['post'].pop('uname')
        # 
        self.D['post']['mdate'] = ut.now_timestamp()
        self.D['post']['content'] = self.html_encode(self.D['post']['content'])

        qry = self.DB.qry_update(tbl,self.D['post'],con)
        self.DB.exe(qry)

        if self.bid == 'daily_trading' : 
            self.save_chart(no)
            return self.moveto(f"board/list/{self.parm[0]}/page={self.page}/csh=on")
        if self.BCONFIG['stayfom'] == 'on' :
            return self.moveto(f"board/modify/{self.parm[0]}/no={no}/page={self.page}/brother={brother}")
        else :
            return self.moveto(f"board/body/{self.parm[0]}/no={no}/brother={brother}")

    def save_chart(self,no) :

        import matplotlib.pyplot as plt

        self.DB.tbl, self.DB.wre = ('h_daily_trading_board',f'no={no}')
        code, season = self.DB.get('add1,add2',many=1,assoc=False)
        file_name = f"{self.C['DOCU_ROOT']}/개인자료/주식투자/주식챠트/stock_chart_{code}_{season}.png"

        self.DB.wre = f"add1='{code}' and add2={season}"
        c_price = self.DB.get('add5',assoc=False)
        m_price = self.DB.get('add9',assoc=False)

        c_price = [float(x) for x in c_price]
        m_price = [float(x) for x in m_price]
  
        my_dpi = 100
        xx = list(range(0,61))
        plt.figure(facecolor='#24272d')
        plt.figure(figsize=(1400/my_dpi, 300/my_dpi),dpi=my_dpi)
        # plt.rcParams["figure.figsize"] = (20,4)
        plt.rcParams.update({"figure.figsize":(20,4),"axes.grid" : True, "grid.color": "#24272d",'font.size':8})
        ax = plt.axes()
        ax.set_facecolor('#33363b')

        ax.tick_params(color='#33363b',grid_alpha=0.7)
        plt.plot(c_price,color='#58ACFA',  linestyle='dotted')
        plt.plot(m_price,color='#f78181',  linestyle='solid',marker='o')
        plt.xticks(xx,color='darkgray')
        plt.yticks(color='darkgray')
        plt.savefig(file_name,facecolor='#24272d',dpi=my_dpi,pad_inches=0)
        return