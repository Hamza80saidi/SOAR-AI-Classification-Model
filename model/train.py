"""
train_wazuh.py
--------------
Entraînement d'un modèle de classification sur alertes Wazuh réelles.
Features : rule_id, rule_level, rule_groups, firedtimes, mitre_tactic, src_ip_private
Label    : basé sur rule_level
  - level >= 12 → HIGH
  - level 7-11  → MEDIUM
  - level 3-6   → LOW
  - level < 3   → BENIGN
"""

import os, glob
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import joblib

# ── Chemins ───────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(BASE_DIR, 'data', 'simulated')
SAVED_DIR   = os.path.join(BASE_DIR, 'model', 'saved')
os.makedirs(SAVED_DIR, exist_ok=True)

# ── 1. Chargement de tous les CSV ─────────────────────────────────────────────
files = glob.glob(os.path.join(DATA_DIR, 'wazuh_alerts_*.csv'))
print(f"[1/5] Chargement de {len(files)} fichier(s)...")
df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
print(f"   {len(df)} alertes chargées")

# ── 2. Labellisation ──────────────────────────────────────────────────────────
def make_label(row):
    level  = row['rule_level']
    freq   = row['alert_frequency_5min']
    repeat = row['repeat_rule_10min']
    abuse  = row['ip_abuse_score']

    if level >= 7:
        return 'HIGH'
    if level >= 5:
        if freq >= 10 or repeat >= 8 or abuse >= 80:
            return 'HIGH'
        return 'MEDIUM'
    if level >= 3:
        if freq >= 15 or repeat >= 10 or abuse >= 80:
            return 'MEDIUM'
        return 'LOW'
    return 'LOW'

df['label'] = df.apply(make_label, axis=1)
print(f"\n[2/5] Distribution des labels :")
print(df['label'].value_counts())

# ── 3. Feature Engineering ────────────────────────────────────────────────────
print("\n[3/5] Feature engineering...")

# rule_id encodé
le_rule = LabelEncoder()
df['rule_id_enc'] = le_rule.fit_transform(df['rule_id'].astype(str))

# rule_groups : nombre de groupes
df['groups_count'] = df['rule_groups'].fillna('').apply(lambda x: len(x.split(',')) if x else 0)

# mitre_tactic : présence ou non
df['has_mitre'] = df['mitre_tactic'].fillna('').apply(lambda x: 1 if x else 0)

# src_ip : privée ou publique
def is_private(ip):
    if not isinstance(ip, str) or not ip: return 0
    return 1 if (ip.startswith('10.') or ip.startswith('192.168.') or ip.startswith('172.')) else 0

df['src_ip_private'] = df['src_ip'].apply(is_private)

# fired_times normalisé
df['fired_times'] = df['fired_times'].fillna(1).clip(upper=100)

# 5 features temporelles / contextuelles produites par export_wazuh_alerts.py
# → viennent directement du CSV, on remplit les NaN par 0
for col in ['alert_frequency_5min', 'repeat_rule_10min', 'hour_of_day',
            'is_business_hours', 'ip_abuse_score']:
    if col not in df.columns:
        df[col] = 0
    df[col] = df[col].fillna(0)

FEATURES = ['rule_id_enc', 'rule_level', 'groups_count', 'has_mitre', 'src_ip_private',
            'fired_times', 'alert_frequency_5min', 'repeat_rule_10min', 'hour_of_day',
            'is_business_hours', 'ip_abuse_score']

X = df[FEATURES].values
y = df['label'].values

# ── 4. Entraînement ───────────────────────────────────────────────────────────
print("\n[4/5] Entraînement Random Forest...")
le_label = LabelEncoder()
y_enc = le_label.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=0.2, random_state=42, stratify=y_enc)

model = RandomForestClassifier(
    n_estimators=200,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=le_label.classes_))

print("\n[Importance des features]")
for feat, imp in sorted(zip(FEATURES, model.feature_importances_), key=lambda x: -x[1]):
    print(f"  {feat:25s} {imp:.4f}")

# ── 5. Sauvegarde ─────────────────────────────────────────────────────────────
# Nouveaux fichiers _v2 : on ne touche pas aux anciens .pkl (model_wazuh.pkl, etc.)
print("\n[5/5] Sauvegarde...")
joblib.dump(model,    os.path.join(SAVED_DIR, 'model_wazuh_v2.pkl'))
joblib.dump(le_label, os.path.join(SAVED_DIR, 'label_encoder_v2.pkl'))
joblib.dump(le_rule,  os.path.join(SAVED_DIR, 'rule_id_encoder_v2.pkl'))
joblib.dump(FEATURES, os.path.join(SAVED_DIR, 'feature_names_v2.pkl'))
print("✅ Modèle Wazuh v2 sauvegardé !")