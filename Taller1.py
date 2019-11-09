#Nombres: Manuel Trigo y Luciano Larama 
from colorama import init as c_init, Fore as f
import numpy as n
import ply.lex as lex
import ply.yacc as yacc
import sys
import logging

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
    ('left', 'equals'),
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
    #r'\-?\d+\.\d*(e-?\d+)?'
    r'\d+\.\d*(e-?\d+)?'
    t.value = float(t.value)
    return t
     
def t_scalar(t):
    #r'\-?\d+'
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
    taller : assign
           | ifp
           | expr
           | exprmat
           | imprimir
           

    '''

    for x, y in variables.items():
        print(f.BLUE + 'Variable: ' + str(x) + f.YELLOW + ' Valor: ' + str(y))

def p_assign(p):
    '''
    assign : var equals expr
           | var equals exprvar 
           | var equals func
           | var equals exprmat
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


def p_exprvar(p):
    '''
    exprvar : exprvar plus exprvar
            | exprvar minus exprvar
            | exprvar mult exprvar
            | exprvar divide exprvar
            | exprvar pow exprvar
            | exprvar plus expr
            | exprvar minus expr
            | exprvar mult expr
            | exprvar divide expr
            | exprvar pow expr
            | expr plus exprvar
            | expr minus exprvar
            | expr mult exprvar
            | expr divide exprvar
            | expr pow exprvar
    '''
    if(variables.get(p[1]) == None):
        if(variables.get(p[3]) == None):
            p[0] = (p[2], p[1], p[3])
        else:    
            p[0] = (p[2], p[1], variables.get(p[3]))
    elif(variables.get(p[3]) == None):
        if(variables.get(p[1]) == None):
            p[0] = (p[2], p[1], p[3])
        else:
            p[0] = (p[2], variables.get(p[1]), p[3])
    else: 
        p[0] = (p[2], variables.get(p[1]), variables.get(p[3]))
    p[0] = run_p(p[0])

def p_exprvar2(p):
    '''
    exprvar : var
            | minus var
    '''
    if(len(p) == 3):
        ntype = run_type(variables.get(p[2]))
        var = variables.get(p[2])
        if(var == None):
            p[0] = 'aaaaaaaaaaaaaa'
            return
        if(ntype == 'scalar'):
            p[0] = int(-var)
        elif(ntype == 'float'):
            p[0] = float(-var)
        else:
            p[0] = '-'+str(p[2])
    else:
        p[0] = p[1]

def p_exprmat(p):
    '''
    exprmat : exprmat plus exprmat
            | exprmat minus exprmat
            | exprmat mult exprmat
            | exprmat divide exprmat
            | exprmat pow exprmat
            | expr plus exprmat
            | expr minus exprmat
            | expr mult exprmat
            | exprmat divide expr
            | exprmat pow expr
    '''
    if(isinstance(p[1],n.matrix) == False):
        matriz1 = convertMatrix(p[1])
    else:
        matriz1 = p[1]
    if(isinstance(p[3],n.matrix) == False): 
        matriz2 = convertMatrix(p[3])
    else:
        matriz2 = p[3]
    p[0] = (p[2], matriz1, matriz2)
    p[0] = runMatriz_p(p[0])
    print(p[0])

def p_exprmat2(p):
    '''
    exprmat : matrix
            | minus matrix
    '''
    if(len(p) == 3):
        p[0] = p[2]
    p[0] = p[1]


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


def run_type(p):
    if(type(p) == tuple):
        lexer.input(str(p[0]))
        type1 = str(lexer.token().type)
        lexer.input(str(p[1])) 
        type2 = str(lexer.token().type)
        return type1, type2
    else:
        lexer.input(str(p))
        return str(lexer.token().type)

def runMatriz_p(p):
    if(type(p) == tuple):
        if(p[0] == '+'):
            return n.add(runMatriz_p(p[1]), runMatriz_p(p[2]))
        elif(p[0] == '-'):
            return n.subtract(runMatriz_p(p[1]), runMatriz_p(p[2]))
        elif(p[0] == '*'):
            return n.multiply(runMatriz_p(p[1]), runMatriz_p(p[2]))
        elif(p[0] == '/'):
            return n.divide(runMatriz_p(p[1]), runMatriz_p(p[2]))
        elif(p[0] == '^'):
            return 
    else:
        return p

def run_p(p):
    if(type(p) == tuple):
        print(p)()
        try:
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
        except TypeError:
            return str(p[1]) + str(p[0]) + str(p[2])
    else:
        return p

def p_if(p):
    '''
    ifp : if lparen boolexpr rparen then begin assign end
        | if lparen minus boolexpr rparen then begin assign end
    '''

    if(len(p) == 10):
        ntype = run_type(p[4])
        if(ntype == 'scalar'):
            num = int(-p[4])
        else:
            num = float(-p[4])
    else:
        try:
            if(p[3] > 0):
                ntype = run_type(p[3])
                if(ntype == 'scalar'):
                    num = int(p[3])
                else:
                    num = float(p[3])
            else:
                num = p[3]
        except:
            p_error(p)
            num = -1
    try:
        if(num < 0):
            n = 8
            if(len(p) == 9):
                n -= 1
            #Se esta asignando el valor de otra variable a la variable
            #Se esta modificar la valor de una variable ya existente
            if(len(p[n]) == 3):
                tup = p[n]
                variables[tup[0]] = tup[1]
            #Se esta intentando crear una variable nueva dentro del if
            else:
                variables.pop(p[n])
                
    except:
        p_error(p)

def p_boolexpr(p):
    '''
    boolexpr : scalar
             | float
             | var
    '''
    if(variables.get(p[1]) != None):
        p[0] = variables.get(p[1])

    else:
        p[0] = p[1]


def p_expr(p):
    '''
    expr : scalar
         | float
         | string
         | minus scalar
         | minus float

    '''
    if(len(p) == 3):
        ntype = run_type(p[2])
        if(ntype == 'scalar'):
            p[0] = int(-p[2])
        else:
            p[0] = float(-p[2])
    else:
        p[0] = p[1]

def p_print(p):
    '''
    imprimir : print lparen expr rparen
             | print lparen exprvar rparen
    '''
    ntype = run_type(p[3])
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

def p_sum(p):
    '''
    func : sum lparen expr rparen
         | sum lparen exprvar rparen
         | sum lparen exprmat rparen

    '''
    ntype = run_type(p[3])
    if(ntype == 'var'):
        p[0] = variables.get(p[3])
    elif(ntype == 'matrix'):
        matriz = convertMatrix(p[3])
        p[0] = matriz.sum()
    else:
        p[0] = p[3]

def convertMatrix(p):
    if(isinstance(p, int)):
        return p
    lista = p.replace('[', '')
    lista = lista.replace(']', '')
    lista = lista.split(';')
    lista2 = []
    listamax = []
    for i in lista:
        i2 = i.split(',')
        lista2.append(list(map(int, i2)))
        listamax.append(len(i2))
    max1 = max(listamax) 
    for j in lista2:
        largo = len(j)
        if(largo != max1):
            for i in range(max1 - largo):
                j.append(0)
    return n.matrix(lista2)

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

# lexer.input('"este es un mensaje"')

# while 1:
#     tok = lexer.token()
#     if not tok:
#         break
#     print(tok)
