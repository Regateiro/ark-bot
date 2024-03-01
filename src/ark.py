import requests

def manage_mods(config: dict, add: list = [], remove: list = []) -> list:
    mods = []
    lines = []
    
    # Double check that the strings are all numeric
    for mod in (add + remove):
        if not mod.isnumeric():
            return None
    
    # Read configuration file
    with open(config['Ark']['GameUserSettingsIni']) as f:
        # Read the configuration file
        lines = f.readlines()
        
        # Parse the configuration file
        for i, line in enumerate(lines):
            
            # Find the mods in the config
            if line.startswith("ActiveMods"):
                
                # Parse the list of mods
                mods = line.rstrip('\n').split("=")[1].split(",")
                
                # Add desired mods
                for m in add:
                    mods.append(m)
                
                # Remove desired mods
                mods = [m for m in mods if m not in remove]
                
                # Update the list of mods
                lines[i] = f"ActiveMods={','.join(mods)}\n"
                
                # Break the for cycle
                break
        
    # Write the new configuration
    with open(config['Ark']['GameUserSettingsIni'], mode="w") as f:
        f.writelines(lines)

    # Read configuration file
    with open(config['Ark']['GameIni']) as f:
        # Read the configuration file
        lines = f.readlines()
        
        # Parse the configuration file
        for i, line in enumerate(lines):
            
            # Find the mods in the config
            if line.startswith("ModIDS"):
                
                # Update the list of mods
                lines[i] = f"ModIDS={','.join(mods)}\n"
                
                # Break the for cycle
                break
        
    # Write the new configuration
    with open(config['Ark']['GameIni'], mode="w") as f:
        f.writelines(lines)
    
    # Return the list of mods
    return mods