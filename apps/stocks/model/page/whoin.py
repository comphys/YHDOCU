from system.core.load import Model
import system.core.my_utils as my

class M_whoin(Model) :

    def view(self) :
        
        # 기본 값
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