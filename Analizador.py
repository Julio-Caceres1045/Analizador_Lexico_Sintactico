import re

# Definir patrones léxicos
patrones_token = {
    "KEYWORD": r"\b(if|else|while|for|return|int|float|void)\b",
    "IDENTIFIER": r"\b[a-zA-Z_][a-zA-Z0-9_]*\b",
    "NUMBER": r"\b\d+(\.\d+)?\b",
    "OPERATOR": r"[+\-*/=]",
    "RELATIONAL": r"(==|!=|>=|<=|>|<)",
    "LOGICAL": r"(&&|\|\||!)",
    "DELIMITER": r"[(),;{}]",
    "WHITESPACE": r"\s+",
}

def identificar_tokens(texto):
    patron_general = "|".join(f"(?P<{tipo}>{patron})" for tipo, patron in patrones_token.items())
    patron_regex = re.compile(patron_general)
    tokens_encontrados = []
    for match in patron_regex.finditer(texto):
        for tipo, valor in match.groupdict().items():
            if valor is not None and tipo != "WHITESPACE":
                tokens_encontrados.append((tipo, valor))
    return tokens_encontrados

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def obtener_simbolo(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def aceptar_token(self, tipo_esperado):
        simbolo_actual = self.obtener_simbolo()
        if simbolo_actual and simbolo_actual[0] == tipo_esperado:
            self.pos += 1
            return simbolo_actual
        raise SyntaxError(f'Error Sintáctico, se esperaba {tipo_esperado}, pero se encontró {simbolo_actual}')

    def parsear(self):
        self.funcion()

    def funcion(self):
        self.aceptar_token("KEYWORD")
        self.aceptar_token("IDENTIFIER")
        self.aceptar_token("DELIMITER")
        self.parametros()
        self.aceptar_token("DELIMITER")
        self.aceptar_token("DELIMITER")
        self.cuerpo()
        self.aceptar_token("DELIMITER")

    def parametros(self):
        if self.obtener_simbolo() and self.obtener_simbolo()[0] == "KEYWORD":
            self.aceptar_token("KEYWORD")
            self.aceptar_token("IDENTIFIER")
            while self.obtener_simbolo() and self.obtener_simbolo()[1] == ",":
                self.aceptar_token("DELIMITER")
                self.aceptar_token("KEYWORD")
                self.aceptar_token("IDENTIFIER")

    def cuerpo(self):
        while self.obtener_simbolo() and self.obtener_simbolo()[1] != "}":
            if self.obtener_simbolo()[0] == "KEYWORD" and self.obtener_simbolo()[1] == "return":
                self.aceptar_token("KEYWORD")
                self.evaluar_expresion()
                self.aceptar_token("DELIMITER")
            elif self.obtener_simbolo()[0] == "KEYWORD" and self.obtener_simbolo()[1] == "if":
                self.aceptar_token("KEYWORD")
                self.aceptar_token("DELIMITER")  # (
                self.evaluar_condicion()
                self.aceptar_token("DELIMITER")  # )
                self.aceptar_token("DELIMITER")  # {
                self.cuerpo()
                self.aceptar_token("DELIMITER")  # }
            elif self.obtener_simbolo()[0] == "KEYWORD" and self.obtener_simbolo()[1] == "for":
                self.aceptar_token("KEYWORD")
                self.aceptar_token("DELIMITER")  # (
                self.asignacion()
                self.evaluar_condicion()
                self.aceptar_token("DELIMITER")
                self.evaluar_expresion()
                self.aceptar_token("DELIMITER")  # )
                self.aceptar_token("DELIMITER")  # {
                self.cuerpo()
                self.aceptar_token("DELIMITER")  # }
            else:
                self.asignacion()

    def asignacion(self):
        self.aceptar_token("KEYWORD")
        self.aceptar_token("IDENTIFIER")
        self.aceptar_token("OPERATOR")
        self.evaluar_expresion()
        self.aceptar_token("DELIMITER")

    def evaluar_expresion(self):
        self.evaluar_segmento()
        while self.verificar_simbolo("+-"):
            self.aceptar_token("OPERATOR")
            self.evaluar_segmento()

    def evaluar_segmento(self):
        self.evaluar_componente()
        while self.verificar_simbolo("*/"):
            self.aceptar_token("OPERATOR")
            self.evaluar_componente()

    def evaluar_componente(self):
        simbolo_actual = self.obtener_simbolo()
        if simbolo_actual[0] in ["NUMBER", "IDENTIFIER"]:
            self.aceptar_token(simbolo_actual[0])
        elif simbolo_actual[1] == "(":
            self.aceptar_token("DELIMITER")
            self.evaluar_expresion()
            self.aceptar_token("DELIMITER")
        else:
            raise SyntaxError(f"Error al analizar el componente: {simbolo_actual}")

    def evaluar_condicion(self):
        self.evaluar_expresion()
        while self.verificar_simbolo_relacional():
            self.aceptar_token("RELATIONAL")
            self.evaluar_expresion()
        while self.verificar_simbolo_logico():
            self.aceptar_token("LOGICAL")
            self.evaluar_expresion()

    def verificar_simbolo(self, operadores):
        return self.obtener_simbolo() and self.obtener_simbolo()[1] in operadores

    def verificar_simbolo_relacional(self):
        return self.obtener_simbolo() and self.obtener_simbolo()[0] == "RELATIONAL"

    def verificar_simbolo_logico(self):
        return self.obtener_simbolo() and self.obtener_simbolo()[0] == "LOGICAL"
     