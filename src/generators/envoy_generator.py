def generate_envoy_config(haproxy_config):
    envoy_config = {
        "static_resources": {
            "listeners": [],
            "clusters": []
        },
        "admin": {
            "address": {
                "socket_address": {"address": "0.0.0.0", "port_value": 9901}
            }
        }
    }

    # Conversion des backends HAProxy en clusters Envoy
    for backend_name, backend_config in haproxy_config['backends'].items():
        cluster = {
            "name": backend_name,
            "type": "STRICT_DNS",
            "lb_policy": "ROUND_ROBIN",
            "load_assignment": {
                "cluster_name": backend_name,
                "endpoints": [{
                    "lb_endpoints": []
                }]
            }
        }
        
        for server_name, server_host in backend_config.get('servers', {}).items():
            host, port = server_host.split(':')
            cluster["load_assignment"]["endpoints"][0]["lb_endpoints"].append({
                "endpoint": {
                    "address": {
                        "socket_address": {
                            "address": host,
                            "port_value": int(port)
                        }
                    }
                }
            })
        
        envoy_config["static_resources"]["clusters"].append(cluster)

    # Conversion des frontends HAProxy en listeners Envoy
    for frontend_name, frontend_config in haproxy_config['frontends'].items():
        listener = {
            "name": frontend_name,
            "address": {
                "socket_address": {
                    "address": "0.0.0.0",
                    "port_value": int(frontend_config.get('bind', '').split(':')[-1])
                }
            },
            "filter_chains": [{
                "filters": [{
                    "name": "envoy.filters.network.http_connection_manager",
                    "typed_config": {
                        "@type": "type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager",
                        "stat_prefix": frontend_name,
                        "route_config": {
                            "name": f"{frontend_name}_route",
                            "virtual_hosts": [{
                                "name": f"{frontend_name}_vhost",
                                "domains": ["*"],
                                "routes": []
                            }]
                        },
                        "http_filters": [{"name": "envoy.filters.http.router"}]
                    }
                }]
            }]
        }

        # Ajout des routes basées sur les règles 'use_backend' de HAProxy
        for key, value in frontend_config.items():
            if key.startswith('use_backend'):
                condition, backend = value.split()
                route = {
                    "match": {"prefix": "/"},
                    "route": {"cluster": backend}
                }
                if condition != 'default_backend':
                    # Ici, nous pouvons ajouter une logique plus complexe pour gérer différentes conditions
                    pass
                listener["filter_chains"][0]["filters"][0]["typed_config"]["route_config"]["virtual_hosts"][0]["routes"].append(route)

        envoy_config["static_resources"]["listeners"].append(listener)

    return envoy_config