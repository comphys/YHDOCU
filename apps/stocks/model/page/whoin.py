from system.core.load import Model
import system.core.my_utils as my


class M_whoin(Model) :

    def log(self,strinfo ) :

        with open("logs/publicIP.log","a",encoding="utf-8") as f:
            f.write(strinfo)



    def view(self) :

        with open('logs/whoin.txt','r',encoding='utf-8') as f:
            content = f.read()
        self.D['로긴정보'] = content.replace('\n','<br>')
        self.D['공아이피'] = my.get_publicIP()
        cur_time = my.now_to_kordate()
        self.log(f"<span class='who-time'>{cur_time}</span><span class='who-ip'>{self.D['공아이피']}</span>\n")

    def action(self) :

        return
    
class Ajax(Model) :

    def clear_who(self) :
        with open("logs/whoin.txt", "w") as f:
            pass 
        return '___OK___'