import discord
from discord.ext import commands
import re
import json
import hashlib
from datetime import datetime

import os
TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = 741582207537119324  

TEAM = [
    "Platti3p","Rookie","ARGOAT","Jumbo'","brunooiraola_02",
    "Pasti","El peluca","Royal Prestige","CHICHIMOCO SKINS",
    "Huerque.","moskongo"
]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ========================
# NORMALIZAR
# ========================

def clean(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return text

team_clean = [clean(t) for t in TEAM]

# ========================
# RESULTADO
# ========================

def detectar_resultado_simple(text):
    primera = text.split("\n")[0].lower()

    match = re.search(r"(\w+)\s+(\d{1,2})-(\d{1,2})", primera)
    if match:
        mapa = match.group(1).capitalize()
        a = int(match.group(2))
        b = int(match.group(3))

        resultado = f"Victoria {a}-{b}" if a > b else f"Derrota {a}-{b}"
        return mapa, resultado

    return None, None

# ========================
# UTILS
# ========================

def kd_emoji(kd):
    return "📈" if kd >= 1.2 else "📊" if kd >= 0.8 else "📉"

def extraer_float(texto):
    nums = re.findall(r"\d+\.\d+", texto)
    return float(nums[0]) if nums else 0.0

def calcular_puntos(p):
    return round(
        p["kills"] * 8
        - p["deaths"] * 4
        + p["assists"] * 3
        + p["adr"] * 0.5
        + p["kast"] * 0.4
        + p["2k"] * 3
        + p["3k"] * 8
        + p["4k"] * 15
        + p["5k"] * 25
    )

# ========================
# STORAGE
# ========================

def cargar_json(nombre):
    try:
        with open(nombre, "r") as f:
            return json.load(f)
    except:
        return {}

def guardar_json(nombre, data):
    with open(nombre, "w") as f:
        json.dump(data, f, indent=4)

# ========================
# CONTAR PARTIDAS
# ========================

def contar_partidas():
    matches = cargar_json("matches.json")
    if not isinstance(matches, list):
        matches = []

    partidas = {}
    for m in matches:
        for j in m.get("players", []):
            partidas[j["name"]] = partidas.get(j["name"], 0) + 1

    return partidas

# ========================
# ANTI DUPLICADO
# ========================

def generar_match_id(players):
    base = ""
    for p in sorted(players, key=lambda x: x["name"]):
        base += f"{p['name']}-{p['kills']}-{p['deaths']}-{p['adr']}-{p['rating']};"
    return hashlib.md5(base.encode()).hexdigest()

# ========================
# PARSER
# ========================

def parse_leetify(text):
    players = []
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    for i in range(len(lines)):
        if clean(lines[i]) in team_clean:
            name = lines[i]
            mejor = None

            for j in range(i+1, min(i+60, len(lines))):
                if j > i+1 and clean(lines[j]) in team_clean:
                    break

                try:
                    if clean(lines[j]) == clean(name):
                        continue

                    if (
                        j+10 < len(lines)
                        and lines[j].isdigit()
                        and lines[j+1].isdigit()
                        and lines[j+2].isdigit()
                        and re.match(r"^\d+\.\d+$", lines[j+3])
                        and lines[j+4].isdigit()
                        and re.match(r"^\d+%$", lines[j+5])
                        and lines[j+10].replace("+","").replace("-","").replace(".","").isdigit()
                    ):
                        candidato = {
                            "name": name,
                            "kills": int(lines[j]),
                            "assists": int(lines[j+1]),
                            "deaths": int(lines[j+2]),
                            "kd": float(lines[j+3]),
                            "adr": float(lines[j+4]),
                            "kast": float(lines[j+5].replace("%","")),
                            "2k": int(lines[j+6]),
                            "3k": int(lines[j+7]),
                            "4k": int(lines[j+8]),
                            "5k": int(lines[j+9]),
                            "rating": extraer_float(lines[j+10])
                        }

                        if not mejor:
                            mejor = candidato

                except:
                    continue

            if mejor:
                if not any(clean(p["name"]) == clean(mejor["name"]) for p in players):
                    players.append(mejor)

    return players

# ========================
# PROCESAR PARTIDA
# ========================

async def procesar_texto(message, text):
    mapa, resultado = detectar_resultado_simple(text)
    players = parse_leetify(text)

    if len(players) == 0:
        return await message.channel.send("❌ No pude detectar jugadores.")

    match_id = generar_match_id(players)
    matches = cargar_json("matches.json")

    if not isinstance(matches, list):
        matches = []

    if any(m.get("id") == match_id for m in matches):
        return await message.channel.send("⚠️ Esta partida ya fue cargada.")

    for p in players:
        p["points"] = calcular_puntos(p)

    match_data = {
        "id": match_id,
        "mapa": mapa,
        "resultado": resultado,
        "win": True if resultado and "Victoria" in resultado else False,
        "players": []
    }

    for p in players:
        match_data["players"].append({
            "name": p["name"],
            "kills": p["kills"],
            "deaths": p["deaths"],
            "assists": p["assists"],
            "adr": p["adr"],
            "kast": p["kast"],
            "points": p["points"]
        })

    matches.append(match_data)
    guardar_json("matches.json", matches)

    stats = cargar_json("stats.json")
    mes = datetime.now().strftime("%Y-%m")

    if mes not in stats:
        stats[mes] = {}

    last_players = []

    for p in players:
        if clean(p["name"]) in team_clean:
            stats[mes][p["name"]] = stats[mes].get(p["name"], 0) + p["points"]

            last_players.append({
                "name": p["name"],
                "kills": p["kills"],
                "deaths": p["deaths"],
                "assists": p["assists"],
                "adr": p["adr"],
                "kast": p["kast"],
                "points": p["points"]
            })

    guardar_json("stats.json", stats)

    guardar_json("last_match.json", {
        "mes": mes,
        "mapa": mapa,
        "resultado": resultado,
        "players": last_players
    })

    color = discord.Color.green() if resultado and "Victoria" in resultado else discord.Color.red()
    embed = discord.Embed(title="📊 Resultado de la partida", color=color)

    if mapa and resultado:
        emoji = "✅" if "Victoria" in resultado else "❌"
        embed.add_field(name="🗺️ Resultado", value=f"{mapa} | {emoji} {resultado}", inline=False)

    for p in players:
        embed.add_field(
            name=f"👤 {p['name']}",
            value=(
                f"🔫 {p['kills']} / {p['deaths']} / {p['assists']} ({kd_emoji(p['kd'])} {p['kd']})\n"
                f"💥 ADR: {p['adr']}\n"
                f"🧠 KAST: {p['kast']}%\n"
                f"⭐ RATING: {p['rating']}\n"
                f"🔢 ② {p['2k']} ③ {p['3k']} ④ {p['4k']} ⑤ {p['5k']}\n"
                f"🏆 PUNTOS: {p['points']}"
            ),
            inline=False
        )

    ranking = sorted(players, key=lambda x: x["points"], reverse=True)
    texto = "━━━━━━━━━━━━━━━\n\n"

    for i, p in enumerate(ranking, 1):
        texto += f"{i}° {p['name']} → {p['points']} pts\n"

    embed.add_field(name="🏆 Ranking del equipo", value=texto, inline=False)

    await message.channel.send(embed=embed)

# ========================
# COMANDOS
# ========================

@bot.command()
async def ranking(ctx):
    stats = cargar_json("stats.json")
    partidas = contar_partidas()
    mes = datetime.now().strftime("%Y-%m")

    meses = {
        "01":"Enero","02":"Febrero","03":"Marzo","04":"Abril",
        "05":"Mayo","06":"Junio","07":"Julio","08":"Agosto",
        "09":"Septiembre","10":"Octubre","11":"Noviembre","12":"Diciembre"
    }

    mes_nombre = meses[datetime.now().strftime("%m")]
    anio = datetime.now().strftime("%Y")

    ranking = {j: stats.get(mes, {}).get(j, 0) for j in TEAM}
    ordenado = sorted(ranking.items(), key=lambda x: x[1], reverse=True)

    texto = f"🏆 Ranking {mes_nombre} {anio}\n\n"

    for i, (j, pts) in enumerate(ordenado, 1):
        pj = partidas.get(j, 0)
        prom = int(pts / pj) if pj > 0 else 0
        texto += f"{i}. {j} → {pts} pts ({pj} pj | {prom} prom)\n"

    await ctx.send(texto)

@bot.command()
async def clear(ctx):
    if ctx.author.id != OWNER_ID:
        return await ctx.send("❌ No tenés permiso.")

    guardar_json("matches.json", [])
    guardar_json("stats.json", {})
    guardar_json("last_match.json", {})

    await ctx.send("💀 Todo borrado.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    if "%" in message.content:
        await procesar_texto(message, message.content)

    await bot.process_commands(message)

bot.run(TOKEN)