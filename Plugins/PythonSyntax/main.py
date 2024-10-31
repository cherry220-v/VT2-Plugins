def initAPI(api):
    global vtapi, format, highlighting_rules, jedi
    vtapi = api
    sys = vtapi.FSys.sysModule()
    os = vtapi.FSys.osModule()
    QtGui = vtapi.FSys.importModule("PyQt6.QtGui")
    QtCore = vtapi.FSys.importModule("PyQt6.QtCore")
    sys.path.insert(0, os.path.join(vtapi.App.pluginsDir, "PythonSyntax/Lib/site-packages"))
    import jedi
    vtapi.SigSlots.tabCreated.connect(completeNlight)

    def format(color, style=''):
        _color = QtGui.QColor()
        if type(color) is not str:
            _color.setRgb(color[0], color[1], color[2])
        else:
            _color.setNamedColor(color)

        _format = QtGui.QTextCharFormat()
        _format.setForeground(_color)
        if 'bold' in style:
            _format.setFontWeight(QtGui.QFont.Weight.Bold)
        if 'italic' in style:
            _format.setFontItalic(True)

        return _format

    STYLES = {
        'keyword': format([200, 120, 50], 'bold'),
        'operator': format([150, 150, 150]),
        'brace': format('darkGray'),
        'defclass': format([220, 220, 255], 'bold'),
        'string': format([20, 110, 100]),
        'string2': format([30, 120, 110]),
        'comment': format([128, 128, 128]),
        'self': format([150, 85, 140], 'italic'),
        'numbers': format([100, 150, 190]),
    }

    python_highlighter_rules = {
        'keywords': [
            r'\b%s\b' % w for w in [
                'and', 'assert', 'break', 'class', 'continue', 'def',
                'del', 'elif', 'else', 'except', 'exec', 'finally',
                'for', 'from', 'global', 'if', 'import', 'in',
                'is', 'lambda', 'not', 'or', 'pass', 'print',
                'raise', 'return', 'try', 'while', 'yield',
                'None', 'True', 'False',
            ]
        ],
        'operators': [
            r'%s' % o for o in [
                '=', '==', '!=', '<', '<=', '>', '>=',  # Comparison
                r'\+', '-', r'\*', '/', '//', r'\%', r'\*\*',  # Arithmetic
                r'\+=', '-=', r'\*=', '/=', r'\%=',  # In-place
                r'\^', r'\|', r'\&', r'\~', r'>>', r'<<',  # Bitwise
            ]
        ],
        'braces': [
            r'%s' % b for b in ['\{', '\}', '\(', '\)', '\[', '\]']
        ],
        'string': [
            r'"[^"\\]*(\\.[^"\\]*)*"',  # Double-quoted strings
            r"'[^'\\]*(\\.[^'\\]*)*'",   # Single-quoted strings
        ],
        'multi_line_strings': [
            r"'''.*?'''",  # Triple single-quoted strings
            r'""".*?"""',   # Triple double-quoted strings
        ],
        'self': [
            r'\bself\b',
        ],
        'defclass': [
            r'\bdef\b\s*(\w+)',  # Function definition
            r'\bclass\b\s*(\w+)',  # Class definition
        ],
        'comment': [
            r'#[^\n]*',  # Comments
        ],
        'numbers': [
            r'\b[+-]?[0-9]+[lL]?\b',  # Integer literals
            r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b',  # Hexadecimal literals
            r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b',  # Float literals
        ]
    }

    highlighting_rules = {
        'keywords': [(QtCore.QRegularExpression(rule), 0, STYLES['keyword']) for rule in python_highlighter_rules['keywords']],
        'operators': [(QtCore.QRegularExpression(rule), 0, STYLES['operator']) for rule in python_highlighter_rules['operators']],
        'braces': [(QtCore.QRegularExpression(rule), 0, STYLES['brace']) for rule in python_highlighter_rules['braces']],
        'strings': [(QtCore.QRegularExpression(rule), 0, STYLES['string']) for rule in python_highlighter_rules['string']],
        'multi_line_strings': [(QtCore.QRegularExpression(rule), 0, STYLES['string2']) for rule in python_highlighter_rules['multi_line_strings']],
        'self': [(QtCore.QRegularExpression(rule), 0, STYLES['self']) for rule in python_highlighter_rules['self']],
        'defclass': [(QtCore.QRegularExpression(rule), 1, STYLES['defclass']) for rule in python_highlighter_rules['defclass']],
        'comments': [(QtCore.QRegularExpression(rule), 0, STYLES['comment']) for rule in python_highlighter_rules['comment']],
        'numbers': [(QtCore.QRegularExpression(rule), 0, STYLES['numbers']) for rule in python_highlighter_rules['numbers']],
    }


def completeNlight():
    i = vtapi.Tab.currentTabIndex()
    if vtapi.Tab.getTabFile(i) and vtapi.Tab.getTabFile(i).endswith(".py"):
        text, line, column = vtapi.Text.getCompletePos(i)

        script = jedi.Script(text)
        try:
            completions = script.complete(line, column)
            vtapi.Text.setCompleteList(i, [completion.name for completion in completions])
        except jedi.api.exceptions._JediError:
            return

        vtapi.Text.setHighlighter(i, highlighting_rules)
        vtapi.Text.rehighlite(i)