from analisis_lexico import identificar_tokens
from analisis_sintactico import Parser, exportar_ast
from ensamblador import GeneradorEnsamblador
from ensamblador import generar_codigo_lenguaje_maquina
from analisis_semantico import AnalizadorSemantico


# Código fuente de prueba
codigo_fuente = """
int suma(int a, int b) {
    int c = a + b;
    return c;
}

void main() {
    int s;
    int a = 3;
    int b = 4;
    s = suma(a, b);
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

    print("\nÁrbol AST generado:")
    print(ast.to_dict())

    exportar_ast(ast, "ast.json")
    print("Árbol AST exportado a 'ast.json'.")

    print("\nIniciando análisis semántico...")
    analizador_semantico = AnalizadorSemantico()
    analizador_semantico.analizar(codigo_fuente)
    print("Análisis semántico completado sin errores.")

    # Generación de código ensamblador
    generador = GeneradorEnsamblador()
    codigo_ensamblador = generador.generar_codigo(ast)
    print("\nCódigo en ensamblador:")
    print(codigo_ensamblador)

    lenguaje = generar_codigo_lenguaje_maquina(codigo_ensamblador)
    print("\nCódigo lenguaje máquina (hexadecimal):")
    print(lenguaje)

except SyntaxError as e:
    print(f"\nError de sintaxis: {e}")
except Exception as e:
    print(f"\nError semántico: {e}")
