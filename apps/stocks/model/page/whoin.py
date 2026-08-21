from system.core.load import Model
import requests

class M_whoin(Model) :

    def view(self) :

        response = requests.get('https://api.ipify.org?format=json')
        self.D['공아이피'] = response.json()['ip']

        with open('whoin.txt','r',encoding='utf-8') as f:
            content = f.read()

        self.D['로긴정보'] = content.replace('\n','<br>')



    def action(self) :

        return
    
class Ajax(Model) :

    def clear_who(self) :
        with open("whoin.txt", "w") as f:
            pass 
        return '___OK___'