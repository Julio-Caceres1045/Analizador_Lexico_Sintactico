from analisis_lexico import identificar_tokens

class AnalizadorSemantico:
    def __init__(self):
        self.variables = {}
        self.funciones = {}

    def analizar(self, tokens):
        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token[0] == "KEYWORD":
                if token[1] == "int" or token[1] == "float":
                    # Declaración de variable
                    tipo = token[1]
                    i += 1  # Avanzamos para obtener el identificador
                    if tokens[i][0] == "IDENTIFIER":
                        var_name = tokens[i][1]
                        if var_name in self.variables:
                            raise Exception(f"Error: Variable '{var_name}' ya declarada.")
                        self.variables[var_name] = tipo
                    i += 1  # Avanzamos al siguiente token

                elif token[1] == "return":
                    # Verificar retorno (se asume que el valor debe ser de tipo correcto)
                    i += 1  # Avanzamos para obtener el valor del retorno
                    if tokens[i][0] == "IDENTIFIER":
                        var_name = tokens[i][1]
                        if var_name not in self.variables:
                            raise Exception(f"Error: Variable '{var_name}' no declarada para retorno.")
                    i += 1

                elif token[1] == "void":
                    # Declaración de función (por ejemplo, main())
                    i += 1  # Avanzamos para obtener el nombre de la función
                    if tokens[i][0] == "IDENTIFIER":
                        func_name = tokens[i][1]
                        if func_name in self.funciones:
                            raise Exception(f"Error: Función '{func_name}' ya declarada.")
                        self.funciones[func_name] = "void"
                    i += 1

                elif token[1] == "print":
                    # Verificar que 'print' tiene un argumento válido
                    i += 1
                    if tokens[i][0] == "IDENTIFIER":
                        var_name = tokens[i][1]
                        if var_name not in self.variables:
                            raise Exception(f"Error: Variable '{var_name}' no declarada en la llamada a 'print'.")
                    i += 1

            # Procesamos operadores y otros elementos según sea necesario
            i += 1