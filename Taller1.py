#Nombres: Manuel Trigo y Luciano Larama 
from colorama import init as c_init, Fore as f
import ply.lex as lex
import ply.yacc as yacc
import sys
import logging

c_init(autoreset=True)

variables = {}
variables2 = {}

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
    r'\-?\d+\.\d*(e-?\d+)?'
    t.value = float(t.value)
    return t
     
def t_scalar(t):
    r'\-?\d+'
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
    taller : assign
           | ifp
           | expr
           | imprimir
           

    '''

    for x, y in variables.items():
        print(f.BLUE + 'Variable: ' + str(x) + f.YELLOW + ' Valor: ' + str(y))

def p_assign(p):
    '''
    assign : var equals expr 
    '''
    #Busco si la variable ya existe, si no...
    if(variables.get(p[3]) == None):
        #Si es diferente de vacio
        if(p[3] != '') :  
            lexer.input(str(p[3]))
            #Si es una variable y entra en este if quiere decir que la variable no esta dentro del diccionario osea error
            if(lexer.token().type == 'var'):
                p_error(p)
                return
            if(p[1] in variables):
                p[0] = (p[1], variables.get(p[1]) , p[3])
            else:
                p[0] = p[1]
            variables[p[1]] = p[3]
            
    
    #Si ya existe se buscara el valor de la variable y este sera el nuevo valor de la variable izquierda
    else:
        var1 = variables.get(p[1])
        variables[p[1]] = variables.get(p[3])
        p[0] = (p[1], var1, variables.get(p[3]))


def p_op(p):
    '''
    expr : expr plus expr
         | expr minus expr
         | expr mult expr
         | expr divide expr
         | expr pow expr

    '''
    # lexer.input(str(p[1]))
    # ntype = str(lexer.token().type)
    # lexer.input(str(p[3]))
    # ntype2 = str(lexer.token().type)
    # if(ntype == 'var' and ntype2 == 'var'):
    #     print('operaciones entre variables')
        # if(p[1] in variables and p[3] in variables):
        #     p[1] = variables.get(p[1])
        #     p[3] = variables.get(p[3])
        # else:
        #     print('variables no disponibels')        
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
    ifp : if lparen boolexpr rparen then begin assign end
    '''

    lexer.input(str(p[3]))
    ntype = str(lexer.token().type)

    if(ntype == 'scalar'):
        num = int(p[3])
    elif(ntype == 'float'):
        num = float(p[3])
    else:
        num = ''

    try:
        if(num > 0):
            print('true')
        else:
            print('false')
            #Se esta asignando el valor de otra variable a la variable
            #Se esta modificar la valor de una variable ya existente
            if(len(p[7]) == 3):
                tup = p[7]
                variables[tup[0]] = tup[1]
            #Se esta intentando crear una variable nueva dentro del if
            else:
                variables.pop(p[7])
                
    except:
        p_error(p)

def p_boolexpr(p):
    '''
    boolexpr : scalar
             | float
    '''
    p[0] = p[1]


def p_expr(p):
    '''
    expr : scalar
         | matrix
         | float
         | string
         | var

    '''
    # lexer.input(str(p[1]))

    # a = str(lexer.token().type)
    # print(a)
    # if(a == "scalar"):
    #     p[0] = int(p[1])
    # elif(a == "float"):
    #     p[0] = float(p[1])
    # else:
    p[0] = p[1]

def p_print(p):
    '''
    imprimir : print lparen expr rparen
    '''
    lexer.input(str(p[3]))
    ntype = str(lexer.token().type)
    if(ntype == 'var'):
        if(p[3] in variables):
            print(variables.get(p[3]))
        else:
            p_error(p)
    elif(ntype == 'string'):
        p2 = p[3].replace('"', '')  
        print(p2)
    else:
        print(p[3])

# def p_error(p):
#     print(f.RED + "ERROR EN EL ANALISIS GRAMATICO")
#     p.lexer.skip(100)

parser = yacc.yacc(debug=True)

while 1:
    try:
        s = input('>>> ')
    except EOFError:
        break
    log = logging.getLogger()
    parser.parse(s,debug=log)
    #parser.parse(s)

# lexer.input('"este es un mensaje"')

# while 1:
#     tok = lexer.token()
#     if not tok:
#         break
#     print(tok)
