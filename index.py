import os
import configparser
from datetime import timedelta
from flask import ( Flask,request,render_template,redirect,send_from_directory,jsonify,session, g,)
import config
from system.core.load import load_control

# ----------------------------------------------------------------------------------------------------------
# Flask 앱 초기화 및 기본 설정
app = Flask(__name__)
app.config.from_object(config.Config)
app.url_map.strict_slashes = False

app_root = os.path.dirname(os.path.abspath(__file__))
app.template_folder = os.path.join(app_root, 'apps')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=10)
app.config['JSON_AS_ASCII'] = False

# ----------------------------------------------------------------------------------------------------------
# 요청 전처리: 스레드 세이프(Thread-Safe)한 클라이언트 IP 저장
@app.before_request
def resolve_client_ip():
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for :
        g.client_ip = forwarded_for.split(',')[0].strip()
    else :
        g.client_ip = request.remote_addr or ''

# ----------------------------------------------------------------------------------------------------------
# 정적 에셋 라우팅
@app.route('/sys/<path:filename>')
def sys_assets(filename):
    directory = os.path.join(app_root, 'system', 'client')
    return send_from_directory(directory, filename)

@app.route('/skn/<string:app_name>/<path:filename>')
def skin_assets(app_name, filename):
    directory = os.path.join(app_root, 'apps', app_name, 'skin')
    return send_from_directory(directory, filename)

# ----------------------------------------------------------------------------------------------------------
# 파일 다운로드 (세션 KeyError 및 경로 검증 안전 처리)
@app.route('/download/<path:filename>')
def download(filename):
    u_ino = session.get('__u_Ino__')
    
    if filename == 'stock_mydata' and u_ino == 'comphys':
        directory = os.path.join(app_root, 'mydb')
        return send_from_directory(directory, 'stocks.sqlite', as_attachment=True)
    
    epl_path = session.get('epl_path')
    if not epl_path or not os.path.isdir(epl_path):
        return render_template('sys/sys_msg.html', msg="다운로드 권한이 없거나 경로가 존재하지 않습니다."), 400
    
    return send_from_directory(epl_path, filename, as_attachment=True)

# ----------------------------------------------------------------------------------------------------------
# 동적 HMVC 디스패처 라우트
@app.route('/')
@app.route('/<string:myapp>')
@app.route('/<string:myapp>/<string:control>')
@app.route('/<string:myapp>/<string:control>/<string:method>', methods=['GET', 'POST'])
@app.route('/<string:myapp>/<string:control>/<string:method>/<path:option>', methods=['GET', 'POST'])
def main(myapp='stocks', control='board', method='index', option=None):
    
    loc_myapp = os.path.join(app_root, 'apps', myapp)
    if not os.path.isdir(loc_myapp): return render_template('sys/sys_msg.html', msg=f"[{myapp}] 앱 위치를 찾을 수 없습니다."), 404
    # 인증 체크 (API 앱 제외)
    if myapp != 'api' and '__u_Ino__' not in session: control = 'access'; method = 'login'

    # 컨트롤러 동적 로딩
    try:
        controller_class = load_control(control, myapp)
    except ModuleNotFoundError:
        return render_template('sys/sys_msg.html', msg=f"{myapp}/{control} 해당 컨트롤을 찾을 수 없습니다."), 404
    # Private 메서드(__init__, _auto 등) 직접 호출 방지 및 존재 여부 검증
    if method.startswith('_') or not hasattr(controller_class, method): return render_template('sys/sys_msg.html', msg="해당 메서드를 찾을 수 없거나 접근할 수 없습니다."), 404

    target_method = getattr(controller_class, method)
    if not callable(target_method): return render_template('sys/sys_msg.html', msg="호출 가능한 메서드가 아닙니다."), 404

    # 앱 설정 파일 로드 (변수 섀도잉 방지: cfg_parser 사용)
    cfg_parser = configparser.ConfigParser()
    cfg_parser.optionxform = lambda optionstr: optionstr
    config_file = os.path.join(loc_myapp, 'config.ini')
    try:
        cfg_parser.read(config_file, encoding='utf-8')
        myconfig = cfg_parser
    except Exception:
        myconfig = None

    # 컨트롤러 전달 파라미터 패킹 (g.client_ip 사용으로 스레드 세이프)
    parameters = {
        '_opt': option,
        '_pos': request.get_json(silent=True) if (myapp == 'api' and request.is_json) else request.form,
        '_aut': request.headers.get('Authorization') if myapp == 'api' else None,
        '_cfg': myconfig,
        '_pth': app_root,
        '_app': myapp,
        '_bse': f'/{myapp}/',
        '_skn': f'{myapp}/skin/',
        '_mth': method,
        '_lcl': (g.client_ip == '127.0.0.1')
    }

    # 인스턴스 생성 및 메서드 실행
    instance = controller_class(parameters)
    data = getattr(instance, method)()

    # 결과 반환 처리
    if data is not None:
        if myapp == 'api': return jsonify(data)
        if isinstance(data, dict) and '_redirect' in data: return redirect(data['_redirect'])
        if isinstance(data, str): return data
        if isinstance(data, dict) and 'skin' in data: return render_template(f"{myapp}/skin/{data['skin']}", D=data)

    return ''

# ----------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)