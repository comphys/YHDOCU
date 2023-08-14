from system.core.load import Control
from flask import session
import system.core.my_utils as my

class Page(Control) : 

    def _auto(self) :
        self.DB = self.db('jbk')

        self.D['bid']     = self.parm[0] 
        self.D['BCONFIG'] = self.DB.exe(f"SELECT * FROM h_board_config WHERE bid='{self.D['bid']}'",many=1,assoc=True)
        self.D['xwidth'] = self.D['BCONFIG']['width'] if self.D['BCONFIG']['width'] else '815px'

        self.skin = 'page/'+self.D['BCONFIG']['skin']
        self.D['DOCU_ROOT'] = self.C['DOCU_ROOT']

        qry = f"SELECT section FROM h_board_config GROUP BY section ORDER BY sposition"
        self.D['MENU_SECTION'] = self.DB.exe(qry)
        
        for val in self.D['MENU_SECTION'] :
            qry = f"SELECT title,bid,type FROM h_board_config WHERE section='{val[0]}' ORDER BY bposition"
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

    def save_outsourcing(self) :
        self.M = {}
        outsource = self.D['post']['out_co_list']
        self.DB.exe(f"UPDATE h_estimate_config SET out_co_list='{outsource}' WHERE no=1")
        M = self.model('page-'+self.D['bid'])
        M.view()
        D={'skin':f"{self.skin}/{self.D['bid']}.html"}
        D['output'] = "외주 업체 리스트를 저장하였습니다."
        return self.echo(D)

    def save_imgdown(self) :
        self.M = {}
        saveimg1 = self.D['post']['save_img_dir']
        saveimg2 = self.D['post']['save_img_dir2']
        self.DB.exe(f"UPDATE h_estimate_config SET save_img_dir='{saveimg1}', save_img_dir2='{saveimg2}' WHERE no=1")
        M = self.model('page-'+self.D['bid'])
        M.view()
        D={'skin':f"{self.skin}/{self.D['bid']}.html"}
        D['output'] = "이미지 보관 위치를 저장하였습니다."
        
        return self.echo(D)
  


