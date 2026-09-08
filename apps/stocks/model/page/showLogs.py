from system.core.load import Model
import system.core.my_utils as my
import requests

class M_showLogs(Model) :

    def view(self) :

        self.D['logs'] = my.get_file_names('logs')
        self.D['logfile'] = 'publicIP'
        with open('logs/publicIP.log','r',encoding='utf-8') as f:
            content = f.read()

        self.D['logContent'] = content.replace('\n','<br>')


    def action(self) :
        self.D['logs'] = my.get_file_names('logs')
        self.D['logfile'] = self.D['post']['log_file']
        if not self.D['logfile'] : self.D['logfile'] = 'publicIP'

        with open('logs/'+self.D['logfile']+'.log','r',encoding='utf-8') as f:
            content = f.read()

        self.D['logContent'] = content.replace('\n','<br>')
        
    
class Ajax(Model) :

    def clear_logcontent(self) :
        del_file = self.D['post']['logfile']
        with open("logs/"+del_file+".log", "w") as f:
            pass 
        return '___OK___'

    def new_token(self) :
        kiwoom_token = self.DB.store('kiwoom_token')
        kiwoom_token_date = self.DB.store('kiwoom_token_date')
        # 서버로 요청 
        if  self.D['_lcl'] :
            api_token= self.DB.store('api_token')
            host = "https://comphys.pythonanywhere.com/api/sprice/new_token"
            headers = {'Content-Type':'application/json;charset=UTF-8','Authorization':api_token}
            data = {"token":kiwoom_token,"token_date":kiwoom_token_date}
            rst = requests.post(host,headers=headers,json=data)
            return rst.json()

    def old_token(self) :
        data = {}
        # 서버로 요청 
        if  self.D['_lcl'] :
            api_token= self.DB.store('api_token')
            host = "https://comphys.pythonanywhere.com/api/sprice/old_token"
            headers = {'Content-Type':'application/json;charset=UTF-8','Authorization':api_token}
            rst = requests.post(host,headers=headers,json=data).json()

            self.DB.store('kiwoom_token',rst['token'])
            self.DB.store('kiwoom_token_date',rst['token_date'])
            return '___OK___'
        return '___OK___'