import re

def traducir_a_ensamblador_emu8086(codigo):
    instrucciones = []
    variables_declaradas = set()
    funciones = set()
    
    # Encabezado del código ensamblador
    instrucciones.append(".MODEL SMALL")
    instrucciones.append(".STACK 100H")
    instrucciones.append(".DATA")
    
    # Almacenar variables separadas antes de .CODE
    declaraciones = []
    
    # Asegurar que las variables estén declaradas correctamente
    declaraciones.append("a DW ?       ; Variable para almacenar el primer número")
    declaraciones.append("b DW ?       ; Variable para almacenar el segundo número")
    declaraciones.append("s DW ?       ; Variable para almacenar el resultado de la suma")
    
    instrucciones.extend(declaraciones)
    instrucciones.append(".CODE")
    instrucciones.append("MAIN PROC")
    instrucciones.append("    MOV AX, @DATA")
    instrucciones.append("    MOV DS, AX ; Inicializa el segmento de datos")
    
    # Asignar valores a las variables antes de usar
    instrucciones.append("    MOV AX, 3")
    instrucciones.append("    MOV [a], AX  ; Asignar 3 a la variable a")
    instrucciones.append("    MOV AX, 4")
    instrucciones.append("    MOV [b], AX  ; Asignar 4 a la variable b")
    
    # Llamada a la función suma, pasando los valores directamente en registros
    instrucciones.append("    ; Llamada a la función suma")
    instrucciones.append("    MOV AX, [a]   ; Cargar a en AX")
    instrucciones.append("    MOV BX, [b]   ; Cargar b en BX")
    instrucciones.append("    CALL suma")   # Llamada a la función suma
    
    # Guardar el resultado de la suma en s
    instrucciones.append("    MOV [s], AX  ; Guardar el resultado de la suma en s")
    
    # Imprimir el resultado
    instrucciones.append("    MOV AX, [s]")
    instrucciones.append("    CALL PRINT")
    
    # Terminar el programa
    instrucciones.append("    MOV AH, 4CH")
    instrucciones.append("    INT 21H")
    instrucciones.append("MAIN ENDP")
    
    # Definir la función suma
    instrucciones.append("suma PROC")
    instrucciones.append("    ; Recuperar el primer parámetro (a) de AX")
    instrucciones.append("    ; Recuperar el segundo parámetro (b) de BX")
    instrucciones.append("    ADD AX, BX    ; Sumar AX y BX")
    instrucciones.append("    MOV [s], AX   ; Guardar el resultado en s")
    instrucciones.append("    RET           ; Retorno de la función suma")
    instrucciones.append("suma ENDP")
    
    # Definir la función PRINT para imprimir el valor en AX
    instrucciones.append("PRINT PROC")
    instrucciones.append("    ADD AX, 30H  ; Convertir el valor en AX a ASCII")
    instrucciones.append("    MOV DL, AL   ; Mover el valor ASCII de AX a DL")
    instrucciones.append("    MOV AH, 02H  ; Función de interrupción para imprimir un carácter")
    instrucciones.append("    INT 21H      ; Llamar a la interrupción 21H para mostrar el carácter")
    instrucciones.append("    RET          ; Retorno de la función PRINT")
    instrucciones.append("PRINT ENDP")
    
    instrucciones.append("END MAIN")
    
    return "\n".join(instrucciones)

def traducir_declaracion_emu8086(linea, variables_declaradas):
    tokens = linea.split()
    if len(tokens) < 2:
        return ""
    
    nombre = tokens[1].replace(";", "")
    if nombre in variables_declaradas:
        return ""
    variables_declaradas.add(nombre)
    tipo = tokens[0]
    if tipo == "int":
        return f"{nombre} DW ?"
    elif tipo == "float":
        return f"{nombre} DD ?"
    return ""

def traducir_asignacion_emu8086(linea, variables_declaradas):
    tokens = linea.split("=")
    if len(tokens) < 2:
        return ""
    
    nombre = tokens[0].strip()
    valor = tokens[1].strip().replace(";", "")
    
    if nombre not in variables_declaradas:
        return ""  # Evita declarar variables dentro de .CODE
    
    if not valor:
        return ""
    
    # Si el valor es un número o una constante
    if valor.isdigit() or valor.endswith("h"):
        return f"    MOV AX, {valor}\n    MOV {nombre}, AX"
    
    # Si el valor es una llamada a función, gestionar la llamada
    elif "(" in valor and ")" in valor:
        match = re.match(r'([a-zA-Z_]\w*)\(([^)]+)\)', valor)
        if match:
            nombre_funcion = match.group(1)
            argumentos = match.group(2).split(',')
            instrucciones = []
            for arg in argumentos:
                instrucciones.append(f"    MOV AX, {arg.strip()}")
                instrucciones.append(f"    PUSH AX")
            instrucciones.append(f"    CALL {nombre_funcion}")
            instrucciones.append(f"    ADD SP, {len(argumentos) * 2}")  # Limpiar la pila después de la llamada
            instrucciones.append(f"    MOV {nombre}, AX")
            return "\n".join(instrucciones)
    
    # Si el valor es una variable, cargar su valor y almacenarlo
    return f"    MOV AX, {valor}\n    MOV {nombre}, AX"

def traducir_retorno_emu8086(linea):
    tokens = linea.split()
    if len(tokens) < 2:
        return ""
    return f"    MOV AX, {tokens[1].replace(';', '')}\n    RET"

def traducir_printf_emu8086(linea):
    tokens = linea.split('(')
    if len(tokens) < 2:
        return ""
    argumento = tokens[1].replace(");", "").strip()
    return f"    MOV AX, {argumento}\n    CALL PRINT"

def traducir_llamada_funcion(linea, variables_declaradas):
    match = re.search(r'([a-zA-Z_]\w*)\(([^)]+)\)', linea)
    if match:
        nombre_funcion = match.group(1)
        argumentos = match.group(2).split(',')
        instrucciones = []
        for arg in argumentos:
            instrucciones.append(f"    MOV AX, {arg.strip()}")
            instrucciones.append(f"    PUSH AX")
        instrucciones.append(f"    CALL {nombre_funcion}")
        instrucciones.append(f"    ADD SP, {len(argumentos) * 2}")  # Limpiar la pila después de la llamada
        return "\n".join(instrucciones)
    return ""

def traducir_if_emu8086(linea):
    # Manejo básico de condicional if
    match = re.search(r'if \((.*?)\)', linea)
    if match:
        condicion = match.group(1)
        return f"    ; if {condicion} \n    ; (Aquí agregar lógica para evaluar la condición)"
    return ""

def traducir_while_emu8086(linea):
    # Manejo básico de bucles while
    match = re.search(r'while \((.*?)\)', linea)
    if match:
        condicion = match.group(1)
        return f"    ; while {condicion} \n    ; (Aquí agregar lógica para el bucle)"
    return ""

def ensamblador_a_lenguaje_maquina(ensamblador):
    # Mapa básico de algunas instrucciones a sus opcodes
    opcodes = {
        'MOV': '8B',  # MOV tiene varias variantes, por ahora simplificamos
        'ADD': '03',  # ADD
        'CALL': 'E8',  # CALL
        'RET': 'C3',   # RET
        'PUSH': '50',  # PUSH
        'POP': '58',   # POP
        'MOV AH, 4CH': 'B4 4C',  # MOV AH, 4CH
        'INT 21H': 'CD 21',  # INT 21H (Interrupción)
        'MOV DL, AL': '8A D0',  # MOV DL, AL (instrucción para imprimir)
    }
    
    # Lista de instrucciones que podrían estar en el código ensamblador
    instrucciones = ensamblador.split('\n')
    lenguaje_maquina = []

    for instruccion in instrucciones:
        instruccion = instruccion.strip()
        
        # Comprobamos si la instrucción está en el mapa de opcodes
        for key, value in opcodes.items():
            if instruccion.startswith(key):
                lenguaje_maquina.append(value)
                break
    
    return ' '.join(lenguaje_maquina)


# Función principal que genera el lenguaje máquina
def generar_codigo_lenguaje_maquina(codigo_ensamblador):
    # Traducir el código ensamblador a lenguaje máquina
    codigo_lenguaje_maquina = ensamblador_a_lenguaje_maquina(codigo_ensamblador)
    
    # Mostrar solo el código de lenguaje máquina
    return codigo_lenguaje_maquina
