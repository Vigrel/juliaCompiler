from classes.Node import *
from classes.PrePro import Tokenizer


class Parser:
    tknz = Tokenizer("")

    @staticmethod
    def parseBlock() -> Node:
        children = []
        while Parser.tknz.next.type != "EOF":
            children.append(Parser.parseStatement())
        return Block(children)

    @staticmethod
    def parseStatement() -> Node:
        node = NoOp()
        while Parser.tknz.next.type not in ["LN", "EOF"]:
            if Parser.tknz.next.type == "IDENTIFIER":
                idtf = Parser.tknz.next.value
                if idtf == "println":
                    Parser.tknz.selectNext()
                    if Parser.tknz.next.type != "PARENO":
                        raise SyntaxError("'(' needed")
                    Parser.tknz.selectNext()
                    node = Print([Parser.parseRealExpression()])
                    if Parser.tknz.next.type != "PARENC":
                        raise SyntaxError("'(' was never closed")
                    Parser.tknz.selectNext()
                    continue

                if idtf == "readline":
                    Parser.tknz.selectNext()
                    if Parser.tknz.next.type != "PARENO":
                        raise SyntaxError("Missing (")
                    Parser.tknz.selectNext()
                    if Parser.tknz.next.type != "PARENC":
                        raise SyntaxError("'(' was never closed")
                    Parser.tknz.selectNext()
                    return ReadLn()

                if idtf == "while":
                    Parser.tknz.selectNext()
                    while_exp = Parser.parseRealExpression()
                    if Parser.tknz.next.type != "LN":
                        raise SyntaxError(f"ivalid syntax")
                    Parser.tknz.selectNext()
                    children = []
                    while Parser.tknz.next.value != "end":
                        children.append(Parser.parseStatement())
                        if Parser.tknz.next.type == "EOF":
                            raise SyntaxError(f"end not used")

                    Parser.tknz.selectNext()
                    node = While([while_exp, Block(children)])
                    continue

                if idtf == "if":
                    childs = []
                    Parser.tknz.selectNext()
                    childs.append(Parser.parseRealExpression())

                    if Parser.tknz.next.type != "LN":
                        raise SyntaxError(f"ivalid syntax")
                    Parser.tknz.selectNext()

                    children_if = []
                    while Parser.tknz.next.value not in ["else", "end"]:
                        children_if.append(Parser.parseStatement())
                        if Parser.tknz.next.type == "EOF":
                            raise SyntaxError(f"end not used")

                    childs.append(Block(children_if))
                    if Parser.tknz.next.value == "else":
                        Parser.tknz.selectNext()
                        if Parser.tknz.next.type != "LN":
                            raise SyntaxError(f"ivalid syntax")
                        Parser.tknz.selectNext()

                        children_else = []
                        while Parser.tknz.next.value != "end":
                            children_else.append(Parser.parseStatement())
                            if Parser.tknz.next.type == "EOF":
                                raise SyntaxError(f"end not used")
                        Parser.tknz.selectNext()
                        childs.append(Block(children_else))

                    node = If(childs)
                    continue

                Parser.tknz.selectNext()
                if Parser.tknz.next.type == "TYPE":
                    Parser.tknz.selectNext()
                    typ = Parser.tknz.next.value
                    Parser.tknz.selectNext()
                    if Parser.tknz.next.type == "EQUALS":
                        Parser.tknz.selectNext()
                        node = VarDec(
                            idtf, [Identifier(typ), Parser.parseRealExpression()]
                        )
                        continue
                    node = VarDec(idtf, [Identifier(typ)])
                    continue

                if Parser.tknz.next.type == "EQUALS":
                    Parser.tknz.selectNext()
                    node = Assignment(idtf, [Parser.parseRealExpression()])
                    continue

        Parser.tknz.selectNext()
        return node

    @staticmethod
    def parseRealExpression() -> Node:
        node = Parser.parseExpression()

        while Parser.tknz.next.type in ["EQUALSS", "GT", "LT"]:
            op = Parser.tknz.next.value
            Parser.tknz.selectNext()

            node = BinOp(
                op,
                [node, Parser.parseExpression()],
            )

        return node

    @staticmethod
    def parseExpression() -> Node:
        node = Parser.parseTerm()

        while Parser.tknz.next.type in ["PLUS", "MINUS", "OR", "CONC"]:
            op = Parser.tknz.next.value
            Parser.tknz.selectNext()

            if Parser.tknz.next.type in ["DIV", "MULT"]:
                raise SyntaxError(f"ivalid syntax - {op}{Parser.tknz.next.value}")

            node = BinOp(
                op,
                [node, Parser.parseTerm()],
            )

        return node

    @staticmethod
    def parseTerm() -> Node:
        node = Parser.parseFactor()

        while Parser.tknz.next.type in ["DIV", "MULT", "AND"]:
            op = Parser.tknz.next.value
            Parser.tknz.selectNext()

            if Parser.tknz.next.type in ["DIV", "MULT"]:
                raise SyntaxError(f"ivalid syntax - {op}{Parser.tknz.next.value}")

            node = BinOp(
                op,
                [node, Parser.parseFactor()],
            )

        return node

    @staticmethod
    def parseFactor() -> Node:
        tkn = Parser.tknz.next
        Parser.tknz.selectNext()

        if tkn.type == "STR":
            return StrVal(tkn.value)

        if tkn.type == "INT":
            return IntVal(tkn.value)

        if tkn.value == "readline":
            if Parser.tknz.next.type != "PARENO":
                raise SyntaxError("Missing (")
            Parser.tknz.selectNext()
            if Parser.tknz.next.type != "PARENC":
                raise SyntaxError("'(' was never closed")
            Parser.tknz.selectNext()
            return ReadLn()

        if tkn.type == "IDENTIFIER":
            return Identifier(tkn.value)

        if tkn.type in ["PLUS", "MINUS", "NOT"]:
            if Parser.tknz.next.type in ["DIV", "MULT"]:
                raise SyntaxError(
                    f"ivalid syntax - {tkn.value}{Parser.tknz.next.value}"
                )

            return UnOp(tkn.value, [Parser.parseFactor()])

        if tkn.type == "PARENO":
            node = Parser.parseRealExpression()
            if Parser.tknz.next.type == "PARENC":
                Parser.tknz.selectNext()
                return node
            raise SyntaxError("'(' was never closed")

    @staticmethod
    def run(code: str) -> any:
        Parser.tknz.__init__(code)
        return Parser.parseBlock().evaluate()
