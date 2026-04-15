import discord
from openai import OpenAI
import random
import re
import json
from datetime import datetime

def cargar_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return {}

import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client_ai = OpenAI(api_key=OPENAI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

# ========================
# APODOS
# ========================
APODOS = {
    "platti": "Platti3p",
    "platti3p": "Platti3p",
    "plati": "Platti3p",
    "jumbo": "Jumbo'",
    "jumbo'": "Jumbo'",
    "jumbito": "Jumbo'",
    "mosko": "moskongo",
    "mos": "moskongo",
    "moskongo": "moskongo",
    "bruno": "brunooiraola_02",
    "brunoo": "brunooiraola_02",
    "brunooiraola": "brunooiraola_02",
    "pasti": "Pasti",
    "pastii": "Pasti",
    "huer": "Huerque.",
    "huerque": "Huerque.",
    "huerque.": "Huerque.",
    "argo": "ARGOAT",
    "argoat": "ARGOAT",
    "chichi": "CHICHIMOCO SKINS",
    "chichimoco": "CHICHIMOCO SKINS",
    "chichimoco skins": "CHICHIMOCO SKINS",
    "mati": "Royal Prestige",
    "royal": "Royal Prestige",
    "marcos": "Huerque.",
    "marquitos": "Huerque."
}

def normalizar(nombre):
    return APODOS.get(nombre.lower(), nombre)

# ========================
# RANKING
# ========================
def obtener_ranking():
    try:
        stats = cargar_json("stats.json")
    except:
        return []

    mes = datetime.now().strftime("%Y-%m")
    ranking = stats.get(mes, {})
    return sorted(ranking.items(), key=lambda x: x[1], reverse=True)

def contar_partidas():
    try:
        matches = cargar_json("matches.json")
    except:
        return {}

    partidas = {}
    for match in matches:
        for jugador in match.get("players", []):
            nombre = jugador["name"]
            partidas[nombre] = partidas.get(nombre, 0) + 1

    return partidas

# ========================
# W/L
# ========================
def calcular_wl():
    try:
        matches = cargar_json("matches.json")
    except:
        return {}

    wl = {}

    for match in matches:
        win = match.get("win", False)

        for p in match.get("players", []):
            nombre = p["name"]

            if nombre not in wl:
                wl[nombre] = {"w": 0, "l": 0}

            if win:
                wl[nombre]["w"] += 1
            else:
                wl[nombre]["l"] += 1

    return wl

# ========================
# ANALISIS
# ========================
def analizar(data, texto_original):

    intro = random.choice([
        "A ver qué pasó acá…",
        "Bueno… analizamos esto…",
        "Desmenuzando la partida…",
        "Vamos a ver este game…"
    ])

    texto = intro + "\n\n"

    usadas = set()
    def elegir(lista):
        opciones = [x for x in lista if x not in usadas] or lista
        elegido = random.choice(opciones)
        usadas.add(elegido)
        return elegido

    orden = sorted(data.items(), key=lambda x: x[1].get("adr",0), reverse=True)

    top = [
        "nivel altísimo durante todo el game",
        "marcó la diferencia en las rondas clave",
        "se puso el equipo al hombro",
        "dominó el servidor",
        "fue el jugador más determinante",
        "impactó en casi todas las rondas",
        "lideró al equipo con autoridad",
        "estuvo un paso adelante todo el partido",
        "manejó los tiempos del game",
        "fue clave en los momentos importantes"
    ]

    mid = [
        "acompañó bien al equipo",
        "tuvo un rendimiento sólido",
        "cumplió correctamente su rol",
        "aportó lo necesario para el equipo",
        "estuvo a la altura del partido",
        "correcto dentro del contexto del game",
        "sumó en varias rondas importantes",
        "mantuvo un nivel estable",
        "no desentonó dentro del equipo",
        "hizo un trabajo correcto"
    ]

    low = [
        "le costó entrar en ritmo",
        "tuvo poco impacto",
        "no logró influir demasiado",
        "le faltó presencia en las rondas",
        "no encontró su juego",
        "quedó lejos del ritmo del equipo",
        "le costó generar impacto",
        "muy irregular durante el partido",
        "no logró adaptarse al ritmo",
        "poca incidencia en el resultado"
    ]

    worst = [
        "no apareció en el servidor",
        "muy bajo nivel durante la partida",
        "partida muy floja",
        "totalmente fuera del partido",
        "muy lejos de su nivel habitual",
        "no logró meterse en el game en ningún momento",
        "rendimiento muy por debajo del equipo",
        "no aportó prácticamente nada",
        "muy desconectado del partido",
        "día para el olvido"
    ]

    # 🔥 ORDEN GENERAL (ARREGLADO)
    for i,(j,stats) in enumerate(orden):
        adr = stats.get("adr",0)

        if i == 0:
            texto += f"{j} {elegir(top)}.\n"
        elif i == len(orden)-1:
            texto += f"{j} {elegir(worst)}.\n"
        elif adr < 60:
            texto += f"{j} {elegir(low)}.\n"
        else:
            texto += f"{j} {elegir(mid)}.\n"

    texto += "\n🧠 Tips:\n"
    usadas.clear()

    # 🔥 TIPS (ARREGLADO)
    for j,stats in data.items():

        adr = stats.get("adr",0)
        kast = stats.get("kast",0)
        k = stats.get("kills",0)
        d = stats.get("deaths",0)

        frases = []

        # ADR
        if adr >= 90:
            frases.append(elegir([
                "dominó en daño",
                "mucho daño constante",
                "impacto altísimo en daño",
                "marcó diferencia con el ADR",
                "fue el que más daño metió"
            ]))
        elif adr <= 60:
            frases.append(elegir([
                "ADR muy bajo",
                "daño insuficiente",
                "te faltó daño en las rondas",
                "casi no generaste impacto",
                "poco aporte en daño"
            ]))

        # KAST
        if kast >= 75:
            frases.append(elegir([
                "siempre presente en rondas",
                "muy buen KAST",
                "gran impacto colectivo",
                "muy consistente en cada ronda",
                "buen timing y decisiones"
            ]))
        elif kast <= 65:
            frases.append(elegir([
                "muy poca presencia",
                "KAST bajo",
                "no estuviste en rondas clave",
                "te costó entrar en juego",
                "poco impacto en el equipo"
            ]))

        # KILLS
        if k >= 20:
            frases.append(elegir([
                "muchas kills importantes",
                "ganaste varios duelos",
                "fuiste clave en los enfrentamientos",
                "cerraste muchas rondas",
                "gran aporte en kills"
            ]))
        elif k <= 10:
            frases.append(elegir([
                "muy pocas kills",
                "te faltó cerrar duelos",
                "poco aporte ofensivo",
                "no pudiste ganar enfrentamientos",
                "faltó agresividad"
            ]))

        # MUERTES
        if d > k:
            frases.append(elegir([
                "muchas muertes",
                "moriste más de lo que aportaste",
                "te eliminaron seguido",
                "poca supervivencia en rondas",
                "te costó mantenerte vivo"
            ]))

        # FINAL
        if len(frases) >= 2:
            base = f"{frases[0]} y {frases[1]}"
        elif frases:
            base = frases[0]
        else:
            base = elegir([
                "rendimiento correcto",
                "nivel aceptable",
                "cumpliste sin destacar"
            ])

        recomendaciones = [
            "tratá de jugar más con el equipo",
            "mejorá el posicionamiento",
            "buscá más impacto en rondas clave",
            "intentá jugar más seguro",
            "tenés que involucrarte más en el game"
        ]

        texto += f"{j}: {base}, {elegir(recomendaciones)}.\n"

    # ========================
    # LECTURA (MEJORADA)
    # ========================
    resultado = re.search(r"(\d+)-(\d+)", texto_original)
    partes = texto_original.split()

    mapa = partes[0] if partes else "Mapa"
    a,b = (int(resultado.group(1)), int(resultado.group(2))) if resultado else (0,0)

    texto += "\n🧠 Lectura:\n"

    diff = abs(a-b)

    if a > b:

        if diff <= 2:
            inicio = elegir([
                f"Victoria ajustada {a}-{b} en {mapa}. Lo ganaron sufriendo.",
                f"Victoria ajustada {a}-{b} en {mapa}. Partido para cardíacos.",
                f"Victoria ajustada {a}-{b} en {mapa}. Se definió por detalles.",
                f"Victoria ajustada {a}-{b} en {mapa}. Lo cerraron mejor al final.",
                f"Victoria ajustada {a}-{b} en {mapa}. Supieron sufrir y ganar."
            ])

            extra = elegir([
                "Supieron cerrar mejor las rondas finales.",
                "Buen clutch en momentos clave.",
                "Se mantuvieron firmes bajo presión.",
                "Mejor toma de decisiones en el cierre.",
                "Ajustaron bien en las últimas rondas."
            ])

        elif diff <= 5:
            inicio = elegir([
                f"Victoria sólida {a}-{b} en {mapa}. Siempre un paso adelante.",
                f"Victoria sólida {a}-{b} en {mapa}. Partido controlado.",
                f"Victoria sólida {a}-{b} en {mapa}. Buen manejo del game.",
                f"Victoria sólida {a}-{b} en {mapa}. Supieron imponer su ritmo.",
                f"Victoria sólida {a}-{b} en {mapa}. Lo jugaron con cabeza."
            ])

            extra = elegir([
                "Buen manejo del ritmo y decisiones correctas.",
                "Supieron mantener la ventaja todo el partido.",
                "Buena lectura del rival.",
                "Controlaron bien las rondas importantes.",
                "Jugaron ordenados como equipo."
            ])

        else:
            inicio = elegir([
                f"Paliza {a}-{b} en {mapa}. Esto parecía un lobby de Premier contra bots.",
                f"Paliza {a}-{b} en {mapa}. Los pasaron por arriba sin frenar.",
                f"Paliza {a}-{b} en {mapa}. Diferencia de nivel total.",
                f"Paliza {a}-{b} en {mapa}. Jugaban a otra velocidad.",
                f"Paliza {a}-{b} en {mapa}. Dominio absoluto del server."
            ])

            extra = elegir([
                "Se los vio muy coordinados como equipo, dominaron todo.",
                "Excelente control del ritmo y ejecución.",
                "Aprovecharon cada error del rival.",
                "Dominio total en todas las fases del juego.",
                "Controlaron completamente el mapa."
            ])

        texto += inicio + "\n"

    else:

        if diff <= 2:
            inicio = elegir([
                f"Derrota ajustada {a}-{b} en {mapa}. Se escapó por poco.",
                f"Derrota ajustada {a}-{b} en {mapa}. Estaba para cualquiera.",
                f"Derrota ajustada {a}-{b} en {mapa}. Perdieron por detalles.",
                f"Derrota ajustada {a}-{b} en {mapa}. Duele porque estaba ahí.",
                f"Derrota ajustada {a}-{b} en {mapa}. Faltó cerrar."
            ])

            extra = elegir([
                "Faltó cerrar mejor algunas rondas.",
                "Errores puntuales terminaron costando.",
                "Les faltó definición.",
                "Buen nivel pero sin cierre.",
                "Necesitan mejorar el final de ronda."
            ])

        elif diff <= 5:
            inicio = elegir([
                f"Derrota clara {a}-{b} en {mapa}. El rival fue mejor.",
                f"Derrota clara {a}-{b} en {mapa}. Partido complicado.",
                f"Derrota clara {a}-{b} en {mapa}. Siempre atrás.",
                f"Derrota clara {a}-{b} en {mapa}. Les costó el ritmo.",
                f"Derrota clara {a}-{b} en {mapa}. No lograron imponerse."
            ])

            extra = elegir([
                "Les costó adaptarse al rival.",
                "Faltó coordinación.",
                "No controlaron las rondas clave.",
                "Poco impacto general.",
                "No lograron imponer su juego."
            ])

        else:
            inicio = elegir([
                f"Derrota aplastante {a}-{b} en {mapa}. Preparan las valijas muchachos.",
                f"Derrota aplastante {a}-{b} en {mapa}. Los pasaron por arriba.",
                f"Derrota aplastante {a}-{b} en {mapa}. Diferencia total.",
                f"Derrota aplastante {a}-{b} en {mapa}. No hubo respuesta.",
                f"Derrota aplastante {a}-{b} en {mapa}. Partido para olvidar."
            ])

            extra = elegir([
                "No lograron competir en ningún momento.",
                "Faltó totalmente la coordinación.",
                "Muy bajo nivel general.",
                "El rival dominó todo.",
                "Necesitan mejorar en todos los aspectos."
            ])

        texto += inicio + "\n"

    texto += "\n👉 " + extra

    return texto


# ========================
# 🔥 RACHAS (AGREGADO)
# ========================
def calcular_rachas():
    try:
        matches = cargar_json("matches.json")
    except:
        return {}

    rachas = {}

    for match in reversed(matches):
        win = match.get("win", False)

        for p in match.get("players", []):
            nombre = p["name"]

            if nombre not in rachas:
                rachas[nombre] = {"tipo": None, "streak": 0, "activo": True}

            if not rachas[nombre]["activo"]:
                continue

            if rachas[nombre]["tipo"] is None:
                rachas[nombre]["tipo"] = "win" if win else "lose"
                rachas[nombre]["streak"] = 1

            elif (win and rachas[nombre]["tipo"] == "win") or (not win and rachas[nombre]["tipo"] == "lose"):
                rachas[nombre]["streak"] += 1

            else:
                rachas[nombre]["activo"] = False

    return rachas


# ========================
# EVENTO
# ========================
@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    contenido = message.content.lower()

    if bot.user in message.mentions or "roaster" in contenido:

        # ========================
        # RANKING (NUEVO PRO)
        # ========================
        if "ranking" in contenido or "tabla" in contenido:
            jugadores = obtener_ranking()
            partidas = contar_partidas()
            wl = calcular_wl()
            rachas = calcular_rachas()

            meses = {
                "01":"Enero","02":"Febrero","03":"Marzo","04":"Abril",
                "05":"Mayo","06":"Junio","07":"Julio","08":"Agosto",
                "09":"Septiembre","10":"Octubre","11":"Noviembre","12":"Diciembre"
            }

            mes_nombre = meses[datetime.now().strftime("%m")]
            anio = datetime.now().strftime("%Y")

            texto = f"🏆 Ranking {mes_nombre} {anio}\n\n"

            data = []
            for j, pts in jugadores:
                pj = partidas.get(j, 0)
                prom = int(pts / pj) if pj else 0
                data.append((j, pts, pj, prom))

            max_prom = max(x[3] for x in data if x[2] > 0)
            min_prom = min(x[3] for x in data if x[2] > 0)

            usadas = set()
            def elegir(lista):
                opciones = [x for x in lista if x not in usadas] or lista
                elegido = random.choice(opciones)
                usadas.add(elegido)
                return elegido

            for i,(j,pts,pj,prom) in enumerate(data):

                if i == 0:
                    frase = elegir([
                        "→ lidera con consistencia",
                        "→ arriba de todo con gran nivel",
                        "→ puntero sólido del ranking",
                        "→ marca el ritmo del ranking"
                    ])
                elif prom == max_prom:
                    frase = elegir([
                        "→ el más impactante por partida",
                        "→ mejor promedio del equipo",
                        "→ rendimiento individual altísimo"
                    ])
                elif prom < 100:
                    frase = elegir([
                        "→ bajo rendimiento",
                        "→ le está costando",
                        "→ flojo nivel por ahora"
                    ])
                else:
                    frase = elegir([
                        "→ buen nivel general",
                        "→ rendimiento correcto",
                        "→ cumple bien dentro del equipo"
                    ])

                emoji = ""
                if i == 0: emoji = " 🏆"
                elif prom == max_prom: emoji = " 🔥"
                elif prom == min_prom: emoji = " 💀"

                w = wl.get(j, {}).get("w", 0)
                l = wl.get(j, {}).get("l", 0)
                total = w + l
                wr = int((w / total) * 100) if total > 0 else 0

                r = rachas.get(j, {})
                racha_txt = ""

                if r.get("tipo") == "win" and r.get("streak",0) >= 2:
                    racha_txt = f" 🔥({r['streak']}W)"
                elif r.get("tipo") == "lose" and r.get("streak",0) >= 2:
                    racha_txt = f" 💀({r['streak']}L)"

                texto += f"{i+1}. {j} - {pts} pts ({pj} pj | {prom} prom) {w}W/{l}L • {wr}%{racha_txt} {frase}{emoji}\n"

            await message.channel.send(texto)
            return

        # ========================
        # COMPARAR
        # ========================
        if "compara" in contenido:
            m = re.findall(r"compara (.+?) (?:vs|y|contra) (.+)", contenido)
            if not m:
                await message.channel.send("usa: compara jugador vs jugador")
                return

            j1 = normalizar(m[0][0].strip())
            j2 = normalizar(m[0][1].strip())

            matches = cargar_json("matches.json")

            s = {
                j1.lower(): {"k":0,"d":0,"adr":0,"kast":0,"g":0},
                j2.lower(): {"k":0,"d":0,"adr":0,"kast":0,"g":0}
            }

            for match in matches:
                for p in match.get("players", []):
                    n = p["name"].lower()
                    if n in s:
                        s[n]["k"]+=p["kills"]
                        s[n]["d"]+=p["deaths"]
                        s[n]["adr"]+=p["adr"]
                        s[n]["kast"]+=p["kast"]
                        s[n]["g"]+=1

            def pr(j,x): return s[j.lower()][x]/s[j.lower()]["g"] if s[j.lower()]["g"] else 0

            adr1, adr2 = pr(j1,'adr'), pr(j2,'adr')
            kast1, kast2 = pr(j1,'kast'), pr(j2,'kast')
            k1, k2 = s[j1.lower()]['k'], s[j2.lower()]['k']
            d1, d2 = s[j1.lower()]['d'], s[j2.lower()]['d']

            msg = f"📊 {j1} vs {j2}\n\n"
            msg += f"ADR: {adr1:.1f} vs {adr2:.1f}\n"
            msg += f"KAST: {kast1:.1f} vs {kast2:.1f}\n"
            msg += f"Kills: {k1} vs {k2}\n"
            msg += f"Deaths: {d1} vs {d2}\n\n"

            await message.channel.send(msg)
            return

        # ========================
        # ANALISIS
        # ========================
        if any(p in contenido for p in ["analiza","data","game","analisis","tirame data"]):
            last = cargar_json("last_match.json")

            data={p["name"]:p for p in last["players"]}
            txt=f"{last.get('mapa','Mapa')} {last.get('resultado','0-0')}"

            await message.channel.send(analizar(data,txt))
            return

        # ========================
        # RACHAS
        # ========================
        if any(p in contenido for p in ["racha","rachas"]):

            rachas = calcular_rachas()

            if not rachas:
                await message.channel.send("no hay datos todavía")
                return

            texto = "🔥 Rachas actuales\n\n"

            for j, r in rachas.items():

                if r["tipo"] == "win" and r["streak"] >= 2:
                    texto += f"🔥 {j} viene con {r['streak']} wins seguidas\n"

                elif r["tipo"] == "lose" and r["streak"] >= 2:
                    texto += f"💀 {j} lleva {r['streak']} derrotas seguidas\n"

            if texto.strip() == "🔥 Rachas actuales":
                texto += "todo muy parejo por ahora"

            await message.channel.send(texto)
            return

        # ========================
        # RESPUESTAS RAPIDAS
        # ========================
        if any(p in contenido for p in [
            "hola","que onda","como andas","todo bien","que haces","como va","todo tranqui"
        ]):
            respuestas = [
                "todo tranqui 😈",
                "acá ando esperando que no fedeen",
                "todo bien, vos carreás hoy o qué?",
                "ready para humillar 😎",
                "todo bien pero no quiero ver 0.7 hoy eh 💀"
            ]
            await message.channel.send(random.choice(respuestas))
            return

        # ========================
        # IA
        # ========================
        try:
            r = client_ai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role":"system","content":"Sos Roaster, jugador de CS2, argentino, picante."},
                    {"role":"user","content": message.content}
                ],
                max_tokens=60
            )
            await message.channel.send(r.choices[0].message.content)
        except:
            await message.channel.send("ni idea 💀")

bot.run(DISCORD_TOKEN)