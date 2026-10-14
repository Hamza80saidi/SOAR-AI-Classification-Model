---
theme: default
title: AI-Enhanced SOAR for Automated Incident Response in Enterprise SIEM
titleTemplate: '%s'
info: |
  Soutenance PFE — Master D3SI — FSA Béni Mellal — 2025-2026
author: Hamza Saidi
colorSchema: light
aspectRatio: 16/9
canvasWidth: 1280
fonts:
  sans: Inter
  mono: Fira Code
transition: fade
mdc: true
exportFilename: soutenance-pfe-hamza-saidi
layout: cover
---

<div class="cover-badge">Projet de fin d'études</div>

# AI-Enhanced SOAR for Automated Incident Response in Enterprise SIEM

<div class="sub">Une couche de classification par apprentissage automatique entre Wazuh et Shuffle</div>

<div class="cover-meta">
<div><div class="lab">Présenté par</div><div class="val"><b>Hamza Saidi</b><br>Master Data Science et Sécurité des Systèmes d'Information</div></div>
<div><div class="lab">Encadrant pédagogique</div><div class="val">Pr. Mohamed El Fezazi<br>FSA Béni Mellal</div></div>
<div><div class="lab">Encadrants professionnels</div><div class="val">M. Fahmi Abderrahim<br>M. Erraji Hamza</div></div>
<div><div class="lab">Année universitaire</div><div class="val">2025 – 2026</div></div>
</div>

<!--
[0:00 – 0:30] Bonjour à tous. Je m'appelle Hamza Saidi. Je vous présente mon projet de fin d'études, réalisé à l'OCP : une couche d'intelligence artificielle qui trie les alertes de sécurité entre un SIEM et un SOAR.
-->

---

<div class="kicker">Déroulé</div>

# Plan de la présentation

<div class="cards c2" style="margin-top:8px">
<div class="card accent"><div class="big" style="font-size:41px">01</div><h3>Contexte et problématique</h3><p>L'OCP, le problème des 100 alertes par seconde, les objectifs du projet</p></div>
<div class="card blue"><div class="big" style="font-size:41px;color:var(--blue)">02</div><h3>État de l'art et conception</h3><p>Choix SIEM et SOAR, apprentissage automatique pour la détection, architecture en 5 couches</p></div>
<div class="card violet"><div class="big" style="font-size:41px;color:var(--violet)">03</div><h3>Réalisation</h3><p>Dataset, 11 features, labellisation comportementale, Random Forest, API Flask, workflow Shuffle</p></div>
<div class="card orange"><div class="big" style="font-size:41px;color:var(--orange)">04</div><h3>Résultats et discussion</h3><p>Performances, escalade comportementale, tests de bout en bout, limites et perspectives</p></div>
</div>

<!--
[0:30 – 1:00] Quatre parties : le contexte et le problème, l'état de l'art et la conception, la réalisation, puis les résultats avec une discussion critique, y compris les limites.
-->

---

<div class="kicker">01 · Contexte</div>

# Le cadre du projet : le Groupe OCP

<div class="row" style="gap:36px; margin-top:6px">
<div class="col" style="flex:1.6">
<p><span class="chip g">Groupe</span>Premier exportateur mondial de phosphate. Fondé en 1920, présent dans plus de 160 pays.</p>
<p><span class="chip b">Site</span>Benguerir, laverie de Gantour, département Maintenance. Stage de 4 mois, de mars à juillet 2026, en cybersécurité industrielle.</p>
<p><span class="chip o">Enjeu</span>Le programme OCP 4.0 relie les capteurs, l'automatisation et les données. Les systèmes industriels, longtemps isolés, deviennent accessibles depuis le réseau informatique : la surface d'attaque s'élargit.</p>
<p><span class="chip s">Besoin</span>Détecter les incidents et y répondre vite, malgré un volume d'alertes qui augmente.</p>
</div>
<div class="col" style="flex:1">
<div class="card" style="margin-bottom:14px"><div class="big">1920</div><div class="cap">création du Groupe OCP</div></div>
<div class="card" style="margin-bottom:14px"><div class="big">160+</div><div class="cap">pays où le groupe est présent</div></div>
<div class="card"><div class="big">4 mois</div><div class="cap">de stage à Benguerir (mars à juillet 2026)</div></div>
</div>
</div>

<!--
[1:00 – 2:00] L'OCP est le premier exportateur mondial de phosphate. J'ai fait mon stage de quatre mois à la laverie de Gantour, à Benguerir. Avec le programme OCP 4.0, l'informatique et l'industriel se rapprochent : c'est bien pour la production, mais cela expose davantage les systèmes aux cyberattaques.
-->

---

<div class="kicker">01 · Problématique</div>

# Le problème : un SOAR sans triage ne sert à rien

<div style="display:grid; grid-template-columns: 300px 1fr; gap:28px; margin-top:6px; align-items:center">
<div class="card dark" style="text-align:center; padding:26px 18px"><div class="big" style="font-size:79px">≈100</div><div class="cap" style="font-size:26px">alertes par seconde générées par le SIEM de l'OCP en production</div></div>
<div>
<div style="font-size:19px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--red); margin-bottom:6px">Sans triage</div>
<div style="display:flex; align-items:center; gap:12px; margin-bottom:22px; font-size:20px; line-height:1.3">
<div class="card blue" style="padding:12px 20px"><b>SIEM</b> Wazuh</div>
<div class="small" style="min-width:120px; text-align:center">flux brut<br><b style="color:var(--red)">100 alertes/s</b></div>
<div class="card violet" style="padding:12px 20px"><b>SOAR</b> Shuffle</div>
<div class="card warn" style="padding:12px 20px"><b>Analystes saturés</b></div>
</div>
<div style="font-size:19px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--green); margin-bottom:6px">Avec notre couche de triage</div>
<div style="display:flex; align-items:center; gap:12px; font-size:20px; line-height:1.3">
<div class="card blue" style="padding:12px 20px"><b>SIEM</b> Wazuh</div>
<div class="card accent" style="padding:12px 20px; background:var(--green-soft)"><b>Classification ML</b><br><span class="small">LOW · MEDIUM · HIGH</span></div>
<div class="card violet" style="padding:12px 20px"><b>SOAR</b></div>
<div class="card accent" style="padding:12px 20px"><b>Seul l'utile arrive</b></div>
</div>
</div>
</div>

<div class="banner" style="margin-top:34px">Sans filtre, le SOAR reçoit le même flux brut et reproduit <b>la saturation qu'il devait résoudre</b>. Les analystes retrouvent le même volume non priorisé, dans un autre outil.</div>

<!--
[2:00 – 3:00] Le SIEM de l'OCP génère environ 100 alertes par seconde. Le projet SOAR devait automatiser la réponse. Mais sans tri en amont, le SOAR reçoit exactement le même flux et sature de la même façon. C'est ce constat, fait pendant le déploiement, qui est à l'origine de mon sujet. J'ai proposé d'insérer un classifieur entre les deux, et mon encadrant professionnel, M. Erraji, a validé l'idée.
-->

---

<div class="kicker">01 · Objectifs</div>

# Objectifs et exigences du système

<div class="row" style="gap:30px">
<div class="col" style="flex:1.35">
<div style="font-size:19px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); margin-bottom:8px">Ce que le système doit faire</div>
<div style="font-size:24px; line-height:1.38">
<p><span class="chip">BF1</span>Surveiller les logs en temps réel et générer des alertes</p>
<p><span class="chip">BF2</span>Transmettre chaque alerte au SOAR par webhook</p>
<p><span class="chip g">BF3</span>Classer en LOW, MEDIUM ou HIGH avec un score de confiance</p>
<p><span class="chip g">BF4</span>Escalader selon le comportement dans le temps</p>
<p><span class="chip r">BF5</span>Bloquer l'IP attaquante pour les alertes HIGH</p>
<p><span class="chip b">BF6</span>Notifier par Telegram et par e-mail</p>
<p><span class="chip s">BF7</span>Exposer <code>/health</code> et <code>/stats</code></p>
</div>
</div>
<div class="col" style="flex:1">
<div style="font-size:19px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); margin-bottom:8px">Contraintes à respecter</div>
<div class="cards c2">
<div class="card"><div class="big" style="font-size:43px">&lt; 2&nbsp;s</div><div class="cap">temps de réponse de l'API</div></div>
<div class="card"><div class="big" style="font-size:43px">10&nbsp;Go</div><div class="cap">de RAM et 4 vCPU pour toute l'infrastructure</div></div>
<div class="card"><div class="big" style="font-size:43px">100&nbsp;%</div><div class="cap">des composants serveur sous Docker</div></div>
<div class="card"><div class="big" style="font-size:36px; padding-top:6px">Dataset</div><div class="cap">reproductible, généré depuis Wazuh</div></div>
</div>
</div>
</div>

<!--
[3:00 – 4:00] Sept besoins fonctionnels. Les deux au cœur du projet sont BF3 et BF4 : classer chaque alerte avec un score, et escalader selon le comportement. Côté contraintes, la principale est un temps de réponse inférieur à deux secondes, avec seulement 10 Go de RAM.
-->

---

<div class="kicker">02 · État de l'art</div>

# Choix de la pile SIEM et SOAR

<div class="row" style="gap:26px">
<div class="col card blue" style="padding:22px 26px">
<div style="display:flex; justify-content:space-between; align-items:baseline"><h3 style="font-size:36px">Wazuh 4.9.2</h3><span class="small">SIEM</span></div>
<ul style="margin-top:10px">
<li>Open source et gratuit</li>
<li>Nombreuses règles <b>MITRE ATT&amp;CK</b></li>
<li>Webhook natif vers le SOAR</li>
<li>Image Docker officielle</li>
</ul>
<p class="small" style="margin-top:14px">Écartés : Splunk et IBM QRadar (commerciaux, coûteux), Elastic (webhook via Logstash)</p>
</div>
<div class="col card violet" style="padding:22px 26px">
<div style="display:flex; justify-content:space-between; align-items:baseline"><h3 style="font-size:36px">Shuffle 2.2.0</h3><span class="small">SOAR</span></div>
<ul style="margin-top:10px">
<li>Open source et gratuit</li>
<li>Léger : tient dans 10&nbsp;Go de RAM</li>
<li>Blocs HTTP natifs</li>
<li>Limite : pas de conditionnel natif, contournée par des conditions sur les flèches</li>
</ul>
<p class="small" style="margin-top:14px">Écartés : TheHive (webhook par plugin), Cortex XSOAR et Swimlane (commerciaux)</p>
</div>
</div>

<!--
[4:00 – 5:00] J'ai comparé plusieurs solutions. Wazuh a été retenu pour ses règles MITRE, son webhook natif et son image Docker officielle. Shuffle pour sa légèreté et ses blocs HTTP natifs. Les solutions commerciales sont écartées pour leur coût.
-->

---
class: mid
---

<div class="kicker">02 · État de l'art</div>

# Ce que dit la littérature sur le ML appliqué aux IDS

<div class="cards c2" style="margin-top:4px">
<div class="card"><h3>Gu et al. (2019)</h3><p>Random Forest bat SVM et Naive Bayes sur CICIDS2017 : <b>F1 de 98,7&nbsp;%</b> sur la classe DoS.</p></div>
<div class="card"><h3>Sharafaldin et al. (2018)</h3><p>Les modèles entraînés sur des features réseau se généralisent mal d'un environnement à l'autre.</p></div>
<div class="card"><h3>Catillo et al. (2022)</h3><p>Le même problème de <b>domain shift</b> apparaît quand on applique ces modèles à des logs système.</p></div>
<div class="card"><h3>Hindy et al. (2020)</h3><p>Les features sémantiques (type d'événement, source, fréquence) sont plus stables que les features réseau.</p></div>
</div>
<div class="banner green" style="margin-top:22px"><b>Notre position :</b> entraîner le modèle directement sur les alertes du SIEM cible (approche <i>domain-native</i>) et ajouter ce qui manque à la littérature : <b>la fréquence des alertes et la réputation de l'IP source</b>.</div>

<!--
[5:00 – 6:00] La littérature montre que Random Forest est très performant sur les datasets publics, mais que ces modèles se généralisent mal d'un domaine à l'autre. Je pars donc des alertes réelles du SIEM cible, et j'ajoute deux dimensions : le comportement dans le temps et la réputation des IP.
-->

---

<div class="kicker">02 · Première approche</div>

# Pourquoi CICIDS2017 a été abandonné

<div class="row" style="gap:30px; align-items:center">
<div class="col" style="flex:1.05; text-align:center">
<img src="/images/confusion_matrix_random_forest.png" style="width:100%; border:1px solid var(--line); border-radius:8px; background:#fff" />
<div class="small" style="margin-top:6px">Matrice de confusion, Random Forest sur CICIDS2017</div>
</div>
<div class="col" style="flex:1">
<div class="card warn" style="margin-bottom:14px"><div class="big" style="color:var(--red)">60,9&nbsp;%</div><div class="cap">du pouvoir discriminant vient de 5 features de trafic réseau (taille de paquets, port, débit). <b>Aucune n'existe dans une alerte Wazuh.</b></div></div>
<div class="card warn" style="margin-bottom:14px"><div class="big" style="color:var(--red)">2 436</div><div class="cap">exemples LOW prédits BENIGN par le Random Forest (2 410 pour XGBoost)</div></div>
<div class="banner" style="font-size:24px">Incompatibilité structurelle : un mapping heuristique ne la corrige pas. D'où un <b>dataset natif Wazuh</b>.</div>
</div>
</div>

<!--
[6:00 – 7:00] Ma première approche utilisait CICIDS2017. Elle a échoué, et pas à cause d'un mauvais réglage : les cinq features les plus importantes, soit 60,9 % du pouvoir de décision, sont des mesures de trafic réseau qui n'existent pas dans une alerte Wazuh. Le modèle prend donc tout pour du trafic bénin. J'ai changé d'approche.
-->

---

<div class="kicker">02 · Conception</div>

# Architecture en cinq couches

<div class="arch" style="margin-top:6px">
<div class="layer sim"><div class="n">Couche 1</div><div class="t">Simulation</div><div class="tech">simulate_attacks.py</div><div class="d">4 types d'attaques : brute force SSH, scan de ports, XSS, connexions suspectes</div></div>
<div class="link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 6l6 6-6 6"/></svg></div>
<div class="layer siem"><div class="n">Couche 2</div><div class="t">SIEM</div><div class="tech">Wazuh 4.9.2</div><div class="d">Détecte, corrèle, envoie l'alerte en JSON par webhook</div></div>
<div class="link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 6l6 6-6 6"/></svg></div>
<div class="layer soar"><div class="n">Couche 3</div><div class="t">SOAR</div><div class="tech">Shuffle 2.2.0</div><div class="d">Reçoit l'alerte et appelle l'API de classification</div></div>
<div class="link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 6l6 6-6 6"/></svg></div>
<div class="layer ia"><div class="n">Couche 4</div><div class="t">IA</div><div class="tech">Flask + Random Forest</div><div class="d">Calcule 11 features, renvoie un label et un score de confiance</div></div>
<div class="link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 6l6 6-6 6"/></svg></div>
<div class="layer rep"><div class="n">Couche 5</div><div class="t">Réponse</div><div class="tech">Actions automatiques</div><div class="d">Blocage IP, Telegram, e-mail ou simple journal selon le label</div></div>
</div>

<div class="row" style="gap:20px; margin-top:24px; align-items:stretch">
<div class="col" style="flex:1.25"><div class="code-box" style="font-size:20px; padding:16px 20px; height:100%; box-sizing:border-box; white-space:normal"><span class="c">// réponse de POST /predict</span><br>{ <span class="s">"label"</span>: <span class="s">"HIGH"</span>,<br>&nbsp;&nbsp;<span class="s">"confidence"</span>: 0.88,<br>&nbsp;&nbsp;<span class="s">"action"</span>: <span class="s">"BLOCK_AND_ALERT"</span>,<br>&nbsp;&nbsp;<span class="s">"rule_id"</span>: <span class="s">"5712"</span> }</div></div>
<div class="col" style="flex:1"><div class="banner" style="font-size:24px; height:100%; box-sizing:border-box; display:flex; align-items:center"><span>Les couches ne se parlent qu'en <b>JSON</b> : on peut remplacer le modèle ou la plateforme SOAR sans toucher au reste.</span></div></div>
</div>

<!--
[7:00 – 8:30] Voici l'architecture. Cinq couches : on simule des attaques, Wazuh les détecte, Shuffle orchestre, mon API classe l'alerte avec un Random Forest, puis la couche réponse agit. Les couches échangent uniquement du JSON, donc chacune peut évoluer indépendamment.
-->

---
class: dense
---

<div class="kicker">02 · Conception</div>

# Le parcours d'une alerte HIGH, étape par étape

<svg viewBox="0 0 1152 430" style="width:100%; height:auto; margin-top:-6px" font-family="Inter, Segoe UI, sans-serif">
<defs>
<marker id="ah" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="11" refX="13" refY="5.5" orient="auto"><path d="M0,0 L14,5.5 L0,11 Z" fill="#10233f"/></marker>
<marker id="ahg" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="11" refX="13" refY="5.5" orient="auto"><path d="M0,0 L14,5.5 L0,11 Z" fill="#5b6776"/></marker>
</defs>
<g class="sq-actor">
<rect x="26" y="4" width="140" height="42" rx="7" fill="#1b7ba8"/><text x="96" y="32" fill="#fff">Wazuh</text>
<rect x="218" y="4" width="140" height="42" rx="7" fill="#6b4fa3"/><text x="288" y="32" fill="#fff">Shuffle</text>
<rect x="410" y="4" width="140" height="42" rx="7" fill="#2e8b2e"/><text x="480" y="32" fill="#fff">API Flask</text>
<rect x="602" y="4" width="140" height="42" rx="7" fill="#5b6776"/><text x="672" y="32" fill="#fff">AbuseIPDB</text>
<rect x="794" y="4" width="140" height="42" rx="7" fill="#2e8b2e"/><text x="864" y="32" fill="#fff">Random Forest</text>
<rect x="986" y="4" width="140" height="42" rx="7" fill="#b5473a"/><text x="1056" y="32" fill="#fff">Réponse</text>
</g>
<g stroke="#c3ccd7" stroke-width="2" stroke-dasharray="6 6">
<line x1="96" y1="46" x2="96" y2="425"/><line x1="288" y1="46" x2="288" y2="425"/><line x1="480" y1="46" x2="480" y2="425"/><line x1="672" y1="46" x2="672" y2="425"/><line x1="864" y1="46" x2="864" y2="425"/><line x1="1056" y1="46" x2="1056" y2="425"/>
</g>
<g stroke="#10233f" stroke-width="2.4" fill="none">
<line x1="96" y1="96" x2="286" y2="96" marker-end="url(#ah)"/>
<line x1="288" y1="148" x2="478" y2="148" marker-end="url(#ah)"/>
<line x1="480" y1="200" x2="670" y2="200" marker-end="url(#ah)"/>
<line x1="480" y1="252" x2="862" y2="252" marker-end="url(#ah)"/>
<line x1="480" y1="396" x2="1054" y2="396" marker-end="url(#ah)"/>
</g>
<g stroke="#5b6776" stroke-width="2.4" fill="none" stroke-dasharray="7 5">
<line x1="864" y1="304" x2="482" y2="304" marker-end="url(#ahg)"/>
<line x1="480" y1="352" x2="290" y2="352" marker-end="url(#ahg)"/>
</g>
<g class="sq-msg">
<text x="191" y="85">alerte JSON (règle 5712)</text>
<text x="383" y="137">POST /predict</text>
<text x="575" y="189">réputation de l'IP</text>
<text x="671" y="241">extraction des 11 features</text>
<text x="673" y="293">label + probabilités</text>
<text x="385" y="341" style="font-size:18px">&#123;HIGH, 0,88&#125;</text>
<text x="768" y="385">blocage IP · Telegram · e-mail</text>
</g>
<g class="sq-num">
<circle cx="70" cy="96" r="14" fill="#10233f"/><text x="70" y="102">1</text>
<circle cx="262" cy="148" r="14" fill="#10233f"/><text x="262" y="154">2</text>
<circle cx="454" cy="200" r="14" fill="#10233f"/><text x="454" y="206">3</text>
<circle cx="454" cy="252" r="14" fill="#10233f"/><text x="454" y="258">4</text>
<circle cx="890" cy="304" r="14" fill="#5b6776"/><text x="890" y="310">5</text>
<circle cx="454" cy="352" r="14" fill="#5b6776"/><text x="454" y="358">6</text>
<circle cx="506" cy="396" r="14" fill="#10233f"/><text x="506" y="402">7</text>
</g>
</svg>

<div class="banner green" style="margin-top:6px; display:flex; justify-content:space-between; align-items:center; font-size:25px"><span>Cas simulé : brute force SSH, règle Wazuh 5712</span><span style="font-size:34px; font-weight:800">1,231&nbsp;s &nbsp;<span style="font-size:22px; font-weight:500">mesuré, objectif &lt; 2&nbsp;s</span></span></div>

<!--
[8:30 – 10:00] Prenons une attaque par force brute SSH. Un : Wazuh détecte la règle 5712 et envoie l'alerte à Shuffle. Deux : Shuffle appelle l'API. Trois et quatre : l'API interroge AbuseIPDB et calcule les 11 features. Cinq et six : le Random Forest renvoie le label avec un score, ici HIGH à 88 %. Sept : la couche réponse bloque l'IP et notifie. Le tout en 1,231 seconde, sous la limite de deux secondes.
-->

---

<div class="kicker">03 · Réalisation</div>

# Le dataset : 3 945 alertes natives de Wazuh

<div class="row" style="gap:34px">
<div class="col" style="flex:1">
<div style="font-size:19px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); margin-bottom:8px">Construit en trois couches</div>
<div class="card accent" style="margin-bottom:12px; padding:12px 18px"><h3 style="font-size:24px">1. Alertes organiques</h3><p style="font-size:22px">Générées par <code>simulate_attacks.py</code> et détectées par Wazuh</p></div>
<div class="card blue" style="margin-bottom:12px; padding:12px 18px"><h3 style="font-size:24px">2. Alertes injectées</h3><p style="font-size:22px">Niveaux 10 et 12, difficiles à déclencher naturellement</p></div>
<div class="card orange" style="padding:12px 18px"><h3 style="font-size:24px">3. IP publiques malveillantes</h3><p style="font-size:22px">Pour entraîner la feature de réputation AbuseIPDB</p></div>
</div>
<div class="col" style="flex:1.1">
<div style="font-size:19px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); margin-bottom:12px">Distribution des labels</div>
<div class="bar-row"><div class="lab" style="width:110px">HIGH</div><div class="track"><div class="fill" style="width:44.5%; background:var(--red)"></div></div><div class="val" style="width:210px; white-space:nowrap">1 756 · 44,5&nbsp;%</div></div>
<div class="bar-row"><div class="lab" style="width:110px">LOW</div><div class="track"><div class="fill" style="width:31.9%; background:var(--green)"></div></div><div class="val" style="width:210px; white-space:nowrap">1 258 · 31,9&nbsp;%</div></div>
<div class="bar-row"><div class="lab" style="width:110px">MEDIUM</div><div class="track"><div class="fill" style="width:23.6%; background:var(--orange)"></div></div><div class="val" style="width:210px; white-space:nowrap">931 · 23,6&nbsp;%</div></div>
<p class="small" style="margin-top:16px">Sans l'injection ciblée, HIGH n'aurait représenté que 5&nbsp;% du dataset. Découpage 80 / 20 stratifié : <b>789 alertes de test</b>.</p>
<p class="small">Les 5 342 alertes du dashboard Wazuh incluent des événements système (démarrages, SCA, rootcheck), exclus volontairement.</p>
</div>
</div>

<!--
[10:00 – 11:00] Le dataset compte 3 945 alertes, construit en trois couches : des alertes organiques, des alertes injectées pour les niveaux élevés, et des alertes avec des IP publiques malveillantes. Sans injection, la classe HIGH serait à 5 %. Le chiffre de 5 342 du dashboard est différent : il inclut les événements système.
-->

---

<div class="kicker">03 · Réalisation</div>

# Les 11 features du modèle

<div class="row" style="gap:20px; align-items:stretch">
<div class="col card" style="border-top:7px solid var(--blue)">
<h3>Natives Wazuh <span class="small">(6)</span></h3>
<p class="small" style="margin-bottom:10px">Présentes dans chaque alerte</p>
<div class="frow"><code>rule_id_enc</code></div><div class="frow"><code>rule_level</code><b>26,85&nbsp;%</b></div><div class="frow"><code>groups_count</code></div><div class="frow"><code>has_mitre</code></div><div class="frow"><code>src_ip_private</code><span>1,13&nbsp;%</span></div><div class="frow"><code>fired_times</code><span>5,17&nbsp;%</span></div>
</div>
<div class="col card" style="border-top:7px solid var(--orange); background:#fffaf2">
<h3>Comportementales <span class="small">(4)</span></h3>
<p class="small" style="margin-bottom:10px">Calculées en temps réel</p>
<div class="frow"><code>alert_frequency_5min</code><b>13,10&nbsp;%</b></div><div class="frow"><code>repeat_rule_10min</code><b>13,84&nbsp;%</b></div><div class="frow"><code>hour_of_day</code></div><div class="frow"><code>is_business_hours</code><span>1,78&nbsp;%</span></div>
</div>
<div class="col card" style="border-top:7px solid var(--red)">
<h3>Threat intelligence <span class="small">(1)</span></h3>
<p class="small" style="margin-bottom:10px">Appel externe</p>
<div class="frow"><code>ip_abuse_score</code><b>8,32&nbsp;%</b></div>
<p class="small" style="margin-top:10px">Réputation de l'IP via AbuseIPDB. Vaut 0 pour une IP privée (cache, timeout 2&nbsp;s).</p>
</div>
</div>
<div class="banner" style="margin-top:20px">Les features comportementales n'existent pas dans le JSON brut : elles viennent d'un <b>historique en mémoire</b> par IP source, thread-safe, mis à jour <b>après</b> chaque calcul.</div>

<!--
[11:00 – 12:00] Onze features en trois familles. Six sont natives : on les lit dans l'alerte. Quatre sont calculées à la volée à partir d'un historique en mémoire : la fréquence sur cinq minutes, les répétitions de la même règle sur dix minutes, l'heure, et si on est en heures ouvrées. Une est de la threat intelligence : le score AbuseIPDB. L'ordre d'appel est important : on calcule avant de mettre à jour l'historique, pour ne pas compter l'alerte dans sa propre fréquence.
-->

---

<div class="kicker">03 · Réalisation</div>

# Labellisation comportementale

<div class="row" style="gap:28px">
<div class="col" style="flex:1.5">
<table><tbody>
<tr><th style="width:150px">Niveau Wazuh</th><th>Label par défaut</th><th>Escalade si…</th></tr>
<tr><td><b>7 et plus</b></td><td><span class="chip r">HIGH</span></td><td class="small" style="font-size:22px">toujours HIGH</td></tr>
<tr><td><b>5 – 6</b></td><td><span class="chip o">MEDIUM</span></td><td style="font-size:23px">fréquence ≥ 10, ou répétition ≥ 8, ou abuse ≥ 80, alors <span class="chip r">HIGH</span></td></tr>
<tr><td><b>3 – 4</b></td><td><span class="chip g">LOW</span></td><td style="font-size:23px">fréquence ≥ 15, ou répétition ≥ 10, ou abuse ≥ 80, alors <span class="chip o">MEDIUM</span></td></tr>
</tbody></table>
<p class="small" style="margin-top:12px">Fonction <code>make_label</code> de <code>train.py</code>, code complet en annexe.</p>
</div>
<div class="col" style="flex:1">
<div class="card accent" style="margin-bottom:14px"><h3>Ce que ça permet</h3><p>Deux alertes de même <code>rule.level</code> reçoivent des labels différents selon leur fréquence, leur répétition et la réputation de l'IP.</p></div>
<div class="card warn"><h3>Point méthodologique</h3><p>Le label est construit avec des critères liés aux features. Cela explique les scores très élevés, et nous y reviendrons dans les limites.</p></div>
</div>
</div>

<!--
[12:00 – 13:00] Pour entraîner le modèle, il faut des labels. Je les construis avec un schéma comportemental : le niveau Wazuh donne le label de base, et la fréquence, la répétition ou la réputation de l'IP peuvent l'escalader. Je précise tout de suite que ces critères sont corrélés aux features, et j'en discuterai dans les limites.
-->

---
class: dense
---

<div class="kicker">03 · Réalisation</div>

# Random Forest et API Flask

<div class="row" style="gap:28px">
<div class="col" style="flex:1">
<div style="font-size:19px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); margin-bottom:8px">Pourquoi Random Forest</div>
<div class="card accent" style="margin-bottom:12px; padding:12px 18px"><h3 style="font-size:24px">Classes déséquilibrées</h3><p style="font-size:22px"><code>class_weight='balanced'</code>, 200 arbres</p></div>
<div class="card accent" style="margin-bottom:12px; padding:12px 18px"><h3 style="font-size:24px">Interprétable</h3><p style="font-size:22px"><code>feature_importances_</code> pour l'analyse après coup</p></div>
<div class="card accent" style="padding:12px 18px"><h3 style="font-size:24px">Portable</h3><p style="font-size:22px">Fonctionne sur CPU et GPU, contrairement à XGBoost <code>device='cuda'</code></p></div>
</div>
<div class="col" style="flex:1.25">
<div style="font-size:19px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); margin-bottom:8px">Six endpoints</div>
<table><tbody>
<tr><th style="width:80px">HTTP</th><th>Endpoint</th><th>Rôle</th></tr>
<tr><td>POST</td><td><code>/predict</code></td><td style="font-size:22px">Classe l'alerte et lance la réponse</td></tr>
<tr><td>POST</td><td><code>/respond/high</code></td><td style="font-size:22px">Blocage IP, Telegram, e-mail</td></tr>
<tr><td>POST</td><td><code>/respond/medium</code></td><td style="font-size:22px">Telegram compact, e-mail</td></tr>
<tr><td>POST</td><td><code>/respond/low</code></td><td style="font-size:22px">Journal <code>incidents.json</code></td></tr>
<tr><td>GET</td><td><code>/health</code></td><td style="font-size:22px">Disponibilité</td></tr>
<tr><td>GET</td><td><code>/stats</code></td><td style="font-size:22px">Statistiques</td></tr>
</tbody></table>
</div>
</div>
<div class="banner" style="margin-top:18px; font-size:25px">Shuffle n'a <b>qu'un seul bloc HTTP</b> à appeler : <code style="background:#26446f;color:#fff">/predict</code> déclenche lui-même le bon <code style="background:#26446f;color:#fff">/respond/&lt;label&gt;</code>.</div>

<!--
[13:00 – 14:00] J'ai choisi Random Forest pour trois raisons : il gère le déséquilibre des classes, il est interprétable, et il est portable. L'API Flask expose six endpoints. Le point clé : Shuffle fait un seul appel à /predict, et c'est l'API qui déclenche la bonne réponse.
-->

---

<div class="kicker">03 · Réalisation</div>

# Workflow Shuffle et actions selon le label

<div style="display:flex; align-items:center; gap:10px; margin-bottom:22px">
<div class="card violet" style="padding:10px 16px; font-size:23px"><b>Webhook</b><br><span class="small">alerte Wazuh</span></div>
<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#10233f" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 6l6 6-6 6"/></svg>
<div class="card violet" style="padding:10px 16px; font-size:23px"><b>HTTP</b><br><span class="small">POST /predict</span></div>
<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#10233f" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 6l6 6-6 6"/></svg>
<div class="card violet" style="padding:10px 16px; font-size:23px"><b>Shuffle Tools</b><br><span class="small">extrait le label</span></div>
<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#10233f" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 6l6 6-6 6"/></svg>
<div class="card" style="padding:10px 16px; font-size:23px; flex:1"><b>3 branches</b> avec une condition sur chaque flèche : HIGH, MEDIUM, LOW</div>
</div>

<div class="cards c3">
<div class="card" style="border-top:8px solid var(--red)"><span class="chip r">HIGH</span><p style="margin-top:12px"><b>Blocage de l'IP</b> par Wazuh Active Response (<code>firewall-drop</code>)</p><p style="margin-top:8px">Telegram enrichi et e-mail structuré, avec le statut du blocage</p></div>
<div class="card" style="border-top:8px solid var(--orange)"><span class="chip o">MEDIUM</span><p style="margin-top:12px"><b>Notification de surveillance</b></p><p style="margin-top:8px">Telegram compact et e-mail à l'analyste, sans le surcharger</p></div>
<div class="card" style="border-top:8px solid var(--green)"><span class="chip g">LOW</span><p style="margin-top:12px"><b>Journalisation silencieuse</b></p><p style="margin-top:8px">Une ligne dans <code>incidents.json</code> : règle, horodatage, agent</p></div>
</div>
<p class="small" style="margin-top:16px">Le workflow tourne en permanence (Runtime Location : Running). L'analyste reçoit l'alerte avec l'action déjà exécutée.</p>

<!--
[14:00 – 15:00] Côté Shuffle : un webhook, un bloc HTTP, une extraction du label, puis trois branches. HIGH : blocage de l'IP, Telegram enrichi, e-mail. MEDIUM : notification compacte. LOW : simple journal. L'analyste reçoit donc une alerte avec l'action déjà prise.
-->

---
class: dense
---

<div class="kicker">04 · Résultats</div>

# Résultats du modèle V2

<div class="row" style="gap:30px">
<div class="col" style="flex:.8">
<div class="card dark" style="margin-bottom:14px"><div class="big" style="font-size:70px">100&nbsp;%</div><div class="cap">accuracy sur le jeu de test (789 / 789 alertes)</div></div>
<table><tbody>
<tr><th>Classe</th><th>F1</th><th>Support</th></tr>
<tr><td>HIGH</td><td>1,00</td><td>352</td></tr>
<tr><td>LOW</td><td>1,00</td><td>302</td></tr>
<tr><td>MEDIUM</td><td>1,00</td><td>135</td></tr>
</tbody></table>
</div>
<div class="col" style="flex:1.2">
<div style="font-size:19px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); margin-bottom:10px">Importance des features (V2 final)</div>
<div class="bar-row"><div class="lab" style="width:230px">rule_level</div><div class="track"><div class="fill" style="width:26.85%"></div></div><div class="val">26,85&nbsp;%</div></div>
<div class="bar-row"><div class="lab" style="width:230px">repeat_rule_10min</div><div class="track"><div class="fill" style="width:13.84%; background:var(--orange)"></div></div><div class="val">13,84&nbsp;%</div></div>
<div class="bar-row"><div class="lab" style="width:230px">alert_frequency_5min</div><div class="track"><div class="fill" style="width:13.1%; background:var(--orange)"></div></div><div class="val">13,10&nbsp;%</div></div>
<div class="bar-row"><div class="lab" style="width:230px">ip_abuse_score</div><div class="track"><div class="fill" style="width:8.32%; background:var(--red)"></div></div><div class="val">8,32&nbsp;%</div></div>
<div class="bar-row"><div class="lab" style="width:230px">fired_times</div><div class="track"><div class="fill" style="width:5.17%"></div></div><div class="val">5,17&nbsp;%</div></div>
<div class="bar-row"><div class="lab" style="width:230px">is_business_hours</div><div class="track"><div class="fill" style="width:1.78%"></div></div><div class="val">1,78&nbsp;%</div></div>
<div class="bar-row"><div class="lab" style="width:230px">src_ip_private</div><div class="track"><div class="fill" style="width:1.13%"></div></div><div class="val">1,13&nbsp;%</div></div>
<p class="small" style="margin-top:8px">Barres orange : features comportementales, rouge : threat intelligence. Échelle : 0 à 100&nbsp;%.</p>
</div>
</div>
<div class="banner" style="margin-top:12px; font-size:24px"><code style="background:#26446f;color:#fff">rule_level</code> passe de <b>39,74&nbsp;% (V1) à 26,85&nbsp;% (V2)</b> : le comportement et la réputation d'IP pèsent désormais <b>environ 35&nbsp;%</b> dans la décision.</div>

<!--
[15:00 – 16:00] Le modèle V2 atteint 100 % sur 789 alertes de test. Je reviens sur ce chiffre dans les limites. Ce qui est intéressant, c'est l'importance des features : rule_level descend de près de 40 % à 26,85 %, et les features comportementales plus la réputation d'IP pèsent ensemble environ 35 % de la décision.
-->

---
class: dense
---

<div class="kicker">04 · Résultat clé</div>

# Escalade comportementale : la preuve

<p style="margin-bottom:10px; font-size:23px">Même alerte, <code>rule.level = 5</code>, répétée 9 fois depuis la même source. Les 9 colonnes sont les 9 alertes successives.</p>

<div class="esc">
<div class="rl"></div>
<div class="cell hd">1</div><div class="cell hd">2</div><div class="cell hd">3</div><div class="cell hd">4</div><div class="cell hd">5</div><div class="cell hd">6</div><div class="cell hd">7</div><div class="cell hd">8</div><div class="cell hd">9</div>
</div>
<div class="esc">
<div class="rl">Répétitions sur 10 min<br><span style="font-weight:400;color:var(--muted)">repeat_rule_10min</span></div>
<div class="cell k">0</div><div class="cell k">1</div><div class="cell k">2</div><div class="cell k">3</div><div class="cell k">4</div><div class="cell k">5</div><div class="cell k">6</div><div class="cell k">7</div><div class="cell k" style="color:var(--red);font-weight:800">8</div>
</div>
<div class="esc">
<div class="rl">Seuil Shuffle<br><span style="font-weight:400;color:var(--muted)">rule.level ≥ 7</span></div>
<div class="cell n">MEDIUM</div><div class="cell n">MEDIUM</div><div class="cell n">MEDIUM</div><div class="cell n">MEDIUM</div><div class="cell n">MEDIUM</div><div class="cell n">MEDIUM</div><div class="cell n">MEDIUM</div><div class="cell n">MEDIUM</div><div class="cell n">MEDIUM</div>
</div>
<div class="esc">
<div class="rl">Notre Random Forest</div>
<div class="cell m">MEDIUM</div><div class="cell m">MEDIUM</div><div class="cell m">MEDIUM</div><div class="cell m">MEDIUM</div><div class="cell m">MEDIUM</div><div class="cell m">MEDIUM</div><div class="cell m">MEDIUM</div><div class="cell m">MEDIUM</div><div class="cell h">HIGH</div>
</div>

<div class="row" style="gap:20px; margin-top:20px">
<div class="col card accent"><p>À la 9<sup>e</sup> alerte, <code>repeat_rule_10min</code> atteint 8 : la classe bascule en <b>HIGH (58&nbsp;%)</b>. Les alertes 1 à 8 sont MEDIUM, entre 49 et 53&nbsp;%. Un seuil sur <code>rule.level</code> ne peut pas faire cela.</p></div>
<div class="col card warn"><p><b>Deuxième preuve :</b> une IP publique avec un score AbuseIPDB de 100 est classée HIGH, même avec un niveau Wazuh faible.</p></div>
</div>

<!--
[16:00 – 17:30] C'est la démonstration centrale. Une même alerte de niveau 5, répétée neuf fois. Un seuil Shuffle sur le niveau la classerait MEDIUM à chaque fois. Mon modèle, lui, la garde en MEDIUM pendant huit répétitions, puis la bascule en HIGH à la neuvième, quand le compteur de répétitions atteint huit. Même chose pour une IP publique malveillante : score AbuseIPDB de 100, classée HIGH malgré un niveau faible.
-->

---
class: dense
---

<div class="kicker">04 · Validation</div>

# Tests du pipeline de bout en bout

<div class="cards c3" style="margin-top:4px">
<div class="card" style="border-top:8px solid var(--green)"><span class="chip g">LOW</span><div class="big" style="margin-top:12px; font-size:48px; color:var(--navy)">98&nbsp;%</div><p class="cap">Règle 5715, authentification SSH réussie</p><p style="margin-top:8px; font-size:23px">Journalisation dans <code>incidents.json</code></p></div>
<div class="card" style="border-top:8px solid var(--orange)"><span class="chip o">MEDIUM</span><div class="big" style="margin-top:12px; font-size:48px; color:var(--navy)">63&nbsp;%</div><p class="cap">Règle 31103, attaque XSS (niveau 6)</p><p style="margin-top:8px; font-size:23px">Telegram compact et e-mail analyste</p></div>
<div class="card" style="border-top:8px solid var(--red)"><span class="chip r">HIGH</span><div class="big" style="margin-top:12px; font-size:48px; color:var(--navy)">94&nbsp;%</div><p class="cap">Règle 5712, brute force SSH (niveau 10)</p><p style="margin-top:8px; font-size:23px">Blocage IP, Telegram enrichi, e-mail</p></div>
</div>
<p class="small" style="margin-top:8px">Trois alertes successives traitées en temps réel, sans configuration entre chaque. Score = confiance du modèle.</p>

<div class="row" style="gap:20px; margin-top:14px">
<div class="col card dark"><h3>Réponse HIGH vérifiée</h3><p style="font-size:24px">IP <code style="background:#26446f;color:#fff">185.220.101.1</code> (AbuseIPDB 100). L'API renvoie <code style="background:#26446f;color:#fff">blocked: true</code>, <code style="background:#26446f;color:#fff">telegram_sent: true</code>, <code style="background:#26446f;color:#fff">email_sent: true</code>, exécutés en parallèle.</p></div>
<div class="col card dark" style="flex:.7"><div class="big" style="font-size:53px">1,231&nbsp;s</div><div class="cap">temps de réponse mesuré (objectif BNF1 : &lt; 2&nbsp;s)</div></div>
</div>

<!--
[17:30 – 19:00] Trois scénarios testés de bout en bout. LOW : une authentification réussie, simplement journalisée. MEDIUM : une attaque XSS, notification à l'analyste. HIGH : un brute force SSH, avec blocage de l'IP, Telegram et e-mail, exécutés en parallèle. Et le temps de réponse mesuré est de 1,231 seconde, sous les deux secondes demandées.
-->

---

<div class="kicker">04 · Bilan personnel</div>

# Mes contributions

<div class="cards c3" style="margin-top:2px">
<div class="card accent"><h3>Problème et idée</h3><p>Constat que le SOAR sans triage sature comme le SIEM. Proposition de la couche ML, validée par M. Erraji.</p></div>
<div class="card accent"><h3>Diagnostic CICIDS</h3><p>Analyse des features dominantes, puis changement d'approche vers un dataset natif.</p></div>
<div class="card accent"><h3>Feature engineering</h3><p>Features temporelles et threat intelligence, historique en mémoire thread-safe, intégration AbuseIPDB avec cache.</p></div>
<div class="card accent"><h3>Labellisation dynamique</h3><p>Schéma <code>make_label</code> avec fréquence, répétition et score de réputation.</p></div>
<div class="card accent"><h3>API Flask V2</h3><p>6 endpoints, appel automatique de <code>/respond/*</code>, blocage via l'API JWT de Wazuh.</p></div>
<div class="card accent"><h3>Infrastructure et tests</h3><p>Docker, LVM, Orborus, ossec.conf. Trois scénarios complets et la démonstration d'escalade.</p></div>
</div>

<!--
[19:00 – 19:45] Mes contributions : j'ai identifié le problème et proposé la solution, diagnostiqué l'échec de CICIDS, conçu les features et la labellisation, développé l'API, et résolu les difficultés d'infrastructure.
-->

---

<div class="kicker">04 · Difficultés</div>

# Difficultés rencontrées et solutions

<table><tbody>
<tr><th style="width:40%">Problème</th><th style="width:60%">Solution adoptée</th></tr>
<tr><td>Modèle CICIDS prédit toujours BENIGN</td><td>Dataset natif Wazuh et features sémantiques</td></tr>
<tr><td>XGBoost <code>cuda</code> non portable entre GPU et CPU</td><td>Random Forest entraîné sur la VM, en CPU</td></tr>
<tr><td>Orborus : timeout des workers Shuffle</td><td><code>SWARM=off</code> et <code>BASE_URL=192.168.56.100</code></td></tr>
<tr><td><code>ossec.conf</code> écrasé à chaque redémarrage</td><td>Modifier <code>wazuh_manager.conf</code> (bind mount)</td></tr>
<tr><td><code>/home</code> plein à 100&nbsp;% (deux fois)</td><td>Extension du volume LVM via VBoxManage</td></tr>
<tr><td>Docker daemon : « too many open files »</td><td>Réglage <code>sysctl</code> inotify et redémarrage de containerd</td></tr>
</tbody></table>

<!--
[19:45 – 20:30] Six difficultés, dont la plus importante sur le plan méthodologique est l'échec de CICIDS. Les autres sont des problèmes d'infrastructure réels : Orborus, Wazuh qui écrase sa configuration, le disque. Ce sont des défis typiques d'un déploiement SOC.
-->

---

<div class="kicker">04 · Discussion critique</div>

# Que valent vraiment les 100&nbsp;% ?

<div class="row" style="gap:26px">
<div class="col" style="flex:1.1">
<div class="card warn" style="margin-bottom:14px"><h3>Cohérence interne, pas généralisation</h3><p>Les labels sont construits à partir de critères corrélés aux features : <code>rule_level</code> sert dans <code>make_label</code>, et <code>rule_id_enc</code> l'encode indirectement. Le modèle atteint 100&nbsp;% même sans <code>rule_level</code>.</p></div>
<div class="card accent"><h3>Ce qui le distingue d'un seuil</h3><p>Il décide dans un espace à <b>11 dimensions</b> : un score de confiance gradué (49&nbsp;% à 88&nbsp;%) et une escalade comportementale, impossibles avec <code>rule.level ≥ 7</code>.</p></div>
</div>
<div class="col" style="flex:1">
<div style="font-size:19px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); margin-bottom:8px">Limites assumées</div>
<ul>
<li>Dataset de laboratoire : 3 945 alertes, IP simulées</li>
<li><code>ip_abuse_score</code> vaut 0 sur les IP privées</li>
<li><code>is_business_hours</code> (1,78&nbsp;%) : timestamps peu variés</li>
<li>Pas d'étude d'ablation formelle</li>
<li>Blocage validé côté API ; un agent Wazuh est requis sur la cible</li>
<li>API en mode développement (Gunicorn en production)</li>
</ul>
</div>
</div>

<!--
[20:30 – 22:00] Soyons honnêtes sur les 100 %. Ils reflètent la cohérence entre les labels et les features, pas une capacité de généralisation. Pour généraliser, il faudrait des données de plusieurs infrastructures et des labels d'experts. Ce que le modèle apporte malgré tout, c'est la décision dans un espace à onze dimensions, avec une escalade que ni Wazuh ni Shuffle ne peuvent faire seuls.
-->

---

<div class="kicker">04 · Suite du projet</div>

# Perspectives

<div class="cards c2" style="margin-top:4px">
<div class="card blue"><span class="chip b">1</span><b>Dataset de production</b><p style="margin-top:6px; font-size:23px">Collecter des alertes OCP réelles pour gagner en diversité.</p></div>
<div class="card blue"><span class="chip b">2</span><b>Agents Wazuh sur les serveurs</b><p style="margin-top:6px; font-size:23px">Activer le blocage IP effectif sur l'infrastructure OCP.</p></div>
<div class="card blue"><span class="chip b">3</span><b>Conteneuriser l'API</b><p style="margin-top:6px; font-size:23px">Docker et Gunicorn dans le docker-compose global.</p></div>
<div class="card blue"><span class="chip b">4</span><b>Détection multi-étapes</b><p style="margin-top:6px; font-size:23px">LSTM sur des séquences d'alertes pour des attaques complexes.</p></div>
<div class="card blue" style="grid-column: span 2"><span class="chip b">5</span><b>Mesures de latence robustes</b><p style="margin-top:6px; font-size:23px">Plus de 50 mesures pour une moyenne et un écart-type.</p></div>
</div>

<!--
[22:00 – 22:45] Cinq perspectives : des données de production, des agents Wazuh pour un blocage réel, la conteneurisation de l'API, une détection de séquences d'attaques, et des mesures de latence plus robustes.
-->

---
class: mid
---

<div class="kicker">Conclusion</div>

# Ce qu'il faut retenir

<div class="cards c3" style="margin-top:4px">
<div class="card" style="border-top:8px solid var(--red)"><h3>Le problème</h3><p>Un SOAR sans triage reproduit la saturation du SIEM : 100 alertes par seconde à l'OCP.</p></div>
<div class="card" style="border-top:8px solid var(--blue)"><h3>La solution</h3><p>Un Random Forest entre Wazuh et Shuffle, entraîné sur des alertes natives, avec 11 features comportementales et de réputation d'IP.</p></div>
<div class="card" style="border-top:8px solid var(--green)"><h3>Le résultat</h3><p>Pipeline complet en 1,231&nbsp;s : blocage IP, Telegram, e-mail pour HIGH ; notification pour MEDIUM ; journal pour LOW.</p></div>
</div>
<div class="banner green" style="margin-top:22px; font-size:29px"><b>Apport central :</b> deux alertes de même niveau Wazuh obtiennent des criticités différentes selon leur comportement. Une alerte de niveau 5 devient HIGH après 8 répétitions.</div>
<p class="small" style="margin-top:14px">Une base technique pour intégrer l'IA au futur déploiement SOAR de l'OCP, avec des limites connues et des pistes claires pour les lever.</p>

<!--
[22:45 – 24:00] En conclusion : le problème, la solution, le résultat. L'apport central est la démonstration que deux alertes de même niveau peuvent avoir des criticités différentes selon leur comportement. Le système est opérationnel de bout en bout, avec des limites assumées et des perspectives claires. Merci.
-->

---
layout: end
---

# Merci de votre attention

<p>Place à vos questions</p>

<!--
Questions. Les annexes suivantes sont prêtes : environnement technique, chiffres du dashboard Wazuh, code de make_label.
-->

---

<div class="kicker">Annexe A</div>

# Environnement technique

<table style="max-width:900px"><tbody>
<tr><th style="width:240px">Composant</th><th>Spécification</th></tr>
<tr><td>Hyperviseur</td><td>Oracle VirtualBox</td></tr>
<tr><td>Système</td><td>Ubuntu Server 24.04 LTS</td></tr>
<tr><td>Ressources</td><td>10&nbsp;Go de RAM, 4 vCPU, disque de 100&nbsp;Go (LVM)</td></tr>
<tr><td>Réseau</td><td>Host-Only 192.168.56.100/24 et NAT</td></tr>
<tr><td>Accès aux interfaces</td><td>Tunnel SSH <code>-L 3001:localhost:3001</code></td></tr>
<tr><td>Python</td><td>3.12.3 (venv), scikit-learn 1.4.2, Flask</td></tr>
<tr><td>Conteneurs</td><td>7 : Wazuh (Manager, Indexer, Dashboard) et Shuffle (Frontend, Backend, OpenSearch, Orborus)</td></tr>
</tbody></table>

---

<div class="kicker">Annexe B</div>

# Chiffres du dashboard Wazuh

<div class="cards c4" style="margin-top:6px">
<div class="card"><div class="big">5 342</div><div class="cap">alertes sur la période de test</div></div>
<div class="card"><div class="big">839</div><div class="cap">échecs d'authentification</div></div>
<div class="card"><div class="big">287</div><div class="cap">authentifications réussies</div></div>
<div class="card"><div class="big">11</div><div class="cap">alertes de niveau 12 ou plus</div></div>
</div>
<p style="margin-top:22px">Trois agents actifs : <b>Sejjil-1</b>, <b>wazuh.manager</b> et <b>windows-agent</b>. Les techniques MITRE ATT&amp;CK dominantes sont <i>Password Guessing</i> (T1110) et <i>SSH</i> (T1021.004), cohérentes avec les scénarios de brute force simulés.</p>
<p class="small">Le dataset d'entraînement (3 945 alertes) exclut les 1 397 alertes système (démarrages, SCA, rootcheck, netstat).</p>

---

<div class="kicker">Annexe C</div>

# Code de la labellisation : <code>make_label</code>

<div class="code-box" style="white-space:normal"><span class="k">def</span> make_label(row):<br>&nbsp;&nbsp;&nbsp;&nbsp;level, freq = row['rule_level'], row['alert_frequency_5min']<br>&nbsp;&nbsp;&nbsp;&nbsp;repeat, abuse = row['repeat_rule_10min'], row['ip_abuse_score']<br>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">if</span> level >= 7:<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">return</span> <span class="s">'HIGH'</span><br>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">if</span> level >= 5:<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">if</span> freq >= 10 <span class="k">or</span> repeat >= 8 <span class="k">or</span> abuse >= 80:<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">return</span> <span class="s">'HIGH'</span>      <span class="c"># escalade comportementale</span><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">return</span> <span class="s">'MEDIUM'</span><br>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">if</span> level >= 3:<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">if</span> freq >= 15 <span class="k">or</span> repeat >= 10 <span class="k">or</span> abuse >= 80:<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">return</span> <span class="s">'MEDIUM'</span>    <span class="c"># escalade comportementale</span><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">return</span> <span class="s">'LOW'</span><br>&nbsp;&nbsp;&nbsp;&nbsp;<span class="k">return</span> <span class="s">'LOW'</span></div>
