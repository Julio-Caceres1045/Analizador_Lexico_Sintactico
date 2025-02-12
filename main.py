import Analizador

# Código fuente de prueba
codigo_fuente = """
int suma(int a, int b) {
    int resultado = a + b * 2;

    if (resultado > 10 && a != 0) {
        resultado = resultado / 2;
    } else if (b < 5 || a == 3) {
        resultado = resultado + 1;
    }

    return resultado;
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
    parser.parsear()
    print("Análisis sintáctico completado sin errores.")
except SyntaxError as e:
    print(e)
