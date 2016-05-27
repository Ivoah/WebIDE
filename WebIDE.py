from bottle import get, post, route, run, debug, template, request, static_file, error, redirect # Import bottle's functions (from bottle import * might be better)
import contextlib, json, os, socket # Import standard python libraries that we need

try:
    from urllib.request import pathname2url # Try to import pathname2url from the python 3 location
except ImportError:
    from urllib import pathname2url # Whoops, looks like we're python 2

try: # Try to import Pythonista specific libraries
    import editor # For reloading files in pythonista
    from objc_util import * # Magic Bonjour stuff (idk how this really works :P)
    PYTHONISTA = True # Yep, we're running in Pythonista!
except ImportError: # If we can't import the Pythonista libraries...
    PYTHONISTA = False # Then we aren't running in Pythonista (duh)!

IDE_ROOT = os.path.dirname(os.path.realpath(__file__)) # Find the root directory of the program
os.chdir(IDE_ROOT) # Make sure we're in it
ROOT = os.path.realpath('..') + '/' # Get the folder just above us (presumably the one that has all the stuff you want to edit)

def make_file_tree(dir_path=ROOT):
    # Make a dict of the folder hierarchy (starting at ROOT if not specified)
    # It looks something like this:
    '''
    file_list = {
        'filename1': 'path1',
        'filename2': 'path2',
        'dirname1': {
            'filename3': 'path3',
            'dirname2': {
                'filename4': 'path4',
                'filename5': 'path5'
            }
        }
    }
    '''
    file_dict = {} # Our main dictionary that will eventually hold the tree
    dir_path = dir_path.rstrip('/') # Get rid of those nasty slashes at the end of the string (for matching purposes later)
    def recur(path, list): # Our recursive function to delve into the depths of the directory tree
        for l in os.listdir(path): # For each file/folder in the current folder we're working on...
            f = os.path.join(path, l) # Make the full pathname (path of the folder we're in + the filename)
            if l[0] == '.': # Every folder has a '.' folder inside, which is itsself, so skip it
              continue # Poor '.' is alone and forgotten :(
            elif os.path.isdir(f): # If we've stumbled upon a directory...
                list[l] = {} # Then make a new sub-dict for our tree
                recur(f, list[l]) # And run the recur function on our newly found directory
            elif l.split('.')[-1] in ['py', 'txt', 'pyui', 'json']: # Or if we found a valid file...
                list[l] = pathname2url(f[len(dir_path)+1:]) # Then add the filename to the tree along with it's full pathname (relative to ROOT)
    recur(dir_path, file_dict) # Start the chain reaction
    return file_dict # And then return our baby tree (they grow up so fast *sniffle*)

@get('/') # Map this function to the root of the website for GET requests
def edit(): # This function will get called for each GET request to /
    tree = make_file_tree(ROOT) # Make the file tree for ROOT
    filename = request.GET.get('filename') # Get the filename to edit
    if filename: # If there is a filename...
        fullname = os.path.realpath(os.path.join(ROOT, filename)) # Get the full path (relative to /, not ROOT this time)
        if os.path.isfile(fullname) and fullname.startswith(ROOT): # If it's a file, and it is inside our ROOT directory (for safety)
            with open(fullname, 'r') as in_file: # Open the file...
                code = in_file.read() # And read all of it's juicy insides
                if fullname.split('.')[-1] in ['pyui', 'json']: # If it's a JSON formatted file...
                    code = json.dumps(json.loads(code), indent=4, separators=(',', ': ')) # Then make it look pretty
                return template('./main.tpl', files = tree, filename = filename, code = code) # Read our template and give it the file tree, the name of the file, and the code
        else: # If it's not a file or not in the ROOT directory...
            return template('./main.tpl', files = tree, error = 'Invalid filename') # Then yell at the user for being an idiot
    else: # If we have no file to open...
        return template('./main.tpl', files = tree) # Then just return the main page with no file loaded

@post('/') # Map this function to the root of the website for POST requests
def submit(): # This function will get called for each POST request to /
    filename = request.forms.get('filename') # Get the name of the file we are writing to
    fullname = os.path.realpath(os.path.join(ROOT, filename)) # Get the full path (relative to /, not ROOT this time)
    if fullname.startswith(ROOT): # If our file is in ROOT...
        with open(fullname, 'w') as f: # Then open the file...
            f.write(request.forms.get('code').replace('\r', '')) # And dump our code into it
        if PYTHONISTA: # And if we are in Pythonista
            editor.reload_files() # Then we need to reload the files so our newly edited file is visible
    else: # If it's not a valid file...
        return template('./main.tpl', files = make_file_tree(ROOT), error = 'Invalid filename') # Yell at the user some more

@get('/static/<filepath:path>') # Map this function to any GET request in the /static folder
def server_static(filepath): # This function will just return anything in the /static folder
    return static_file(filepath, root='./static') # Return whatever was requested

@error(403) # Bind the error403 function to the 403 error code
def error403(code): # Whenever there is a 403 error, this function will be called
    return 'There is a mistake in your url!' # Yell at the user

@error(404) # Bind the error404 function to the 404 error code
def error404(code): # This function will be called whenever there is a 404 error
    return template('./main.tpl', files = make_file_tree(ROOT), error = 'This is not the page you\'re looking for *waves hand*') # Guess what this does? Yep, yell at the user

def get_local_ip_addr(): # Get the local ip address of the device
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as s: # Make a socket object
            s.connect(('8.8.8.8', 80)) # Connect to google
            return s.getsockname()[0] # And get our ip address from the socket

print('''\nTo remotely edit files:
   On your computer open a web browser to http://{}:8080'''.format(get_local_ip_addr())) # Print out some instructions

if PYTHONISTA: # If we are running in Pythonista...
    print('''\nIf you're using Safari to connect, you can simply select "Pythonista WebIDE" from the Bonjour menu (you may need to enable Bonjour in Safari's advanced preferences).\n''') # Print out more (Pythonista specific) instructions
    NSNetService = ObjCClass('NSNetService') # Do some Objective-C magic
    service = NSNetService.alloc().initWithDomain_type_name_port_('', '_http._tcp', 'Pythonista WebIDE', 8080) # Do ALL THE MAGICS!
    try: # Try to publish our service (I guess)
        service.publish() # Publish our service so Bonjour things can find it
        debug(True) # Set the debugging mode to true
        run(reloader=False, host='0.0.0.0') # And finally run the actual site (without reloading, as that doesn't work in Pythonista)
    finally: # When all is said and done...
        service.stop() # Stop the service
        service.release() # And release it from it's shackles
else: # Looks like we're running on a normal computer...
    debug(True) # Set the debugging mode to true
    run(reloader=True, host='0.0.0.0') # And run the site! (with reloading, horray!)
