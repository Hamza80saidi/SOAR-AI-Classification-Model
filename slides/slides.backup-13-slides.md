---
theme: default
title: AI-Enhanced SOAR for Automated Incident Response
titleTemplate: '%s'
info: |
  Soutenance PFE — Master D3SI
  Hamza Saidi — FSA Béni Mellal — 2025-2026
author: Hamza Saidi
keywords: SIEM, SOAR, Wazuh, Shuffle, Random Forest
colorSchema: light
aspectRatio: 16/9
canvasWidth: 980
fonts:
  sans: 'Inter'
  serif: 'Inter'
  mono: 'Fira Code'
transition: fade
mdc: true
---
layout: cover
---

<div class="flex gap-4 justify-center mb-8">
  <div class="logo-badge">FSA</div>
  <div class="logo-badge">OCP</div>
</div>

# Une IA pour trier les alertes de sécurité

### Insérer un module de Machine Learning entre un SIEM et un SOAR

<br>

**Hamza Saidi**
Master Data Science et Sécurité des Systèmes d'Information

<div class="mt-8 text-sm" style="opacity:0.85">
Encadrant pédagogique&nbsp;: Pr.&nbsp;Mohamed El Fezazi<br>
Encadrants OCP&nbsp;: M.&nbsp;Fahmi Abderrahim, M.&nbsp;Erraji Hamza<br>
Année universitaire 2025-2026
</div>

<!--
[0:00] Bonjour, je m'appelle Hamza Saidi. Mon PFE répond à un problème concret
rencontré sur le terrain à l'OCP, que je vais vous présenter.
-->

---

# Le problème chez OCP

Le SIEM de l'OCP (Wazuh) surveille déjà l'infrastructure en continu.

<div class="big-number mt-6">~100 alertes / seconde</div>

<div class="callout-warning mt-6">
Brancher un SOAR dessus sans trier avant ne change rien&nbsp;: il reçoit le même flux brut et finit tout aussi saturé que le SIEM. Les analystes restent noyés, juste dans un autre outil.
</div>

<!--
[0:40] Le vrai souci n'est pas l'absence d'outil SOAR, c'est l'absence de tri
en amont. J'ai identifié ça moi-même en observant le déploiement en cours.
-->

---

# L'idée

<div class="mt-16 text-center" style="font-size:1.5em; line-height:1.6;">

Ajouter une couche qui <strong>classe chaque alerte</strong>
selon son comportement réel,
pas selon un simple seuil fixe.

</div>

<div class="mt-10 text-center text-sm" style="opacity:0.8">
Fréquence des attaques · répétition depuis la même source · réputation de l'IP
</div>

<!--
[1:30] C'est l'idée centrale que j'ai proposée et fait valider par mon
encadrant OCP. Tout le reste du projet en découle.
-->

---

# Architecture du système

```mermaid {scale: 1.0}
%%{init: {'theme':'base', 'themeVariables': {'fontSize':'20px','primaryColor':'#ffffff','primaryTextColor':'#1b2a41','primaryBorderColor':'#1b2a41','lineColor':'#1b2a41'}}}%%
graph LR
  A["Simulation"] --> B["Wazuh<br/>SIEM"]
  B --> C["Shuffle<br/>SOAR"]
  C --> D["API Flask<br/>Random Forest"]
  D --> E["Réponse<br/>blocage IP, Telegram, email"]
  classDef accent fill:#2e7d32,color:#ffffff,stroke:#1b2a41,stroke-width:2px;
  class D accent;
```

<div class="text-sm mt-4" style="opacity:0.8">
Wazuh et Shuffle sont retenus pour trois raisons&nbsp;: open source, webhooks natifs, déploiement Docker simple.
</div>

<!--
[2:30] Cinq briques, chacune avec un rôle précis. La brique IA au centre
est celle que j'ai conçue et développée.
-->

---

# Que se passe-t-il pour une alerte&nbsp;?

<div class="text-sm mb-2" style="opacity:0.8">Exemple&nbsp;: une attaque par force brute sur SSH</div>

```mermaid {scale: 0.95}
%%{init: {'theme':'base', 'themeVariables': {'fontSize':'19px','actorBkg':'#ffffff','actorBorder':'#1b2a41','actorTextColor':'#1b2a41','signalColor':'#1b2a41','signalTextColor':'#1b2a41'}}}%%
sequenceDiagram
    autonumber
    participant W as Wazuh
    participant S as Shuffle
    participant A as API Flask
    participant Ab as AbuseIPDB
    participant T as Telegram

    W->>S: Alerte détectée (webhook)
    S->>A: POST /predict
    A->>Ab: Réputation de l'IP
    Ab-->>A: Score de confiance
    A-->>S: HIGH, confiance 0.88
    S->>T: Alerte et blocage IP
```

<div class="big-number mt-2" style="font-size:1.6em;">Temps mesuré&nbsp;: 1,231 seconde</div>

<!--
[3:30] Tout ce cycle, de la détection à la notification, tient en un peu
plus d'une seconde. C'est largement sous notre objectif de 2 secondes.
-->

---

# Pourquoi pas un dataset existant&nbsp;?

Premier essai&nbsp;: entraîner le modèle sur **CICIDS2017**, un dataset public de référence.

<div class="callout mt-4">
Les 5 features les plus importantes de ce dataset (60,9&nbsp;% du score) viennent toutes de captures réseau&nbsp;: taille de paquets, port de destination... Une alerte Wazuh ne contient aucune de ces informations.
</div>

<div class="mt-4 text-sm">
Résultat&nbsp;: <strong>2&nbsp;410 à 2&nbsp;436</strong> alertes réelles classées à tort comme du trafic normal.
</div>

<div class="mt-2 text-center font-bold" style="color:#1b2a41;">
Un dataset réseau ne peut pas servir à classer des logs système.
</div>

<!--
[4:45] C'est le vrai tournant du projet&nbsp;: j'ai dû abandonner CICIDS2017
et construire mon propre dataset à partir de vraies alertes Wazuh.
-->

---

# Les données et les critères retenus

<div grid="~ cols-2 gap-6">
<div>

**3&nbsp;945 alertes**, 3 classes

| Classe | Part |
|---|---|
| HIGH | 44,5&nbsp;% |
| LOW | 31,9&nbsp;% |
| MEDIUM | 23,6&nbsp;% |

</div>
<div>

**Top critères du modèle**

| Critère | Poids |
|---|---|
| Niveau Wazuh | 26,9&nbsp;% |
| Répétitions (10 min) | 13,8&nbsp;% |
| Fréquence (5 min) | 13,1&nbsp;% |
| Réputation IP | 8,3&nbsp;% |

</div>
</div>

<!--
[5:45] 11 critères au total, mais ceux-ci dominent la décision. Les deux
du milieu sont calculés en direct à partir de l'historique des alertes.
-->

---

# Le modèle et ses résultats

Un **Random Forest** à 200 arbres, choisi pour sa robustesse et sa capacité à gérer des classes déséquilibrées.

| Classe | Précision | Rappel | F1 |
|---|---|---|---|
| HIGH | 1,00 | 1,00 | 1,00 |
| LOW | 1,00 | 1,00 | 1,00 |
| MEDIUM | 1,00 | 1,00 | 1,00 |

<div class="callout-warning mt-4 text-sm">
100&nbsp;% sur 789 alertes de test, mais attention&nbsp;: le modèle apprend la règle qui a servi à construire les labels. Ça prouve sa cohérence, pas sa capacité à généraliser à un autre site.
</div>

<!--
[6:45] J'insiste sur cette nuance volontairement&nbsp;: un 100&nbsp;% qui
cache un biais de construction n'a aucune valeur si on ne le signale pas.
-->

---

# Mieux qu'un simple seuil

<div class="text-sm mb-2">Même règle Wazuh (niveau 5), deux issues différentes&nbsp;:</div>

| Alertes | Répétitions | Décision |
|---|---|---|
| 1 à 8 | 0 à 7 | MEDIUM |
| 9 | 8 | **HIGH** |

<div class="callout mt-4">
Un seuil fixe du type <code>niveau&nbsp;&gt;=&nbsp;7</code> n'aurait jamais vu ce changement&nbsp;: il ne regarde que l'alerte en cours, jamais son historique.
</div>

<div class="mt-3 text-center font-bold" style="color:#1b2a41;">
Le modèle a appris un comportement, pas juste une règle Wazuh.
</div>

<!--
[7:45] C'est la preuve expérimentale de l'intérêt du ML ici&nbsp;: la
même source, vue plusieurs fois, finit par déclencher une vraie réaction.
-->

---

# Le pipeline en conditions réelles

Trois scénarios testés de bout en bout, sans réglage manuel entre chacun&nbsp;:

| Scénario | Résultat | Action |
|---|---|---|
| LOW (niveau 3) | confiance 76-98&nbsp;% | journalisation |
| MEDIUM (XSS) | confiance 63&nbsp;% | notification analyste |
| HIGH (IP malveillante) | confiance 88-94&nbsp;% | blocage + alertes |

<div class="callout mt-4 text-sm">
Sur le cas HIGH&nbsp;: blocage IP, Telegram et email partent en parallèle, le tout en moins de 10 secondes.
</div>

<!--
[8:30] Les trois branches du pipeline fonctionnent réellement, pas
seulement sur le papier.
-->

---

# Ce que je n'ai pas encore résolu

- Dataset constitué en laboratoire, pas sur des IPs attaquantes réelles
- Le blocage IP est validé côté API, mais il faut un agent Wazuh sur chaque serveur pour qu'il agisse vraiment
- Pas encore d'étude d'ablation formelle sur les 11 critères
- L'API tourne encore en mode développement, pas en production

<!--
[9:10] Je préfère les citer moi-même que les laisser découvrir en
question. Aucune de ces limites ne remet en cause le résultat central.
-->

---
layout: center
---

# En résumé

Une couche de Machine Learning entre Wazuh et Shuffle, qui classe chaque alerte selon son comportement réel plutôt que selon un seuil fixe.

<div class="callout mt-6">
Deux alertes de même niveau Wazuh peuvent recevoir deux traitements différents&nbsp;: c'est ce qu'un simple seuillage ne permet pas, et c'est la contribution centrale de ce travail.
</div>

<br>

Prochaine étape&nbsp;: déployer un agent Wazuh sur l'infrastructure OCP pour rendre le blocage IP effectif.

<div class="mt-10 text-center text-sm" style="opacity:0.7">
Merci de votre attention — questions bienvenues
</div>

<!--
[9:40] Je termine ici, prêt à répondre à vos questions.
-->
