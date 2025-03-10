import re
import json

# Definir patrones léxicos
patrones_token = {
    "KEYWORD": r"\b(if|else|while|for|return|int|float|void|print)\b",
    "IDENTIFIER": r"\b[a-zA-Z_][a-zA-Z0-9_]*\b",
    "NUMBER": r"\b\d+(\.\d+)?\b",
    "OPERATOR": r"[+\-*/=]",
    "RELATIONAL": r"(==|!=|>=|<=|>|<)",
    "LOGICAL": r"(&&|\|\||!)",
    "DELIMITER": r"[(),;{}]",
    "STRING": r'"[^"]*"',
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

class NodoAst:
    def to_dict(self):
        result = {"tipo": self.__class__.__name__}
        for key, value in self.__dict__.items():
            if isinstance(value, list):
                result[key] = [v.to_dict() if isinstance(v, NodoAst) else v for v in value]
            elif isinstance(value, NodoAst):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result

class NodoFuncion(NodoAst):
    def __init__(self, tipo, nombre, parametros, cuerpo):
        self.tipo = tipo
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo

class NodoParametro(NodoAst):
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre

class NodoAsignacion(NodoAst):
    def __init__(self, nombre, expresion):
        self.nombre = nombre
        self.expresion = expresion

class NodoOperacion(NodoAst):
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha

class NodoRetorno(NodoAst):
    def __init__(self, expresion):
        self.expresion = expresion

class NodoIdentificador(NodoAst):
    def __init__(self, nombre):
        self.nombre = nombre

class NodoNumero(NodoAst):
    def __init__(self, valor):
        self.valor = valor

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
        return self.funcion()

    def funcion(self):
        tipo = self.aceptar_token("KEYWORD")[1]
        nombre = self.aceptar_token("IDENTIFIER")[1]
        self.aceptar_token("DELIMITER")
        parametros = self.parametros()
        self.aceptar_token("DELIMITER")
        self.aceptar_token("DELIMITER")
        cuerpo = self.cuerpo()
        self.aceptar_token("DELIMITER")
        return NodoFuncion(tipo, nombre, parametros, cuerpo)

    def parametros(self):
        parametros = []
        if self.obtener_simbolo() and self.obtener_simbolo()[0] == "KEYWORD":
            tipo = self.aceptar_token("KEYWORD")[1]
            nombre = self.aceptar_token("IDENTIFIER")[1]
            parametros.append(NodoParametro(tipo, nombre))
            while self.obtener_simbolo() and self.obtener_simbolo()[1] == ",":
                self.aceptar_token("DELIMITER")
                tipo = self.aceptar_token("KEYWORD")[1]
                nombre = self.aceptar_token("IDENTIFIER")[1]
                parametros.append(NodoParametro(tipo, nombre))
        return parametros

    def cuerpo(self):
        cuerpo = []
        while self.obtener_simbolo() and self.obtener_simbolo()[1] != "}":
            simbolo_actual = self.obtener_simbolo()
            if simbolo_actual[0] == "KEYWORD":
                if simbolo_actual[1] == "return":
                    self.aceptar_token("KEYWORD")
                    expresion = self.evaluar_expresion()
                    self.aceptar_token("DELIMITER")
                    cuerpo.append(NodoRetorno(expresion))
                else:
                    cuerpo.append(self.asignacion())
            else:
                cuerpo.append(self.asignacion())
        return cuerpo

    def asignacion(self):
        nombre = self.aceptar_token("IDENTIFIER")[1]
        self.aceptar_token("OPERATOR")
        expresion = self.evaluar_expresion()
        self.aceptar_token("DELIMITER")
        return NodoAsignacion(nombre, expresion)

    def evaluar_expresion(self):
        izquierda = self.evaluar_componente()
        while self.obtener_simbolo() and self.obtener_simbolo()[0] == "OPERATOR":
            operador = self.aceptar_token("OPERATOR")[1]
            derecha = self.evaluar_componente()
            izquierda = NodoOperacion(izquierda, operador, derecha)
        return izquierda

    def evaluar_componente(self):
        simbolo_actual = self.obtener_simbolo()
        if simbolo_actual[0] == "NUMBER":
            return NodoNumero(self.aceptar_token("NUMBER")[1])
        elif simbolo_actual[0] == "IDENTIFIER":
            return NodoIdentificador(self.aceptar_token("IDENTIFIER")[1])
        raise SyntaxError(f"Error al analizar el componente: {simbolo_actual}")

# Función para exportar el AST a un archivo JSON
def exportar_ast(ast, filename="ast.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(ast.to_dict(), f, indent=4)
