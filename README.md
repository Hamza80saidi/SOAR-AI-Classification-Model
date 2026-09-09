# SOAR-AI Classification Model

Modèle de classification d'alertes de sécurité basé sur
Random Forest, entraîné sur des alertes natives Wazuh.

## Ce que fait le modèle

Classe chaque alerte en trois niveaux de criticité :
- **LOW** — événement informatif, journalisation uniquement
- **MEDIUM** — événement notable, notification analyste
- **HIGH** — menace active, réponse immédiate requise

La classification repose sur 11 features comportementales
et temporelles extraites directement des champs JSON Wazuh,
incluant la fréquence d'attaque, la répétition depuis la
même source et la réputation de l'IP (AbuseIPDB).

## Emplacement du modèle

model/
├── train.py ← entraînement
├── predict.py ← prédiction
└── saved/
├── model_wazuh_v2.pkl
├── label_encoder_v2.pkl
├── rule_id_encoder_v2.pkl
└── feature_names_v2.pkl


## Utilisation

```python
from model.predict import predict

result = predict(wazuh_alert_json)
# result = { "label": "HIGH", "score": 94, "action": "BLOCK_AND_ALERT" }
```

---
*PFE Master D3SI — Université Sultan Moulay Slimane 2025-2026*
