import psycopg2 as psy
import random as r
import getpass
import os
from datetime import date
import logica_lucha
import logica_mejora
import logica_estadisticas_globales

cls = lambda: os.system('cls')


def insertar_usuario(nombre_completo, contrasena, nickname_usuario, faccion):
    """
    Inserta un usuario en la tabla usuario de la BD

    :param nombre_completo: nombre de la persona
    :param contrasena: contraseña
    :param nickname_usuario: nickname del usuario
    :param faccion: tierra | mundo exterior
    :return: None
    """
    today = ",'" + str(date.today()) + "')"

    conn = psy.connect("dbname=Taller3 user=postgres password=123456")

    cur = conn.cursor()

    values = "('" + nickname_usuario + "','" + nombre_completo + "','" + contrasena + "','" + faccion + "',5" + today

    cur.execute("insert into usuario values" + values)

    conn.commit()

    cur.close()


def insertar_luchador(nombre_avatar, vida, ataque, velocidad, nickname_usuario):
    """
    Ingresa un luchador en la tabla luchador

    :param nombre_avatar: nombre del avatar
    :param vida: ptje vida
    :param ataque: ptje ataque
    :param velocidad: ptje velocidad
    :param nickname_usuario: nickname del usuario
    :return: None
    """

    # Asumir que se empieza en nivel 1 con 0 experiencia

    conn = psy.connect("dbname=Taller3 user=postgres password=123456")

    cur = conn.cursor()

    values = "('" + nombre_avatar + "','" + nickname_usuario + "',1,0," + str(ataque) + "," + str(
        velocidad) + "," + str(vida)
    values_final = values + ",NULL,NULL,NULL,NULL,NULL,NULL)"

    cur.execute("insert into luchador values" + values_final)

    conn.commit()

    cur.close()


def existe_en_registro(nickname_usuario, contrasena):
    """
    Función para comprobar si el usuario existe en la base de datos

    :param nickname_usuario: nickname del usuario
    :param contrasena: contraseñan del usuario
    :return: True si existe | False si no existe
    """
    conn = psy.connect("dbname=Taller3 user=postgres password=123456")

    cur = conn.cursor()

    cur.execute("select * from usuario where nickname='" + nickname_usuario + "' and contraseña='" + contrasena + "'")
    row = cur.fetchone()
    cur.close()
    if row is None:
        print("El usuario no está registrado")
        return False
    else:
        return True


def mostrar_estadisticas_luchador(nickname_usuario):
    """
    Muestra toda la info del jugador

    :param nickname_usuario: nickname del usuario
    :return: None
    """

    conn = psy.connect("dbname=Taller3 user=postgres password=123456")

    cur = conn.cursor()

    cur.execute("select * from luchador where nickname='" + nickname_usuario + "'")
    row = cur.fetchone()

    row = str(row).strip("()")  # se quitan los parentesis de la query
    info_usuario = row.split(",")  # se añaden los datos a una lista

    print("-----------ESTADISTICAS LUCHADOR -------------------------")
    print("  INFO del luchador:", info_usuario[0].strip("'"))
    print("  Nivel -->" + str(info_usuario[2]))
    print("  Experiencia -->" + str(info_usuario[3]))
    print("  Ataque -->" + str(info_usuario[4]))
    print("  Velocidad -->" + str(info_usuario[5]))
    print("  Vida -->" + str(info_usuario[6]))
    cont = 1
    for i in range(7, 13):
        print("  Mejora" + str(cont) + ":" + info_usuario[i])
        cont += 1

    print("----------------------------------------------------------")
    cur.close()


def verificar_cant_combates(nickname_usuario):
    """
    Comprueba que el jugador no exceda el limite de combates diarios

    :param nickname_usuario: nickname del usuario
    :return: 1 para que pueda luchar | 0 para que no luche
    """

    '''
    select count(*)
    from lucha
    where nombre_avatar1 = 'avatar1' and fecha_combate = '2022-06-12'
    '''

    conn = psy.connect("dbname=Taller3 user=postgres password=123456")

    cur = conn.cursor()

    cur.execute("select nombre_avatar from luchador where nickname = 'nickname1'")

    row = cur.fetchone()

    q = "select count(*) from lucha where nombre_avatar1 = '" + row[0] + "' and fecha_combate = '" \
        + str(date.today()) + "'"

    cur.execute(q)

    row = cur.fetchone()
    cur.close()

    if row[0] >= 5:
        print("--------------------------------------")
        print("LIMITE DE COMBATES DIARIOS EXCEDIDOS")
        print("--------------------------------------")
        return 0

    return 1


# ------------INICIO DEL LOGIN-----------------------------
# se solicita nickname y contraseña para iniciar sesion
existe = None
opcion_usuario = None
while 1:

    print("Bienvenido al login")
    nickname_usuario = input("Ingrese su nickname de usuario: ")
    contrasena = getpass.getpass("Ingrese su contrasena: ")  # para conseguir contraseña sin q se vea en la consola
    existe = existe_en_registro(nickname_usuario, contrasena)

    if existe:
        cls()  # borra texto en consola
        break
    else:
        print("DATOS ERRONEOS")
        opcion_usuario = input("Para intentar de nuevo ingrese 1 para registrarse ingrese 2: ")
        cls()  # borra texto en consola

    if opcion_usuario == "2":
        break

'''
LOGICA DE INICIO DE SESION
opciones de:
-muestra perfil con estadísticas de luchador
-luchar
-mejorar
-ver estadisticas globales
-cerrar sesion
'''
if existe:
    mostrar_estadisticas_luchador(nickname_usuario)
    print("Eliga una de las siguientes opciones: ")
    print("a) Luchar")
    print("b) Mejorar")
    print("c) Estadisticas globales")
    print("d) Cerrar sesión")
    op = input("Ingresa tu opcion: ")

    if op == "a" and verificar_cant_combates(nickname_usuario):
        logica_lucha.luchar(nickname_usuario)  # Ingresa al archivo con logica de lucha
    elif op == "b":
        logica_mejora.testeo()  # ingresa archivo para mejora
    elif op == "c":
        logica_estadisticas_globales.testeo()  # ingresa archivo con logica stats globales
    elif op == "d":
        print("Sesión terminada")

'''
LOGICA PARA REGISTRARSE

Debe ingresar:
nombre completo
contrasena 
nickname de usuario
nombre avatar
faccion
Se entregan aleatoriamente datos del luchador
-Ataque entre 1 y 5
-Vida entre 10 y 20
-velocidad entre 1 y 10
-6 espacios de mejora vacios 
'''
if not existe:
    print("Bienvenido al menu de registro\n")
    nombre_completo = input("Ingrese su nombre completo: ")
    while 1:
        contrasena = input("Ingrese su contrasena: ")
        contrasena_verificar = input("Ingrese de nuevo su contrasena para verificar: ")

        if contrasena == contrasena_verificar:
            break
        else:
            print("Las contraseñas no son iguales intente de nuevo")

    nickname_usuario = input("Ingrese su nickname de usuario: ")
    nombre_avatar = input("Ingrese el nombre de su avatar: ")
    faccion = input("Ingrese el nombre de su faccion (tierra/mundo exterior): ")

    ataque = r.randint(1, 5)
    vida = r.randint(10, 20)
    velocidad = r.randint(1, 10)

    print(nombre_avatar + ", obtuvo los siguientes puntajes: ")
    print("Ataque: " + str(ataque))
    print("Vida: " + str(vida))
    print("Velocidad: " + str(velocidad))
    print("Ademas de 6 espacios vacíos para mejoras")
    # logica que inserta  el usuario y su luchador en la bd
    insertar_usuario(nombre_completo, contrasena, nickname_usuario, faccion)
    insertar_luchador(nombre_avatar, vida, ataque, velocidad, nickname_usuario)
