from system.core.load import Control
from flask import session, request
import system.core.my_utils as my

class Access(Control) : 

    def index(self) :
        return self.moveto('access/login')

    def _auto(self) :

        self.DB = self.db('stocks')
        self.D['platform'] = 'On Local' if  self.D['_lcl'] else ''

    def login(self) :
        
        if self.D['post'] :

            qry = f"SELECT uid FROM h_user_list WHERE uid='{self.D['post']['userid']}' and upass='{self.D['post']['userpass']}'"
            uid = self.DB.one(qry)
            
            if  uid : 

                user_ip   = request.headers.get('X-Forwarded-For').split(',')[0] if request.headers.get('X-Forwarded-For') else request.remote_addr
                user_time = my.now_to_kordate()
                user_agent = request.headers.get('User-Agent')
                
                user_agent = user_agent.replace("Android","<span class='who-gear'>Android</span>")
                user_agent = user_agent.replace("Windows","<span class='who-gear'>Windows</span>")

                with open('whoin.txt','a',encoding='utf-8') as f:
                    f.write(f"<span class='who-id'>{uid}</span><span class='who-time'>{user_time}</span><span class='who-ip'>{user_ip}</span><span class='who-agent'>{user_agent}</span>\n")
                session['__u_Ino__'] = uid
                session['CSH'] = {}
                home = self.DB.one(f"SELECT home FROM h_user_list WHERE uid='{uid}'")
                return self.moveto(home)
        
        else : return self.echo({'title':'접근금지', 'skin':'access/login.html'})

    def logout(self) : 
        
        if '__u_Ino__' in session : 
            del session['__u_Ino__'] 
            del session['CSH']
        return self.moveto('access/login')
    