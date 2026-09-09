"""
simulate_attacks.py
-------------------
Génère des logs d'attaques simulées dans un fichier
que Wazuh va lire et analyser automatiquement.

Types d'attaques simulées :
1. Brute Force SSH     → plusieurs tentatives de connexion échouées
2. Port Scan           → tentatives de connexion sur multiples ports
3. Web Attack XSS      → requêtes HTTP suspectes dans les logs Apache/Nginx
4. Suspicious Login    → connexion à une heure anormale

Explication du fonctionnement :
- Ce script écrit des logs dans /var/log/simulated_attacks.log
- Tu configures Wazuh pour surveiller ce fichier (localfile)
- Wazuh analyse les logs et génère des alertes réelles
- Ces alertes apparaissent dans le dashboard et dans Shuffle
"""

import random
import time
import datetime
import os
import argparse

# ── Configuration ─────────────────────────────────────────────────────────────
LOG_FILE = '/var/log/simulated_attacks.log'

# IPs simulées pour les attaquants
ATTACKER_IPS = [
    '10.0.0.100', '192.168.1.50', '172.16.0.25',
    '10.10.10.10', '192.168.100.5', '10.0.1.200'
]

# Ports courants pour les scans
COMMON_PORTS = [22, 23, 80, 443, 3389, 8080, 8443, 3306, 5432, 6379, 27017]

# Utilisateurs souvent ciblés
TARGET_USERS = ['root', 'admin', 'user', 'test', 'ubuntu', 'oracle', 'postgres']


def get_timestamp(offset_seconds=0):
    """Retourne un timestamp syslog formaté."""
    now = datetime.datetime.now() - datetime.timedelta(seconds=offset_seconds)
    return now.strftime('%b %d %H:%M:%S')


def write_log(message: str):
    """Écrit une ligne dans le fichier de log."""
    with open(LOG_FILE, 'a') as f:
        f.write(message + '\n')
    print(f"  LOG → {message[:80]}...")


# ── Générateurs d'attaques ───────────────────────────────────────────────────

def simulate_brute_force_ssh(n_attempts=20, ip=None):
    """
    Simule une attaque brute force SSH.
    Génère des logs identiques à ceux produits par sshd réel.
    Wazuh Rule 5710/5763 va se déclencher.
    """
    print(f"\n[BRUTE FORCE SSH] {n_attempts} tentatives...")
    src_ip = ip or random.choice(ATTACKER_IPS)
    user   = random.choice(TARGET_USERS)
    port   = random.randint(40000, 65000)

    for i in range(n_attempts):
        ts = get_timestamp(n_attempts - i)
        log = (f"{ts} ocp sshd[{random.randint(1000,9999)}]: "
               f"Failed password for invalid user {user} "
               f"from {src_ip} port {port} ssh2")
        write_log(log)
        time.sleep(0.1)

    print(f"  ✅ {n_attempts} tentatives SSH depuis {src_ip}")


def simulate_port_scan(n_ports=15, ip=None):
    """
    Simule un scan de ports.
    Génère des logs de connexions refusées sur multiples ports.
    Wazuh Rule 533 va se déclencher.
    """
    print(f"\n[PORT SCAN] {n_ports} ports scannés...")
    src_ip = ip or random.choice(ATTACKER_IPS)
    ports  = random.sample(COMMON_PORTS * 3, min(n_ports, len(COMMON_PORTS) * 3))

    for port in ports:
        ts = get_timestamp()
        log = (f"{ts} ocp kernel: "
               f"Firewall: *TCP_IN Blocked* IN=eth0 OUT= "
               f"SRC={src_ip} DST=192.168.56.100 "
               f"PROTO=TCP SPT={random.randint(40000,65000)} DPT={port} "
               f"SYN URGP=0")
        write_log(log)
        time.sleep(0.05)

    print(f"  ✅ Scan de {n_ports} ports depuis {src_ip}")


def simulate_web_attack_xss(n_requests=10, ip=None):
    """
    Simule des attaques XSS via des requêtes HTTP suspectes.
    Génère des logs Apache/Nginx.
    Wazuh Rule 31103 va se déclencher.
    """
    print(f"\n[WEB ATTACK XSS] {n_requests} requêtes suspectes...")
    src_ip   = ip or random.choice(ATTACKER_IPS)
    payloads = [
        '<script>alert(1)</script>',
        '"><img src=x onerror=alert(1)>',
        "javascript:alert('XSS')",
        '<svg onload=alert(1)>',
    ]

    for _ in range(n_requests):
        ts      = get_timestamp()
        payload = random.choice(payloads)
        log = (f'{ts} ocp apache2[{random.randint(1000,9999)}]: '
               f'{src_ip} - - [{datetime.datetime.now().strftime("%d/%b/%Y:%H:%M:%S")} +0000] '
               f'"GET /search?q={payload} HTTP/1.1" 400 512')
        write_log(log)
        time.sleep(0.1)

    print(f"  ✅ {n_requests} requêtes XSS depuis {src_ip}")


def simulate_suspicious_login(ip=None):
    """
    Simule une connexion suspecte (heure anormale, IP inhabituelle).
    Wazuh Rule 5501 va se déclencher.
    """
    print(f"\n[SUSPICIOUS LOGIN] Connexion suspecte...")
    src_ip = ip or random.choice(ATTACKER_IPS)
    user   = random.choice(TARGET_USERS)
    ts     = get_timestamp()

    log = (f"{ts} ocp sshd[{random.randint(1000,9999)}]: "
           f"Accepted password for {user} from {src_ip} port "
           f"{random.randint(40000,65000)} ssh2")
    write_log(log)
    print(f"  ✅ Connexion suspecte de {user}@{src_ip}")


def simulate_all_attacks(rounds=3):
    """
    Lance tous les types d'attaques en séquence.
    rounds : nombre de fois qu'on répète le cycle complet
    """
    print(f"\n{'='*50}")
    print(f"  SIMULATION COMPLÈTE — {rounds} rounds")
    print(f"{'='*50}")

    for r in range(1, rounds + 1):
        print(f"\n── Round {r}/{rounds} ──")
        simulate_brute_force_ssh(n_attempts=15)
        time.sleep(2)
        simulate_port_scan(n_ports=10)
        time.sleep(2)
        simulate_web_attack_xss(n_requests=8)
        time.sleep(2)
        simulate_suspicious_login()
        time.sleep(5)

    print(f"\n✅ Simulation terminée — vérifie Wazuh Dashboard et Shuffle !")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simulateur d\'attaques pour Wazuh')
    parser.add_argument('--type', choices=['brute', 'scan', 'xss', 'login', 'all'],
                        default='all', help='Type d\'attaque à simuler')
    parser.add_argument('--rounds', type=int, default=1,
                        help='Nombre de rounds (pour --type all)')
    parser.add_argument('--ip', type=str, default=None,
                        help='IP source de l\'attaquant (aléatoire si non spécifié)')
    args = parser.parse_args()

    # Créer le fichier de log si nécessaire
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    open(LOG_FILE, 'a').close()

    print(f"Logs écrits dans : {LOG_FILE}")
    print(f"Assure-toi que Wazuh surveille ce fichier !")
    print(f"(voir : /var/ossec/etc/ossec.conf → <localfile>)\n")

    if args.type == 'brute' : simulate_brute_force_ssh(ip=args.ip)
    elif args.type == 'scan': simulate_port_scan(ip=args.ip)
    elif args.type == 'xss' : simulate_web_attack_xss(ip=args.ip)
    elif args.type == 'login': simulate_suspicious_login(ip=args.ip)
    else                    : simulate_all_attacks(rounds=args.rounds)
