from system.core.load import SKIN

class 쓰기_견적관리(SKIN) :

    def write(self) :
        OBODY = self.D.get('OBODY',None)
        self.D['BODY'] = OBODY
        self.D['TR_add'] = []
        self.D['TR_cat'] = []
        if self.D['BCONFIG']['width'] : w_width  = int( (self.D['BCONFIG']['width']).replace('px','') )
        else : w_width = 815
        self.D['w_width1'] = str(w_width + 80)+'px'
        self.D['w_width2'] = str(w_width) + 'px'

        self.D['ChkField'] = ','.join(self.D['MustCheck'])
        
        if  self.D['Mode'] == 'write' :
            self.D['w_title']='' ; self.D['w_tleClr']=''

        elif self.D['Mode'] == 'modify' :
            self.D['w_title'] = OBODY['add0'] ; self.D['w_tleClr']= OBODY['tle_color']

        co_list = self.DB.one("SELECT out_co_list FROM h_estimate_config WHERE no=1")
        self.D['out_co_list'] = self.user_custom_select(co_list)
        self.D['save_img_dir'], self.D['save_img_dir2'] = self.DB.oneline("SELECT save_img_dir,save_img_dir2 FROM h_estimate_config WHERE no=1")
        
        self.D['upload_dir'] = self.D['DOCU_ROOT'] + '/'+ self.D['save_img_dir']
   
    def user_custom_select(self,co_list) :
        tmp =''
        co_lists = co_list.split()
        
        for x in co_lists :
            tmp += f"<option value='{x}'>{x}</option>"
		
        return tmp
    

