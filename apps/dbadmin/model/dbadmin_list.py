from apps.dbadmin.model.dbadmin import M_dbadmin as Mom
import math

class M_dbadmin_list(Mom) : 

    def get_tbl_col_names(self,tbl) :
        return self.DB.table_info(tbl,info='col')

    def get_tbl_rows(self,tbl) :
        total_cnt       = self.DB.one('SELECT count(no) FROM {}'.format(tbl))
        page_total      = page_start = page_end = 1
        page            = int(self.gets.get('page',1))  

        if total_cnt :
            rp          = 20 
            rstart      = rp * (page -1)
            page_set    = 10
            page_total  = math.ceil(total_cnt/rp)
            page_b      = math.ceil(page/page_set) - 1
            page_start  = page_b * page_set + 1
            page_end    = page_start + (page_set - 1)
            if page_end > page_total : page_end =  page_total 

            self.D['tbl_rows'] = self.DB.exe('SELECT * FROM {} ORDER BY no DESC LIMIT {} OFFSET {}'.format(tbl,rp,rstart)) 
            self.D['pagenation']=self.page_number_make(page_total,page,page_start,page_end)
            self.D['total_cnt'] =total_cnt 
         



    def page_number_make(self,page_total,this_page,page_start,page_end) :
        page_list = self.SYS.D['_bse'] + 'dbadmin/list/' + self.parm[0]
        page_number_list = ''
        if  page_start > 1 :
            page_number_list += "<li class='page-item'><a class='page-link' href='{}/page=1'>1</a></li>".format(page_list)
            page_number_list += "<li class='page-item'><a class='page-link' href='{}/page={}'>«</a></li>".format(page_list,page_start-1)
      
        for i in range(page_start, page_end + 1) : 
            active = "class='page-item active'" if this_page == i else "class='page-item'"
            page_number_list += "<li {0}><a class='page-link' href='{1}/page={2}'>{2}</a></li>".format(active,page_list,i)
      
        if  page_end < page_total :
            page_number_list += "<li class='page-item'><a class='page-link' href='{}/page={}'>»</a></li>".format(page_list,page_end+1)
            page_number_list += "<li class='page-item'><a class='page-link' href='{0}/page={1}'>{1}</a></li>".format(page_list,page_total) 

        return page_number_list

