from system.core.load import Control
import openai

class Pajax(Control) :
    def _auto(self) :
        self.DB = self.db('stocks')
        
    def eng_reply(self) :
        text = self.D['post']['txt']
        openai.api_key = self.DB.store('openai_key')
        messages=[{"role": "system", "content": "You are an English-Korean translation machine. Your role is to trannslate my quesions into English. And give me more than 3 options if you have. prefix your answers with a number."},{}]

        messages[1] = {"role":"user","content":f"{text}"}
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",temperature=0.8,messages=messages)

        assistant_content = completion.choices[0].message['content'].strip()

        return assistant_content
