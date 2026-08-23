from system.core.load import Model
import system.core.my_utils as my

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