from analisis_lexico import identificar_tokens
from analisis_sintactico import Parser, exportar_ast
from ensamblador import traducir_a_ensamblador_emu8086
from ensamblador import generar_codigo_lenguaje_maquina


# Código fuente de prueba
codigo_fuente = """
int suma(int a, int b) {
    int c = a + b;
    return c;
}

void main() {
    int s = suma(3, 4);
    print(s);
}
"""

# Análisis léxico
tokens = identificar_tokens(codigo_fuente)
print("Tokens encontrados:")
for tipo, valor in tokens:
    print(f"{tipo}: {valor}")

print("\nTokens generados:", tokens)

# Análisis sintáctico
try:
    print("\nIniciando análisis sintáctico...")
    parser = Parser(tokens)
    ast = parser.parsear()
    print("Análisis sintáctico completado sin errores.")

    # Imprimir la estructura del AST
    print("\nÁrbol AST generado:")
    print(ast.to_dict())

    # Exportar AST a JSON
    exportar_ast(ast, "ast.json")
    print("Árbol AST exportado a 'ast.json'.")

    codigo_ensamblador = traducir_a_ensamblador_emu8086(codigo_fuente)
    
    # Mostrar el resultado
    print("\nCódigo en ensamblador:")
    print(codigo_ensamblador)

    lenguaje = generar_codigo_lenguaje_maquina(codigo_ensamblador)
    print("\nCodigo lenguaje maquina (hexadecimal)")
    print(lenguaje)

except SyntaxError as e:
    print(f"\nError de sintaxis: {e}")
