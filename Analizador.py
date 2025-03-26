import re
import json

# Definir patrones léxicos
patrones_token = {
    "KEYWORD": r"\b(if|else|while|for|return|int|float|void|print)\b",
    "IDENTIFIER": r"\b[a-zA-Z_][a-zA-Z0-9_]*\b",
    "NUMBER": r"\b\d+(\.\d+)?\b",
    "OPERATOR": r"[+\-*/]",
    "EQUAL": r"=",
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

class NodoPrograma(NodoAst):
    def __init__(self, funciones):
        self.funciones = funciones

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

class NodoRetorno(NodoAst):
    def __init__(self, expresion):
        self.expresion = expresion

class NodoOperacion(NodoAst):
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha

class NodoIdentificador(NodoAst):
    def __init__(self, nombre):
        self.nombre = nombre

class NodoNumero(NodoAst):
    def __init__(self, valor):
        self.valor = valor

class NodoDeclaracion(NodoAst):
    def __init__(self, tipo, nombre, expresion=None):
        self.tipo = tipo
        self.nombre = nombre
        self.expresion = expresion

class NodoLlamadaFuncion(NodoAst):
    def __init__(self, nombre, argumentos):
        self.nombre = nombre
        self.argumentos = argumentos

class NodoPrint(NodoAst):
    def __init__(self, expresion):
        self.expresion = expresion

class NodoIf(NodoAst):
    def __init__(self, condicion, cuerpo_if, cuerpo_else=None):
        self.condicion = condicion
        self.cuerpo_if = cuerpo_if
        self.cuerpo_else = cuerpo_else

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
        funciones = []
        while self.obtener_simbolo():
            funciones.append(self.funcion())
        return NodoPrograma(funciones)
    
    def declaracion_variable(self):
        # Se espera el tipo de la variable (KEYWORD)
        tipo = self.aceptar_token("KEYWORD")[1]
        # Se espera el nombre de la variable (IDENTIFIER)
        nombre = self.aceptar_token("IDENTIFIER")[1]
        
        # La asignación es opcional, pero en el ejemplo se usa '='
        expresion = None
        if self.obtener_simbolo() and self.obtener_simbolo()[0] == "EQUAL":
            self.aceptar_token("EQUAL")
            expresion = self.expresion()
        
        # Se espera un delimitador ';'
        self.aceptar_token("DELIMITER")
        return NodoDeclaracion(tipo, nombre, expresion)


    def parametros(self):
        parametros = []
        while self.obtener_simbolo() and self.obtener_simbolo()[0] == "KEYWORD":
            # Primero, esperamos un tipo (KEYWORD)
            tipo = self.aceptar_token("KEYWORD")[1]
            
            # Luego, esperamos un identificador para el nombre del parámetro
            if self.obtener_simbolo() and self.obtener_simbolo()[0] == "IDENTIFIER":
                nombre = self.aceptar_token("IDENTIFIER")[1]
                parametros.append(NodoParametro(tipo, nombre))
            else:
                raise SyntaxError(f"Error de sintaxis, se esperaba IDENTIFIER, pero se encontró {self.obtener_simbolo()}")
            
            # Si hay más parámetros, deben estar separados por comas
            while self.obtener_simbolo() and self.obtener_simbolo()[1] == ",":
                self.aceptar_token("DELIMITER")  # Consume la coma ','
                
                # Después de la coma, esperamos otro tipo (KEYWORD) y su identificador
                if self.obtener_simbolo() and self.obtener_simbolo()[0] == "KEYWORD":
                    tipo = self.aceptar_token("KEYWORD")[1]
                    if self.obtener_simbolo() and self.obtener_simbolo()[0] == "IDENTIFIER":
                        nombre = self.aceptar_token("IDENTIFIER")[1]
                        parametros.append(NodoParametro(tipo, nombre))
                    else:
                        raise SyntaxError(f"Error de sintaxis, se esperaba IDENTIFIER después de ',' pero se encontró {self.obtener_simbolo()}")
                else:
                    raise SyntaxError(f"Error de sintaxis, se esperaba KEYWORD después de ',' pero se encontró {self.obtener_simbolo()}")
        
        return parametros

        
    def funcion(self):
        # Se espera el tipo de retorno de la función, como 'int', 'void', etc.
        tipo = self.aceptar_token("KEYWORD")[1]
        
        # Se espera el nombre de la función (un IDENTIFIER)
        nombre = self.aceptar_token("IDENTIFIER")[1]
        
        self.aceptar_token("DELIMITER")  # Consume el '('

        # Procesa los parámetros de la función
        parametros = self.parametros()
        
        self.aceptar_token("DELIMITER")  # Consume el ')'
        
        siguiente = self.obtener_simbolo()  # Verifica si el siguiente es ';' o '{'
        
        # **Aquí está el cambio: si encuentra ';', es una declaración de función**
        if siguiente and siguiente[1] == ";":
            self.aceptar_token("DELIMITER")  # Consume el ';'
            return NodoFuncion(tipo, nombre, parametros, [])  # Función sin cuerpo

        self.aceptar_token("DELIMITER")  # Consume el '{'
        
        # Procesa el cuerpo de la función
        cuerpo = self.cuerpo()
        
        self.aceptar_token("DELIMITER")  # Consume el '}'
        
        return NodoFuncion(tipo, nombre, parametros, cuerpo)

    def cuerpo(self):
        cuerpo = []
        while self.obtener_simbolo() and self.obtener_simbolo()[1] != "}":
            simbolo_actual = self.obtener_simbolo()
            if simbolo_actual[0] == "KEYWORD":
                if simbolo_actual[1] == "return":
                    cuerpo.append(self.retorno())
                elif simbolo_actual[1] in ["int", "float"]:
                    cuerpo.append(self.declaracion_variable())
                elif simbolo_actual[1] == "print":  # Nuevo caso para print
                    cuerpo.append(self.imprimir())
                elif simbolo_actual[1] == "if":  # Nuevo caso para if
                    cuerpo.append(self.if_else())
                else:
                    raise SyntaxError(f"Error inesperado en el cuerpo: {simbolo_actual}")
            elif simbolo_actual[0] == "IDENTIFIER":
                cuerpo.append(self.asignacion())
            else:
                raise SyntaxError(f"Error inesperado en el cuerpo: {simbolo_actual}")
        return cuerpo

    def if_else(self):
        self.aceptar_token("KEYWORD")  # Consume "if"
        self.aceptar_token("DELIMITER")  # Consume "("
        condicion = self.expresion()  # Procesa la condición
        self.aceptar_token("DELIMITER")  # Consume ")"
        self.aceptar_token("DELIMITER")  # Consume "{"
        
        cuerpo_if = self.cuerpo()  # Procesa el cuerpo del if
        
        cuerpo_else = None
        if self.obtener_simbolo() and self.obtener_simbolo()[1] == "else":
            self.aceptar_token("KEYWORD")  # Consume "else"
            self.aceptar_token("DELIMITER")  # Consume "{"
            cuerpo_else = self.cuerpo()  # Procesa el cuerpo del else

        self.aceptar_token("DELIMITER")  # Consume "}"
        
        return NodoIf(condicion, cuerpo_if, cuerpo_else)

    # Generación de código ensamblador
    def generar_ensamblador(self, funcion):
        """Genera código ensamblador para la función dada"""
        ensamblador = ""
        
        # Generar código ensamblador para los parámetros de la función
        for parametro in funcion.parametros:
            ensamblador += f"    ; Parámetro {parametro.nombre} de tipo {parametro.tipo}\n"
        
        # Generar código ensamblador para las instrucciones en el cuerpo de la función
        for instruccion in funcion.cuerpo:
            if isinstance(instruccion, NodoAsignacion):
                ensamblador += self.generar_ensamblador_asignacion(instruccion)
            elif isinstance(instruccion, NodoRetorno):
                ensamblador += self.generar_ensamblador_retorno(instruccion)
            elif isinstance(instruccion, NodoPrint):
                ensamblador += self.generar_ensamblador_print(instruccion)
        
        return ensamblador

    def generar_ensamblador_asignacion(self, asignacion):
        """Genera código ensamblador para una asignación"""
        return f"    MOV {asignacion.nombre}, {self.generar_ensamblador_expresion(asignacion.expresion)}\n"
    
    def generar_ensamblador_retorno(self, retorno):
        """Genera código ensamblador para un retorno"""
        return f"    RET {self.generar_ensamblador_expresion(retorno.expresion)}\n"
    
    def generar_ensamblador_print(self, print_instr):
        """Genera código ensamblador para una instrucción de impresión"""
        return f"    PRINT {self.generar_ensamblador_expresion(print_instr.expresion)}\n"
    
    def generar_ensamblador_expresion(self, expresion):
        """Genera código ensamblador para una expresión"""
        if isinstance(expresion, NodoNumero):
            return expresion.valor
        elif isinstance(expresion, NodoIdentificador):
            return expresion.nombre
        elif isinstance(expresion, NodoOperacion):
            izq = self.generar_ensamblador_expresion(expresion.izquierda)
            der = self.generar_ensamblador_expresion(expresion.derecha)
            return f"({izq} {expresion.operador} {der})"
        return ""

    def asignacion(self):
        nombre = self.aceptar_token("IDENTIFIER")[1]
        self.aceptar_token("EQUAL")
        expresion = self.expresion()
        self.aceptar_token("DELIMITER")
        return NodoAsignacion(nombre, expresion)
    
    def retorno(self):
        self.aceptar_token("KEYWORD")
        expresion = self.expresion()
        self.aceptar_token("DELIMITER")
        return NodoRetorno(expresion)
    
    def expresion(self):
        izquierda = self.termino()
        while self.obtener_simbolo() and self.obtener_simbolo()[0] == "OPERATOR":
            operador = self.aceptar_token("OPERATOR")[1]
            derecha = self.termino()
            izquierda = NodoOperacion(izquierda, operador, derecha)
        return izquierda
    
    def termino(self):
        simbolo_actual = self.obtener_simbolo()

        if simbolo_actual[0] == "NUMBER":
            return NodoNumero(self.aceptar_token("NUMBER")[1])

        elif simbolo_actual[0] == "IDENTIFIER":
            nombre = self.aceptar_token("IDENTIFIER")[1]

            # Si el siguiente símbolo es '(', es una llamada a función
            if self.obtener_simbolo() and self.obtener_simbolo()[1] == "(":
                self.aceptar_token("DELIMITER")  # Consume '('
                argumentos = self.argumentos()   # Procesar los argumentos
                self.aceptar_token("DELIMITER")  # Consume ')'
                return NodoLlamadaFuncion(nombre, argumentos)
            
            return NodoIdentificador(nombre)  # Si no es función, es solo un identificador

        raise SyntaxError(f"Error al analizar el término: {simbolo_actual}")
    
    def argumentos(self):
        argumentos = []
        
        # Si el siguiente token es ')', la función no tiene argumentos
        if self.obtener_simbolo() and self.obtener_simbolo()[1] == ")":
            return argumentos

        # Procesar el primer argumento
        argumentos.append(self.expresion())

        # Procesar argumentos adicionales separados por ','
        while self.obtener_simbolo() and self.obtener_simbolo()[1] == ",":
            self.aceptar_token("DELIMITER")  # Consume ','
            argumentos.append(self.expresion())

        return argumentos
    
    def imprimir(self):
        self.aceptar_token("KEYWORD")  # Consume 'print'
        self.aceptar_token("DELIMITER")  # Consume '('
        expresion = self.expresion()  # Analiza la expresión dentro de print
        self.aceptar_token("DELIMITER")  # Consume ')'
        self.aceptar_token("DELIMITER")  # Consume ';'
        return NodoPrint(expresion)

# Función para exportar el AST a un archivo JSON
def exportar_ast(ast, filename="ast.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(ast.to_dict(), f, indent=4)
