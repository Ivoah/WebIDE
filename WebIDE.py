from bottle import get, post, route, run, debug, template, request, static_file, error, redirect
import os, urllib

try:
    import editor
    PYTHONISTA = True
except ImportError:
    PYTHONISTA = False

ROOT = '../'

def make_file_tree(path):
    file_list = {}
    def recur(path, list):
        for l in os.listdir(path):
            f = os.path.join(path, l)
            if os.path.isdir(f):
                list[l] = {}
                recur(f, list[l])
            elif l.split('.')[-1] in ['py', 'txt']:
                list[l] = urllib.pathname2url(f[len(ROOT):])
    recur(path, file_list)
    return file_list

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
        code = open(os.path.join(ROOT, file), 'r').read()
        output = template('main.tpl', files = file_list, save_as = file, code = code)
    else:
        output = template('main.tpl', files = file_list)
    return output

@post('/')
def submit():
    with open(os.path.join(ROOT, request.forms.get('filename')), 'w') as f:
        f.write(request.forms.get('code').replace('\r', ''))
        if PYTHONISTA: editor.reload_files()

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static')

@error(403)
def mistake403(code):
    return 'There is a mistake in your url!'

@error(404)
def mistake404(code):
    return 'This is not the page you\'re looking for *waves hand*'

debug(True)
run(reloader=True if not PYTHONISTA else False)
#remember to remove reloader=True and debug(True) when you move your application from development to a productive environment
