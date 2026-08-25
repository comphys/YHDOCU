from system.core.load import Model
import requests

class M_publicip(Model) :

    def view(self) :


        with open('publicIP.log','r',encoding='utf-8') as f:
            content = f.read()

        self.D['PublicIP'] = content.replace('\n','<br>')


    def action(self) :

        return
    
class Ajax(Model) :

    def clear_publicip(self) :
        with open("publicIP.log", "w") as f:
            pass 
        return '___OK___'

    def send_token(self) :

        kiwoom_token = self.DB.store('kiwoom_token')
        kiwoom_token_date = self.DB.store('kiwoom_token_date')
        # 서버로 요청 
        if  self.D['_lcl'] :
            host = "https://comphys.pythonanywhere.com/api/sprice/get_token"
            headers = {'Content-Type':'application/json;charset=UTF-8','Authorization':'Royal to JYH'}
            data = {"token":kiwoom_token,"token_date":kiwoom_token_date}
            rst = requests.post(host,headers=headers,json=data)
            return rst.json()