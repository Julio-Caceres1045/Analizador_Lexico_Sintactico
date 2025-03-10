import Analizador

# Código fuente de prueba
codigo_fuente = """
int suma(int a, int b) {
    return a + b;
}

"""

# Análisis léxico
tokens = Analizador.identificar_tokens(codigo_fuente)
print("Tokens encontrados:")
for tipo, valor in tokens:
    print(f"{tipo}: {valor}")

# Análisis sintáctico
try:
    print("\nIniciando análisis sintáctico...")
    parser = Analizador.Parser(tokens)
    ast = parser.parsear()
    print("Análisis sintáctico completado sin errores.")

    # Imprimir el AST antes de exportarlo
    print("\nÁrbol AST generado:")
    print(ast.to_dict())

    # Exportar AST a JSON
    Analizador.exportar_ast(ast)
    print("Árbol AST exportado a 'ast.json'.")

except SyntaxError as e:
    print(e)
