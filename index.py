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
# ----------------------------------------------------------------------------------------------------------
@app.before_request
def clear_trailing() :
    rp = request.path
    if rp != '/' and rp.endswith('/') :
        return redirect(rp[:-1])

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
    if  filename == 'stock_mydata' and session['N_NO'] :
        directory = os.path.join(app_root,'mydb')
        return send_from_directory(directory,'stocks.sqlite')
    else :
        directory = session['epl_path']
        return send_from_directory(directory,filename)    

@app.route('/DOCU_ROOT/<path:filename>')
def docu_root(filename) :
    directory = DOCU_ROOT
    return send_from_directory(directory,filename)

@app.route('/')
@app.route('/<string:myapp>/')
@app.route('/<string:myapp>/<string:control>')
@app.route('/<string:myapp>/<string:control>/<string:method>/',methods=['GET','POST'])
@app.route('/<string:myapp>/<string:control>/<string:method>/<path:option>',methods=['GET','POST'])
def main(myapp=None, control=None, method=None, option=None):

#   log = my_log("my_logger")    

    if not myapp : 
        myapp = 'stocks'
        os_myapp = os.path.join(app_root,'apps',myapp)
        if os.path.isdir(os_myapp) : 
            mybase = '/'+myapp+'/'
            myskin = myapp+'/skin/'
        # return render_template('sys/sys_msg.html',msg="호출하실 앱을 명시하지 않았습니다.") 
    else :
        os_myapp = os.path.join(app_root,'apps',myapp)
        if os.path.isdir(os_myapp) : 
            mybase = '/'+myapp+'/'
            myskin = myapp+'/skin/'
        else : return render_template('sys/sys_msg.html',msg="앱 위치를 찾을 수 없습니다.") 

    if not control : 
        control = 'board'
        # return render_template('sys/sys_msg.html',msg="컨트롤이 명시되지 않았습니다.")   
 
    if not method  : 
        return redirect(mybase + control+'/index')

    # log in 
    
    if not 'N_NO' in session : myapp = 'stocks'; control = 'board'; method  = 'login'
    
    
    data = request.form if request.method == 'POST' else None

    try :  CLS = load_control(control,myapp)
    except ModuleNotFoundError : 
        return render_template('sys/sys_msg.html',msg="해당 컨트롤을 찾을 수 없습니다.")
    if not hasattr(CLS,method): 
        return render_template('sys/sys_msg.html',msg="해당 메써드를 찾을 수 없습니다.")
    
    # 기본설정값 읽어 오기 
    config = configparser.ConfigParser()
    config.optionxform = lambda optionstr : optionstr
    config_file = os.path.join(os_myapp, 'config.ini')

    try : 
        config.read(config_file,encoding='utf-8')   
        myconfig = config

    except : 
        myconfig = None

    try :
        global DOCU_ROOT
        DOCU_ROOT = myconfig['general']['DOCU_ROOT']
    except :
        DOCU_ROOT = ''

    # detect mobile

    user_agent = request.headers.get('User-Agent')
    user_agent = user_agent.lower()

    user_agent = True if "android" in user_agent else False

    # option : 매개변수, via : 수단, data : form data
    Instance = CLS(_opt=option,_pos=data,_bse=mybase,_url=request.path,_ctr=control,_mtd=method,_app=myapp,_pth=app_root,_skn=myskin,_cfg=myconfig,_ctl=control,_mbl=user_agent)
    # _auto 함수에서는 클라이언트에 출력정보를 리턴하지 않으며, 해당 메서드에서만 최종 DATA를 전달받는다.
    DATA = getattr(Instance,method)()
    
    if DATA :
        if   '_redirect' in DATA  : return redirect(DATA['_redirect'])
        if   type(DATA)  is str   : return DATA
        elif type(DATA)  is dict  : return render_template(myskin + DATA['skin'],D=DATA)
    else : return ''
# ----------------------------------------------------------------------------------------------------------

if __name__ == "__main__": app.run(host='127.0.0.1', port=5000, debug=True)