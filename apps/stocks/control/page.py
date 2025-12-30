from system.core.load import Control
from flask import session
import system.core.my_utils as my

class Page(Control) : 


    def _auto(self) :
        self.DB = self.db('stocks')

        self.D['USER'] = self.DB.exe(f"SELECT * FROM h_user_list WHERE uid='{session['N_NO']}'",many=1,assoc=True)
        self.D['bid']     = self.parm[0] 
        self.D['BCONFIG'] = self.DB.exe(f"SELECT * FROM h_board_config WHERE bid='{self.D['bid']}'",many=1,assoc=True)
        
        if self.D['BCONFIG']['width'] : self.D['xwidth'] = self.D['BCONFIG']['width']
        else : self.D['xwidth'] = '384px' if self.D['_mbl'] else '815px'
            
        self.skin = 'page/'+self.D['BCONFIG']['skin']
        self.D['DOCU_ROOT'] = self.C['DOCU_ROOT']

        qry = f"SELECT section FROM h_board_config WHERE acc_sect <={self.D['USER']['level']} GROUP BY section ORDER BY sposition"
        self.D['MENU_SECTION'] = self.DB.exe(qry)
        
        for val in self.D['MENU_SECTION'] :
            qry = f"SELECT title,bid,type FROM h_board_config WHERE section='{val[0]}' AND acc_board <= {self.D['USER']['level']} ORDER BY bposition"
            self.D[val[0]] = self.DB.exe(qry,assoc=True)
            for temp in self.D[val[0]] :
                if      temp['type'] == 'yhboard' : temp['bid'] = 'board/list/'+temp['bid']
                elif    temp['type'] == 'yhtable' : temp['bid'] = 'board/list/'+temp['bid']
                elif    temp['type'] == 'page'    : temp['bid'] =  'page/view/'+temp['bid']

    def view(self) :

        M = self.model('page-'+self.D['bid'])
        M.view()
        D={'skin':f"{self.skin}/{self.D['bid']}.html"}
        
        return self.echo(D)

    def action(self) :

        M = self.model('page-'+self.D['bid'])
        M.action()
        D={'skin':f"{self.skin}/{self.D['bid']}.html"}

        return self.echo(D)
    
    def ajax(self) :

        M = self.load_pajax(self.D['bid'],self.parm[1])
        return M()
    