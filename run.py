import sys
import argparse
import numbers
from os.path import exists

variables = {}
arrays = {}

def get_array_identifier(token):
    if "(" in token  and  ")" in token:
        start = token.find("(")
        end = token.find(")")
        if start > 0  and  end == len(token)-1:
            # If last two characters are (), return just the name
            if token[len(token)-2:] == "()":
                return token[0:start]
            return token[0:start], int(token[start+1:end])
    return False

def get_token_value(token, substrings):
    if token[0:7] == "#STRING":
        token = substrings[int(token[8:])-1]
    try:
        token = int(token)
    except ValueError:
        try:
            token = float(token)
        except ValueError:
            pass
    return token

def get_left_right(tokens, index, substrings):
    if index == 1  or  index >= len(tokens)-1:
        print_error(200,"Invalid token index for addition")
    left = get_token_value(tokens[index-1], substrings)
    right = get_token_value(tokens[index+1], substrings)
    return left, right

def remove_adjacent_tokens(tokens, index):
    if index == 0  or  index >= len(tokens)-1:
        print_error(201,"Invalid token index for removal")
    del tokens[index+1]
    del tokens[index-1]
    return tokens

def perform_math(tokens, substrings):
    for index, token in enumerate(tokens):
        if token == "+":
            left, right = get_left_right(tokens, index, substrings)
            tokens[index] = str(left + right)
            tokens = remove_adjacent_tokens(tokens, index)
        elif token == "-":
            left, right = get_left_right(tokens, index, substrings)
            tokens[index] = str(left - right)
            tokens = remove_adjacent_tokens(tokens, index)
        elif token == "*":
            left, right = get_left_right(tokens, index, substrings)
            tokens[index] = str(left * right)
            tokens = remove_adjacent_tokens(tokens, index)
        elif token == "/":
            left, right = get_left_right(tokens, index, substrings)
            tokens[index] = str(left / right)
            tokens = remove_adjacent_tokens(tokens, index)
    return tokens

def tokenize_statement(statement):
    tokens = []
    # For every substring, extract it into a temporary variable
    substrings = []
    while statement.find('"') >= 0:
        start = statement.find('"')
        if statement[start+1:].find('"') == -1:
            return {"code":1,"error":"Unmatched quote"}
        end = statement[start+1:].find('"')
        substrings.append(statement[start+1:start+end+1])
        statement = statement[0:start] + "#STRING-" + str(len(substrings)) + statement[start+end+2:]
    statement = " ".join(statement.split())
    tokens = statement.split(" ")
    for var_name, var_value in variables.items():
        for i in range(0,len(tokens)):
            if tokens[i] == var_name:
                tokens[i] = var_value
    for i in range(1,len(tokens)):
        array_id = get_array_identifier(tokens[i])
        if array_id:
            if array_id[0] not in arrays:
                arrays[array_id[0]] = [0]
                arrays[array_id[0]][array_id[1]-1] = 0
            else:
                tokens[i] = arrays[array_id[0]][array_id[1]-1]
    tokens = perform_math(tokens, substrings)
    return {"code":0,"tokens":tokens,"substrings":substrings}

def print_error(code, error_statement):
    print( "ERROR " + str(code) + ": " + error_statement )
    sys.exit(1)

def execute_statement(statement):
    tokens = tokenize_statement(statement)
    if "code" not in tokens:
        print_error(100,"No code returned from tokenize")
    if tokens["code"] != 0:
        if( "error" not in tokens ):
            print_error(101,"Error code " + str(tokens.code) + " returned from tokenize with no error")
        print_error( tokens.code, tokens.error )
    if len(tokens["tokens"]) > 0:
        command = tokens["tokens"][0].upper()
        if command == "PRINT":
            cmd_print(tokens)
        elif command == "INPUT":
            result = input()
            if len(tokens["tokens"]) > 1:
                variables[tokens["tokens"][1]] = result
            #print(variables)
        elif len(tokens["tokens"]) > 1  and  tokens["tokens"][1] == "=":
            cmd_assign(tokens)
        elif command == "REM":
            do_nothing = True
        elif command == ""  and  len(tokens["tokens"]) == 1:
            do_nothing = True
        else:
            print_error(102,"Unknown command: " + tokens["tokens"][0])

def cmd_print(tokens):
    eol = True
    if tokens["tokens"][-1] == ";":
        del tokens["tokens"][-1]
        eol = False
    result = ""
    for token in tokens["tokens"]:
        if token in arrays:
            result += " ".join(map(str,arrays[token])) + " "
        elif isinstance(token, int) or isinstance(token, float):
            result += str(token) + " "
        elif token[0:7] == "#STRING":
            result += tokens["substrings"][int(token[8:])-1]
        elif token != "PRINT":
            result += token + " "
    if eol:
        print( result.rstrip() )
    else:
        print( result.rstrip(), end="" )

def cmd_assign(tokens):
    if len(tokens["tokens"]) < 3:
        print_error(103,"Not enough tokens for assignment")
    if tokens["tokens"][0] in variables:
        print_error(104,"Variable already exists: " + tokens["tokens"][0])
    array_id = get_array_identifier(tokens["tokens"][0])
    if array_id:
        # If array_id is an array, exit
        if not isinstance(array_id, tuple):
            array_name = array_id
            if array_name in arrays:
                print_error(105,"Array already exists: " + array_name)
            arrays[array_name] = []
            values = tokens["tokens"][2:]
            for value in values:
                value = get_token_value(value, tokens["substrings"])
                arrays[array_name].append(value)
        else:
            array_name = array_id[0]
            array_index = array_id[1] - 1
            if array_id[0] not in arrays:
                arrays[array_name] = []
            while array_index >= len(arrays[array_name]):
                arrays[array_name].append(0)
            arrays[array_name][array_index] = tokens["tokens"][2]
    if tokens["tokens"][2][0:7] == "#STRING":
        variables[tokens["tokens"][0]] = tokens["substrings"][int(tokens["tokens"][2][8:])-1]
    else:
        variables[tokens["tokens"][0]] = tokens["tokens"][2]

parser = argparse.ArgumentParser(description="Execute TREE commands.")
parser.add_argument("--code", help="Code to execute")
parser.add_argument("--file", help="Name of file containing code to execute")
args = parser.parse_args()

if("code" in args  and  args.code != None):
    execute_statement(args.code)
if("file" in args  and  args.file != None):
    if exists(args.file):
        f = open(args.file,"r")
        for line in f:
            execute_statement(line)

#execute_statement("PRINT \"HELLO, WORLD\"")