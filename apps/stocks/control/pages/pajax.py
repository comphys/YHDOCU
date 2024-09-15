from system.core.load import Control
import openai

class Pajax(Control) :
    def _auto(self) :
        self.DB = self.db('stocks')
        
    def eng_reply(self) :
        text = self.D['post']['txt']
        opt  = self.D['post']['opt']
        system_role = ''

        if  opt == 'eng_teacher' : 
            system_role = self.DB.store('openai_english_teacher')
            text = f'"{text}" 를 영어로 번역해 주세요.'

        if  opt == 'kor_teacher' : 
            system_role = self.DB.store('openai_kind_teacher')
            text = f'"{text}" 를 한글로 번역해 주세요.'
                    
        elif opt == 'gen_teacher' :
            system_role = self.DB.store('openai_kind_teacher')
            
        messages=[{'role':'system','content':system_role}]
        
        openai.api_key = self.DB.store('openai_key')
        
        messages.append({"role":"user","content":f"{text}"})
        
        completion = openai.chat.completions.create(model="gpt-3.5-turbo",temperature=0.7,messages=messages,max_tokens=2048)
        assistant_content = completion.choices[0].message.content.strip()
        return assistant_content
    
    def update_parameters(self) :

        key = self.D['post']['key']
        val = self.D['post']['val']
        no  = self.D['post']['no']

        sql = f"UPDATE parameters SET {key}= '{val}' WHERE no={no}"
        self.DB.exe(sql)
            
        return 
    
    def delete_parameters(self) :
        
        no  = self.D['post']['no']
        sql = f"DELETE FROM parameters WHERE no={no}"
        self.DB.exe(sql)
        
        return 
    
    def insert_parameters(self) :
        
        cat = self.D['post']['cat']
        ID  = {'key':'000','name':'XXX','val':'   ','type':'char','description':'-----','cat':cat}
        sql = self.DB.qry_insert('parameters',ID)
        self.DB.exe(sql)

        return 
    
    def get_ohlc(self) :
        code = self.gets['code']
        date = self.gets['date']
        self.DB.tbl, self.DB.wre = ('h_stockHistory_board',f"add1='{code}' and add0='{date}'")
        ohlc = self.DB.get_line("add4,add5,add6,add3,add8,add9,add10")
        # day_change = (float(ohlc['add5']) - float(ohlc['add4'])) / float(ohlc['add4']) * 100
        change = float(ohlc['add8'])
        output  = "<div id='stock_prices' style='width:430px;height:80px;padding:10px;background-color:#1d1f24;color:#e1e1e1;border:2px solid slategray;' ondblclick=\"h_dialog.close('OHLC_DAY')\">"
        output += "<table class='table' style='text-align:center'><tr><th>시가</th><th>고가</th><th>저가</th><th>종가</th><th>변동</th><th>상승</th><th>하락</th></tr><tr>"
        output += f"<td>{ohlc['add4']}</td>"
        output += f"<td style='color:#F6CECE'>{ohlc['add5']}</td>"
        # output += f"<td>{day_change:.1f}</td>"
        output += f"<td style='color:#CED8F6'>{ohlc['add6']}</td>"
        output += f"<td style='color:#F5F6CE'>{ohlc['add3']}</td>"
        output += f"<td>{change:.1f}%</td>"
        output += f"<td>{ohlc['add9']}</td>"
        output += f"<td>{ohlc['add10']}</td>"
        output += "</tr></table></div>"
        return self.echo(output)


    # for RST strategy
    def rst_sync(self) :
        s_date   = self.D['post']['s_date']
        s_begin  = self.D['post']['begin']
        
        order = 'add0 DESC' if s_begin == 'pick' else 'add0 ASC'

        V_board = self.DB.parameters('03500')
        R_board = self.DB.parameters('03501')

        V_date = self.DB.one(f"SELECT add0 FROM {R_board} WHERE add0 < '{s_date}' and sub12 = '1' ORDER BY {order} LIMIT 1")
  
        V_money = self.DB.one(f"SELECT add3 FROM {V_board} WHERE add0 < '{V_date}' and sub12= '0' ORDER BY {order} LIMIT 1")
        R_money = self.DB.one(f"SELECT add3 FROM {R_board} WHERE add0 < '{V_date}' and sub12= '0' ORDER BY {order} LIMIT 1")
        S_money = T_money = R_money
        
        if  not (V_date and V_money and R_money and S_money) : 
            RST = {'date':'None','msg':f"주어진 날자 이전의 동기화된 데이타는 존재하지 않습니다."}
        else :
            RST = {'date':V_date,'V_money':f"{float(V_money):,.2f}",'R_money':f"{float(R_money):,.2f}",'S_money':f"{float(S_money):,.2f}",'T_money':f"{float(T_money):,.2f}"}
        return self.json(RST)
    
    def vtac_sync(self) :
        s_date   = self.D['post']['s_date']
        s_begin  = self.D['post']['begin']
        
        order = 'add0 DESC' if s_begin == 'pick' else 'add0 ASC'

        V_board = 'h_IGUIDE_board'

        V_date = self.DB.one(f"SELECT add0 FROM {V_board} WHERE add0 <= '{s_date}' and sub12 = '1' ORDER BY {order} LIMIT 1")
        V_money = self.DB.one(f"SELECT add3 FROM {V_board} WHERE add0 < '{V_date}' and sub12= '0' ORDER BY {order} LIMIT 1")
        
        if  not (V_date and V_money) : 
            V = {'date':'None','msg':f"주어진 날자 이전의 동기화된 데이타는 존재하지 않습니다."}
        else :
            V = {'date':V_date,'V_money':f"{float(V_money):,.2f}"}
        return self.json(V)