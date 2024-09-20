from src.parsers.haproxy_parser import parse_haproxy_config
from src.generators.envoy_generator import generate_envoy_config
from src.utils.config_utils import save_yaml

def main():
    haproxy_file = "config/haproxy.cfg"  # Chemin vers le fichier de configuration HAProxy
    envoy_file = "output/envoy.yaml"  # Fichier de sortie pour la configuration Envoy
    
    haproxy_config = parse_haproxy_config(haproxy_file)
    envoy_config = generate_envoy_config(haproxy_config)
    
    save_yaml(envoy_config, envoy_file)
    print(f"Configuration Envoy générée et sauvegardée dans {envoy_file}")

if __name__ == "__main__":
    main()