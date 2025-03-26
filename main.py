import Analizador

# Código fuente de prueba
codigo_fuente = """
int suma(int a, int b);

void main() {
    int s = suma(3,4);
    print(s);
}

int suma(int a, int b) {
    int c = a + b;
    return c;
}
"""

# Análisis léxico
tokens = Analizador.identificar_tokens(codigo_fuente)
print("Tokens encontrados:")
for tipo, valor in tokens:
    print(f"{tipo}: {valor}")

print("\nTokens generados:", tokens)

# Análisis sintáctico
try:
    print("\nIniciando análisis sintáctico...")
    parser = Analizador.Parser(tokens)
    ast = parser.parsear()
    print("Análisis sintáctico completado sin errores.")

    # Imprimir la estructura del AST
    print("\nÁrbol AST generado:")
    print(ast.to_dict())

    # Exportar AST a JSON
    Analizador.exportar_ast(ast)
    print("Árbol AST exportado a 'ast.json'.")

    # Generación de código ensamblador
    print("\nGenerando código ensamblador...")
    ensamblador = ""
    for funcion in ast.funciones:
        ensamblador_funcion = parser.generar_ensamblador(funcion)
        if ensamblador_funcion:
            ensamblador += ensamblador_funcion + "\n"
        else:
            print("No se generó código ensamblador para la función.")

    print("\nCódigo ensamblador generado:")
    print(ensamblador)

except SyntaxError as e:
    print(f"\nError de sintaxis: {e}")
