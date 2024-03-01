import configparser
import os
import logging
import requests
import ark

import discord
from discord import Message

logging.basicConfig(filename='/var/log/ark-bot.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s : %(message)s')

config = configparser.ConfigParser()
config.read("/home/regateiro/.config/ark-bot/config.ini")

class ArkBot(discord.Client):
    def __init__(self, intents):
        super().__init__(
            command_prefix="!ark",
            intents=intents,
            help_command=None
        )

    async def on_ready(self):
        logging.info('Logged on as {0}!'.format(self.user))

    async def on_message(self, message: Message):
        try:
            # Do not process non-bot commands
            if not message.content.startswith('!ark'):
                return

            # Accept messages from the DND or test guild only
            if str(message.guild.id) not in ["904457286574018631"]:
                await message.channel.send("Unauthorized guild.")
                return

            # Process messages from Sieg, Tasia or me only
            if str(message.author.id) not in [
                "191582418094915585",
                "190577161038594048",
                "66891112857477120"
            ]:
                await message.channel.send("Unauthorized user.")
                return

            fields = message.content.lower().split(' ')

            # Ensure a command is passed
            if len(fields) < 2:
                await message.channel.send("Incorrect number of parameters. Use `!ark help` for help.")

            # Start the server
            elif fields[1] == "start":
                # Clear the Public IP cache
                os.remove(config['Ark']['PublicIP'])
                # Execute the command
                await message.channel.send("Starting the server...")
                os.popen(f"{config['Ark']['Executable']} start").read()
                await message.channel.send("Done. It may take a few minutes for the server to show.")

            # Stop the server
            elif fields[1] == "stop":
                # Execute the command
                await message.channel.send("Stopping the server...")
                os.popen(f"{config['Ark']['Executable']} stop").read()
                await message.channel.send("Done.")

            # Restart the server
            elif fields[1] == "restart":
                # Clear the Public IP cache
                os.remove(config['Ark']['PublicIP'])
                # Execute the command
                await message.channel.send("Restarting the server...")
                os.popen(f"{config['Ark']['Executable']} restart").read()
                await message.channel.send("Done. It may take a few minutes for the server to show.")

            # Check server status
            elif fields[1] == "status":
                running = False
                listed = True

                if len(os.popen("pidof ShooterGameServer").read()) > 0:
                    running = True

                if "not listed" in os.popen(f"{config['Ark']['Executable']} details").read():
                    listed = False

                await message.channel.send(f"Server is {'NOT ' if not running else ''}running and {'NOT ' if not listed else ''}listed.")

            # Process mod commands
            elif fields[1] == "mods":
                # Ensure mod has a subcommand
                if len(fields) < 3:
                    await message.channel.send("Incorrect number of parameters. Use `!ark help` for help.")
            
                elif fields[2] == "list":
                    # Get the list of mods
                    mods = ark.manage_mods(config)
                    
                    # Build the response
                    response = "Server mods:\n"
                    for mod in mods:
                        response = f"{response}- {mod}\n"
                    
                    # Return the list of mods
                    await message.channel.send(response)
            
                elif fields[2] == "add":
                    # Ensure there are mods to add
                    if len(fields) < 4:
                        await message.channel.send("Incorrect number of parameters. Use `!ark help` for help.")
                        return
                    
                    # Get the list of mods to add and ensure they are strings
                    mods_to_add = [str(m) for m in fields[3:]]
                    
                    # Add the mods
                    mods = ark.manage_mods(config, add=mods_to_add)
                    
                    # Respond
                    if mods is None:
                        await message.channel.send("Invalid mod value received.")
                    else:
                        await message.channel.send("Mods added successfully, please restart the server.")
                
                elif fields[2] == "remove":
                    # Ensure there are mods to remove
                    if len(fields) < 4:
                        await message.channel.send("Incorrect number of parameters. Use `!ark help` for help.")
                        return
                    
                    # Get the list of mods to add and ensure they are strings
                    mods_to_remove = [str(m) for m in fields[3:]]
                    
                    # Remove the mods
                    mods = ark.manage_mods(config, remove=mods_to_remove)
                    
                    # Respond
                    if mods is None:
                        await message.channel.send("Invalid mod value received.")
                    else:
                        await message.channel.send("Mods removed successfully, please restart the server.")

            # Process configuration commands
            elif fields[1] == "config":
                # Ensure config has a subcommand
                if len(fields) < 3:
                    await message.channel.send("Incorrect number of parameters. Use `!ark help` for help.")

                elif fields[2] == "get":
                    # Build the list of parameters required by pastebin
                    params = {
                        "api_dev_key": config['Pastebin']['ApiDevKey'],
                        "api_user_key": config['Pastebin']['ApiUserKey'],
                        "api_paste_code": None,
                        "api_paste_private": 1,
                        "api_paste_name": None,
                        "api_paste_expire_date": "10M",
                        "api_paste_format": "ini",
                        "api_option": "paste"
                    }

                    # Read configuration files
                    with open(config['Ark']['GameUserSettingsIni']) as f:
                        data = f.read()

                    # Create the pastebin
                    params["api_paste_name"] = "GameUserSettings.ini"
                    params["api_paste_code"] = data
                    gus_ini_url = requests.post("https://pastebin.com/api/api_post.php", data=params)


                    # Read configuration files
                    with open(config['Ark']['GameIni']) as f:
                        data = f.read()

                    # Create the pastebin
                    params["api_paste_name"] = "Game.ini"
                    params["api_paste_code"] = data
                    game_ini_url = requests.post("https://pastebin.com/api/api_post.php", data=params)

                    # Send the links
                    await message.channel.send(
                        "Ark configuration files:\n"
                        f"- [GameUserSettings.ini]({gus_ini_url.text})\n"
                        f"- [Game.ini]({game_ini_url.text})"
                    )

                elif fields[2] == "set-gus" or fields[2] == "set-game":
                # Ensure config has a parameter
                    if len(fields) < 4:
                        await message.channel.send("Incorrect number of parameters. Use `!ark help` for help.")
                        return

                    # Select the requested target
                    if fields[2] == "set-gus":
                        target = config['Ark']['GameUserSettingsIni']
                    else:
                        target = config['Ark']['GameIni']

                    # Get the pastebin id
                    pastebin_id = message.content.split(' ')[3].split("/")[-1]

                    # Get the config file
                    url = f"https://pastebin.com/raw/{pastebin_id}"
                    target_content = requests.get(url).text
                    
                    # Sanity Check
                    if fields[2] == "set-gus" and "[ServerSettings]" not in target_content:
                        await message.channel.send("Expected section not found in the file. Aborting!")
                        return
                    elif fields[2] == "set-game" and "[ModInstaller]" not in target_content:
                        await message.channel.send("Expected section not found in the file. Aborting!")
                        return
                    
                    # Write the new configuration to file
                    with open(target, 'w') as out:
                        out.write(target_content)
                    
                    # Provide feedback
                    await message.channel.send("The configuration has been updated, please restart the server.")

            # Send the help message
            elif fields[1] == "help":
                await message.channel.send(
                    'Available Commands:\n'
                    '```'
                    '!ark start                       # Starts the server.\n'
                    '!ark stop                        # Stops the server.\n'
                    '!ark restart                     # Restarts the server.\n'
                    '!ark status                      # Checks the status of the server.\n\n'
                    '!ark config get                  # Gets the server configuration. Links expire in 10 minutes.\n'
                    '!ark config set-gus <pastebin>   # Sets the GameUserSettings.ini file. Provide a pastebin (https://pastebin.com/) link to the file.\n'
                    '!ark config set-game <pastebin>  # Sets the Game.ini file. Provide a pastebin (https://pastebin.com/) link to the file.\n\n'
                    '!ark mods list                   # Gets the list of mods currently configured on the server.\n'
                    '!ark mods add <id> [id] ...      # Adds a list of mods to the server configuration.\n'
                    '!ark mods remove <id> [id] ...   # Removes a list of mods to the server configuration.\n'
                    '```'
                )
            
            else:
                await message.channel.send("Incorrect number of parameters or unknown command. Use `!ark help` for help.")
                
        except:
            await message.channel.send("An error occurred while processing your request. Use `!ark help` for help.")


intents = discord.Intents.default()
intents.message_content = True
client = ArkBot(intents)
client.run(config['Discord']['Token'])