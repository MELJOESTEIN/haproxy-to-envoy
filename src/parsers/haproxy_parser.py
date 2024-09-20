def parse_haproxy_config(file_path):
    # Initialisation de la structure de configuration
    config = {
        'global': {},
        'defaults': {},
        'frontends': {},
        'backends': {}
    }
    current_section = None

    # Ouverture et lecture du fichier de configuration
    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, 1):
            line = line.strip()
            # Ignorer les lignes vides et les commentaires
            if not line or line.startswith('#'):
                continue

            # Détection des sections principales
            if line.startswith('global'):
                current_section = 'global'
            elif line.startswith('defaults'):
                current_section = 'defaults'
            elif line.startswith('frontend'):
                current_section = 'frontends'
                frontend_name = line.split()[1]
                config['frontends'][frontend_name] = {}
            elif line.startswith('backend'):
                current_section = 'backends'
                backend_name = line.split()[1]
                config['backends'][backend_name] = {}
            elif current_section:
                # Traitement des lignes dans les sections global et defaults
                if current_section in ['global', 'defaults']:
                    try:
                        key, value = line.split(maxsplit=1)
                        config[current_section][key] = value
                    except ValueError:
                        print(f"Warning: Unable to parse line {line_number}: '{line}'. Skipping.")
                # Traitement des lignes dans les sections frontends et backends
                elif current_section in ['frontends', 'backends']:
                    section_name = list(config[current_section].keys())[-1]
                    # Traitement spécial pour les lignes de définition de serveur
                    if line.startswith('server'):
                        parts = line.split()
                        if len(parts) >= 3:
                            server_name = parts[1]
                            server_host = parts[2]
                            config[current_section][section_name].setdefault('servers', {})[server_name] = server_host
                        else:
                            print(f"Warning: Invalid server definition at line {line_number}: '{line}'. Skipping.")
                    else:
                        # Traitement des autres options dans frontends et backends
                        try:
                            key, value = line.split(maxsplit=1)
                            config[current_section][section_name][key] = value
                        except ValueError:
                            print(f"Warning: Unable to parse line {line_number}: '{line}'. Skipping.")
            else:
                # Avertissement pour les lignes en dehors de toute section connue
                print(f"Warning: Line {line_number} outside of any section: '{line}'. Skipping.")

    return config