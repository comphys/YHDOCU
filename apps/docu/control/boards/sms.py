from system.core.load import Control
import system.core.my_utils as ut
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class Sms(Control) :

    def _auto(self) :
        self.client = WebClient(token="xoxb-2274214573489-2281355211458-gs4fpyWRrA5Jhf69eRMHnLk0")

    def post_slack(self):

        # app.slack.com / comphys2@gmail.com 으로 회원가입 되어 있음... 
        text = self.D['post']['text']
        channel = self.D['post']['channel']
        if not channel : channel = "잡담"

        try:
            response = self.client.chat_postMessage(channel= channel, text= text)
            assert response["message"]["text"] == text
        except SlackApiError as e:
            assert e.response["ok"] is False
            assert e.response["error"]  
            print(f"slack error : {e.response['error']}")
        
        else :
            return "메세지가 전송되었습니다"


    def post_slack_file(self):

        up_file=self.D['post']['up_file']
        channel = self.D['post']['channel']
        if not channel : channel = "잡담"
        up_file_name = ut.file_split(up_file)[1]

        try :
            response = self.client.files_upload(channels=channel, file=up_file)
            assert response["file"]
        except SlackApiError as e:
            assert e.response["ok"] is False
            assert e.response["error"]  
            print(f"slack error : {e.response['error']}")
        else :
            return f"{up_file_name}"
