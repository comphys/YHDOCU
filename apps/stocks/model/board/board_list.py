from system.core.load import Model
from flask import session
import math

class M_board_list(Model) :

    def list_head(self) :
        self.D['Page']    = self.gets.get('page','')
        self.D['No']      = self.gets.get('no',0)
        self.D['Sort']    = self.gets.get('sort','')
        self.D['Sort1']   = self.gets.get('sort1','')
        self.D['Cat_use'] = True if self.D['BCONFIG']['category'] else False
        self.D['Title'] = self.D['BCONFIG']['title']

        if self.D['Cat_use'] :

            if (not self.D['No'] and not self.D['search'] and not self.D['csh'] and not self.D['Page']) or self.D['csh'] == 'off' : session['CSH'].clear()

            if self.D['post'] :
                # key : csh_add1, csh_add2 ... 
                for key, val in self.D['post'].items() : session['CSH'][key] = val 
            else :
                if self.D['bid'] in ('daily_first','daily_second','daily_virtual') : 
                    # session['CSH']['csh_add19'] = '시즌진행' 
                    session['CSH']['csh_add1'] =  session['CSH'].get('csh_add1','SOXL')
                    session['CSH']['csh_add2'] =  session['CSH'].get('csh_add2',self.DB.one(f"SELECT max(add2) FROM h_{self.D['bid']}_board"))
            
            session.modified = True # for mutable variable in session

            ycat = self.SYS.load_app_lib('yhcategory')
            self.D['CAT_LIST'] = ycat.make_select(self.D['BCONFIG']['category'],self.D['EXTITLE'])
        else : session['CSH'].clear()

    def list_main(self) :
        
        self.date1 = self.gets.get('date1','')
        self.date2 = self.gets.get('date2','')

        C_search = ['brother <= 0']

        if self.D['BCONFIG']['user_query'] : C_search.append(self.D['BCONFIG']['user_query'])

        if self.D['search_f'] and self.D['search'] :
            search_key = 'content' if self.D['search_f'] == '본 문' else self.find_key(self.D['EXTITLE'],self.D['search_f']) 
            C_search.append( search_key +" like '%"+ self.D['search']+"%' ")
        
        elif self.D['search'] : C_search.append(" add0 like '%" + self.D['search'] + "%' OR content like '%"+self.D['search']+"%' ")
        

        if session['CSH'] :
            for key,val in session['CSH'].items() :
                if val and 'csh' in key : C_search.append(f"{key.replace('csh_','')} = '{val}' ")

        tbl = f"h_{self.D['bid']}_board"
        
        if self.date1 : C_search.append(f"add0 >='{self.date1}'")
        if self.date2 : C_search.append(f"add0 <='{self.date2}'")

        Cond = 'WHERE '+ ' AND '.join(C_search) 

        total_cnt = self.DB.one(f"SELECT count(no) FROM {tbl} {Cond}")

        page_total = page_start = page_end = 1
        page = int(self.D['page']) if self.D['page'] else 1

        if total_cnt :

            rp = self.D['BCONFIG']['row_per_page']
            rStart = rp * (page-1)
            page_set = 10
            page_total = math.ceil(total_cnt/rp)
            page_b = math.ceil(page/page_set) - 1
            page_start = page_b * page_set + 1
            page_end = page_start + (page_set -1)
            if page_end > page_total : page_end = page_total

            sorder = self.D['BCONFIG']['sort_order'] if self.D['BCONFIG']['sort_order'] else 'no desc'

            if self.D['Sort'] :  sorder = self.D['Sort']
            if self.D['Sort1'] : sorder = self.D['Sort1'] + ' DESC'

            qry = f"SELECT {self.D['list_full']} FROM {tbl} {Cond} ORDER BY {sorder} LIMIT {rStart},{rp}"
            self.D['LIST'] = self.DB.exe(qry,assoc=True)
            self.D['Tr_cnt'] = total_cnt - (page-1) * rp
        
        self.page_maker(page_total,page,page_start,page_end)

        # from apps.docu.skin.board.my_dark.list.목록_표준 import SKIN
        SKIN = self.SYS.load_skin("list")
        SKIN.list()

   
    def page_maker(self,page_total,this_page,page_start,page_end) :
        pagelist = '/stocks/board/list/'+self.D['bid']
        if self.D['Sort']  : pagelist += '/sort=' + self.D["Sort"]
        if self.D['Sort1'] : pagelist += '/sort1=' + self.D["Sort1"]

        append = ''
        if self.date1 : append += f"/date1={self.date1}" 
        if self.date2 : append += f"/date2={self.date2}"

        page_number_list =''
        if page_start > 1 :
            page_number_list += f"<li><a href='{pagelist}/page=1{append}'>1</a></li>"
            page_number_list += f"<li><a href='{pagelist}/page={page_start-1}{append}'>«</a></li>"
        
        for i in range(page_start,page_end+1) :
            active = "class='active'" if this_page == i else ''
            page_number_list += f"<li {active}><a href='{pagelist}/page={i}{append}'>{i}</a></li>"

        if page_end < page_total :
            page_number_list += f"<li><a href='{pagelist}/page={page_end+1}{append}'>»</a></li>"
            page_number_list += f"<li><a href='{pagelist}/page={page_total}{append}'>{page_total}</a></li>"
        
        self.D['Pagination'] =page_number_list