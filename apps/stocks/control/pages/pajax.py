from system.core.load import Control
from PyKakao import Message
import openai

class Pajax(Control) :
    def _auto(self) :
        self.DB = self.db('stocks')
        
    def eng_reply(self) :
        text = self.D['post']['txt']
        opt  = self.D['post']['opt']
        system_role = ''

        if  opt == 'eng_teacher' : 
            system_role = self.DB.store('openai_english_teacher')
            text = f'"{text}" 를 영어로 번역해 주세요.'

        if  opt == 'kor_teacher' : 
            system_role = self.DB.store('openai_kind_teacher')
            text = f'"{text}" 를 한글로 번역해 주세요.'
                    
        elif opt == 'gen_teacher' :
            system_role = self.DB.store('openai_kind_teacher')
            
        messages=[{'role':'system','content':system_role}]
        openai.api_key = self.DB.store('openai_key')
        
        messages.append({"role":"user","content":f"{text}"})
        
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",temperature=0.7,messages=messages,max_tokens=2048)
        assistant_content = completion.choices[0].message['content'].strip()
        return assistant_content
    
    def update_parameters(self) :

        key = self.D['post']['key']
        val = self.D['post']['val']
        no  = self.D['post']['no']

        sql = f"UPDATE parameters SET {key}= '{val}' WHERE no={no}"
        self.DB.exe(sql)
            
        return 
    
    def delete_parameters(self) :
        
        no  = self.D['post']['no']
        sql = f"DELETE FROM parameters WHERE no={no}"
        self.DB.exe(sql)
        
        return 
    
    def insert_parameters(self) :
        
        cat = self.D['post']['cat']
        ID  = {'key':'000','name':'XXX','val':'   ','type':'char','description':'-----','cat':cat}
        sql = self.DB.qry_insert('parameters',ID)
        self.DB.exe(sql)


        API = Message(service_key = "7a6eac2b906d5399908979a777f97505")

        access_token = "Vz88lHuEKzTG02VIuwhZfv-g-wN1n4xlty0KPXWbAAABjMVQ0gJyxKx5jTsi9A"

        API.set_access_token(access_token)

        message_type = "feed"

        # 파라미터
        content = {
                    "title": "오늘의 디저트",
                    "description": "아메리카노, 빵, 케익",
                    "image_url": "https://mud-kage.kakao.com/dn/NTmhS/btqfEUdFAUf/FjKzkZsnoeE4o19klTOVI1/openlink_640x640s.jpg",
                    "image_width": 640,
                    "image_height": 640,
                    "link": {
                        "web_url": "http://www.daum.net",
                        "mobile_web_url": "http://m.daum.net",
                        "android_execution_params": "contentId=100",
                        "ios_execution_params": "contentId=100"
                    }
                }

        item_content = {
                    "profile_text" :"Kakao",
                    "profile_image_url" :"https://mud-kage.kakao.com/dn/Q2iNx/btqgeRgV54P/VLdBs9cvyn8BJXB3o7N8UK/kakaolink40_original.png",
                    "title_image_url" : "https://mud-kage.kakao.com/dn/Q2iNx/btqgeRgV54P/VLdBs9cvyn8BJXB3o7N8UK/kakaolink40_original.png",
                    "title_image_text" :"Cheese cake",
                    "title_image_category" : "Cake",
                    "items" : [
                        {
                            "item" :"Cake1",
                            "item_op" : "1000원"
                        },
                        {
                            "item" :"Cake2",
                            "item_op" : "2000원"
                        },
                        {
                            "item" :"Cake3",
                            "item_op" : "3000원"
                        },
                        {
                            "item" :"Cake4",
                            "item_op" : "4000원"
                        },
                        {
                            "item" :"Cake5",
                            "item_op" : "5000원"
                        }
                    ],
                    "sum" :"Total",
                    "sum_op" : "15000원"
                }

        social = {
                    "like_count": 100,
                    "comment_count": 200,
                    "shared_count": 300,
                    "view_count": 400,
                    "subscriber_count": 500
                }

        buttons = [
                    {
                        "title": "웹으로 이동",
                        "link": {
                            "web_url": "http://www.daum.net",
                            "mobile_web_url": "http://m.daum.net"
                        }
                    },
                    {
                        "title": "앱으로 이동",
                        "link": {
                            "android_execution_params": "contentId=100",
                            "ios_execution_params": "contentId=100"
                        }
                    }
                ]

        API.send_message_to_me(
            message_type=message_type,
            content=content, 
            item_content=item_content, 
            social=social, 
            buttons=buttons
            )


        return 

        