"""
prepare_data.py
---------------
Ce script lit le dataset CICIDS brut, mappe les 15 classes d'attaques
vers 3 niveaux de criticité (LOW / MEDIUM / HIGH) + BENIGN,
nettoie les données et sauvegarde le résultat dans data/processed/.

Explication des étapes :
1. Chargement du CSV brut (peut être volumineux ~18M lignes)
2. Mapping des labels vers 3 classes métier
3. Suppression des colonnes inutiles / valeurs aberrantes
4. Échantillonnage équilibré (pour éviter le déséquilibre des classes)
5. Sauvegarde du dataset propre
"""

import pandas as pd
import numpy as np
import os

# ── Chemins ──────────────────────────────────────────────────────────────────
RAW_DIR       = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
os.makedirs(PROCESSED_DIR, exist_ok=True)

# ── Paramètres ───────────────────────────────────────────────────────────────
# Mets ici le nom exact de ton fichier CSV téléchargé depuis Kaggle
CSV_FILENAME  = 'cic.csv'          # ← change si nécessaire
OUTPUT_FILE   = os.path.join(PROCESSED_DIR, 'alerts_clean.csv')

# Nombre max de lignes par classe (pour équilibrer sans surcharger la RAM)
MAX_ROWS_PER_CLASS = 50_000

# ── Mapping des 15 labels → 3 classes ────────────────────────────────────────
# Explication : on regroupe les attaques selon leur impact réel dans un SOC
LABEL_MAPPING = {
    'Benign'            : 'BENIGN',   # trafic normal
    # LOW : attaques de reconnaissance, pas destructives
    'PortScan'          : 'LOW',
    'Infiltration'      : 'LOW',
    # MEDIUM : attaques ciblées sur des services spécifiques
    'FTP-BruteForce'    : 'MEDIUM',
    'SSH-BruteForce'    : 'MEDIUM',
    'BruteForce-Web'    : 'MEDIUM',
    'BruteForce-XSS'    : 'MEDIUM',
    'SQL-Injection'     : 'MEDIUM',
    # HIGH : attaques à fort impact, réponse immédiate requise
    'DDoS'              : 'HIGH',
    'DoS-Hulk'          : 'HIGH',
    'DoS-GoldenEye'     : 'HIGH',
    'DoS-Slowloris'     : 'HIGH',
    'DoS-SlowHTTPTest'  : 'HIGH',
    'Bot'               : 'HIGH',
    'Heartbleed'        : 'HIGH',
}

# ── Colonnes à garder pour le modèle ────────────────────────────────────────
# Explication : on garde les features réseau les plus discriminantes
# pour la classification d'attaques réseau
FEATURES = [
    'Dst Port', 'Protocol', 'Flow Duration',
    'Flow Bytes/s', 'Flow Packets/s',
    'Fwd Packets/s', 'Bwd Packets/s',
    'Total Fwd Packet', 'Total Bwd packets',
    'Total Length of Fwd Packet', 'Total Length of Bwd Packet',
    'Fwd Packet Length Max', 'Fwd Packet Length Min',
    'Fwd Packet Length Mean', 'Fwd Packet Length Std',
    'Bwd Packet Length Max', 'Bwd Packet Length Min',
    'Bwd Packet Length Mean', 'Bwd Packet Length Std',
    'Packet Length Max', 'Packet Length Min',
    'Packet Length Mean', 'Packet Length Std',
    'Flow IAT Mean', 'Flow IAT Max', 'Flow IAT Min', 'Flow IAT Std',
    'Fwd IAT Total', 'Fwd IAT Mean', 'Fwd IAT Std',
    'Bwd IAT Total', 'Bwd IAT Mean', 'Bwd IAT Std',
    'SYN Flag Count', 'ACK Flag Count', 'FIN Flag Count',
    'RST Flag Count', 'PSH Flag Count',
    'Average Packet Size', 'Down/Up Ratio',
    'FWD Init Win Bytes', 'Bwd Init Win Bytes',
    'Active Mean', 'Active Std', 'Idle Mean', 'Idle Std',
    'Label'
]


def load_and_map(filepath: str) -> pd.DataFrame:
    """Charge le CSV et mappe les labels vers 3 classes."""
    print(f"[1/5] Chargement du fichier : {filepath}")
    
    # Chargement en chunks pour éviter la saturation RAM sur 18M lignes
    chunks = []
    chunk_size = 500_000
    
    for i, chunk in enumerate(pd.read_csv(filepath, chunksize=chunk_size, low_memory=False)):
        chunk.columns = chunk.columns.str.strip()
        # Garder seulement les colonnes utiles
        cols_available = [c for c in FEATURES if c in chunk.columns]
        chunk = chunk[cols_available]
        # Mapper les labels
        chunk['Label'] = chunk['Label'].str.strip().map(LABEL_MAPPING)
        chunk = chunk.dropna(subset=['Label'])
        chunks.append(chunk)
        print(f"   Chunk {i+1} chargé ({len(chunk):,} lignes)")
    
    df = pd.concat(chunks, ignore_index=True)
    print(f"   Total après chargement : {len(df):,} lignes")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie les valeurs aberrantes."""
    print("[2/5] Nettoyage des données...")
    before = len(df)
    
    # Supprimer les infinis
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()
    
    print(f"   Supprimé {before - len(df):,} lignes avec NaN/inf")
    return df


def balance(df: pd.DataFrame) -> pd.DataFrame:
    """Équilibre les classes pour éviter le biais du modèle."""
    print("[3/5] Équilibrage des classes...")
    
    balanced_parts = []
    for label, group in df.groupby('Label'):
        n = min(len(group), MAX_ROWS_PER_CLASS)
        sampled = group.sample(n=n, random_state=42)
        balanced_parts.append(sampled)
        print(f"   {label:8s} → {n:,} lignes")
    
    df_balanced = pd.concat(balanced_parts, ignore_index=True)
    df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)
    print(f"   Total équilibré : {len(df_balanced):,} lignes")
    return df_balanced


def save(df: pd.DataFrame, output_path: str):
    """Sauvegarde le dataset propre."""
    print(f"[4/5] Sauvegarde dans : {output_path}")
    df.to_csv(output_path, index=False)
    print(f"[5/5] ✅ Dataset prêt ! {len(df):,} lignes, {len(df.columns)} colonnes")
    print(f"\nDistribution finale des classes :")
    print(df['Label'].value_counts())


if __name__ == '__main__':
    raw_path = os.path.join(RAW_DIR, CSV_FILENAME)
    
    if not os.path.exists(raw_path):
        print(f"❌ Fichier introuvable : {raw_path}")
        print(f"   Place ton CSV dans : {RAW_DIR}")
        exit(1)
    
    df = load_and_map(raw_path)
    df = clean(df)
    df = balance(df)
    save(df, OUTPUT_FILE)
