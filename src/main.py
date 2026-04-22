import os; from os import path
import json, io, asyncio
import discord as dc
import util, helper


#TODO: functions in main to reduce code redundancy!

async def check_user(client: dc.Client, user_id:str) -> bool:
    if not util.validate_user_id(user_id, verbose=True):
        return False
    user = await client.fetch_user(int(user_id))
    if user:
        print(f"RESOLVED: User ID <{user_id}> is @{user.name} \'{user.display_name}\'")
        return True
    else:
        print(f'WARNING: User ID <{user_id}> could not be resolved!')
        return False


class MyClient(dc.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")
        try:
            synced = await tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

        print("Checking Masters:")
        for user_id in util.load_masters():
            user_id = user_id.replace('\n', '')
            await check_user(client, user_id)
        
        print('CLIENT READY!')

    async def on_message(self, msg):
        try:
            print(f"[{msg.guild.name}]#{msg.channel.name} @{msg.author.name}: {msg.content}")
        except:
            pass

intents = dc.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
tree = dc.app_commands.CommandTree(client)

@tree.command(name="test", description="test command")
async def test_command(
    interaction: dc.Interaction
):
    await interaction.response.send_message('Hello World')
    if util.check_master(interaction.user.id):
        print('All shall bow to you almighty master ' + interaction.user.display_name)
    return

@tree.command(name="list_masters", description="List all registered Gamemasters")
async def list_masters(
    interaction: dc.Interaction,
    silent_reply: bool = True
):
    await interaction.response.defer(ephemeral=silent_reply)
  
    out = 'Registered Gamemasteres:\n'

    for user_id in util.load_masters():
        user_id = user_id.replace('\n', '')
        user = None
        if await check_user(client, user_id):
            user = await client.fetch_user(int(user_id))
            out += f"- {user.name}\n"

    await interaction.followup.send(out, ephemeral=silent_reply)
    return

@tree.command(name="list_players", description="MASTER ONLY: List all registered Players")
async def list_players(
    interaction: dc.Interaction,
    silent_reply: bool = True
):
    await interaction.response.defer(ephemeral=True)
    if not (util.check_master(interaction.user.id)):
        await interaction.followup.send(util.WARNING_NOT_A_MASTER, ephemeral=True)
        return

    out = 'Registered Players:\n'

    for user_id in util.load_players():
        user_id = user_id.replace('\n', '')
        user = None
        if await check_user(client, user_id):
            user = await client.fetch_user(int(user_id))
            out += f"- {user.name}\n"

    await interaction.followup.send(out, ephemeral=silent_reply)
    return

@tree.command(name="add_player", description="MASTER ONLY: Adds a Player to the Directory")
async def add_player(
    interaction: dc.Interaction,
    player: dc.Member,
    silent_reply: bool = True
):
    await interaction.response.defer(ephemeral=silent_reply)

    if not (util.check_master(interaction.user.id)):
        await interaction.followup.send(util.WARNING_NOT_A_MASTER, ephemeral=silent_reply)
        return

    reply = util.REPLIES_ADD_PLAYER[util.add_player(player.id)]
    reply += f" <{player.id}> @{player.name}"

    print(reply)
    await interaction.followup.send(reply, ephemeral=silent_reply)
    return

@tree.command(name="remove_player", description="MASTER ONLY: Removes a Player from the Directory")
async def remove_player(
    interaction: dc.Interaction,
    player: dc.Member,
    #clear_directory: bool = False, #TODO implement clear directory?
    silent_reply: bool = True
):
    await interaction.response.defer(ephemeral=silent_reply)
    
    if not (util.check_master(interaction.user.id)):
        await interaction.followup.send(util.WARNING_NOT_A_MASTER, ephemeral=silent_reply)
        return

    reply = util.REPLIES_REMOVE_PLAYER[util.remove_player(player.id)]
    reply += f" <{player.id}> @{player.name}"

    print(reply)
    await interaction.followup.send(reply, ephemeral=silent_reply)
    return

#TODO: fix this shit
@tree.command(name="upload_character", description="Upload a character.json")
async def upload_character(
    interaction: dc.Interaction,
    upload_file: dc.Attachment,
    silent_reply: bool = True
):
    await interaction.response.defer(ephemeral=silent_reply)
    
    if not (util.check_player(interaction.user.id)):
        await interaction.followup.send(util.WARNING_NOT_A_PLAYER, ephemeral=silent_reply)
        return
     
    try:
        util.create_player_dir(interaction.user.id)
    except:
        await interaction.followup.send('ERROR: Could not create Player dir', ephemeral=silent_reply)
        return

    if not helper.validate_file_name(upload_file.filename, 'json'):
        await interaction.followup.send('ERROR: File must be .json', ephemeral=silent_reply)
        return

    if upload_file.size > util.MAX_CHAR_FILE_SIZE['INT']:
        await interaction.followup.send('ERROR: File size exceeds ' + util.MAX_CHAR_FILE_SIZE['STR'], ephemeral=silent_reply)
        return
    
    #TODO: Harder file validation?
    json_cache = {}
    try:
        f = await upload_file.read()
        json_cache = json.loads(f.decode('UTF-8'))
    except Exception as e:
        print(e)
        await interaction.followup.send('ERROR: File could not be converted into JSON object', ephemeral=silent_reply)
        return

    reply = util.REPLIES_ADD_CHAR[util.add_character(
        interaction.user.id,
        upload_file.filename,
        json_cache
    )]
    reply += f" {upload_file.filename}"

    print(reply)
    await interaction.followup.send(reply, ephemeral=silent_reply)
    return

#TODO: try catch
@tree.command(name="list_characters", description="List all uploaded characters from a player")
async def list_characters(
    interaction: dc.Interaction,
    player: dc.Member = None,
    silent_reply: bool = True
): 
    await interaction.response.defer(ephemeral=silent_reply)
    
    if player is None:
        player = interaction.user
    if not util.check_player(player.id):
        await interaction.followup.send(util.WARNING_NOT_A_PLAYER, ephemeral=silent_reply)
        return
    if not interaction.user.id == player.id:
        if not util.check_master(interaction.user.id):
            await interaction.followup.send(util.WARNING_NOT_A_MASTER, ephemeral=silent_reply)
            return
    
    reply = f"@{player.name}'s characters:"
    for char in util.list_characters(player.id):
        if char != 'ACTIVE_CHAR':
            reply += f"\n- {char.split('.')[0]}"
    
    await interaction.followup.send(reply, ephemeral=silent_reply)
    return


@tree.command(name="select_character", description="Select a character to use commands on")
async def select_character(
    interaction: dc.Interaction,
    file_name: str
):
    await interaction.response.defer(ephemeral=True)

    if not util.check_player(interaction.user.id):
        await interaction.followup.send(util.WARNING_NOT_A_PLAYER, ephemeral=True)
        return

    file_name = file_name.replace('.json', ''); file_name += '.json'
    util.change_character(interaction.user.id, file_name)
    
    await interaction.followup.send('Character selected!', ephemeral=True)
    return

@tree.command(name="remove_character", description="Remove character from your directory")
async def remove_character(
    interaction: dc.Interaction,
    file_name: str
):
    await interaction.response.defer(ephemeral=True)

    if not util.check_player(interaction.user.id):
        await interaction.followup.send(util.WARNING_NOT_A_PLAYER, ephemeral=True)
        return

    file_name = file_name.replace('.json', ''); file_name += '.json'
    

    await interaction.followup.send('Character removed!', ephemeral=True)
    return

@tree.command(name="show_info", description="Shows info of the selected player character")
async def show_info(
    interaction: dc.Interaction,
    player: dc.Member = None,
    silent_reply: bool = True
):    
    await interaction.response.defer(ephemeral=silent_reply)
    
    if player is None:
        player = interaction.user
    if not util.check_player(player.id):
        await interaction.followup.send(util.WARNING_NOT_A_PLAYER, ephemeral=silent_reply)
        return
    if not interaction.user.id == player.id:
        if not util.check_master(interaction.user.id):
            await interaction.followup.send(util.WARNING_NOT_A_MASTER, ephemeral=silent_reply)
            return
    
    if player.id not in util.PLAYER_CHARACTER_CACHE.keys():
        util.cache_player_character(player.id)
    
    char = util.PLAYER_CHARACTER_CACHE[player.id]
    await interaction.followup.send(char.showInfo(), ephemeral=silent_reply)
    return

@tree.command(name="show_attributes", description="Shows attributes of the selected player character")
async def show_attributes(
    interaction: dc.Interaction,
    player: dc.Member = None,
    silent_reply: bool = True
):    
    await interaction.response.defer(ephemeral=silent_reply)
    
    if player is None:
        player = interaction.user
    if not util.check_player(player.id):
        await interaction.followup.send(util.WARNING_NOT_A_PLAYER, ephemeral=silent_reply)
        return
    if not interaction.user.id == player.id:
        if not util.check_master(interaction.user.id):
            await interaction.followup.send(util.WARNING_NOT_A_MASTER, ephemeral=silent_reply)
            return
    
    if player.id not in util.PLAYER_CHARACTER_CACHE.keys():
        util.cache_player_character(player.id)
    
    char = util.PLAYER_CHARACTER_CACHE[player.id]
    await interaction.followup.send(char.showAttributes(), ephemeral=silent_reply)
    return

@tree.command(name="show_talents", description="Shows talents of the selected player character")
async def show_talents(
    interaction: dc.Interaction,
    id_1: int = 0,
    id_2: int = 58,
    player: dc.Member = None,
    silent_reply: bool = True
):
    await interaction.response.defer(ephemeral=silent_reply)
    
    if player is None:
        player = interaction.user
    if not util.check_player(player.id):
        await interaction.followup.send(util.WARNING_NOT_A_PLAYER, ephemeral=silent_reply)
        return
    if not interaction.user.id == player.id:
        if not util.check_master(interaction.user.id):
            await interaction.followup.send(util.WARNING_NOT_A_MASTER, ephemeral=silent_reply)
            return
    
    if player.id not in util.PLAYER_CHARACTER_CACHE.keys():
        util.cache_player_character(player.id)
    
    char = util.PLAYER_CHARACTER_CACHE[player.id]
    buffer = char.showTalente([id_1, id_2])

    try:
        inMemoryFile = io.BytesIO()
        writer = io.BufferedWriter(raw=inMemoryFile)

        writer.write(buffer.encode('utf-8'))
        
        writer.flush()
        inMemoryFile.seek(0)

        await interaction.followup.send(
            content = f"Show talents of @{player.name}'s chararcter: {char.info['name']}",
            file = dc.File(fp = inMemoryFile, filename='talents.txt'),
            ephemeral=silent_reply
            )
    except Exception as e:
        print(e)
        await interaction.followup.send("error, to be explained", ephemeral=silent_reply)
    finally:
        writer.close()
        inMemoryFile.close()

    return

@tree.command(name="roll_dice", description="Rolls times d size")
async def roll_dice(
    interaction: dc.Interaction,
    size: int,
    times: int,
    silent_reply: bool = False
):
    await interaction.response.defer(ephemeral=silent_reply)

    await interaction.followup.send(util.dice_roll_string(times, size), ephemeral=silent_reply)
    
    return

@tree.command(name="roll_attribute", description="Rolls on an attribute of a selected player character")
async def roll_talent(
    interaction: dc.Interaction,
    id: str,
    mod: int = 0,
    player: dc.Member = None,
    silent_reply: bool = False
):
    await interaction.response.defer(ephemeral=silent_reply)
    
    if player is None:
        player = interaction.user
    if not util.check_player(player.id):
        await interaction.followup.send(util.WARNING_NOT_A_PLAYER, ephemeral=silent_reply)
        return
    if not interaction.user.id == player.id:
        if not util.check_master(interaction.user.id):
            await interaction.followup.send(util.WARNING_NOT_A_MASTER, ephemeral=silent_reply)
            return

    if player.id not in util.PLAYER_CHARACTER_CACHE.keys():
        util.cache_player_character(player.id)

    char = util.PLAYER_CHARACTER_CACHE[player.id]
    await interaction.followup.send(char.doProbeAttribut(id, mod), ephemeral=silent_reply)
    
    return


@tree.command(name="roll_talent", description="Rolls on a talent of a selected player character")
async def roll_talent(
    interaction: dc.Interaction,
    id: int,
    mod: int = 0,
    player: dc.Member = None,
    silent_reply: bool = False
):
    await interaction.response.defer(ephemeral=silent_reply)
    
    if player is None:
        player = interaction.user
    if not util.check_player(player.id):
        await interaction.followup.send(util.WARNING_NOT_A_PLAYER, ephemeral=silent_reply)
        return
    if not interaction.user.id == player.id:
        if not util.check_master(interaction.user.id):
            await interaction.followup.send(util.WARNING_NOT_A_MASTER, ephemeral=silent_reply)
            return

    if player.id not in util.PLAYER_CHARACTER_CACHE.keys():
        util.cache_player_character(player.id)

    char = util.PLAYER_CHARACTER_CACHE[player.id]
    await interaction.followup.send(char.doProbeTalent(id, mod).getResultStr(), ephemeral=silent_reply)

def main() -> None:
    util.setup_res()
    try:
        with open(path.join(util.RES_PATH, 'TOKEN'), 'r') as file:
            os.environ['TOKEN'] = file.readline()
    except Exception as e:
        print(f"{e}\nERROR: Could not read TOKEN file")
        exit()

    client.run(os.environ['TOKEN'])

if __name__ == '__main__':
    main()