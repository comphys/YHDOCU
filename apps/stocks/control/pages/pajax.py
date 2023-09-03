from system.core.load import Control
import openai

class Pajax(Control) :
    def _auto(self) :
        self.DB = self.db('stocks')
        
    def eng_reply(self) :
        text = self.D['post']['txt']
        text = f'"{text}" 를 영어로 번역해 주세요.'
        openai.api_key = self.DB.store('openai_key')
        system_role = self.DB.store('openai_english_teacher')
        messages=[{"role": "system", "content": system_role}]
        messages.append({"role":"user","content":f"{text}"})
        
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",temperature=0.8,messages=messages)
        assistant_content = completion.choices[0].message['content'].strip()
        return assistant_content
