# Simple regular expression based tokenizer. A lot of the regular expressions
# are taken from the Python stdlib[1].
#
# The re.Scanner idea was mentioned by AXK[2] on Stack Overflow[3], to use
# that as a Lexer in Python. It's a nice idea and it works great.
#
# [1] http://hg.python.org/cpython/file/2.7/Lib/tokenize.py
# [2] http://servut.us/akx/
# [3] http://stackoverflow.com/questions/691148/pythonic-way-to-implement...

import re
try:
    re.Scanner
except AttributeError:
    # For Python 2.4, we patch the module
    from sre import Scanner
    re.Scanner = Scanner

def group(*options):
    return '(%s)' % ('|'.join(options),)

def any(*options):
    return ''.join([group(*options), '*'])

def maybe(*options):
    return ''.join([group(*options), '?'])


# Whitespace/comments
WHITESPACE  = r'[ \f\t]*'
IGNORE      = WHITESPACE + any(r'\\\r?\n' + WHITESPACE)
VARIABLE    = r'\$\w+'
NAME        = r'[a-zA-Z_]\w*'
ATTRIBUTE   = r'\.' + NAME
STRING      = group(
                r'"(?:[^"\\]|\\.)*"',
                r"'(?:[^'\\]|\\.)*'",
                )

# Numbers
HEX_NUMBER  = r'0[xX][\da-fA-F]+[lL]?'
OCT_NUMBER  = r'(0[oO][0-7]+)|(0[0-7]*)[lL]?'
BIN_NUMBER  = r'0[bB][01]+[lL]?'
DEC_NUMBER  = r'[1-9]\d*[lL]?'
NUMBER      = group(HEX_NUMBER, BIN_NUMBER, OCT_NUMBER, DEC_NUMBER)
EXPONENT    = r'[eE][-+]?\d+'
PNT_FLOAT   = group(r'\d+\.\d*', r'\.\d+') + maybe(EXPONENT)
EXP_FLOAT   = r'\d+' + EXPONENT
FLOAT       = group(PNT_FLOAT, EXP_FLOAT)

# Tail end of / string.
PATTERN     = r'/(?:[^\/\\]|\\.)*/'

# Operators
INFIX       = group(
                r'\.',
                r'\+',
                r'\-',
                r'\*',
                r'\~',
                r'\%',
                r'\^',
                r'\b\$\b',
                r'/',
                r'<<',
                r'>>',
                r'[!<>=]=?',
                r'\bin\b',
                r'\bis\b',
                r'\bnot\b',
                )
INFIXR      = group(
                r'&&',
                r'\|\|',
                r'and',
                r'or',
                )
PREFIX      = group(
                r'\!',
                r'\(',
                r'\)',
                r'\[',
                r'\]',
                r',',
                )
END         = r'$'

scanner = re.Scanner((
    (PATTERN,       lambda scanner, token: ('string',   token)),
    (PREFIX,        lambda scanner, token: ('symbol',   token)),
    (INFIX,         lambda scanner, token: ('symbol',   token)),
    (INFIXR,        lambda scanner, token: ('symbol',   token)),
    (STRING,        lambda scanner, token: ('string',   token)),
    (VARIABLE,      lambda scanner, token: ('variable', token)),
    (NAME,          lambda scanner, token: ('name',     token)),
    (FLOAT,         lambda scanner, token: ('float',    token)),
    (NUMBER,        lambda scanner, token: ('number',   token)),
    (END,           lambda scanner, token: ('end',      '(end)')),
    (WHITESPACE,    None),
))

def tokenize(text):
    result, remain = scanner.scan(text)
    if remain:
        raise SyntaxError('Could not parse %r' % (remain,))
    return result

if __name__ == '__main__':
    print tokenize('host ~ /test/')
    print tokenize('host ^ /test/ and status > 0')
    print tokenize('host $ /test/ and status > 0.0')
    print tokenize('host $ /test/ and status.foo > 0.0')

