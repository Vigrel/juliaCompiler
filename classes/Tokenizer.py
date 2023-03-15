from classes.Token import Token
from constants.grammar import INT, OPS


class Tokenizer:
    def __init__(self, source: str) -> None:
        self.source: str = source
        self.position: int = 0
        self.next: Token = self.selectNext()

    def selectNext(self) -> Token:
        for letter in self.source[self.position :]:
            if letter == " ":
                self.position += 1
                continue

            if letter in OPS.keys():
                self.next = Token(OPS[letter], letter)
                self.position += 1
                return self.next

            if letter in INT:
                num = ""
                while letter in INT:
                    num += letter
                    self.position += 1
                    if self.position == len(self.source):
                        break
                    letter = self.source[self.position]
                self.next = Token("INT", num)
                return self.next

            if letter == "(":
                self.next = Token("PARENO", letter)
                self.position += 1
                return self.next

            if letter == ")":
                self.next = Token("PARENC", letter)
                self.position += 1
                return self.next

            raise SyntaxError("invalid syntax")

        self.next = Token("EOF", "")
        return self.next
