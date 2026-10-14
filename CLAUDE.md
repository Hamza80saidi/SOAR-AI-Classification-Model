# CLAUDE.md — Contexte du projet SOAR-AI

## Vue d'ensemble

Projet de Fin d'Études (Master D3SI) réalisé à l'OCP.
Système de détection et de réponse automatisée aux incidents de 
sécurité, intégrant une couche de Machine Learning entre un 
SIEM (Wazuh) et un SOAR (Shuffle).

- **Auteur :** Hamza Saidi
- **Encadrant pédagogique :** Pr. Mohamed El Fezazi
- **Encadrants OCP :** M. Fahmi Abderrahim, M. Erraji Hamza
- **Établissement :** Faculté des Sciences Appliquées de Béni Mellal
- **Site de stage :** OCP Benguerir — Laverie Gantour — Dépt Maintenance
- **Année :** 2025-2026

## Problématique

Le SIEM de l'OCP génère environ 100 alertes par seconde. Déployer 
un SOAR sans triage préalable reproduirait la saturation observée 
au niveau du SIEM. Solution proposée par l'auteur : une couche ML 
de triage comportemental insérée entre le SIEM et le SOAR.

## Architecture en 5 couches

1. **Simulation** — simulate_attacks.py génère des logs d'attaque
2. **SIEM** — Wazuh 4.9.2 détecte et transmet via webhook
3. **SOAR** — Shuffle 2.2.0 orchestre le flux
4. **IA** — API Flask + Random Forest classifie l'alerte
5. **Réponse** — Blocage IP / Telegram / Email / Logger

## Flux de traitement

simulate_attacks.py → /var/log/simulated_attacks.log → 
Wazuh → webhook → Shuffle → POST /predict → 
Random Forest → label → /respond/{label} → action automatisée

## Le modèle ML

- Algorithme : Random Forest (200 arbres, class_weight=balanced)
- 3 classes : LOW / MEDIUM / HIGH
- 11 features comportementales et temporelles
- Labellisation dynamique avec escalade comportementale

### Les 11 features

- Natives Wazuh : rule_id_enc, rule_level, groups_count, has_mitre, 
  src_ip_private, fired_times
- Temporelles : alert_frequency_5min, repeat_rule_10min, hour_of_day, 
  is_business_hours
- Threat Intelligence : ip_abuse_score (via AbuseIPDB)

### Importance des features (modèle V2 final)

rule_level 26,85% | alert_frequency_5min 17,26% | 
repeat_rule_10min 15,18% | rule_id_enc 10,72% | groups_count 9,70% | 
ip_abuse_score 8,32% | fired_times | has_mitre | hour_of_day | 
is_business_hours | src_ip_private

## Contribution scientifique centrale

Une alerte de rule.level=5 (classée MEDIUM par défaut) bascule 
automatiquement en HIGH après 8 répétitions depuis la même source. 
Ce comportement est impossible avec un simple seuillage Shuffle 
sur rule.level. De même, une IP publique avec un score AbuseIPDB 
de 100 est classée HIGH même avec un niveau de sévérité faible.

## Architecture du projet

soar-ai-project/
├── CLAUDE.md ← contexte pour Claude Code
├── README.md ← description du modèle
├── .gitignore
├── data/
│ ├── raw/ ← dataset CICIDS2017 (approche initiale)
│ ├── processed/ ← dataset nettoyé
│ └── simulated/ ← alertes Wazuh exportées (CSV)
├── scripts/
│ ├── simulate_attacks.py ← génération de logs d'attaque
│ └── export_wazuh_alerts.py ← export alertes Wazuh + features temporelles
├── model/
│ ├── train.py ← entraînement Random Forest V2
│ ├── predict.py ← classification + AbuseIPDB + historique
│ └── saved/
│ ├── model_wazuh_v2.pkl
│ ├── label_encoder_v2.pkl
│ ├── rule_id_encoder_v2.pkl
│ └── feature_names_v2.pkl
├── api/
│ ├── app.py ← API Flask (/predict /respond/* /health /stats)
│ ├── .env ← variables d'environnement (non versionné)
│ ├── .env.example
│ └── logs/
│ └── incidents.json ← alertes LOW journalisées
└── rapport/
├── main.tex ← rapport PFE LaTeX
├── images/ ← captures et diagrammes
└── presentation/ ← slides Slidev (soutenance)


### Rôle de chaque composant

- **data/** — datasets : CICIDS2017 (abandonné) et alertes Wazuh natives
- **scripts/** — génération d'attaques et export du dataset depuis Wazuh
- **model/** — entraînement et inférence du Random Forest
- **api/** — API Flask, pont entre Shuffle et le modèle, gère la réponse
- **rapport/** — document PFE et présentation de soutenance

## Environnement technique

- VM Ubuntu Server 24.04 LTS (VirtualBox, 10 Go RAM, 4 vCPU)
- Docker : 7 conteneurs (Wazuh x3, Shuffle x4)
- Python 3.12.3, scikit-learn 1.4.2, Flask
- Réseau Host-Only 192.168.56.100

## Résultats clés

- Accuracy : 100% (jeu de test, 789 exemples)
- Temps de réponse API : 1,231 s
- 5 342 alertes traitées sur la période de test
- Pipeline opérationnel end-to-end (Telegram + Email + blocage IP)

## Limites assumées

- Dataset de laboratoire (corrélation feature-label documentée)
- 100% accuracy reflète la cohérence interne, pas la généralisation
- Blocage IP validé côté API, nécessite un agent Wazuh déployé en production
- API en mode développement (Gunicorn requis en production)

## Captures disponibles (dossier rapport/images/)

- escalade_medium_high.png — démonstration de l'escalade comportementale
- feature_importance_v2_final.png — importance des 11 features
- telegram_high_blocked.png — notification Telegram HIGH enrichie
- email_high_blocked.png — email HIGH avec statut de blocage
- confusion_matrix_xgboost.png / confusion_matrix_random_forest.png
- wazuh_dashboard.png — statistiques globales
- docker_ps.png / api_predictions.png / workflow_shuffle.png
