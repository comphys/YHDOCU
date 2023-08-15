from system.core.load import Model
import copy

class M_board_main(Model) :

    def _auto(self) :
        
        self.D['search'] =   self.gets.get('search','') 
        self.D['search_f'] = self.gets.get('search_f','') 
        self.D['page'] = self.gets.get('page','1')
        self.D['csh'] = self.gets.get('csh','') 
        searchplus = ''

        if self.D['search'] :   searchplus  = '/search='+self.D['search']
        if self.D['search_f'] : searchplus += '/search_f='+self.D['search_f']
        self.D['xwidth'] = self.D['BCONFIG']['width'] if self.D['BCONFIG']['width'] else '815px' 

        self.D['Searchplus'] = searchplus

        self.D['list_order'] = self.D['BCONFIG']['list_order'].replace('subject','add0').split('/')

        USE_KEY = []
        NOT_KEY = []
        for i in range(16) :
            key = f'add{i}' 
            if self.D['BCONFIG'][key] :  USE_KEY.append(key)
            else : NOT_KEY.append(key)

        self.D['list_full'] = 'no,brother,tle_color,uid,uname,reply,hit,wdate,mdate,'+','.join(USE_KEY)

        self.D['EXTITLE'] = {} ; self.D['EXFTYPE'] = {} ; self.D['EXALIGN'] = {} ; self.D['EXCOLOR'] = {} ; 
        self.D['EXFORMA'] = {} ; self.D['EXWIDTH'] = {} ; self.D['MustCheck'] = []


        for i in USE_KEY :
            exConf = self.D['BCONFIG'][i].split('/')
            self.D['EXTITLE'][i] = exConf[0]
            self.D['EXFTYPE'][i] = exConf[1]
            self.D['EXALIGN'][i] = exConf[2]
            self.D['EXCOLOR'][i] = exConf[3]
            self.D['EXFORMA'][i] = exConf[4]
            self.D['EXWIDTH'][i] = exConf[5]
            if exConf[6] == 'true' : 
                self.D['MustCheck'].append("'"+ i + "'")
                self.D['MustCheck'].append("'"+ exConf[0] + "'")
        
        qry = f"SELECT section FROM h_board_config GROUP BY section ORDER BY sposition"
        self.D['MENU_SECTION'] = self.DB.exe(qry)
        
        for val in self.D['MENU_SECTION'] :
            qry = f"SELECT title,bid,type FROM h_board_config WHERE section='{val[0]}' ORDER BY bposition"
            self.D[val[0]] = self.DB.exe(qry,assoc=True)
            for temp in self.D[val[0]] :
                if      temp['type'] == 'yhboard' : temp['bid'] = 'board/list/'+temp['bid']
                elif    temp['type'] == 'yhtable' : temp['bid'] = 'board/list/'+temp['bid']
                elif    temp['type'] == 'page'    : temp['bid'] =  'page/view/'+temp['bid']

