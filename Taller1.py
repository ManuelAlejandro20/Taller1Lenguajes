import ply.lex as lex
import ply.yacc as yacc
import sys

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
        'float',
        'char',
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
        ) + tuple(reservadas.values())

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
     
def t_scalar(t):
    r'\d+'
    t.value = int(t.value)
    return t 

def t_error(t):
    print("ERROR >>> CARÁCTER NO VALIDO")
    t.lexer.skip(1)
  
lexer = lex.lex()

lexer.input('1+2^;]/=')

while 1:
    tok = lexer.token()
    if not tok:
        break
    print(tok)
