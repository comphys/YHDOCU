import requests
import myutils.my_utils as my


response = requests.get('https://api.ipify.org?format=json')

myIP = response.json()['ip']
cur_time = my.now_to_kordate()

with open("/home/comphys/YHDOCU/publicIP.log","a",encoding="utf-8") as f:
    f.write(f"<span class='who-time'>{cur_time}</span><span class='who-ip'>{myIP}</span>&nbsp;&nbsp; recorded on server side\n")
         