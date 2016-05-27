<html>
    <head>
        <title>Pythonista WebIDE</title>
        <!-- Latest compiled and minified CSS -->
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous">
        <script src="http://code.jquery.com/jquery-2.2.0.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js" integrity="sha384-0mSbJDEHialfmuBBQP6A4Qrprq5OVfW37PRR3j5ELqxss1yVqOtnepnHVP9aJ7xS" crossorigin="anonymous"></script>

        <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.15.2/codemirror.min.css">
        <link rel="stylesheet" type="text/css" href="/static/solarized.css">
        <!-- <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.15.2/theme/solarized.min.css"> -->
        <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.15.2/codemirror.min.js"></script>
        <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.15.2/mode/python/python.min.js"></script>
        <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.15.2/mode/javascript/javascript.min.js"></script>
        <script type="text/javascript">
            window.onload = function() {
                var editor = CodeMirror.fromTextArea(document.getElementById("codemirror"), {
                    lineNumbers: true,
                    theme: "solarized light",
                    <%if defined('filename'):
                        import os.path
                        ext = os.path.splitext(filename)[1][1:]
                        if ext == 'py':%>
                            mode: "python"
                        %elif ext in ['json', 'pyui']:
                            mode: {name: "javascript", json: true}
                        %else:
                            mode: false
                        <%end
                    end%>
                });

                $("#submit").click(function() {
                    editor.save();
                    $.post('/', $('#save').serialize());
                    return false;
                });
            }
        </script>
        <link rel="stylesheet" type="text/css" href="/static/style.css">
    </head>
    <body class="base3-background">
        <nav class="navbar navbar-default base2-background base00-color">
            <div class="container-fluid">
                <!-- Brand and toggle get grouped for better mobile display -->
                <div class="navbar-header">
                    <a class="navbar-brand" href="#">Pythonista WebIDE</a>
                </div>

                <!-- Collect the nav links, forms, and other content for toggling -->
                <ul class="nav navbar-nav">
                    <li class="dropdown">
                    <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Open <span class="caret"></span></a>
                    <ul class="dropdown-menu base3-background">
                        <li><a href='/'>New</a></li>
                        <li class="divider base01-color"></li>
                        <%def print_tree(tree):
                            for item in tree:
                                if type(tree[item]) == dict:%>
                                    <li class="dropdown-submenu base00-color"><a href="#">{{item}}</a><ul class="dropdown-menu base3-background">
                                    <%print_tree(tree[item])%>
                                    </ul></li>
                                <%else:%>
                                    <li><a class="base00-color" href="/?filename={{tree[item]}}">{{item}}</a></li>
                                <%end
                            end
                        end%>
                        %print_tree(files)
                    </ul>
                    </li>
                </ul>
                <form action="/" class="navbar-form navbar-left" role="search" id="save" method="post">
                    <div class="form-group">
                        %if defined('filename'):
                        <input name="filename" type="text" class="form-control base00-color base3-background" placeholder="Save as..." value="{{filename}}">
                        %else:
                        <input name="filename" type="text" class="form-control base00-color base3-background" placeholder="Save as...">
                        %end
                    </div>
                    <button id="submit" type="submit" class="btn btn-default base01-color base3-background">Save</button>
                </form>
            </div><!-- /.container-fluid -->
        </nav>

        <div class="container">
            %if defined('error'):
            <div class="alert alert-danger">
                <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>
                {{error}}
            </div>
            %end
            <h2 class="base01-color">Edit File</h2>
            <p>
                <textarea name="code" id="codemirror" form="save">{{code if defined('code') else ''}}</textarea>
            </p>
        </div>
    </body>
</html>
