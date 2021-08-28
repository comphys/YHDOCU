# [필수] 콘트롤을 로드하기 위한 기본 임포트 
from system.core.load import Control

class Echo(Control) :
    def index(self) :
        return "Hellow Jung Yong Hoon. Nice to meet you"

    def index2(self) :
        # 스킨의 룻 데이터는 현재 app 위치 입니다.
        D = {'test' : '안녕하세요', 'skin' : 'basic.html'}
        return self.echo(D) 
    
    def index3(self) :
        # 스킨의 룻 데이터는 현재 app 위치 입니다.
        D = {'test' : '안녕하세요', 'skin' : 'main.html'}
        return self.echo(D) 