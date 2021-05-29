import json

from discord.ext import commands

from playerscraper import PlayerScraper

bot = commands.Bot(command_prefix=".")

@bot.command()
async def info(ctx, *args):
    player_name = " ".join(args)
    await ctx.send(f"🕵️‍♂️ Je vais me renseigner à propos de {player_name} ...")
    try:
        # Scrap data about the player
        player = PlayerScraper(player_name)
        market_value = player.market_value
        response_mkt_content = (
            f">>> Voilà ce que j'ai trouvé    :arrow_down:\n"
            + f"\n:white_small_square: **{player.data['player']}** a une valeur marchande de **{market_value}** 💶 selon TransferMarkt"
            + f"\n:white_small_square: Dernière mise à jour le **{player.last_update}**"
            + "\n"
            + f"\n:globe_with_meridians:    **Nationalité** : {' - '.join(player.data.get('Nationalité', '-').split())}"
            + f"\n:date:    **Âge** : {player.data.get('Âge', '-')}, ({player.data.get('Date de naissance', '-')})"
            + f"\n:man_lifting_weights:    **Taille** : {player.data.get('Taille', '-')}"
            + f"\n:foot:    **Pied** : {player.data.get('Pied', '-')}"
            + f"\n:tools:    **Position** : {player.data.get('Position', '-')}"
            + f"\n:soccer:    **Club actuel** : {player.data.get('Club actuel', '-')}"
            + f"\n:clock2:    **Fin du contrat** : {player.data.get('Contrat jusqu’à', '-')}\n"
        )
        await ctx.send(response_mkt_content)
        mvs = market_value.split(" ")
        mv = float(mvs[0].replace(",", ".")) * (1000 if mvs[1] == "K€" else 1000000)
        if mv > 1500000:
            await ctx.send("*Tu rêves ! Nous sommes les épiciers du foot, dois-je te le rappeler ?*")
        elif mv >= 1000000:
            await ctx.send("*Hum... un peu juste, il va falloir en parler au Patron*")
        elif mv >= 500000:
            await ctx.send("*Ok, avec un panier garni et un bon salaire ça peut peut-être passer...*")
        elif mv >= 250000:
            await ctx.send("*C'est presque trop cher... t'es sûr de toi ?*")
        else:
            await ctx.send("*Je sais pas pourquoi mais ça sent la pépite, tu le sens toi aussi ?*")
        
        await ctx.send(player.player_page_url)
    except:
        await ctx.send("Désolé, je n'ai pas trouvé de joueur avec ta requête !")
    

discord_secret = ""
with open("credentials.json", "r") as f:
    discord_secret = json.loads(f.read())["discord-secret"]

bot.run(discord_secret)