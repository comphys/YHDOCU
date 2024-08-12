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
    
    def overall_test_sync(self) :
        s_date  = self.D['post']['s_date']
        V_board = self.DB.parameters('03500')
        R_board = self.DB.parameters('03600')
        S_board = self.DB.parameters('03700')
        V_sdate = self.DB.one(f"SELECT add0 FROM {V_board} WHERE add0 < '{s_date}' and sub12 = '1' ORDER BY add0 DESC LIMIT 1")
  
        V_money = self.DB.one(f"SELECT add3 FROM {V_board} WHERE add0 < '{V_sdate}' and sub12 = '0' ORDER BY add0 DESC LIMIT 1")
        R_money = self.DB.one(f"SELECT add3 FROM {R_board} WHERE add0 < '{V_sdate}' and sub12 = '0' ORDER BY add0 DESC LIMIT 1")
        S_money = self.DB.one(f"SELECT add3 FROM {S_board} WHERE add0 < '{V_sdate}' and sub12 = '0' ORDER BY add0 DESC LIMIT 1")
        
        if  not (V_sdate and V_money and R_money and S_money) : 
            RST = {'date':'None','msg':f"주어진 날자 이전의 동기화된 데이타는 존재하지 않습니다."}
        else :
            RST = {'date':V_sdate,'V_money':f"{float(V_money):,.2f}",'R_money':f"{float(R_money):,.2f}",'S_money':f"{float(S_money):,.2f}"}
        return self.json(RST)
    
    # for RST strategy
    def overall_test_sync2(self) :
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