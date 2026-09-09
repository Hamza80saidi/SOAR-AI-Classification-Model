"""
app.py
------
API Flask — pont entre Shuffle SOAR et le modèle AI.

Endpoints :
  POST /predict      → reçoit une alerte Wazuh JSON, retourne le score AI
  GET  /health       → vérifie que l'API est en vie
  GET  /stats        → statistiques des prédictions depuis le démarrage

Explication du rôle de cette API :
  Shuffle SOAR ne peut pas appeler directement un modèle Python.
  Cette API Flask fait le pont :
  Shuffle → POST /predict → modèle AI → résultat → Shuffle → playbook
"""

from flask import Flask, request, jsonify
from datetime import datetime
from email.mime.text import MIMEText
import sys
import os
import json
import smtplib
import requests
import threading
import urllib3
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')

# Ajouter le dossier parent au path pour importer predict.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.predict import predict

# Le blocage IP via l'API Wazuh utilise verify=False (certificat auto-signé) :
# on coupe l'avertissement associé pour ne pas polluer les logs.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# ── Configuration réponse automatisée (variables d'environnement) ───────────
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID   = os.environ.get('TELEGRAM_CHAT_ID')
EMAIL_FROM         = os.environ.get('EMAIL_FROM')
EMAIL_TO           = os.environ.get('EMAIL_TO')
EMAIL_PASSWORD     = os.environ.get('EMAIL_PASSWORD')
WAZUH_API_URL      = os.environ.get('WAZUH_API_URL', 'https://192.168.56.100:55000')
WAZUH_API_USER     = os.environ.get('WAZUH_API_USER', 'wazuh-wui')
WAZUH_API_PASSWORD = os.environ.get('WAZUH_API_PASSWORD')

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')


# ── Fonctions de réponse automatisée ─────────────────────────────────────────
def _send_telegram(message: str) -> bool:
    """Envoie un message Telegram. Silencieux (False) si config absente."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    try:
        resp = requests.post(
            f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
            json={'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'Markdown'},
            timeout=5
        )
        return resp.status_code == 200
    except Exception as e:
        print(f"   ⚠️  Erreur Telegram : {e}")
        return False


def _send_email(subject: str, body: str) -> bool:
    """Envoie un email via SMTP_SSL Gmail. Silencieux (False) si config absente."""
    if not EMAIL_FROM or not EMAIL_TO or not EMAIL_PASSWORD:
        return False
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From']    = EMAIL_FROM
        msg['To']      = EMAIL_TO
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10) as server:
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())
        return True
    except Exception as e:
        print(f"   ⚠️  Erreur Email : {e}")
        return False


def _block_ip_wazuh(srcip: str, agent_id: str) -> bool:
    """Authentifie sur l'API Wazuh puis déclenche l'active response firewall-drop0."""
    if not srcip or not agent_id or not WAZUH_API_PASSWORD:
        return False
    try:
        auth_resp = requests.get(
            f'{WAZUH_API_URL}/security/user/authenticate',
            auth=(WAZUH_API_USER, WAZUH_API_PASSWORD),
            verify=False,
            timeout=10
        )
        token = auth_resp.json().get('data', {}).get('token')
        if not token:
            return False

        block_resp = requests.put(
            f'{WAZUH_API_URL}/active-response?agents_list={agent_id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'command'  : 'firewall-drop0',
                'arguments': ['-', 'null', '0', 'srcip', srcip]
            },
            verify=False,
            timeout=5
        )
        return block_resp.status_code == 200
    except Exception as e:
        print(f"   ⚠️  Erreur blocage Wazuh : {e}")
        return False


def _format_telegram_high(r: dict) -> str:
    f = r.get('features', {}) or {}
    blocked = r.get('response_executed', {}).get('blocked', False)
    statut = "✅ Exécuté" if blocked else "❌ Non exécuté (agent indisponible)"
    return (
        f"🚨 *ALERTE HIGH DÉTECTÉE* 🚨\n\n"
        f"*Label* : {r.get('label')}\n"
        f"*Score* : {r.get('score')}%\n"
        f"*IP source* : `{r.get('srcip')}`\n"
        f"*Agent* : {r.get('agent')}\n"
        f"*Description* : {r.get('description')}\n"
        f"*Rule ID* : {r.get('rule_id')}\n"
        f"*Timestamp* : {r.get('timestamp')}\n\n"
        f"📊 *Contexte*\n"
        f"  • Fréquence 5min : {f.get('alert_frequency_5min')}\n"
        f"  • Répétitions 10min : {f.get('repeat_rule_10min')}\n"
        f"  • Score abus IP : {f.get('ip_abuse_score')}\n"
        f"  • Heure : {f.get('hour_of_day')}h\n"
        f"  • Heures ouvrées : {'Oui' if f.get('is_business_hours') else 'Non'}\n"
        f"🔒 *Blocage IP* : {statut}\n"
    )


def _format_telegram_medium(r: dict) -> str:
    return (
        f"⚠️ *Alerte MEDIUM*\n"
        f"Label: {r.get('label')} | Score: {r.get('score')}%\n"
        f"Rule: {r.get('rule_id')} | IP: {r.get('srcip')} | Agent: {r.get('agent')}"
    )

# ── Compteurs statistiques ───────────────────────────────────────────────────
stats = {
    'total'   : 0,
    'BENIGN'  : 0,
    'LOW'     : 0,
    'MEDIUM'  : 0,
    'HIGH'    : 0,
    'errors'  : 0,
    'started' : datetime.utcnow().isoformat()
}


@app.route('/health', methods=['GET'])
def health():
    """
    Endpoint de vérification de vie.
    Shuffle peut appeler cet endpoint pour vérifier que l'API tourne.
    """
    return jsonify({
        'status'  : 'ok',
        'message' : 'SOAR AI API is running',
        'uptime'  : datetime.utcnow().isoformat()
    }), 200


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    """
    Endpoint principal.

    Reçoit une alerte Wazuh en JSON depuis Shuffle SOAR.
    Retourne le niveau de criticité + l'action recommandée.

    Exemple de requête depuis Shuffle :
    POST http://192.168.56.100:5000/predict
    Body: { "rule": {...}, "agent": {...}, "data": {...} }

    Exemple de réponse :
    {
        "label"      : "HIGH",
        "confidence" : 0.92,
        "score"      : 92,
        "action"     : "BLOCK_AND_ALERT",
        "rule_id"    : "5710",
        "agent"      : "ocp"
    }
    """
    # Vérifier que le body est bien du JSON
    if not request.is_json:
        stats['errors'] += 1
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    alert = request.get_json()

    # Log de la requête reçue
    rule_id = alert.get('rule', {}).get('id', '?')
    agent   = alert.get('agent', {}).get('name', '?')
    print(f"[{datetime.utcnow().isoformat()}] Alerte reçue | rule={rule_id} | agent={agent}")

    # Prédiction
    result = predict(alert)

    # Mise à jour des stats
    stats['total'] += 1
    label = result.get('label', 'UNKNOWN')
    if label in stats:
        stats[label] += 1
    else:
        stats['errors'] += 1

    print(f"   → Prédiction : {label} (score={result.get('score')})")

    # Déclenchement de la réponse automatisée correspondante (best-effort)
    response_executed = None
    try:
        resp = requests.post(
            f"http://localhost:5000/respond/{label.lower()}",
            json=result,
            timeout=15
        )
        try:
            response_executed = resp.json()
        except Exception:
            response_executed = {'status_code': resp.status_code}
    except Exception as e:
        print(f"   ⚠️  Erreur /respond/{label.lower()} : {e}")
        response_executed = {'error': str(e)}

    result['response_executed'] = response_executed

    return jsonify(result), 200


@app.route('/respond/high', methods=['POST'])
def respond_high():
    """
    Réponse automatisée pour les alertes HIGH :
    blocage IP (Wazuh active-response) + notification Telegram + email,
    lancés en parallèle.
    """
    r = request.get_json(force=True, silent=True) or {}
    srcip    = r.get('srcip')
    agent_id = r.get('agent_id')

    # 1) Blocage IP en premier (synchrone) pour connaître le statut réel
    blocked = _block_ip_wazuh(srcip, agent_id)
    r['response_executed'] = {'blocked': blocked}

    # 2) Message Telegram formaté avec le statut de blocage réel
    message = _format_telegram_high(r)

    result = {}

    def _do_telegram():
        result['telegram_sent'] = _send_telegram(message)

    def _do_email():
        result['email_sent'] = _send_email(
            f"🚨 SOAR-AI : Alerte HIGH — {r.get('rule_id')}",
            message
        )

    # 3) Telegram et Email en parallèle
    threads = [
        threading.Thread(target=_do_telegram),
        threading.Thread(target=_do_email),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)

    return jsonify({
        'blocked'      : blocked,
        'telegram_sent': result.get('telegram_sent', False),
        'email_sent'   : result.get('email_sent', False),
    }), 200


@app.route('/respond/medium', methods=['POST'])
def respond_medium():
    """Réponse automatisée pour les alertes MEDIUM : notification Telegram + email."""
    r = request.get_json(force=True, silent=True) or {}

    telegram_sent = _send_telegram(_format_telegram_medium(r))
    email_sent = _send_email(
        f"⚠️ SOAR-AI : Alerte MEDIUM — {r.get('rule_id')}",
        _format_telegram_medium(r)
    )

    return jsonify({'telegram_sent': telegram_sent, 'email_sent': email_sent}), 200


@app.route('/respond/low', methods=['POST'])
def respond_low():
    """Réponse pour les alertes LOW : simple journalisation dans logs/incidents.json."""
    r = request.get_json(force=True, silent=True) or {}

    os.makedirs(LOGS_DIR, exist_ok=True)
    incidents_path = os.path.join(LOGS_DIR, 'incidents.json')

    incidents = []
    if os.path.exists(incidents_path):
        try:
            with open(incidents_path, 'r') as f:
                incidents = json.load(f)
        except Exception:
            incidents = []

    incidents.append({**r, 'logged_at': datetime.utcnow().isoformat()})

    with open(incidents_path, 'w') as f:
        json.dump(incidents, f, indent=2)

    return jsonify({'logged': True}), 200


@app.route('/stats', methods=['GET'])
def get_stats():
    """
    Retourne les statistiques des prédictions depuis le démarrage.
    Utile pour le dashboard et le rapport.
    """
    return jsonify(stats), 200


@app.route('/test', methods=['GET'])
def test_prediction():
    """
    Test rapide de l'API avec une fausse alerte brute force SSH.
    Utile pour vérifier que tout fonctionne sans Shuffle.
    """
    fake_alert = {
        "rule": {
            "level": 10,
            "id": "5763",
            "description": "sshd: brute force trying to get access to the system",
            "firedtimes": 15,
            "groups": ["syslog", "sshd", "authentication_failures"]
        },
        "agent": {"id": "001", "name": "ocp"},
        "data": {"srcip": "192.168.56.40", "srcuser": "root"}
    }
    result = predict(fake_alert)
    return jsonify(result), 200


if __name__ == '__main__':
    print("=" * 50)
    print("  SOAR AI API — démarrage")
    print("=" * 50)
    print("  POST /predict  → prédire une alerte")
    print("  GET  /health   → vérifier l'API")
    print("  GET  /stats    → statistiques")
    print("  GET  /test     → test rapide")
    print("=" * 50)
    
    # host='0.0.0.0' → accessible depuis l'extérieur (Shuffle)
    # port=5000 → port par défaut Flask
    # debug=False en production
    app.run(host='0.0.0.0', port=5000, debug=False)
