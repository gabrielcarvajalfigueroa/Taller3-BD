import random
from datetime import date
import psycopg2 as psy


def aplicar_mejoras(nickname, vida, ataque, velocidad):  # para player y enemigo
    """
    Aplica las mejoras que tenga equipada un jugador a sus stats

    :param nickname: nickname usuario
    :param vida: vida usuario
    :param ataque: ataque usuario
    :param velocidad: velocidad usuario
    :return: lista con las stats finales con orden [vida,ataque,velocidad]
    """

    '''
    select me.id_mejora, me.nom_atributo, me.cant_puntos
    from luchador l
    inner join mejora me
    on me.id_mejora = l.mejora3
    '''

    vida_total = vida
    ataque_total = ataque
    velocidad_total = velocidad
    conn = psy.connect("dbname=Taller3 user=postgres password=123456")

    cur = conn.cursor()

    for i in range(1, 7):
        q = "select me.id_mejora, me.nom_atributo, me.cant_puntos " \
            "from luchador l " \
            "inner join mejora me " \
            "on me.id_mejora = l.mejora" + str(i) + \
            " where nickname = '" + nickname + "'"
        cur.execute(q)
        record = cur.fetchone()

        if record is not None:
            if record[1] == "vida":
                vida_total += record[2]
            elif record[1] == "ataque":
                ataque_total += record[2]
            else:
                velocidad_total += record[2]

    cur.close()

    return vida_total, ataque_total, velocidad_total


def combate(p1, enemy, stats_player, stats_enemigo):  # retorna tupla con el ganador y el perdedor
    """
    Realiza la pelea y retorna el ganador con el perdedor en una lista

    :param p1: nombre player 1
    :param enemy: nombre enemigo
    :param stats_player: [vida, ataque, velocidad]
    :param stats_enemigo: [vida, ataque, velocidad]
    :return: [nombre_ganador, nombre_perdedor]
    """
    p1_vida = stats_player[0]
    enemy_vida = stats_enemigo[0]
    porc_esquivar_player = stats_player[2]
    porc_esquivar_enemy = stats_enemigo[2]

    if porc_esquivar_player > 80:
        porc_esquivar_player = 80
    if porc_esquivar_enemy > 80:
        porc_esquivar_enemy = 80

    if stats_player[2] >= stats_enemigo[2]:
        # inicia p1
        while 1:
            if random.randint(1, 100) > porc_esquivar_enemy:
                enemy_vida -= stats_player[1]
                if enemy_vida <= 0:
                    print("has ganado")
                    return p1, enemy
            p1_vida -= stats_enemigo[1]
            if random.randint(1, 100) > porc_esquivar_player:
                if p1_vida <= 0:
                    print("has perdido")
                    return enemy, p1

    else:
        # inicia p2
        while 1:
            if random.randint(1, 100) > porc_esquivar_player:
                p1_vida -= stats_enemigo[1]
                if p1_vida <= 0:
                    print("has muerto")
                    return enemy, p1

            if random.randint(1, 100) > porc_esquivar_enemy:
                enemy_vida -= stats_player[1]
                if enemy_vida <= 0:
                    print("has ganado")
                    return p1, enemy


def update_exp_y_nivel(avatar, xp_ganada):
    """
    Hace un update de la exp y en caso de que se suba de nivel, informa al usuario
    y le agrega los puntos que haya ganado por subir de nivel

    :param avatar: nombre del avatar
    :param xp_ganada: xp que gano por el combate
    :return: None
    """
    conn = psy.connect("dbname=Taller3 user=postgres password=123456")

    cur = conn.cursor()
    '''
    update luchador
    set experiencia = experiencia + cant_exp
    where nombre_avatar = avatar
    '''
    q = "select nivel, experiencia from luchador where nombre_avatar = '" + avatar + "'"

    cur.execute(q)

    row = cur.fetchone()

    lvl_up_at = 100 + (row[0] * 50)
    xp_actual = row[1] + xp_ganada
    xp_update = xp_actual - lvl_up_at

    if xp_actual >= lvl_up_at:
        print("FELICITACIONES", avatar, "SUBISTE AL NIVEL:", row[0] + 1)
        q = "update luchador set experiencia = " + str(xp_update) + " where nombre_avatar = '" + avatar + "'"
        q2 = "update luchador set nivel = " + str(row[0] + 1) + " where nombre_avatar = '" + avatar + "'"
        cur.execute(q)
        cur.execute(q2)
        # Puntos por subir de nivel
        opciones = ["ataque", "velocidad", "vida"]
        eleccion = opciones[random.randint(0, 2)]
        puntaje = random.randint(1, 5)
        print("-----------------------------------------------------")
        print(avatar + ", ha ganado:", puntaje, "puntos de", eleccion)
        cur.execute("update luchador set " + eleccion + " = " + eleccion + " + " + str(puntaje)
                    + " where nombre_avatar = '" + avatar + "'")

    else:
        q = "update luchador set experiencia = " + str(xp_actual) + " where nombre_avatar = '" + avatar + "'"
        cur.execute(q)

    conn.commit()
    cur.close()


def agregar_historial_lucha(ganador, perdedor):
    """
    Agrega el combate al historial para llevar registro

    :param ganador: Ganador combate
    :param perdedor: perdedor combate
    :return: None
    """
    # tabla lucha
    # id_lucha | nombre_avatar1 | nombre_avatar2 | fecha_comabate | ganador | perdedor |

    conn = psy.connect("dbname=Taller3 user=postgres password=123456")

    cur = conn.cursor()

    # conseguir la fecha de hoy
    today = str(date.today())

    # conseguir el id de lucha

    q = "select count(*) from lucha "

    cur.execute(q)

    row = cur.fetchone()

    id = row[0] + 1

    # hacer el insert y commit
    q = "insert into lucha values('" + str(id) + "'," "'" + ganador + "'," + "'" + perdedor + "'" + ",'" \
        + today + "'" + ",'" + ganador + "'" + ",'" + perdedor + "')"

    cur.execute(q)
    conn.commit()
    cur.close()


'''
se empareja aleatoriamente con otro luchador
que tenga max: 1 nivel de diferencia
'''


def luchar(nickname_usuario):
    """
    Hace la logica de combate en base al usuario que se le pasa

    :param nickname_usuario: nombre del usuario
    :return: Si es que no hay con quien luchar o si se cumple el combate
    """

    res_nivel = "select * from luchador l where nickname = '" + nickname_usuario + "';"

    conn = psy.connect("dbname=Taller3 user=postgres password=123456")

    cur = conn.cursor()

    cur.execute(res_nivel)

    player = cur.fetchone()  # En player quedan los datos del usuario que inicio el combate

    nivel = player[2]

    nivel = int(nivel)

    res = "select * from luchador where not nickname ='" + nickname_usuario + \
          "' and nivel between " + str((nivel - 1)) + " and " + str((nivel + 1)) + ";"

    cur.execute(res)

    records = cur.fetchall()

    posibles_luchadores = [luchador for luchador in records]  # se llena la lista con los posibles luchadores

    if len(posibles_luchadores) == 0:
        print("NO HAY LUCHADORES QUE ESTEN DENTRO DEL NIVEL ACEPTADO PARA COMBATIR")  # retornar
        return
    else:
        enemigo = random.choice(posibles_luchadores)

    print("---COMBATE---")
    print(player[0], "vs", enemigo[0], "\n-------------")

    nom_player, nom_enemigo = player[0], enemigo[0]
    ataque_player, ataque_enemigo = player[4], enemigo[4]
    velocidad_player, velocidad_enemigo = player[5], enemigo[5]
    vida_player, vida_enemigo = player[6], enemigo[6]

    #  Este codigo muestra las stats de ambos luchadores por consola

    info = ["nombre", "nickname", "nivel", "experiencia", "ataque", "velocidad",
            "vida"]  # Ocurre problema con mejoras por ser None
    jugadores = ["PLAYER1", "ENEMIGO"]
    data = [player, enemigo]
    format_row = "{:>12}" * (len(info) + 1)
    print(format_row.format("", *info))
    for team, row in zip(jugadores, data):
        print(format_row.format(team, *row))

    stats_player = aplicar_mejoras(player[1], vida_player, ataque_player, velocidad_player)

    stats_enemigo = aplicar_mejoras(enemigo[1], vida_enemigo, ataque_enemigo, velocidad_enemigo)

    print(stats_player, "\n", stats_enemigo)

    ganador_perdedor = combate(player[0], enemigo[0], stats_player,
                               stats_enemigo)  # retorna tupla con el ganador y el perdedor

    print("ganador", ganador_perdedor[0], "-> Ganó 100 EXP")
    print("perdedor", ganador_perdedor[1], "-> Ganó 20 EXP")

    # realizar updates a los luchadores para actualizar experiencias
    # ver la cantidad de combates antes de ingresar aqui usando la tabla con las luchas
    update_exp_y_nivel(ganador_perdedor[0], 100)
    update_exp_y_nivel(ganador_perdedor[1], 20)

    # realizar insert a la tabla lucha para guardar el historial del combate
    agregar_historial_lucha(ganador_perdedor[0], ganador_perdedor[1])

    cur.close()

    return
