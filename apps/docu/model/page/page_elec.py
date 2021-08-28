from system.core.load import Model

class M_page_elec(Model) :

    def view(self) :

        S = self.SYS.load_app_lib('scrap')
        S.url = "http://www.kpx.or.kr"
        S.id = 'kpx_realtime'
        S.selector = "#m_contents > div.m_cont_lf > div:nth-child(1) > div:nth-child(2)"
        S.interval = 300
        
        html_text = S.get()

        D = {}
        D['date']       = html_text.select_one("p.date").text 
        D['img']        = S.url+html_text.select_one("p.level > img").get("src")
        D['current']    = html_text.select_one("dl > dd").text
        D['creserve']   = html_text.select_one("dl.graph_list.point > dd").text
        D['preserve']   = html_text.select_one("dl:nth-child(6) > dd").text

        S.id = 'kpx_smc'
        S.selector = "#smp_01 > table"
        S.interval = 600
        html_text = S.get()

        D['smp_date'] = html_text.select_one("tbody > tr:nth-child(1) > td").text
        D['smp_max']  = html_text.select_one("tbody > tr:nth-child(2) > td").text
        D['smp_min']  = html_text.select_one("tbody > tr:nth-child(3) > td").text
        D['smp_mean'] = html_text.select_one("tbody > tr:nth-child(4) > td").text

        S.id = 'kpx_rec'
        S.selector = "#m_contents > div.m_cont_rg > div.m_today_rec > div.rec > table"
        S.interval = 3600
        html_text = S.get()

        D['rec_date'] = html_text.select_one("tbody > tr:nth-child(1) > td").text
        D['rec_max']  = html_text.select_one("tbody > tr:nth-child(4) > td").text
        D['rec_min']  = html_text.select_one("tbody > tr:nth-child(5) > td").text
        D['rec_mean'] = html_text.select_one("tbody > tr:nth-child(3) > td").text      

        self.D['EX'] = D  
