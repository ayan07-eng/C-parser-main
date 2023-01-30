# C-parser

In this project, I developed concise context-free grammar for the C language. Given the C
program, the parser will try to check if the program follows the rules or not. In other words, it
checks for the syntactic correctness of the given C program. I used Lark parser in Python
to tokenise and parse the given code. The lark parser reads the grammar in EBNF (Extended
Backus-Naur Form) and provides us with the freedom to choose from a varied range of
parsing algorithms like CYK, Earley, LALR and so on to parse the code and generate its
respective parse-tree / Abstract Syntax Tree (AST).

Context-free grammar (also called phrase structure grammar) is a set of rules or productions,
each expressing how symbols of the language can be grouped and ordered together. It is
equivalent to Backus-Naur Form, or BNF. Context-free rules can be hierarchically embedded
so that we can combine the previous rules with others. There are two types of symbols in any
context-free grammar of any language. These are terminals and non-terminals. The symbols
correspond to words in the language. Non-terminals express abstraction over these terminals.
