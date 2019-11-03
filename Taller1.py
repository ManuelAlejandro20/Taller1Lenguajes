#Nombres: Manuel Trigo y Luciano Larama 
from colorama import init as c_init, Fore as f
import ply.lex as lex
import ply.yacc as yacc
import sys

c_init(autoreset=True)

variables = {}

reserved = {
#representacion : que palabra reservada representa       
    'if' : 'if',
    'print' : 'print',
    'sum' : 'sum',
    'begin' : 'begin',
    'end' : 'end',
    'matrix' : 'matrix', 
    'scalar' : 'scalar',
    'then' : 'then',   
}

tokens = (

    'string',
    'var',
    'float',
    'plus',
    'minus',
    'mult',
    'pow',
    'divide',
    'equals',
    'lparen',
    'lbracket',
    'rparen',
    'rbracket',
    'semicolon',
    'comment',

) + tuple(reserved.values())

precedence = (
    ('right', 'equals'),
    ('left', 'plus', 'minus'),
    ('left', 'mult', 'divide'),
    ('left', 'pow'),
)

t_ignore = r' ' 
t_ignore_comment = r'\//'

t_plus = r'\+'
t_minus = r'-'
t_mult = r'\*'
t_pow = r'\^'
t_divide = r'\/'
t_equals = r'\='
t_lparen = r'\('
t_lbracket = r'\['
t_rparen = r'\)'
t_rbracket = r'\]'
t_semicolon = r'\;'

def t_float(t):
    r'\d+\.\d*(e-?\d+)?'
    t.value = float(t.value)
    return t
     
def t_scalar(t):
    r'\d+'
    t.value = int(t.value)
    return t 

def t_var(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value,'var')
    return t

def t_string(t):
    #r'\"[A-Za-z0-9]+\"'
    r'\"((\S+)\s?)+\"'
    t.value = str(t.value)
    return t

def t_matrix(t):
    r'\[  ( \d+ (,\d+) * )   (  \;\d+ (,\d+)  *  ) * \]'
    t.value = (t.value)
    return t 

def t_error(t):
    print(f.RED + "ERROR >>> CARÁCTER NO VALIDO")
    t.lexer.skip(100)
    
  
lexer = lex.lex()

#------------------------------------------------------------------------------------------#


def p_taller(p):
    '''
    taller : ifp
           | assign
           | expr
           

    '''

    for x, y in variables.items():
        print(f.BLUE + 'Variable: ' + str(x) + f.YELLOW + ' Valor: ' + str(y))

def p_assign(p):
    '''
    assign : var equals expr
    '''
    if(variables.get(p[3]) == None):
        if(p[3] != '') :  
            lexer.input(str(p[3]))
            if(lexer.token().type == 'var'):
                p_error(p)
                return
            variables[p[1]] = p[3]
            p[0] = p[3]
    
    else:
        variables[p[1]] = variables.get(p[3])
        p[0] = variables.get(p[3])


def p_op(p):
    '''
    expr : expr plus expr
         | expr minus expr
         | expr mult expr
         | expr divide expr
         | expr pow expr

    '''
    p[0] = (p[2], p[1], p[3])
    p[0] = run_p(p[0])

def run_p(p):
    if(type(p) == tuple):
        if(p[0] == '+'):
            return run_p(p[1]) + run_p(p[2])
        elif(p[0] == '-'):
            return run_p(p[1]) - run_p(p[2])
        elif(p[0] == '*'):
            return run_p(p[1]) * run_p(p[2])
        elif(p[0] == '/'):
            return run_p(p[1]) / run_p(p[2])
        elif(p[0] == '^'):
            return run_p(p[1])**run_p(p[2])

    else:
        return p

def p_if(p):
    '''
    ifp : if lparen rparen then begin end
    '''


def p_expr(p):
    '''
    expr : scalar
         | matrix
         | float
         | string
         | var

    '''
    p[0] = p[1] 

def p_error(p):
    print(f.RED + "ERROR EN EL ANALISIS GRAMATICO")
    p.lexer.skip(100)

parser = yacc.yacc(debug=True)

while 1:
    try:
        s = input('>>> ')
    except EOFError:
        break
    parser.parse(s)

# lexer.input('"este es un mensaje"')

# while 1:
#     tok = lexer.token()
#     if not tok:
#         break
#     print(tok)
