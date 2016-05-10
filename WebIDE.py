from bottle import get, post, route, run, debug, template, request, static_file, error, redirect
import contextlib, json, os, socket, urllib

try:
    import editor
    from objc_util import *
    PYTHONISTA = True
except ImportError:
    PYTHONISTA = False

IDE_ROOT = os.path.dirname(os.path.realpath(__file__))
os.chdir(IDE_ROOT)
ROOT = os.path.realpath('..') + '/'

def make_file_tree(dir_path=ROOT):
    file_dict = {}
    def recur(path, list):
        for l in os.listdir(path):
            f = os.path.join(path, l)
            if l[0] == '.':
              continue
            elif os.path.isdir(f):
                list[l] = {}
                recur(f, list[l])
            elif l.split('.')[-1] in ['py', 'txt', 'pyui', 'json']:
                list[l] = urllib.pathname2url(f[len(dir_path)+1:])
    recur(dir_path.rstrip('/'), file_dict)
    return file_dict

@get('/')
def edit():
    #file_list = {
    #    'filename1': 'path1',
    #    'filename2': 'path2',
    #    'dirname1': {
    #        'filename3': 'path3',
    #        'dirname2': {
    #            'filename4': 'path4',
    #            'filename5': 'path5'
    #        }
    #    }
    #}
    file_list = make_file_tree(ROOT)
    filename = request.GET.get('filename')
    if filename:
        fullname = os.path.realpath(os.path.join(ROOT, filename))
        if os.path.isfile(fullname) and fullname.startswith(ROOT):
            with open(fullname, 'r') as in_file:
                code = in_file.read()
                if fullname.split('.')[-1] in ['pyui', 'json']:
                    code = json.dumps(json.loads(code), indent=4, separators=(',', ': '))
                output = template('./main.tpl', files = file_list, save_as = filename, code = code)
        else:
            return error404(404)
    else:
        output = template('./main.tpl', files = file_list)
    return output

@post('/')
def submit():
    filename = request.forms.get('filename')
    fullname = os.path.realpath(os.path.join(ROOT, filename))
    if os.path.isfile(fullname) and fullname.startswith(ROOT):
        with open(fullname, 'w') as f:
            f.write(request.forms.get('code').replace('\r', ''))
        if PYTHONISTA:
            editor.reload_files()

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')

@error(403)
def error403(code):
    return 'There is a mistake in your url!'

@error(404)
def error404(code):
    return "This is not the page you're looking for *waves hand*"

def get_local_ip_addr():
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as s:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]

print('''\nTo remotely edit files:
   On your computer open a web browser to http://{}:8080'''.format(get_local_ip_addr()))

if PYTHONISTA:
    print('''\nIf you're using Safari to connect, you can simply select "Pythonista WebIDE" from the Bonjour menu (you may need to enable Bonjour in Safari's advanced preferences).\n''')
    NSNetService = ObjCClass('NSNetService')
    service = NSNetService.alloc().initWithDomain_type_name_port_('', '_http._tcp', 'Pythonista WebIDE', 8080)
    try:
        service.publish()
        debug(True)
        run(reloader=False, host='0.0.0.0')
    finally:
        service.stop()
        service.release()
else:
    debug(True)
    run(reloader=True, host='0.0.0.0')
