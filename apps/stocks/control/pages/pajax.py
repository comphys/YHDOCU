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
        
        elif opt == 'gen_teacher' :
            system_role = self.DB.store('openai_kind_teacher')
            
        messages=[{'role':'system','content':system_role}]
        openai.api_key = self.DB.store('openai_key')
        
        messages.append({"role":"user","content":f"{text}"})
        
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",temperature=0.7,messages=messages,max_tokens=2048)
        assistant_content = completion.choices[0].message['content'].strip()
        return assistant_content
