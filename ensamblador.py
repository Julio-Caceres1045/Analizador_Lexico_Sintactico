import re

def traducir_a_ensamblador_emu8086(codigo):
    instrucciones = []

    # Añadir cabeceras y segmentos de datos
    instrucciones.append(".model small")
    instrucciones.append(".stack 100h")
    instrucciones.append(".data")
    instrucciones.append("x dw 0")
    instrucciones.append("y dw 0")
    instrucciones.append(".code")
    instrucciones.append("main:")

    # Procesar el código C (declaraciones, asignaciones, retornos)
    lineas = codigo.splitlines()
    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue

        if "int" in linea or "float" in linea:  # Declaraciones
            instrucciones.append(traducir_declaracion_emu8086(linea))
        elif "=" in linea:  # Asignaciones
            instrucciones.append(traducir_asignacion_emu8086(linea))
        elif "return" in linea:  # Retornos
            instrucciones.append(traducir_retorno_emu8086(linea))
        elif "print" in linea:  # Impresión
            instrucciones.append(traducir_print_emu8086(linea))

    # Finalizar el código
    instrucciones.append("mov ah, 4Ch")
    instrucciones.append("int 21h")
    instrucciones.append("imprimir:")
    instrucciones.append("add ax, 30h")  # Convertir a ASCII
    instrucciones.append("mov dl, al")  # Mover al registro DL para impresión
    instrucciones.append("mov ah, 02h")  # Función para imprimir
    instrucciones.append("int 21h")
    instrucciones.append("ret")  # Regresar de la función

    return "\n".join(instrucciones)

def traducir_declaracion_emu8086(linea):
    tokens = linea.split()
    if len(tokens) < 2:
        return ""  # No es una declaración válida

    tipo = tokens[0]
    nombre = tokens[1]
    if len(tokens) > 2 and "=" in tokens:
        valor = tokens[3] if len(tokens) > 3 else "0"
        return f"declare {nombre}, word 0\nmov ax, {valor}\nmov {nombre}, ax"
    else:
        return f"declare {nombre}, word 0"

def traducir_asignacion_emu8086(linea):
    tokens = linea.split()
    if len(tokens) < 3:
        return ""  # No es una asignación válida

    nombre = tokens[0]
    valor = tokens[2]
    return f"mov ax, {valor}\nmov {nombre}, ax"

def traducir_retorno_emu8086(linea):
    tokens = linea.split()
    if len(tokens) < 2:
        return ""  # No es una declaración de retorno válida
    return f"mov ax, {tokens[1]}\nret"
    
def traducir_print_emu8086(linea):
    tokens = linea.split()
    if len(tokens) < 2:
        return ""  # No es una instrucción de impresión válida
    return f"mov ax, {tokens[1]}\ncall imprimir"
