from lark import Lark

main_grammar = r'''
preprocessor_hook: "%{$PREPROCESSOR" constant_expression "}%"

program: (external_declaration* | preprocessor_hook)

pragma: "_Pragma" "(" STRING_LITERAL ")" | "printf" "(" STRING_LITERAL ("," expression)* ")" ";" | "scanf" "(" STRING_LITERAL ("," "&" expression)* ")" ";"

?external_declaration: function_definition | declaration | ";" | pragma

function_definition: decl_specifier declarator block_statement

declaration: decl_specifier init_declarator_list ";"
    | decl_specifier ";"

init_declarator_list: init_declarator ("," init_declarator)*

init_declarator: declarator
    | declarator "=" initializer

initializer: assignment_expression
    | "{" initializer_list ","? "}" -> compound_initializer

initializer_list: initializer_item ("," initializer_item)*
initializer_item: designation? initializer
?designation: designator_list "="
?designator_list: designator designator_list | designator
designator: "[" constant_expression "]" -> index_member_reference
    | "." identifier_expr -> name_member_reference

declarator: STAR* direct_declarator

direct_declarator: identifier_expr
    | identifier_expr "[" assignment_expression? "]" -> array_declarator
    | identifier_expr? "(" param_list? ")" -> func_declarator

param_list: param_declaration ("," param_declaration)* ("," VARARGS)?

param_declaration: decl_specifier declarator
    | decl_specifier STAR* -> unnamed_param_declaration

// Use epsilon in child rules rather than make optional so we don't
// loose it from the tree
decl_specifier: storage_class_specifier type_qualifier type_specifier
storage_class_specifier: TYPEDEF | STATIC |
type_qualifier: CONST |

?type_specifier: struct_specifier | typedef_name

typedef_name: TYPEDEF_NAME
TYPEDEF_NAME.2: IDENT

?struct_specifier: struct_spec_reference | struct_spec_declaration
struct_spec_reference: "struct" identifier_expr
struct_spec_declaration: "struct" identifier_expr? "{" struct_declaration_list "}"

struct_declaration_list: struct_declaration+
struct_declaration: type_specifier struct_declarator_list? ";"

struct_declarator_list: struct_declarator ("," struct_declarator)*

?struct_declarator: declarator

type_name: type_specifier STAR*

// So the transformer can distinguish between block-level declarations
// and global
block_declaration: declaration
block_statement: "{" (statement | block_declaration)* "}"

?statement: block_statement | statement_no_block

?statement_no_block: labelled_statement
    | expression ";" -> expression_statement
    | "if" "(" expression ")" statement ["else" statement] -> if_statement
    | "switch" "(" expression ")" "{" switch_case_fragment* "}" -> switch_statement
    | "while" "(" expression ")" statement -> while_statement
    | "do" statement "while" "(" expression ")" ";" -> do_while_statement
    | "for" "(" expression? ";" expression? ";" expression? ")" statement -> for_statement
    | "goto" identifier_expr ";" -> goto_statement
    | "continue" ";" -> continue_statement
    | "break" ";" -> break_statement
    | "return" expression? ";" -> return_statement
    | "sync" ";" -> sync_statement
    | pragma

switch_case_fragment: "case" constant_expression ":" switch_case_body?
    | "default" ":" switch_case_body? -> switch_default_fragment
?switch_case_body: block_statement | statement_no_block+

?labelled_statement: identifier_expr ":" statement -> label_statement
//    | "case" constant_expression ":" statement -> case_statement
//    | "default" ":" statement -> default_statement

?expression: assignment_expression
    | expression "," assignment_expression

?constant_expression: conditional_expression

?assignment_expression: conditional_expression
    | unary_expression (ASSIGN | ASSIGN_OP) assignment_expression

?conditional_expression: logical_or_expression ["?" expression ":" conditional_expression]

?logical_or_expression: logical_and_expression
    | logical_or_expression LOG_OR_OP logical_and_expression -> binop_expr

?logical_and_expression: inclusive_or_expression
    | logical_and_expression LOG_AND_OP inclusive_or_expression -> binop_expr

?inclusive_or_expression: exclusive_or_expression
    | inclusive_or_expression OR_OP exclusive_or_expression -> binop_expr

?exclusive_or_expression: and_expression
    | exclusive_or_expression XOR_OP and_expression -> binop_expr

?and_expression: equality_expression
    | and_expression AND_OP equality_expression -> binop_expr

?equality_expression: relational_expression
    | equality_expression EQ relational_expression -> binop_expr
    | equality_expression NEQ relational_expression -> binop_expr

?relational_expression: shift_expression
    | relational_expression REL_OP shift_expression -> binop_expr

?shift_expression: additive_expression
    | shift_expression SHIFT_OP additive_expression -> binop_expr

?additive_expression: multiplicative_expression
    | additive_expression ADD_OP multiplicative_expression -> binop_expr

?multiplicative_expression: cast_expression
    | multiplicative_expression (STAR | MUL_OP) cast_expression -> binop_expr

?cast_expression: "(" type_name ")" cast_expression
    | unary_expression

?unary_expression: postfix_expression
    | INCREMENT_OP unary_expression -> pre_increment_expr
    | UNARY_OP cast_expression
    | "sizeof" ( "(" type_name ")" | unary_expression ) -> sizeof_expr

?postfix_expression: primary_expression
    | postfix_expression "[" expression "]" -> array_subscript_expr
    | postfix_expression "(" (assignment_expression ("," assignment_expression)*)? ")" -> function_call_expr
    | postfix_expression (DOT | ARROW) identifier_expr -> member_access_expr
    | postfix_expression INCREMENT_OP -> post_increment_expr

?primary_expression: identifier_expr
    | INT_CONSTANT -> int_literal
    | STRING_LITERAL+ -> string_literal
    | "(" expression ")"


identifier_expr: IDENT

VARARGS: "..."

TYPEDEF: "typedef"
STATIC: "static"
CONST: "const"

STAR.0: "*" 
EQ.2: "=="
ASSIGN: "="
ASSIGN_OP: ASSIGN | "*=" | "/=" | "%=" | "+=" | "-=" | "<<=" | ">>=" | "&=" | "^=" | "|="

LOG_OR_OP: "||"
LOG_AND_OP: "&&"
OR_OP: "|"
XOR_OP: "^"
AND_OP: "&"
NEQ: "!="
REL_OP: "<=" | ">=" | "<" | ">"
SHIFT_OP: "<<" | ">>"
ADD_OP: "+" | "-"
MUL_OP: "*" | "/" | "%"
UNARY_OP: "&" | "*" | "+" | "-" | "~" | "!"
INCREMENT_OP: "++" | "--"
DOT: "."
ARROW: "->"

INT_CONSTANT: DEC_CONSTANT | OCT_CONSTANT | HEX_CONSTANT | BIN_CONSTANT | CHAR_CONSTANT | "0"
DEC_CONSTANT: NON_ZERO_DIGIT DIGIT*
OCT_CONSTANT: "0" ("0".."7")+
HEX_CONSTANT: "0" ("x" | "X") ("0".."9" | "A".."F" | "a".."f")+
BIN_CONSTANT: "0" ("b" | "B") ("0" | "1")+

SINGLE_CHAR: (/(<?!\\)./ | "\\" /([abefnrtv\\'"?]|x[\da-fA-F]+|[0-7]{1,3})/ )

CHAR_CONSTANT: "'" SINGLE_CHAR "'" | "'" LETTER "'"

%import common.ESCAPED_STRING
STRING_LITERAL: ESCAPED_STRING

DIGIT: "0" .. "9"

NON_ZERO_DIGIT: "1" .. "9"

LETTER: "a".."z" | "A".."Z"
%import common.SIGNED_NUMBER
ID_START: LETTER | "_"

IDENT: ID_START (ID_START | DIGIT)*

WHITESPACE: " " | "\t" | "\f" | "\n"
%ignore WHITESPACE+

COMMENT: "//" /[^\n]/* | "/*" /(\S|\s)*?/ "*/"
%ignore COMMENT
'''

initial_grammar = r'''start : header_files
preprocessor_commands : "#include" | definition
definition : def (string)+ (header_files)*
def : "#define" | "#undef" | "#ifdef" | "#ifndef" | "#if" | "#else" | "#elif" | "#endif" | "#error" | "#pragma"
header_files : preprocessor_commands (file_names)? (header_files)*
file_names : "<stdio.h>" | "<math.h>" | "<conio.h>" | "<stdlib.h>" | "<string.h>" | "<ctype.h>" | "<time.h>" | "<float.h>" | "<limits.h>" | "<wctype.h>"

%import common.SIGNED_NUMBER
letter : "a".."z" | "A".."Z"
char : letter | SIGNED_NUMBER | "}" | ")" | "]"
string : /[a-zA-Z0-9_.-]{2,}/ | (char)*

WHITESPACE: " " | "\t" | "\f" | "\n"
%ignore WHITESPACE+

COMMENT: "//" /[^\n]/* | "/" /(\S|\s)?/ "*/"
%ignore COMMENT 
'''
par = Lark(grammar=initial_grammar, parser='earley', start='start')
parser = Lark(grammar=main_grammar, parser="lalr", start="program")
code = r'''
#include<stdio.h>
#include<math.h>
#define PI 3.14
void main(){
float a,b,c;
scanf("%f%f%f",&a,&b,&c);
printf("%f",d);
return;
}
'''
if (code.find('void') == -1):
    i_void = 10000
else:
    i_void = code.find('void')
if (code.find('int') == -1):
    i_int = 10000
else:
    i_int = code.find('int')
if (code.find('static') == -1):
    i_static = 10000
else:
    i_static = code.find('static')
if (code.find('long') == -1):
    i_long = 10000
else:
    i_long = code.find('long')
if (code.find('float') == -1):
    i_float = 10000
else:
    i_float = code.find('float')
if (code.find('double') == -1):
    i_double = 10000
else:
    i_double = code.find('double')
if (code.find('string') == -1):
    i_string = 10000
else:
    i_string = code.find('string')
if (code.find('bool') == -1):
    i_bool = 10000
else:
    i_bool = code.find('bool')
idx = [i_void, i_bool, i_int, i_static, i_long, i_float, i_double, i_string]
idx.sort()
min = idx[0]
code1 = code[:min]
code2 = code[min:]


print(par.parse(code1).pretty())
print(parser.parse(code2).pretty())

