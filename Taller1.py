#Nombres: Manuel Trigo y Luciano Larama 
from colorama import init as c_init, Fore as f
import ply.lex as lex
import ply.yacc as yacc
import sys

c_init(autoreset=True)

variables = {}

reservadas = {
        
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

) + tuple(reservadas.values())

t_ignore = r' ' 

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

def t_comment(t):
    r'\//'
    return

def t_float(t):
    r'\d+\.\d*(e-?\d+)?'
    t.value = float(t.value)
    return t
     
def t_scalar(t):
    r'\d+'
    t.value = int(t.value)
    return t 

def t_string(t):
    r'[a-z0-9]+'
    return t

def t_matrix(t):
    r'\[  ( \d+ (,\d+) * )   (  \;\d+ (,\d+)  *  ) * \]'
    t.value = (t.value)
    return t 

def t_error(t):
    print(f.RED + "ERROR >>> CARÁCTER NO VALIDO")
    t.lexer.skip(1)
    
  
lexer = lex.lex()

#------------------------------------------------------------------------------------------#


def p_taller(p):
    '''
    taller : expr
           | asign

    '''
    
    print(p[1])
    for x, y in variables.items():
        print(f.BLUE + 'Variable: ' + str(x) + f.YELLOW + ' Valor: ' + str(y))

def p_asign(p):
    '''
    asign : string equals expr 
    '''
    if p[3] != '':
        variables[p[1]] = p[3]
        p[0] = p[3]
        lexer.input(str(p[0]))
        print(lexer.token().type)


def p_op(p):
    '''
    expr : expr pow expr
         | expr mult expr
         | expr divide expr
         | expr plus expr
         | expr minus expr

    '''
    lexer.input(str(p[1]))
    tipo1 = lexer.token().type
    lexer.input(str(p[3]))
    tipo2 = lexer.token().type
    if(tipo1 == 'scalar' and tipo2 == 'scalar'):
        if(p[2] == '^'):
            p[0] = pow(p[1], p[3])
        elif(False): pass
        elif(False): pass
        elif(False): pass
        elif(False): pass
    else:
        p[0] = (p[2], p[1], p[3])

def p_expr(p):
    '''
    expr : scalar
         | matrix
         | float
         | string

    '''
    p[0] = p[1] 

def p_error(p):
    print(f.RED + "ERROR EN EL ANALISIS GRAMATICO")


parser = yacc.yacc()

while 1:
    try:
        s = input('>>> ')
    except EOFError:
        break
    parser.parse(s)

#lexer.input('string 55de prueba55')

# while 1:
#     tok = lexer.token()
#     if not tok:
#         break
#     print(tok)
