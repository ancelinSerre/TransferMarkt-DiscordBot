import json
from datetime import datetime

import discord
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
        joke = ""
        mkt_txt_content = ""
        if market_value == "-":
            mkt_txt_content = (
                f"\n:white_small_square: **{player.data['player']}** n'a pas encore de valeur marchande sur TransferMarkt"
                + f"\n:white_small_square: Pépite ?"
            )
        else:
            mkt_txt_content = (
                f"\n:white_small_square: **{player.data['player']}** a une valeur marchande de **{market_value}** 💶 selon TransferMarkt"
                + f"\n:white_small_square: Dernière mise à jour le **{player.last_update}**"
            )
            mvs = market_value.split(" ")
            mv = float(mvs[0].replace(",", ".")) * (1000 if mvs[1] == "K€" else 1000000)
            if mv > 1500000:
                joke = "*Tu rêves ! Nous sommes les épiciers du foot, dois-je te le rappeler ?*"
            elif mv >= 1000000:
                joke = "*Hum... un peu juste, il va falloir en parler au Patron*"
            elif mv >= 500000:
                joke = "*Ok, avec un panier garni et un bon salaire ça peut peut-être passer...*"
            elif mv >= 250000:
                joke = "*C'est presque trop cher... t'es sûr de toi ?*"
            else:
                joke = "*Je sais pas pourquoi mais ça sent la pépite, tu le sens toi aussi ?*"

        response_mkt_content = (
            f">>> Voilà ce que j'ai trouvé    :arrow_down:\n{mkt_txt_content}"
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
        if joke != "":
            await ctx.send(joke)

        await ctx.send(player.player_page_url)
    except:
        await ctx.send("Désolé, je n'ai pas trouvé de joueur avec ta requête !")

bets = {
    "user": "",
    "competition": "",
    "round": "",
    "bets": {}
}


@bot.command()
async def prono(ctx, *args):
    if len(args) >= 1:
        choices = ["1️⃣", "🇳", "2️⃣"]
        if args[0] == "ok":
            for match in bets["bets"]:
                cache_msg = discord.utils.get(bot.cached_messages, id=bets["bets"][match])
                curr_reacs = cache_msg.reactions
                for cr in curr_reacs:
                    if cr.count == 2 and str(cr) in choices:
                        bets["bets"][match] = str(cr)
                        break

            for match in bets["bets"]:
                bet = bets["bets"][match] 
                if bet == "1️⃣":
                    bets["bets"][match] = 1
                elif bet == "🇳":
                    bets["bets"][match] = 0
                elif bet == "2️⃣":
                    bets["bets"][match] = 2
                
            already_played = False
            all_bets = []
            with open(f"bets/{bets['competition']}.json", "r", encoding="utf8") as f:
                all_bets = json.loads(f.read())
                for b in all_bets:
                    if bets["user"] == b["user"] and bets["round"] == b["round"]:
                        await ctx.message.author.send("Tu as déjà joué pour cette journée ! Tu ne peux pas modifier ton pari...")
                        already_played = True
                        break

            if not already_played:
                all_bets.append(bets)
                with open(f"bets/{bets['competition']}.json", "w", encoding="utf8") as f:
                    f.write(json.dumps(all_bets))
                    await ctx.message.author.send("Ton pari pour cette journée a été enregistré !")

        if args[0] == "grille":
            matches = {}
            with open("matches/euro2020.json", "r", encoding="utf8") as f:
                matches = json.loads(f.read())

            now = datetime.now()
            latest_match_date = ""
            current_round = ""
            for c_round in matches:
                latest_match_date = datetime.strptime(matches[c_round][0]["date"], "%d/%m/%Y")
                for match in matches[c_round]:
                    curr_match_date = datetime.strptime(match["date"], "%d/%m/%Y")
                    if curr_match_date > latest_match_date:
                        latest_match_date = curr_match_date

                if latest_match_date > now:
                    current_round = c_round
                    break

            bet_matches = [x for x in matches[current_round] if datetime.strptime(x["date"], "%d/%m/%Y") > now]
                
            first_message = ">>> \n"
            first_message += f" :soccer: :flag_eu: **Euro 2020** :arrow_right: *{current_round} :* \n"
            await ctx.send(first_message)
            for match in bet_matches:
                opponents = match['match'].split('|')
                match_str = f"**{opponents[0]}**  {match['flags'][0]}    :vs:    {match['flags'][1]}  **{opponents[1]}**"
                await ctx.send(f":white_small_square: [{match['date']}]\n     {match_str}")

            await ctx.send(">>> Envoi la commande `.prono` sur le serveur ou directement à moi-même en DM si tu veux jouer :wink:\n")

    else:

        user = ctx.message.author
        bets["user"] = f"{user.display_name}_{user.id}"
        bets["competition"] = "euro2020"

        matches = {}
        with open("matches/euro2020.json", "r", encoding="utf8") as f:
            matches = json.loads(f.read())

        now = datetime.now()
        latest_match_date = ""
        current_round = ""
        for c_round in matches:
            latest_match_date = datetime.strptime(matches[c_round][0]["date"], "%d/%m/%Y")
            for match in matches[c_round]:
                curr_match_date = datetime.strptime(match["date"], "%d/%m/%Y")
                if curr_match_date > latest_match_date:
                    latest_match_date = curr_match_date

            if latest_match_date > now:
                current_round = c_round
                break

        bets["round"] = current_round
        bet_matches = [x for x in matches[current_round] if datetime.strptime(x["date"], "%d/%m/%Y") > now]
            
        first_message = ">>> \n"
        first_message += f" :soccer: :flag_eu: **Euro 2020** :arrow_right: *{current_round} :* \n"
        await user.send(first_message)
        for match in bet_matches:
            opponents = match['match'].split('|')
            match_str = f"**{opponents[0]}**  {match['flags'][0]}    :vs:    {match['flags'][1]}  **{opponents[1]}**"
            curr_match = await user.send(f":white_small_square: [{match['date']}]\n     {match_str}")
            await curr_match.add_reaction("1️⃣")
            await curr_match.add_reaction("🇳")
            await curr_match.add_reaction("2️⃣")

            bets["bets"][match["match"]] = curr_match.id
        
        await user.send(
            ">>> Pour jouer, clique sur les emotes en dessous de chaque match, [1 = Equipe 1 etc.]\nEnvoi la commande `.prono ok` quand tu as terminé :wink:\nTes pronos seront ensuite sauvegardés dans la base de données"
        )
    

discord_secret = ""
with open("credentials.json", "r") as f:
    discord_secret = json.loads(f.read())["discord-secret"]

bot.run(discord_secret)