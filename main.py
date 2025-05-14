from analisis_lexico import identificar_tokens
from analisis_sintactico import Parser, exportar_ast
from ensamblador import GeneradorEnsamblador
from ensamblador import generar_codigo_lenguaje_maquina
from analisis_semantico import AnalizadorSemantico


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

tokens = identificar_tokens(codigo_fuente)
print("Tokens encontrados:")
for tipo, valor in tokens:
    print(f"{tipo}: {valor}")

print("\nTokens generados:", tokens)

try:
    print("\nIniciando analisis sintactico...")
    parser = Parser(tokens)
    ast = parser.parsear()
    print("Analisis sintactico completado sin errores.")

    print("\nÁrbol AST generado:")
    print(ast.to_dict())

    exportar_ast(ast, "ast.json")
    print("Arbol AST exportado a 'ast.json'.")

    print("\nIniciando analisis semantico...")
    analizador_semantico = AnalizadorSemantico()
    analizador_semantico.analizar(codigo_fuente)
    print("Analisis semantico completado sin errores.")

    generador = GeneradorEnsamblador()
    codigo_ensamblador = generador.generar_codigo(ast)
    print("\nCodigo en ensamblador:")
    print(codigo_ensamblador)

    lenguaje = generar_codigo_lenguaje_maquina(codigo_ensamblador)
    print("\nCodigo lenguaje maquina (hexadecimal):")
    print(lenguaje)

except SyntaxError as e:
    print(f"\nError de sintaxis: {e}")
except Exception as e:
    print(f"\nError semantico: {e}")
