"""
export_wazuh_alerts.py
----------------------
Exporte les alertes Wazuh depuis le conteneur Docker
vers un fichier JSON/CSV utilisable pour les tests du modèle AI.

Explication :
- Les alertes Wazuh sont stockées dans /var/ossec/logs/alerts/alerts.json
- Ce script les extrait et les convertit en CSV
- Tu peux ensuite les utiliser pour tester le modèle sur des données réelles
"""

import subprocess
import json
import pandas as pd
import os
import random
from datetime import datetime

# ── Configuration ─────────────────────────────────────────────────────────────
CONTAINER_NAME = 'single-node_wazuh.manager_1'
ALERTS_PATH    = '/var/ossec/logs/alerts/alerts.json'
OUTPUT_DIR     = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               'data', 'simulated')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def export_alerts(max_lines=1000):
    """Exporte les alertes depuis le conteneur Wazuh."""
    print(f"[1/4] Export des alertes depuis {CONTAINER_NAME}...")
    
    cmd = ['docker', 'exec', CONTAINER_NAME,
           'tail', f'-{max_lines}', ALERTS_PATH]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Erreur : {result.stderr}")
        return []
    
    alerts = []
    for line in result.stdout.strip().split('\n'):
        try:
            alert = json.loads(line)
            alerts.append(alert)
        except json.JSONDecodeError:
            continue
    
    print(f"   {len(alerts)} alertes exportées")
    return alerts


def alerts_to_dataframe(alerts):
    """Convertit les alertes JSON en DataFrame."""
    print("[2/4] Conversion en DataFrame...")
    
    rows = []
    for alert in alerts:
        rule  = alert.get('rule', {})
        agent = alert.get('agent', {})
        data  = alert.get('data', {})
        
        row = {
            'timestamp'        : alert.get('timestamp', ''),
            'rule_id'          : rule.get('id', ''),
            'rule_level'       : rule.get('level', 0),
            'rule_description' : rule.get('description', ''),
            'rule_groups'      : ','.join(rule.get('groups', [])),
            'agent_name'       : agent.get('name', ''),
            'agent_ip'         : agent.get('ip', ''),
            'src_ip'           : data.get('srcip', ''),
            'src_user'         : data.get('srcuser', ''),
            'mitre_tactic'     : ','.join(rule.get('mitre', {}).get('tactic', [])),
            'fired_times'      : rule.get('firedtimes', 1),
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    print(f"   DataFrame créé : {len(df)} lignes, {len(df.columns)} colonnes")
    return df


def _parse_ts(ts_str):
    """Parse un timestamp Wazuh (ex: 2026-06-07T17:14:25.527+0000) en datetime.
    Retourne None si le parsing échoue."""
    if not isinstance(ts_str, str) or not ts_str:
        return None
    try:
        return datetime.strptime(ts_str, '%Y-%m-%dT%H:%M:%S.%f%z')
    except Exception:
        try:
            return datetime.strptime(ts_str, '%Y-%m-%dT%H:%M:%S%z')
        except Exception:
            return None


def add_temporal_features(df):
    """
    Ajoute 5 colonnes calculées à partir de l'historique temporel des alertes :
      - alert_frequency_5min : nb d'alertes du même src_ip dans les 300s précédentes
      - repeat_rule_10min    : nb d'alertes du même rule_id+src_ip dans les 600s précédentes
      - hour_of_day          : heure UTC (0-23) du timestamp
      - is_business_hours    : 1 si lundi-vendredi 8h-18h UTC, sinon 0
      - ip_abuse_score       : 0 si src_ip privée ('10.', '192.168.', '172.'),
                                sinon random.randint(60, 100) (IP publique)
    """
    print("[2b/4] Calcul des features temporelles...")

    df = df.copy()
    df['_parsed_ts'] = df['timestamp'].apply(_parse_ts)

    # Trier par timestamp avant le calcul des features temporelles
    df = df.sort_values(by='_parsed_ts', na_position='first', kind='stable').reset_index(drop=True)

    freq5min     = []
    repeat10min  = []
    hour_of_day  = []
    is_biz_hours = []
    abuse_scores = []

    # historique : src_ip -> liste de (timestamp, rule_id) des alertes déjà vues
    history = {}

    for i in range(len(df)):
        src_ip  = df.at[i, 'src_ip']
        rule_id = df.at[i, 'rule_id']
        ts      = df.at[i, '_parsed_ts']

        valid_ip = isinstance(src_ip, str) and src_ip.strip() != ''

        if not valid_ip or ts is None:
            freq5min.append(0)
            repeat10min.append(0)
        else:
            past   = history.get(src_ip, [])
            count5 = 0
            countR = 0
            for (past_ts, past_rule) in past:
                delta = (ts - past_ts).total_seconds()
                if 0 <= delta <= 300:
                    count5 += 1
                if 0 <= delta <= 600 and past_rule == rule_id:
                    countR += 1
            freq5min.append(count5)
            repeat10min.append(countR)
            past.append((ts, rule_id))
            history[src_ip] = past

        if ts is not None:
            hour_of_day.append(ts.hour)
            is_biz_hours.append(1 if (ts.weekday() < 5 and 8 <= ts.hour < 18) else 0)
        else:
            hour_of_day.append(0)
            is_biz_hours.append(0)

        if valid_ip and (src_ip.startswith('10.') or src_ip.startswith('192.168.') or src_ip.startswith('172.')):
            abuse_scores.append(0)
        elif valid_ip:
            abuse_scores.append(random.randint(60, 100))
        else:
            abuse_scores.append(0)

    df['alert_frequency_5min'] = freq5min
    df['repeat_rule_10min']    = repeat10min
    df['hour_of_day']          = hour_of_day
    df['is_business_hours']    = is_biz_hours
    df['ip_abuse_score']       = abuse_scores

    df = df.drop(columns=['_parsed_ts'])

    print("\nAperçu des nouvelles colonnes :")
    print(df[['timestamp', 'src_ip', 'alert_frequency_5min', 'repeat_rule_10min',
               'hour_of_day', 'is_business_hours', 'ip_abuse_score']].head(10))

    return df


def save(df, alerts):
    """Sauvegarde en CSV et JSON."""
    print("[4/4] Sauvegarde...")
    
    ts       = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_path  = os.path.join(OUTPUT_DIR, f'wazuh_alerts_{ts}.csv')
    json_path = os.path.join(OUTPUT_DIR, f'wazuh_alerts_{ts}.json')
    
    df.to_csv(csv_path, index=False)
    with open(json_path, 'w') as f:
        json.dump(alerts, f, indent=2)
    
    print(f"   CSV  → {csv_path}")
    print(f"   JSON → {json_path}")
    print(f"\n✅ Export terminé !")
    print(f"\nDistribution des niveaux d'alerte :")
    print(df['rule_level'].value_counts().sort_index())


if __name__ == '__main__':
    alerts = export_alerts(max_lines=2000)
    if alerts:
        df = alerts_to_dataframe(alerts)
        df = add_temporal_features(df)
        save(df, alerts)
    else:
        print("❌ Aucune alerte trouvée — génère des attaques d'abord !")
        print("   python scripts/simulate_attacks.py --type all")
