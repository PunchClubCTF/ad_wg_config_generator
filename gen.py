import subprocess
import os
import shutil
import yaml
from jinja2 import Template


from config.Server import ServerBuilder
from config.Vuln import VulnFactoryBuilder

def create_configs(server, teams):
    with open("templates/server.template", "r") as template_file:
        server_template = template_file.read()

    with open("templates/vuln.template", "r") as template_file:
        vuln_template = template_file.read()

    with open("templates/member.template", "r") as template_file:
        member_template = template_file.read()
    
    with open("templates/vuln_peer.template", "r") as template_file:
        vuln_peer_template = template_file.read()

    with open("templates/member_peer.template", "r") as template_file:
        member_peer_template = template_file.read()


    for team in teams:
        template = Template(vuln_template)

        team.config = template.render(
            vuln_ip = team.internal_subnet,
            vuln_private_key = team.get_private_key(),
            vuln_port = vulns_port,
            server_public_key = server.get_public_key(),
            server_subnet = main_server_subnet,
            vulns_subnet = vulns_subnet,
            users_subnet = users_subnet,
            server_endpoint = f"{server.external_ip}:{server.port}",
        )

        for member in team.members:
            template = Template(member_template)

            member.config = template.render(
                member_ip = member.ip + '/32',
                member_private_key = member.get_private_key(),
                server_public_key = server.get_public_key(),
                server_subnet = main_server_subnet,
                vulns_subnet = vulns_subnet,
                users_subnet = users_subnet,
                server_endpoint = f"{server.external_ip}:{server.port}",
            )
    
    template = Template(server_template)

    server.config = template.render(
        server_ip = f"{server.internal_ip}/{main_server_subnet.split("/")[1]}",
        server_private_key = server.get_private_key(),
        server_port = server.port
    )

    for team in teams:
        server.config += f"\n\n# ======================= {team.name} =========================\n\n"

        template = Template(vuln_peer_template)

        config = template.render(
            public_key = team.get_public_key(),
            ip = team.internal_subnet,
            endpoint = f"{team.external_ip}:{vulns_port}"
        )

        server.config += config + "\n"

        for member in team.members:
            template = Template(member_peer_template)

            config = template.render(
                public_key = member.get_public_key(),
                ip = member.ip + '/32',
                endpoint = f"{team.external_ip}:{vulns_port}"
            )

            server.config += f"\n#  {member.name}\n" + config
            

if __name__ == "__main__":
    # Load configuration from YAML file using absolute path
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)

    base_folder = config['base_folder']
    vulns_folder = config['vulns_folder']

    # Extract network configuration
    main_server_subnet = config['network']['main_server']['subnet']
    main_internal_ip = config['network']['main_server']['internal_ip']
    main_external_ip = config['network']['main_server']['external_ip']
    main_server_port = config['network']['main_server']['port']

    vulns_subnet = config['network']['vulns']['subnet']
    vulns_port = config['network']['vulns']['port']

    users_subnet = config['network']['users']['subnet']

    team_members = config['team_settings']['total_members']

    server = (ServerBuilder()
              .set_name           ("server")
              .set_external_ip    (main_external_ip)
              .set_internal_ip    (main_internal_ip)
              .set_internal_subnet(main_server_subnet)
              .set_port           (main_server_port)
              .build())

    factory = (VulnFactoryBuilder()
               .set_internal_subnet(vulns_subnet)
               .set_users_subnet   (users_subnet)
               .set_team_members   (team_members)
               .build())

    teams = list()
    for team_config in config['team_settings']['teams']:
        teams.append(factory.create_vuln(team_config['external_ip'], team_config['name']))

    create_configs(server, teams)

    if os.path.exists(base_folder):
        shutil.rmtree(f"{base_folder}")

    for team in teams:
        output_dir = f"{base_folder}/{team.name}"
        vulns_dir = f"{base_folder}/{vulns_folder}"

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if not os.path.exists(vulns_dir):
            os.makedirs(vulns_dir)

        with open(f"{vulns_dir}/{team.name}.conf", "w") as team_file:
            team_file.write(team.config)

        for member in team.members:
            with open(f"{output_dir}/{member.name}.conf", "w") as member_file:
                member_file.write(member.config)

        # Compress the team's files
        shutil.make_archive(f"{output_dir}", 'zip', f"{output_dir}")
    
    with open(f"{base_folder}/{server.name}.conf", "w") as server_file:
        server_file.write(server.config)