"""
predict.py
----------
Prédiction directe depuis une alerte Wazuh JSON — v2.

Features (11, dans l'ordre de feature_names_v2.pkl) :
  rule_id_enc, rule_level, groups_count, has_mitre, src_ip_private,
  fired_times, alert_frequency_5min, repeat_rule_10min, hour_of_day,
  is_business_hours, ip_abuse_score

Les 5 dernières features sont calculées en temps réel à partir d'un
historique d'alertes tenu en mémoire (thread-safe) et, pour
ip_abuse_score, d'un appel optionnel à l'API AbuseIPDB.
"""

import joblib
import numpy as np
import os
import requests
import threading
from datetime import datetime
from collections import defaultdict, deque

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVED_DIR = os.path.join(BASE_DIR, 'model', 'saved')

print("[predict] Chargement du modèle...")
model          = joblib.load(os.path.join(SAVED_DIR, 'model_wazuh_v2.pkl'))
le_label       = joblib.load(os.path.join(SAVED_DIR, 'label_encoder_v2.pkl'))
le_rule        = joblib.load(os.path.join(SAVED_DIR, 'rule_id_encoder_v2.pkl'))
FEATURE_NAMES  = joblib.load(os.path.join(SAVED_DIR, 'feature_names_v2.pkl'))
print(f"[predict] Modèle chargé ✅ | Classes : {list(le_label.classes_)} | Features : {FEATURE_NAMES}")

ACTION_MAP = {
    'HIGH'  : 'BLOCK_AND_ALERT',
    'MEDIUM': 'NOTIFY_ANALYST',
    'LOW'   : 'LOG_ONLY',
}

# ── Historique temporel thread-safe ──────────────────────────────────────────
_alert_history = defaultdict(lambda: deque(maxlen=500))   # src_ip -> deque[(ts, rule_id)]
_history_lock  = threading.Lock()

WINDOW_5MIN  = 300   # secondes
WINDOW_10MIN = 600   # secondes

# ── Cache scores AbuseIPDB ────────────────────────────────────────────────────
_ip_cache      = {}
_ip_cache_lock = threading.Lock()


# ── Helpers ───────────────────────────────────────────────────────────────────
def _is_private(ip: str) -> int:
    """1 si IP RFC1918 (10.x, 192.168.x, 172.x), sinon 0. Identique à train.py."""
    if not isinstance(ip, str) or not ip:
        return 0
    return 1 if (ip.startswith('10.') or ip.startswith('192.168.') or ip.startswith('172.')) else 0


def _encode_rule_id(rule_id) -> int:
    """Encode rule_id avec le LabelEncoder entraîné. 0 si inconnu."""
    try:
        return int(le_rule.transform([str(rule_id)])[0])
    except Exception:
        return 0


def _get_ip_abuse_score(ip: str) -> int:
    """
    Interroge AbuseIPDB pour un score de réputation (0-100).
    - 0 si ABUSEIPDB_KEY absent de l'environnement
    - 0 si IP privée ou vide
    - résultat mis en cache (_ip_cache)
    - 0 en cas d'exception (timeout=2)
    """
    if not isinstance(ip, str) or not ip:
        return 0
    if _is_private(ip):
        return 0

    api_key = os.environ.get('ABUSEIPDB_KEY')
    if not api_key:
        return 0

    with _ip_cache_lock:
        if ip in _ip_cache:
            return _ip_cache[ip]

    score = 0
    try:
        resp = requests.get(
            'https://api.abuseipdb.com/api/v2/check',
            headers={'Key': api_key, 'Accept': 'application/json'},
            params={'ipAddress': ip, 'maxAgeInDays': 90},
            timeout=2
        )
        score = int(resp.json().get('data', {}).get('abuseConfidenceScore', 0))
    except Exception:
        score = 0

    with _ip_cache_lock:
        _ip_cache[ip] = score
    return score


def _parse_timestamp(ts_str: str):
    """Parse un timestamp Wazuh (ex: 2026-06-07T17:14:25.527+0000) en datetime UTC.
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


def _update_history(srcip, rule_id, ts):
    """Ajoute l'alerte courante dans l'historique de srcip (thread-safe)."""
    if not isinstance(srcip, str) or not srcip or ts is None:
        return
    with _history_lock:
        _alert_history[srcip].append((ts, str(rule_id)))


def _compute_temporal_features(srcip, rule_id, ts) -> dict:
    """
    Calcule les features temporelles à partir de l'historique EXISTANT
    (donc à appeler AVANT _update_history, pour ne pas se compter soi-même).
    """
    freq5min    = 0
    repeat10min = 0

    if isinstance(srcip, str) and srcip and ts is not None:
        with _history_lock:
            history = list(_alert_history.get(srcip, ()))
        rule_id_str = str(rule_id)
        for past_ts, past_rule in history:
            delta = (ts - past_ts).total_seconds()
            if 0 <= delta <= WINDOW_5MIN:
                freq5min += 1
            if 0 <= delta <= WINDOW_10MIN and past_rule == rule_id_str:
                repeat10min += 1

    if ts is not None:
        hour_of_day       = ts.hour
        is_business_hours = 1 if (ts.weekday() < 5 and 8 <= ts.hour < 18) else 0
    else:
        hour_of_day       = 0
        is_business_hours = 0

    return {
        'alert_frequency_5min': freq5min,
        'repeat_rule_10min'   : repeat10min,
        'hour_of_day'         : hour_of_day,
        'is_business_hours'   : is_business_hours,
    }


def extract_features(alert: dict):
    """
    Retourne (vec, feat_dict) :
      - vec       : np.ndarray shape (1, 11) dans l'ordre FEATURE_NAMES
      - feat_dict : les 11 features + champs contextuels
                    (_srcip, _rule_id, _agent, _agent_id, _description, _timestamp)
    """
    rule  = alert.get('rule', {}) or {}
    data  = alert.get('data', {}) or {}
    agent = alert.get('agent', {}) or {}

    rule_id = str(rule.get('id', ''))
    srcip   = data.get('srcip', '')
    ts_str  = alert.get('timestamp', '')
    ts      = _parse_timestamp(ts_str)

    # 1) calculer les features temporelles AVANT de mettre à jour l'historique
    temporal = _compute_temporal_features(srcip, rule_id, ts)
    # 2) puis enregistrer l'alerte courante dans l'historique
    _update_history(srcip, rule_id, ts)

    feat_dict = {
        'rule_id_enc'         : _encode_rule_id(rule_id),
        'rule_level'          : float(rule.get('level', 0)),
        'groups_count'        : len(rule.get('groups', [])),
        'has_mitre'           : 1 if rule.get('mitre') else 0,
        'src_ip_private'      : _is_private(srcip),
        'fired_times'         : min(float(rule.get('firedtimes', 1) or 1), 100.0),
        'alert_frequency_5min': temporal['alert_frequency_5min'],
        'repeat_rule_10min'   : temporal['repeat_rule_10min'],
        'hour_of_day'         : temporal['hour_of_day'],
        'is_business_hours'   : temporal['is_business_hours'],
        'ip_abuse_score'      : _get_ip_abuse_score(srcip),
    }

    vec = np.array([[feat_dict[name] for name in FEATURE_NAMES]])

    feat_dict['_srcip']       = srcip
    feat_dict['_rule_id']     = rule_id
    feat_dict['_agent']       = agent.get('name', 'unknown')
    feat_dict['_agent_id']    = agent.get('id', 'unknown')
    feat_dict['_description'] = rule.get('description', '')
    feat_dict['_timestamp']   = ts_str

    return vec, feat_dict


def predict(alert: dict) -> dict:
    try:
        vec, feat  = extract_features(alert)
        y_pred     = model.predict(vec)[0]
        y_proba    = model.predict_proba(vec)[0]
        label      = le_label.inverse_transform([y_pred])[0]
        confidence = float(np.max(y_proba))
        score      = int(confidence * 100)
        action     = ACTION_MAP.get(label, 'NOTIFY_ANALYST')

        return {
            'label'      : label,
            'confidence' : round(confidence, 4),
            'score'      : score,
            'action'     : action,
            'rule_id'    : feat['_rule_id'],
            'agent'      : feat['_agent'],
            'agent_id'   : feat['_agent_id'],
            'srcip'      : feat['_srcip'],
            'description': feat['_description'],
            'timestamp'  : feat['_timestamp'],
            'features'   : {
                'rule_level'          : feat['rule_level'],
                'alert_frequency_5min': feat['alert_frequency_5min'],
                'repeat_rule_10min'   : feat['repeat_rule_10min'],
                'hour_of_day'         : feat['hour_of_day'],
                'is_business_hours'   : feat['is_business_hours'],
                'ip_abuse_score'      : feat['ip_abuse_score'],
                'fired_times'         : feat['fired_times'],
                'has_mitre'           : feat['has_mitre'],
            }
        }
    except Exception as e:
        return {
            'label'     : 'UNKNOWN',
            'confidence': 0.0,
            'score'     : 0,
            'action'    : 'NOTIFY_ANALYST',
            'error'     : str(e),
        }


if __name__ == '__main__':
    tests = [
        {"timestamp": "2026-06-07T09:14:25.527+0000",
         "rule": {"id": "5712", "level": 10, "description": "SSH brute force", "firedtimes": 15,
                   "groups": ["syslog", "sshd"], "mitre": {"tactic": ["Credential Access"]}},
         "agent": {"id": "001", "name": "ocp"}, "data": {"srcip": "10.0.0.100"}},
        {"timestamp": "2026-06-07T09:14:30.100+0000",
         "rule": {"id": "5712", "level": 10, "description": "SSH brute force", "firedtimes": 16,
                   "groups": ["syslog", "sshd"], "mitre": {"tactic": ["Credential Access"]}},
         "agent": {"id": "001", "name": "ocp"}, "data": {"srcip": "10.0.0.100"}},
        {"timestamp": "2026-06-07T23:14:25.527+0000",
         "rule": {"id": "533", "level": 7, "description": "Port scan", "firedtimes": 50,
                   "groups": ["syslog"], "mitre": {}},
         "agent": {"id": "002", "name": "ocp"}, "data": {}},
        {"timestamp": "2026-06-07T17:20:00.000+0000",
         "rule": {"id": "5763", "level": 12, "description": "SSH brute force massive", "firedtimes": 50,
                   "groups": ["syslog", "sshd"], "mitre": {"tactic": ["Credential Access"]}},
         "agent": {"id": "001", "name": "ocp"}, "data": {"srcip": "10.0.0.100"}},
    ]
    for t in tests:
        r = predict(t)
        print(f"rule={t['rule']['id']} level={t['rule']['level']} → {r['label']} ({r['score']}%) — {r['action']}")
