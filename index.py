from flask import Flask, request, render_template, redirect, send_from_directory
from flask import session
import config, os, configparser
from system.core.load import load_control
# ----------------------------------------------------------------------------------------------------------
app = Flask(__name__)
#app.config.from_object(config.ProductionConfig)
app.config.from_object(config.Config)
app.url_map.strict_slashes = False
app_root  = os.path.dirname(os.path.abspath(__file__)) # 현재 파일의 절대 경로  C:\YHDOCU
app.template_folder = os.path.join(app_root,'apps')    # C:\YHDOCU\apps
white_networks = ['127.0','119.56','118.235','119.201']
client_ip =''
# ----------------------------------------------------------------------------------------------------------
# 허용된 네트워크만 접근 허용
@app.before_request
def ban__remote_addr():
    global client_ip
    client_ip = request.headers.get('X-Forwarded-For').split(',')[0] if request.headers.get('X-Forwarded-For') else request.remote_addr
    client_nw = '.'.join(client_ip.split('.')[:2])

    if client_nw not in white_networks:
        return render_template('sys/sys_msg.html',msg=f"{client_ip} 허용된 접근경로가 아닙니다.")

# href = "/sys/jyh/aaa.js"  url_for('sys',filename='jyh/aaa.js')
@app.route('/sys/<path:filename>')
def sys(filename) :
    directory = os.path.join(app_root,'system','client')
    return send_from_directory(directory,filename)

# href = "/skn/docu/board/aaa.js"  url_for('skn',app='docu',filename='board/aaa.js')
@app.route('/skn/<string:app>/<path:filename>')
def skn(app,filename) :
    directory = os.path.join(app_root,'apps',app,'skin')
    return send_from_directory(directory,filename)

@app.route('/download/<path:filename>')
def download(filename) :
    if  filename == 'stock_mydata' and session['__u_Ino__'] :
        directory = os.path.join(app_root,'mydb')
        return send_from_directory(directory,'stocks.sqlite')
    else :
        directory = session['epl_path']
        return send_from_directory(directory,filename)    

@app.route('/')
@app.route('/<string:myapp>/')
@app.route('/<string:myapp>/<string:control>')
@app.route('/<string:myapp>/<string:control>/<string:method>/',methods=['GET','POST'])
@app.route('/<string:myapp>/<string:control>/<string:method>/<path:option>',methods=['GET','POST'])
def main(myapp='stocks', control='board', method='index', option=None):
    
    loc_myapp = os.path.join(app_root,'apps',myapp)
    if not os.path.isdir(loc_myapp) : return render_template('sys/sys_msg.html',msg=f"[{myapp}] 앱 위치를 찾을 수 없습니다.") 
    if not '__u_Ino__' in session : control = 'access'; method  = 'login'

    try :  CLS = load_control(control,myapp)
    except ModuleNotFoundError : return render_template('sys/sys_msg.html',msg="해당 컨트롤을 찾을 수 없습니다.")
    if not hasattr(CLS,method) : return render_template('sys/sys_msg.html',msg="해당 메써드를 찾을 수 없습니다.")
    
    # 기본설정값 읽어 오기 
    config = configparser.ConfigParser()
    config.optionxform = lambda optionstr : optionstr
    config_file = os.path.join(loc_myapp, 'config.ini')

    try : 
        config.read(config_file,encoding='utf-8')   
        myconfig = config
    except : 
        myconfig = None

    # 기본 매개변수들 전달
    Parameters = {}
    Parameters['_opt'] = option # 매개변수
    Parameters['_pos'] = request.form if request.method == 'POST' else None
    Parameters['_cfg'] = myconfig
    Parameters['_pth'] = app_root
    Parameters['_app'] = myapp
    Parameters['_bse'] = '/'+myapp+'/'
    Parameters['_skn'] = myapp+'/skin/' 
    Parameters['_mth'] = method
    Parameters['_lcl'] = True if client_ip == '127.0.0.1' else False  # check if it is on local or not

    Instance = CLS(Parameters)
    # _auto 함수에서는 클라이언트에 출력정보를 리턴하지 않으며, 해당 메서드에서만 최종 DATA를 전달받는다.
    DATA = getattr(Instance,method)()
    
    if DATA :
        if   '_redirect' in DATA  : return redirect(DATA['_redirect'])
        if   type(DATA)  is str   : return DATA
        elif type(DATA)  is dict  : return render_template(myapp+'/skin/' + DATA['skin'],D=DATA)
    else : return ''






# ----------------------------------------------------------------------------------------------------------
if __name__ == "__main__": app.run(host='127.0.0.1', port=5000, debug=True)