#Nombres: Manuel Trigo y Luciano Larama 
from colorama import init as c_init, Fore as f
import numpy as n
import math as mt
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
    ('right', 'mult', 'divide'),
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
    #r'"([^"\n]|(\\"))*"$'
    #r'\"((\S+[^"])\s?[^"])+\"'
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
           | expr
           | imprimir

    '''

    for x, y in variables.items():
        print(f.BLUE + 'Variable: ' + str(x) + f.YELLOW + ' Valor: ' + str(y))

def p_assign(p):
    '''
    assign : var equals expr
           | var equals func
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

    elemento1 = p[1]
    elemento2 = p[3]

    if(variables.get(p[1]) != None and variables.get(p[3]) != None):
        elemento1 = variables.get(p[1])
        elemento2 = variables.get(p[3])
    else:
        if(variables.get(p[1]) != None):
            elemento1 = variables.get(p[1])
                  
        if(variables.get(p[3]) != None):
            elemento2 = variables.get(p[3])

    ntype = run_type(elemento1)
    ntype2 = run_type(elemento2)

    if(ntype == 'string' or ntype2 == 'string'):
        if(p[2] == '+'):
            p[0] = str(elemento1) + str(elemento2)
            p[0] = p[0].replace('"', '')
            p[0] = '"' + p[0]  + '"'
        else:
            p_error(p)
        return
    if(isinstance(p[1],n.matrix) == False):
        elemento1 = convertMatrix(elemento1)
    if(isinstance(p[3],n.matrix) == False): 
        elemento2 = convertMatrix(elemento2)

    p[0] = (p[2], elemento1, elemento2)
    p[0] = run_p(p[0])
    if(isinstance(p[0], n.matrix)):
        p[0] = matrixConvert(p[0])

def run_type(p):
    if(type(p) == tuple):
        lexer.input(str(p[0]))
        type1 = str(lexer.token().type)
        lexer.input(str(p[1])) 
        type2 = str(lexer.token().type)
        return type1, type2
    else:
        strp = str(p)
        if('-' in strp):
            strp = strp.replace('-', '')
        lexer.input(strp)
        return str(lexer.token().type)

def run_p(p):
    if(type(p) == tuple):
        if(isinstance(p[1], n.matrix) or isinstance(p[2], n.matrix)):
            if(p[0] == '+'):
                return n.add(runMatriz_p(p[1]), runMatriz_p(p[2]))
            elif(p[0] == '-'):
                return n.subtract(runMatriz_p(p[1]), runMatriz_p(p[2]))
            elif(p[0] == '*'):
                return n.dot(runMatriz_p(p[1]), runMatriz_p(p[2]))
            elif(p[0] == '/'):
                return n.divide(runMatriz_p(p[1]), runMatriz_p(p[2]))
            elif(p[0] == '^'):
                return n.power(runMatriz_p(p[1]), runMatriz_p(p[2]))
        else:
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


def p_expr(p):
    '''
    expr : scalar
         | float
         | var
         | matrix
         | minus var
         | minus scalar
         | minus float
         | minus matrix

    '''
    p[0] = retExpr(p)

def retExpr(p):
    if(len(p) == 3):
        ntype = run_type(p[2])
        if(ntype == 'scalar'):
            return int(-p[2])
        elif(ntype == 'float'):
            return float(-p[2])
        elif(ntype == 'matrix'):
            matriz = convertMatrix(p[2])
            matriz = n.dot(-1,matriz)
            return matrixConvert(matriz)
        else:
            if(variables.get(p[2]) == None):
                return p[2]
            return retExpr((p[0], p[1], variables.get(p[2])))
    else:
        return p[1]

def p_print(p):
    '''
    imprimir : print lparen expr rparen

    '''

    retPrint(p)


def retPrint(p):
    ntype = run_type(p[3])
    if(ntype == 'var'):
        if(p[3] in variables):
            return retPrint((p[0], p[1], p[2], variables.get(p[3]), p[4]))
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

    '''
    ntype = run_type(p[3])
    if(ntype == 'var'):
        if(p[3] in variables):
            p[0] = variables.get(p[3])
            ntype2 = run_type(p[0])
            if(ntype2 == 'matrix'):
                matriz = convertMatrix(p[0])
                p[0] = matriz.sum()
            else:
                p[0] = p[3]
        else:
            p_error(p)    
    elif(ntype == 'matrix'):
        matriz = convertMatrix(p[3])
        p[0] = matriz.sum()
    else:
        p[0] = p[3]

def convertMatrix(p):
    if(isinstance(p, int) or isinstance(p, float)):
        return p
    lista = p.replace('[', '')
    lista = lista.replace(']', '')
    lista = lista.split(';')
    lista2 = []
    listamax = []
    for i in lista:
        i2 = i.split(',')
        try:
            lista2.append(list(map(int, i2)))
        except ValueError:
            lista2.append(list(map(float, i2)))
        listamax.append(len(i2))
    max1 = max(listamax) 
    for j in lista2:
        largo = len(j)
        if(largo != max1):
            for i in range(max1 - largo):
                j.append(0)
    return n.matrix(lista2)

def matrixConvert(p):
    matrizStr = '['
    lista = p.tolist()
    for i in lista:
        for j in i:
            if(isinstance(j, float)):
                j = mt.ceil(j)
                j = int(j)
            matrizStr = matrizStr + str(j) + ','
        matrizStr = matrizStr[:-1]
        matrizStr += ';'
    matrizStr = matrizStr[:-1]
    matrizStr += ']'
    return matrizStr

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

# lexer.input('tring"')

# while 1:
#     tok = lexer.token()
#     if not tok:
#         break
#     print(tok)
