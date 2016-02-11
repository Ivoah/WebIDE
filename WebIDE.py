from bottle import get, post, route, run, debug, template, request, static_file, error, redirect
import contextlib, json, os, socket, urllib

try:
    import editor
    PYTHONISTA = True
except ImportError:
    PYTHONISTA = False

ROOT = os.pardir + os.path.sep  # '../'

def make_file_tree(dir_path=os.pardir):
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
                list[l] = urllib.pathname2url(f[len(ROOT):])
    recur(dir_path, file_dict)
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
    file_list = make_file_tree('..')
    file = request.GET.get('file')
    if file:
        with open(os.path.join(ROOT, file), 'r') as in_file:
            code = in_file.read()
      	if file.split('.')[-1] in ['pyui', 'json']:
            code = json.dumps(json.loads(code), indent=4, separators=(',', ': '))
        output = template('main.tpl', files = file_list, save_as = file, code = code)
    else:
        output = template('main.tpl', files = file_list)
    return output

@post('/')
def submit():
    filename = os.path.join(ROOT, request.forms.get('filename'))
    with open(filename, 'w') as f:
        f.write(request.forms.get('code').replace('\r', ''))
    if PYTHONISTA:
        editor.reload_files()

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')

@error(403)
def mistake403(code):
    return 'There is a mistake in your url!'

@error(404)
def mistake404(code):
    return "This is not the page you're looking for *waves hand*"

def get_local_ip_addr():
    with contextlib.closing(
        socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as s:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]

print('''\nTo remotely edit Pythonista files:
   On your computer open a web browser to http://{}:8080'''.format(get_local_ip_addr()))
debug(True)
run(reloader=not PYTHONISTA, host='0.0.0.0')
#remember to remove reloader=True and debug(True) when you move your application from development to a productive environment
