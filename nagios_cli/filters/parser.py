# Crude symbol based top down operator presedence parser, as originally
# implemented by Vaughan Pratt[1] and Douglas Crockford[2].
#
# [1]: http://doi.acm.org/10.1145/512927.512931
# [2]: http://javascript.crockford.com/tdop/tdop.html

import re
#from nagios_cli.filters.tokenizer import tokenize
from tokenizer import tokenize


TOKEN = None
TNEXT = None
SYMBOLS = {}

class SymbolBase(object):
    ident = None
    value = None
    first = None

    def nud(self):
        '''
        Null declaration, is used when a token appears at the beginning
        of a language construct.
        '''
        raise SyntaxError('Syntax error %r' % (self.ident,))

    def led(self, left):
        '''
        Left denotation, is used when it appears inside the construct.
        '''
        raise SyntaxError('Unknown operator %r' % (self.ident,))


def symbol(ident, bp=0):
    '''
    Gets (and create if not exists) as named symbol.

    Optionally, you can specify a binding power (bp) value, which will be used
    to control operator presedence; the higher the value, the tighter a token
    binds to the tokens that follow.
    '''
    try:
        s = SYMBOLS[ident]
    except KeyError:
        class s(SymbolBase):
            pass
        s.__name__ = 'symbol-%s' % (ident,)
        s.ident = ident
        s.lbp = bp
        SYMBOLS[ident] = s
    else:
        s.lbp = max(bp, s.lbp)
    return s

# Helper functions

def infix(ident, bp):
    def led(self, left):
        self.first = left
        self.second = Parser.expression(bp)
        return self
    symbol(ident, bp).led = led

def infixr(ident, bp):
    def led(self, left):
        self.first = left
        self.second = Parser.expression(bp-1)
        return self
    symbol(ident, bp).led = led

def prefix(ident, bp):
    def nud(self):
        self.first = Parser.expression(bp)
        return self
    symbol(ident).nud = nud

def constant(ident, value):
    @method(symbol(ident))
    def nud(self):
        self.ident = '(literal)'
        return value

def method(Symbol):
    assert issubclass(Symbol, SymbolBase)
    def wrapped(fn):
        setattr(Symbol, fn.__name__, fn)
    return wrapped

# Big evil parser

class Parser(object):
    token = None
    next = None
    variables = []

    @classmethod
    def advance(cls, ident=None):
        if ident and cls.token.ident != ident:
            raise SyntaxError('Expected %r, got %r' % (ident, cls.token.ident))
        cls.token = cls.next()

    @classmethod
    def expression(cls, rbp=0):
        t = cls.token
        cls.token = cls.next()
        left = t.nud()
        while rbp < cls.token.lbp:
            t = cls.token
            cls.token = cls.next()
            left = t.led(left)
        return left

    @classmethod
    def parse(cls, program, **scope):
        cls.next = cls.reader(program, **scope).next
        cls.token = cls.next()
        return cls.expression()

    @classmethod
    def reader(cls, program, **scope):
        scope.update({
            'None': None, 'null': None, 
            'True': True, 'true': True,
            'False': False, 'false': False,
            'empty': '',
        })
        for kind, value in tokenize(program):
            #print (kind, value),
            if kind == 'name':
                s = SYMBOLS['(literal)']()
                try:
                    s.value = scope[value]
                except KeyError:
                    raise NameError('Name %r is not defined' % (value,))
                yield s
            elif kind == 'variable':
                s = SYMBOLS['(literal)']()
                try:
                    s.value = cls.variables[int(value[1:])]
                except IndexError:
                    s.value = None
                yield s
            elif kind == 'string':
                s = SYMBOLS['(literal)']()
                s.value = value[1:-1]
                yield s
            elif kind == 'number':
                s = SYMBOLS['(literal)']()
                s.value = long(value)
                yield s
            elif kind == 'float':
                s = SYMBOLS['(literal)']()
                s.value = float(value)
                yield s
            elif kind == 'symbol':
                yield SYMBOLS[value]()
            else:
                raise SyntaxError('Unknown operator %s' % (kind,))

        #print '->',
        yield SYMBOLS['(end)']()

# Definition and order of expressions
infixr('or', 30)
infixr('and', 40)
infixr('not', 50)
infixr('!', 50)
infixr('~', 50)
for item in ['in', 'not', 'is', '<', '<=', '>', '>=', '<>', '!=', '=', '==']:
    infix(item, 60)
for item in ['<<', '>>']:
    infix(item, 100)
for item in '+-':
    infix(item, 110)
for item in '*/%':
    infix(item, 120)
for item in '-+':
    prefix(item, 130)
for item in '.[(':
    symbol(item, 150)
symbol('(literal)')
symbol('(variable)')
symbol('(end)')

# Constants
constant('Null', None)
constant('True', True)
constant('False', False)

# Behaviour of expressions
@method(symbol('(literal)'))
def nud(self):
    return self.value

symbol(')')
@method(symbol('('))
def nud(self):
    # Parentesized form
    expr = Parser.expression()
    Parser.advance(')')
    return expr

symbol(']')
symbol(',')
@method(symbol('['))
def nud(self):
    item = []
    if Parser.token.ident != ']':
        while True:
            if Parser.token.ident == ']':
                break
            item.append(Parser.expression())
            if Parser.token.ident != ',':
                break
            Parser.advance(',')
    Parser.advance(']')
    return item

@method(symbol('<<'))
def led(self, left):
    return left << Parser.expression()

@method(symbol('>>'))
def led(self, left):
    return left >> Parser.expression()

@method(symbol('+'))
def led(self, left):
    return left + Parser.expression(110)

@method(symbol('-'))
def led(self, left):
    return left - Parser.expression()

@method(symbol('*'))
def led(self, left):
    return left * Parser.expression()

@method(symbol('/'))
def led(self, left):
    return left / Parser.expression()

@method(symbol('%'))
def led(self, left):
    return left % Parser.expression()

@method(symbol('or'))
def led(self, left):
    return left or Parser.expression()

@method(symbol('and'))
def led(self, left):
    return left and Parser.expression()

@method(symbol('in'))
def led(self, left):
    return left in Parser.expression(60)

@method(symbol('is'))
def led(self, left):
    if Parser.token.ident == 'not':
        Parser.advance()
        return left is not Parser.expression(60)
    else:
        return left is Parser.expression(60)

@method(symbol('<'))
def led(self, left):
    return left < Parser.expression()

@method(symbol('<='))
def led(self, left):
    return left <= Parser.expression()

@method(symbol('>'))
def led(self, left):
    return left > Parser.expression()

@method(symbol('>='))
def led(self, left):
    return left >= Parser.expression()

@method(symbol('<>'))
def led(self, left):
    return left <> Parser.expression()

@method(symbol('!='))
def led(self, left):
    return left != Parser.expression()

@method(symbol('='))
def led(self, left):
    return left == Parser.expression()

@method(symbol('=='))
def led(self, left):
    return left == Parser.expression()

@method(symbol('!'))
def nud(self):
    return not Parser.expression()

@method(symbol('~'))
def led(self, left):
    pattern = '(%s)' % (Parser.expression(),)
    result = re.search(pattern, left)
    if result:
        Parser.variables = result.groups()
        return Parser.variables
    else:
        return None

if __name__ == '__main__':
    from tokenizer import tokenize

    print 'parse: 1+2 ->',
    print Parser.parse('1+2')
    print

    print 'parse: !1 ->',
    print Parser.parse('!1')
    print

    print 'parse: 1 > 2 ->',
    print Parser.parse('1 > 2')
    print

    print 'parse: (1 + 1) >= 2 ->',
    print Parser.parse('(1 + 1) >= 2')
    print

    print 'parse: 1 + 1 >= 2 ->',
    print Parser.parse('1 + 1 >= 2')
    print

    print 'parse: 2 + 3 * 4 = 14 ->',
    print Parser.parse('2 + 3 * 4 = 14')
    print

    print 'parse: foo = "whiskybar" ->',
    print Parser.parse('foo = "whiskybar"', foo="whiskybar")
    print

    print 'parse: "whiskybar" = foo ->',
    print Parser.parse('"whiskybar" = foo', foo="whiskybar")
    print

    print 'parse: "foo" + "bar" ->',
    print Parser.parse('"foo" + "bar"')
    print

    print 'parse: "foo" + "bar" == "foobar" ->',
    print Parser.parse('"foo" + "bar" == "foobar"')
    print

    print 'parse: "foo" + "bar" in "foobar" ->',
    print Parser.parse('"foo" + "bar" in "foobar"')
    print

    print 'parse: "foo" + "bar" is "foobar" ->',
    print Parser.parse('"foo" + "bar" is "foobar"')
    print

    print 'parse: "foo" is not null ->',
    print Parser.parse('"foo" is not null')
    print 

    print 'parse: foo ~ /bar/ ->',
    print Parser.parse('foo ~ /bar/', foo="whiskybar")
    print

    print 'parse: foo ~ /bar/ = True ->',
    print Parser.parse('foo ~ /bar/ = True', foo="whiskybar")
    print

    print 'parse: foo ~ /(bar)/ ->',
    print Parser.parse('foo ~ /(bar)/', foo="whiskybar")
    print

    print 'parse: foo ~ /(bar)/ and $1 == "bar" ->',
    print Parser.parse('foo ~ /(bar)/ and $1 == "bar"', foo="whiskybar")
    print

    print 'parse: (foo ~ /bar/) ->',
    print Parser.parse('(foo ~ /bar/)', foo="whiskybar")
    print

    print 'parse: !foo ~ /bar/ ->',
    print Parser.parse('!foo ~ /bar/', foo="whiskybar")
    print

    print 'parse: !!(foo ~ /bar/) ->',
    print Parser.parse('!!(foo ~ /bar/)', foo="whiskybar")
    print

    print 'parse: [1, 2, 3] ->',
    print Parser.parse('[1, 2, 3]')
    print

    print 'parse: 1 in [1, 2] ->',
    print Parser.parse('1 in [1, 2]')
    print    

    print 'parse: foo in [bar, biz, qux] ->',
    print Parser.parse('foo in [bar, biz, qux]', foo="bar", bar="foo", biz="qux", qux="bar")
    print

