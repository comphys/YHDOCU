from system.core.load import Control
import system.core.my_utils as ut
from twilio.rest import Client 
import requests

class Sms(Control) :

    def send_sms(self) : # for twilio
        sms_tel = self.D['post']['sms_tel']
        if not ut.rg_ex('mobile',sms_tel) : return "올바른 휴대폰 번호가 아닙니다"
        sms_txt = self.D['post']['sms_txt']
        sms_tel = sms_tel.replace('-','')
        sms_tel = '+82'+ sms_tel[1:]

        self.info(sms_tel)
        self.info(sms_txt)

        account_sid = 'AC56e01be4bf1525b2df6133884275ffe6'
        auth_token = '77cece226818a0ead0070d8aa1242be0'
        client = Client(account_sid, auth_token) 

        message = client.messages.create(
            to=sms_tel, 
            from_="+16122237665", 
            body=sms_txt
        )
        return message.status

    def post_slack(self):

        # app.slack.com / comphys2@gmail.com 으로 회원가입 되어 있음... 
        text = self.D['post']['text']
        channel = self.D['post']['channel']
        if not channel : channel = "잡담"
        myToken = "xoxb-2274214573489-2281355211458-hX79WZbQWcsOYrq9KFKnvPNj"
        response= requests.post("https://slack.com/api/chat.postMessage",headers={"Authorization": "Bearer " + myToken},data={"channel": channel, "text": text})
        return "메세지가 전송 되었습니다"


    def post_slack_file(self):

        up_file=self.D['post']['up_file']
        channel = self.D['post']['channel']
        if not channel : channel = "잡담"
        up_file_name = ut.file_split(up_file)[1]
        up_file_ext  = ut.file_split(up_file)[2]

        my_file = {'file' : (up_file, open(up_file, 'rb'), up_file_ext)}
        
        payload={ "filename":up_file_name, "channels":channel}

        myToken = "xoxb-2274214573489-2281355211458-hX79WZbQWcsOYrq9KFKnvPNj"
        response= requests.post("https://slack.com/api/files.upload",headers={"Authorization": "Bearer " + myToken},params=payload, files=my_file)

        data=response.json()
        return data['file']['name']
