import sys
import queue
import lexer
from queue import Queue
from lexer import Lexer


#Global Variables

peek_next = None
_filename = None
outputFileHandle = None
_error = True
    
#when an error is found, the expected variable is sent here and error is reported
def error(expected):
    global _error
    
    print('\nERROR line: {1}\nExpected: {0}'.format(expected, lexer.line)), #file = outputFileHandle)
    print('Current lexeme: {}'.format(lexer.value)),# file = outputFileHandle)
    print('Current token: {}'.format(lexer._token())),# file = outputFileHandle)

    _error = False   
    
#set current to the next variable to process
def getNext():

    if lexer.token_output != "END": 
        lexer._compute()                          
        printInfo()    

#print information about the token and lexeme. Reports ERROR if current is empty
def printInfo():
        print('Token: {0:14} Lexeme: {1:14} Line: {2:1}'.format(lexer._token(), lexer.value, lexer.line), file = outputFileHandle)
  
#Production Rules 

#R1. <Rat21F>  ::=   <Opt Function Definitions>   #  <Opt Declaration List>  <Statement List>  #
def rat21F():
    #initial production
    print('<Rat21F>  ::=   <Opt Function Definitions>   #  <Opt Declaration List>  <Statement List>  # ', file = outputFileHandle)
    
    optFunctionDefinitions()
    
    if lexer.value == '#':
        getNext()
        optDeclarationList() 
        getNext()
        #continue until EOF
        while True:
            statementList()
            if lexer.token_output == "END":
                break     
    else:
        error('(')

#R2. <Opt Function Definitions> ::= <Function Definitions>     |  <Empty>
def optFunctionDefinitions():
    print('<Opt Function Definitions> ::= <Function Definitions> | <Empty>', file = outputFileHandle)   
    if lexer.value == 'function':
        functionDefinitions()
    elif lexer._token() == 'unknown':
        error('<Function Definitions> | <Empty>')
    else:
        empty()   

#R3. <Function Definitions>  ::= <Function> | <Function> <Function Definitions>   
def functionDefinitions():
    print('<Function Definitions> ::= <Function> | <Function> <Function Definitions>', file = outputFileHandle)
    
    #continue gathering function definitions until there are no more to report
    while True:
        function()
        if lexer.value != 'function':
            break

#R4. <Function> ::= function  <IDENTIFIER> ( <Opt Parameter List> ) <Opt Declaration List>  <Body>
def function():
    print('<Function> ::= function  <IDENTIFIER> ( <Opt Parameter List> ) <Opt Declaration List>  <Body>', file = outputFileHandle)
    
    #function
    if lexer.value == 'function':
        getNext()
    
        #<IDENTIFIER>
        if lexer._token() == 'IDENTIFIER':
            getNext()
            
            # [
            if lexer.value == '(':
                getNext()
                optParameterList()
                
                if lexer.value == ')':
                    getNext()
                    optDeclarationList()
                    body()

                else:
                    error(')')
            
            else:
                error('(')
        
        else:
            error('IDENTIFIER')
    
    else:
        error('function')

#R5. <Opt Parameter List> ::=  <Parameter List>   |  <Empty>
def optParameterList():
    print('<Opt Parameter List> ::=  <Parameter List> | <Empty>', file = outputFileHandle)
    
    if lexer._token() == 'IDENTIFIER':
        parameterList()
    elif lexer._token() == 'unknown':
        error('<Parameter List> | <Empty>')
    else:
        empty()

#R6. <Parameter List> ::= <Parameter> | <Parameter> , <Parameter List>
def parameterList():
    print('<Parameter List> ::= <Parameter> | <Parameter> , <Parameter List>', file = outputFileHandle)
    
    parameter()
    
    if peek_next == ',':
        getNext()
        parameterList()

#R7. <Parameter> ::=  < IDs > : <Qualifier>
def parameter():
    print('<Parameter> ::=  < IDs > : <Qualifier>', file = outputFileHandle)
    
    if lexer._token() == 'IDENTIFIER':
        getNext()
        qualifier()
        
    else:
        error('<Qualifier>')
            

#R8. <Qualifier> ::= integer | boolean | real
def qualifier():
    print('<Qualifier> ::= integer | boolean | real', file = outputFileHandle)
    
    if lexer.value == 'int' or lexer.value == 'integer' or lexer.value == 'boolean' or lexer.value == 'real':
        getNext()
    else:
        error('int | boolean | real')

#R9. <Body>  ::=  {  < Statement List>  }
def body():
    print('<Body>  ::=  {  < Statement List>  }', file = outputFileHandle)
    
    if lexer.value == '{':
        getNext()
        statementList()
        if lexer.value == '}':
            getNext() 
        else:
            error('}')

    else:
        error('{')

#R10. <Opt Declaration List> ::= <Declaration List> | <Empty>
def optDeclarationList():
    print('<Opt Declaration List> ::= <Declaration List> | <Empty>', file = outputFileHandle)
    
    #check for qualifier
    if lexer.value == 'int' or lexer.value == 'integer' or lexer.value == 'boolean' or lexer.value == 'real':
        declarationList()
    elif lexer._token() == 'unknown':
        error('<<Declaration List> | <Empty>')
    else:
        empty()

#R11. <Declaration List> := <Declaration> ; | <Declaration> ; <Declaration List>
def declarationList():
    print('<Declaration List> := <Declaration> ; | <Declaration> ; <Declaration List>', file = outputFileHandle)
    
    declaration()
    
    if lexer.value == ';':
        # getNext()
        #check if the next is a <Declaration List> by seeing if it's a qualifier --> INTEGER, boolean, REAL
        if lexer.value == 'INTEGER' or lexer.value == 'boolean' or lexer.value == 'real':
            declarationList()
    else:
        error(';')

#R12. <Declaration> ::=  <Qualifier > <IDs>
def declaration():
    print('<Declaration> ::= <Qualifier> <IDs>', file = outputFileHandle)
    
    qualifier()
    ids()

#R13. <IDs> ::=  <IDENTIFIER> | <IDENTIFIER>, <IDs>
def ids():
    print('<IDs> ::=  <IDENTIFIER> | <IDENTIFIER>, <IDs>', file = outputFileHandle)

    if lexer._token() == 'IDENTIFIER':
        getNext()
        
        #<IDENTIFIER>, <IDs>    break when no ',' after the IDENTIFIER
        while True:
            if lexer.value == ',':
                getNext()
                
                if lexer._token() == 'IDENTIFIER':
                    getNext()
                else:
                    error('<IDENTIFIER>')
                    
            else:
                break
    else:
        error('<IDENTIFIER>')

#R14. <Statement List> ::= <Statement> | <Statement> <Statement List>
def statementList():
    print('<Statement List> ::= <Statement> | <Statement> <Statement List>', file = outputFileHandle)
    
    while True:
        statement()
        #must test to see if possible statement. Will test for compound, assign, if, return, write,
        #  read, while. If there is another statement then continue loop, otherwise break
        if lexer.value != '{' and lexer._token() != 'IDENTIFIER' and lexer.value != 'if' and lexer.value != 'return' and lexer.value != 'put' and lexer.value != 'get' and lexer.value != 'while':
            break

#R15. <Statement> ::=  <Compound> | <Assign> | <If> |  <Return> | <Print> | <Scan> | <While>
def statement():
    print('<Statement> ::=  <Compound> | <Assign> | <If> |  <Return> | <Print> | <Scan> | <While>', file = outputFileHandle)
    
    #compound starts with '{'
    if lexer.value == '{':
        compound()
    #assign starts with an IDENTIFIER, test for assign by checking if 'IDENTIFIER' token in current
    elif lexer._token() == 'IDENTIFIER':
        assign()
    #if operations all start with 'if', check current lexeme for 'if'
    elif lexer.value == 'if':
        _if()
    #return operators start with return, check current lexeme for 'return'
    elif lexer.value == 'return':
        _return()
    #print begins with print, check current lexeme for 'print'
    elif lexer.value == 'put':
        Print()
    #scan begins with scan, check current lexeme for 'scan'
    elif lexer.value == 'get':
        Scan()
    #while begins with while, check current lexeme for 'while'
    elif lexer.value == 'while':
        _while()
    else:
        error('<Compound> | <Assign> | <If> |  <Return> | <Print> | <Scan> | <While>')
        lexer._compute()

#R16. <Compound> ::= {  <Statement List>  }
def compound():
    print('<Compound> ::= {  <Statement List>  }', file = outputFileHandle)
    
    if lexer.value == '{':
        getNext()
        statementList()
        
        getNext() if lexer.value == '}' else error('}')
        
        
    else:
        error('{')

#R17. <Assign> ::=   <IDENTIFIER> = <Expression> ;
def assign():
    print('<Assign> ::=   <IDENTIFIER> = <Expression> ;', file = outputFileHandle)
    
    if lexer._token() == 'IDENTIFIER':
        getNext()
    
        if lexer.value == '=':
            getNext()
            expression()
        
            getNext() if lexer.value == ';' else error(';')
                
        else:
            error('=')
    
    else:
        error('<IDENTIFIER>')

#R18. <If> ::= if ( <Condition> ) <Statement> endif | if ( <Condition>  ) <Statement> else <Statement> endif
def _if():
    print('<If> ::= if ( <Condition> ) <Statement > <ifPrime>', file = outputFileHandle)
    
    if lexer.value == 'if':
        getNext()
        
        if lexer.value == '(':
            getNext()
            condition()
            
            if lexer.value == ')':
                getNext()
                statement()
                ifPrime()
            else:
                error(')')
        
        else:
            error('(')
    
    else:
        error('if')

# <ifPrime> ::= endif | else <Statement> endif
def ifPrime():
    print('<ifPrime> ::= endif | else <Statement> endif', file = outputFileHandle)
    
    if lexer.value == 'endif':
        getNext()
    elif lexer.value == 'else':
        getNext()
        statement()
        getNext() if lexer.value == 'endif' else error('endif')
    else:
        error('endif | else')
        


#R.19 <Return> ::=  return ; |  return <Expression> ;
def _return():
    print('<Return> ::=  return ; |  return <Expression> ;', file = outputFileHandle)
   
    #condition 1:   return ;  
    if peek_next == ';':
        
        if lexer.value == 'return':
            getNext()   
        
            getNext() if lexer.value == ';' else error(';')
        
        else:
            error('return')
    
    #condition 2:   return <Expression> ;
    else:
        if lexer.value == 'return':
            getNext()
            # print('\nIM IN OF EXPRESSION()\n')
            expression()
            # print('\nIM OUT OF EXPRESSION()\n')
            getNext() if lexer.value == ';' else error(';')
            
        else:
            error('return')
        

#R20. <Print> ::=   put ( <Expression>);
def Print():
    print('<Print> ::=   put ( <Expression>);', file = outputFileHandle)
    
    if lexer.value == 'put':
        getNext()
        
        if lexer.value == '(':
            getNext()
            expression()
        
            if lexer.value == ')':
                getNext()
                    
                getNext() if lexer.value == ';' else error(';')
                
            else:
                error(')')
        
        else:
            error('<Expression>')
    
    else:
        error('print')

#R21. <Scan> ::= get ( <IDs> );
def Scan():
    print('<Scan> ::= get ( <IDs> );', file = outputFileHandle)
    
    if lexer.value == 'get':
        getNext()
        
        if lexer.value == '(':
            getNext()
            ids()
            
            if lexer.value == ')':
                getNext()
                
                getNext() if lexer.value == ';' else error(';')
                
            else:
                error(')')
            
        else:
            error('(')
    
    else:
        error('get')

#R22. <While> ::= while ( <Condition>  )  <Statement>
def _while():
    print('<While> ::= while ( <Condition>  )  <Statement>', file = outputFileHandle)
    
    if lexer.value == 'while':
        getNext()
        
        if lexer.value == '(':
            getNext()
            condition()
            
            if lexer.value == ')':
                getNext()
                statement()
            else:
                error(')')
        
        else:
            error('(')
        
    else:
        error('while')

#R23. <Condition> ::= <Expression> <Relop> <Expression>
def condition():
    print('<Condition> ::= <Expression> <Relop> <Expression>', file = outputFileHandle)
    
    expression()
    relop()
    expression()

#R24. <Relop> ::=   == |  !=  |   >   | <   |  <=   | =>
def relop():
    print('<Relop> ::=   == |  !=  |   >   | <   |  <=   | =>', file = outputFileHandle)
    
    if lexer.value == '==' or lexer.value == '!=' or lexer.value == '>' or lexer.value == '<' or lexer.value == '<=' or lexer.value == '=>':
        getNext()
    else:
        error('== |  !=  |   >   | <   |  <=   | =>') 

#R25. <Expression> ::= <Term> <ExpressionPrime>
def expression():
    print('<Expression> ::= <Term> <ExpressionPrime>', file = outputFileHandle)
    
    term()
    expressionPrime()

# <ExpressionPrime> ::= + <Term> <ExpressionPrime> | - <Term> <ExpressionPrime> | <empty>
def expressionPrime():
    print('<ExpressionPrime> ::= + <Term> <ExpressionPrime> | - <Term> <ExpressionPrime> | <empty>', file = outputFileHandle)
    
    if lexer.value == '+' or lexer.value == '-':
        getNext()
        term()
        expressionPrime()
    elif lexer._token() == 'unknown':
        error('+, -, <empty>')    
    else:
        empty()


#R26. <Term> ::= <Factor> <TermPrime>
def term():
    print('<Term> ::= <Factor> <TermPrime>', file = outputFileHandle)
    
    factor()
    termPrime()

# <TermPrime> ::= * <Factor> <TermPrime> | / <Factor> <TermPrime> | <empty>
def termPrime():
    print('<TermPrime> ::= * <Factor> <TermPrime> | / <Factor> <TermPrime> | <empty>', file = outputFileHandle)
    
    if lexer.value == '*' or lexer.value == '/':
        getNext()
        factor()
        termPrime()
    elif lexer._token() == 'unknown':
        error('*, /, <empty>')    
    else:
        empty()    



#R27. <Factor> ::= - <Primary> | <Primary>
def factor():
    print('<Factor> ::= - <Primary> | <Primary>', file = outputFileHandle)
    
    if lexer._token() == '-':
        getNext()
        primary()
    else:
        primary()
        
#R28. <Primary> ::= <IDENTIFIER> | <INTEGER> | <IDENTIFIER> (<IDs>) | ( <Expression> ) | <REAL> | true | false
def primary():
    print('<Primary> ::= <IDENTIFIER> | <INTEGER> | <IDENTIFIER> (<IDs>) | ( <Expression> ) | <REAL> | true | false', file = outputFileHandle)

    if lexer._token() == 'IDENTIFIER':
        getNext()
        #must test if <IDENTIFIER> (<IDs>)
        if lexer.value == '(':
            getNext()
            ids()
            getNext() if lexer.value == ')' else error(')')

    #    <INTEGER>
    elif lexer._token() == 'INTEGER':
        getNext()
        
    #    ( <Expression> ) 
    elif lexer.value == '(':
        getNext()
        expression()
        getNext() if lexer.value == ')' else error(')')

    #     <REAL>        
    elif lexer._token() == 'REAL':
        getNext()
    #     true
    elif lexer.value == 'true':
        getNext()
    #     false
    elif lexer.value == 'false':
        getNext()
    
    #else does not meet primary requirements
    else:
        error('<IDENTIFIER> | <INTEGER> | <IDENTIFIER> (<IDs>) | ( <Expression> ) |  <REAL>  | true | false')
        

# <Empty> ::= ε
def empty():
    print('<Empty> ::= epsilon', file = outputFileHandle)

def open_file(user_file):
    try:
        with open(user_file) as test:          
            myinput = test.read()
        global outputFileHandle
        outputFileHandle = open('TestOutput.txt','w+')
        mylexer = Lexer(myinput, lexer.tokenq)
        mylexer.start()
        lexer._compute()
        printInfo() 
    except FileNotFoundError:
        print("File not found")


def main():
    lexer.main()
    user_file = input('Enter file you would like to open (type "quit" to exit): ')
    if user_file != 'quit':
        open_file(user_file)
    #user wants to quit    
    else:
        print('Ending program')
        sys.exit()
    while True: 
        #if the lexer has values to pass the SA will begin
        if lexer._token_output() != "END":  
                     
            #Syntax Analyser         
            rat21F()                                        #call Syntax Analyser
            getNext()                                       #get input
            
            #report to user if error or no error in syntax analysis
            print("Syntax Analysis complete")
            print('There were no errors') if _error else print('An error was found')
            
            break
if __name__ == '__main__':
    main()