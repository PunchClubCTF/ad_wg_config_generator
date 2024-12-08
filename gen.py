import subprocess
import os
import shutil
import yaml

from config.Server import ServerBuilder
from config.Vuln import VulnConfFactoryBuilder

if __name__ == "__main__":
    # Load configuration from YAML file using absolute path
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)

    base_folder = config['base_folder']

    # Extract network configuration
    main_external_ip = config['network']['main_server']['external_ip']
    main_server_subnet = config['network']['main_server']['subnet']
    main_internal_ip = config['network']['main_server']['internal_ip']
    main_server_port = config['network']['main_server']['port']

    vulns_subnet = config['network']['vulns']['subnet']
    vulns_port = config['network']['vulns']['port']

    users_subnet = config['network']['users']['subnet']

    team_members = config['team_settings']['total_members']

    server = (ServerBuilder()
          .set_external_ip(main_external_ip)
          .set_internal_ip(main_internal_ip)
          .set_internal_subnet(main_server_subnet)
          .build())

    factory = (VulnConfFactoryBuilder()
               .set_internal_subnet(vulns_subnet)
               .set_users_subnet   (users_subnet)
               .set_team_members   (team_members)
               .build())

    teams = list()
    for team_config in config['team_settings']['teams']:
        teams.append(factory.create_vuln(team_config['external_ip'], team_config['name']))

    print(server)
    print(server.generate_keys())

    if os.path.exists(base_folder):
        shutil.rmtree(f"{base_folder}")

    for team in teams:
        output_dir = f"{base_folder}/{team.name}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for member in team.members:
            with open(f"{output_dir}/{member.name}.conf", "w") as member_file:
                member_file.write(member.config)

        # Compress the team's files
        shutil.make_archive(f"{output_dir}", 'zip', f"{output_dir}")