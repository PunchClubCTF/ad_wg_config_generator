#!/bin/bash

set -e

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

get_main_interface() {
    local interface=$(ip route | grep default | awk '{print $5}' | head -n 1)

    if [ -z "$interface" ]; then
        interface=$(ip -4 route show default | grep -oP '(?<=dev )\w+')
    fi

    if [ -z "$interface" ]; then
        interface=$(ip link show | grep -v "lo:" | grep -oP '(?<=: )\w+' | head -n 1)
    fi

    if [ -z "$interface" ]; then
        echo "Error: Could not detect main network interface" >&2
        exit 1
    fi

    echo "$interface"
}

find_wireguard_config() {
    local current_dir
    current_dir="$(pwd)"

    local config
    config=$(find "$current_dir" -maxdepth 2 -type f -name "*.conf" | head -n 1)

    if [ -z "$config" ]; then
        echo "Error: No WireGuard configuration file found" >&2
        exit 1
    fi

    if [ "$(find "$current_dir" -maxdepth 2 -type f -name "*.conf" | wc -l)" -gt 1 ]; then
        echo "Warning: Multiple .conf files found. Using the first one: $config" >&2
    fi

    echo "$config"
}

echo "Updating system packages..."
apt-get update && apt-get upgrade -y

echo "Installing WireGuard and dependencies..."
apt-get install -y wireguard iptables net-tools

echo "Enabling IP forwarding..."
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p

mkdir -p /etc/wireguard

setup_wireguard_config() {
    local conf_file="$1"
    local interface_name="${2:-wg0}"
    local main_interface="$3"
    
    local temp_conf=$(mktemp)
    
    sed "s/{interface}/${main_interface}/g" "$conf_file" > "$temp_conf"
    
    cp "$temp_conf" "/etc/wireguard/${interface_name}.conf"
    
    rm "$temp_conf"
    rm "$conf_file"
    
    chmod 600 "/etc/wireguard/${interface_name}.conf"
    

    systemctl stop "wg-quick@${interface_name}"
    systemctl enable "wg-quick@${interface_name}"
    systemctl start "wg-quick@${interface_name}"
}

MAIN_INTERFACE=$(get_main_interface)
echo "Detected main interface: $MAIN_INTERFACE"

CONFIG=$(find_wireguard_config)

echo "Using configuration: $CONFIG"
setup_wireguard_config "$CONFIG" "wg0" "$MAIN_INTERFACE"

echo "WireGuard VPN configured and started successfully!"

iptables -A FORWARD -i wg0 -j ACCEPT
iptables -A FORWARD -o wg0 -j ACCEPT
iptables -t nat -A POSTROUTING -o "$MAIN_INTERFACE" -j MASQUERADE

iptables-save > /etc/iptables/rules.v4

rm -- "$0"

exit 0
