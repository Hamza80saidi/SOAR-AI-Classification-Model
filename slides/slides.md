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

<div class="kicker">Contexte et problème</div>

# Un SOAR sans triage sature comme le SIEM

<p class="small" style="margin:-8px 0 18px 0"><span class="chip g">OCP</span>Benguerir, laverie de Gantour &nbsp;·&nbsp; stage de 4 mois, mars à juillet 2026</p>

<div style="display:grid; grid-template-columns: 300px 1fr; gap:28px; margin-top:6px; align-items:center">
<div class="card dark" style="text-align:center; padding:26px 18px"><div class="big" style="font-size:72px">≈100</div><div class="cap" style="font-size:24px">alertes par seconde</div></div>
<div>
<div style="font-size:18px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--red); margin-bottom:8px">Sans triage</div>
<div style="display:flex; align-items:center; gap:12px; margin-bottom:26px; font-size:22px; line-height:1.3">
<div class="card blue" style="padding:12px 20px"><b>SIEM</b></div>
<div class="small" style="min-width:110px; text-align:center"><b style="color:var(--red)">100/s</b></div>
<div class="card violet" style="padding:12px 20px"><b>SOAR</b></div>
<div class="card warn" style="padding:12px 20px"><b>Analystes saturés</b></div>
</div>
<div style="font-size:18px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--green); margin-bottom:8px">Avec notre couche de triage</div>
<div style="display:flex; align-items:center; gap:12px; font-size:22px; line-height:1.3">
<div class="card blue" style="padding:12px 20px"><b>SIEM</b></div>
<div class="card accent" style="padding:12px 20px; background:var(--green-soft)"><b>Classification ML</b></div>
<div class="card violet" style="padding:12px 20px"><b>SOAR</b></div>
<div class="card accent" style="padding:12px 20px"><b>Seul l'utile arrive</b></div>
</div>
</div>
</div>

<div class="banner" style="margin-top:40px; text-align:center">Idée proposée par l'auteur, <b>validée par l'encadrant OCP</b></div>

<!--
[0:20 – 1:00] Contexte : stage de quatre mois à la laverie de Gantour, à Benguerir. Le SIEM de l'OCP génère environ 100 alertes par seconde. Brancher un SOAR dessus sans tri préalable, c'est lui envoyer le même flux brut : les analystes restent noyés, simplement dans un autre outil. J'ai donc proposé d'insérer un classifieur entre les deux, idée validée par M. Erraji.
-->

---
class: sparse
---

<div class="kicker">Contexte et problème</div>

# Objectifs et exigences

<div class="row" style="gap:30px">
<div class="col" style="flex:1.2">
<div style="font-size:18px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); margin-bottom:10px">Le système doit</div>
<div style="font-size:24px; line-height:1.4">
<p><span class="chip">BF1</span>Surveiller les logs</p>
<p><span class="chip">BF2</span>Envoyer chaque alerte au SOAR</p>
<p><span class="chip g">BF3</span>Classer LOW, MEDIUM, HIGH + score</p>
<p><span class="chip g">BF4</span>Escalader selon le comportement</p>
<p><span class="chip r">BF5</span>Bloquer l'IP des alertes HIGH</p>
<p><span class="chip b">BF6</span>Notifier : Telegram et e-mail</p>
</div>
</div>
<div class="col" style="flex:1">
<div style="font-size:18px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); margin-bottom:10px">Contraintes</div>
<div class="cards c2">
<div class="card"><div class="big" style="font-size:44px">&lt; 2&nbsp;s</div><div class="cap">temps de réponse</div></div>
<div class="card"><div class="big" style="font-size:44px">10&nbsp;Go</div><div class="cap">RAM, 4 vCPU</div></div>
<div class="card"><div class="big" style="font-size:44px">Docker</div><div class="cap">tous les composants</div></div>
<div class="card"><div class="big" style="font-size:44px">Natif</div><div class="cap">dataset depuis Wazuh</div></div>
</div>
</div>
</div>

<!--
[1:00 – 1:30] Six besoins fonctionnels, dont les deux au cœur du projet : BF3, classer avec un score, et BF4, escalader selon le comportement. Contraintes : réponse sous deux secondes, 10 Go de RAM, tout en Docker, et un dataset reproductible depuis Wazuh. (Un septième besoin, les endpoints de monitoring, est dans le rapport.)
-->

---
class: sparse2
---

<div class="kicker">État de l'art</div>

# Wazuh et Shuffle : les choix

<div class="row" style="gap:26px">
<div class="col card blue" style="padding:24px 28px">
<div style="display:flex; justify-content:space-between; align-items:baseline"><h3 style="font-size:34px">Wazuh 4.9.2</h3><span class="small">SIEM</span></div>
<ul style="margin-top:14px">
<li>Open source</li>
<li>Règles MITRE ATT&amp;CK</li>
<li>Webhook natif</li>
</ul>
<p class="small" style="margin-top:18px">Écartés : Splunk, QRadar, Elastic</p>
</div>
<div class="col card violet" style="padding:24px 28px">
<div style="display:flex; justify-content:space-between; align-items:baseline"><h3 style="font-size:34px">Shuffle 2.2.0</h3><span class="small">SOAR</span></div>
<ul style="margin-top:14px">
<li>Open source et léger</li>
<li>Blocs HTTP natifs</li>
<li>Conditions sur les flèches</li>
</ul>
<p class="small" style="margin-top:18px">Écartés : TheHive, Cortex XSOAR, Swimlane</p>
</div>
</div>

<!--
[1:30 – 2:00] Wazuh : open source, riche en règles MITRE, webhook natif, image Docker officielle. Shuffle : léger, blocs HTTP natifs ; son seul défaut, pas de conditionnel natif, est contourné avec des conditions sur les flèches. Les solutions commerciales sont écartées pour leur coût.
-->

---
class: sparse
---

<div class="kicker">État de l'art</div>

# Le ML pour la détection d'intrusions

<div class="cards c2" style="margin-top:4px">
<div class="card"><h3>Gu et al. (2019)</h3><p>RF bat SVM et Naive Bayes<br><b>F1 98,7&nbsp;%</b> sur DoS</p></div>
<div class="card"><h3>Sharafaldin et al. (2018)</h3><p>Features réseau : <b>faible généralisation</b></p></div>
<div class="card"><h3>Catillo et al. (2022)</h3><p><b>Domain shift</b> sur les logs système</p></div>
<div class="card"><h3>Hindy et al. (2020)</h3><p>Features sémantiques <b>plus stables</b></p></div>
</div>
<div class="banner green" style="margin-top:26px; font-size:26px"><b>Notre approche :</b> domain-native + comportement (fréquence, réputation d'IP)</div>

<!--
[2:00 – 2:30] La littérature montre que Random Forest est performant sur les datasets publics, mais que ces modèles se généralisent mal d'un domaine à l'autre. Je pars donc des alertes du SIEM cible, et j'ajoute deux dimensions absentes de la littérature : le comportement dans le temps et la réputation de l'IP.
-->

---

<div class="kicker">État de l'art</div>

# Pourquoi CICIDS2017 a échoué

<div class="row" style="gap:30px; align-items:center">
<div class="col" style="flex:1.05; text-align:center">
<img src="/images/confusion_matrix_random_forest.png" style="width:100%; border:1px solid var(--line); border-radius:8px; background:#fff" />
<div class="small" style="margin-top:6px">Random Forest sur CICIDS2017</div>
</div>
<div class="col" style="flex:1">
<div class="card warn" style="margin-bottom:16px"><div class="big" style="color:var(--red)">60,9&nbsp;%</div><div class="cap">du pouvoir discriminant : features réseau <b>absentes des alertes Wazuh</b></div></div>
<div class="card warn" style="margin-bottom:16px"><div class="big" style="color:var(--red)">2&nbsp;436</div><div class="cap">LOW prédits BENIGN</div></div>
<div class="banner" style="font-size:24px">D'où un <b>dataset natif Wazuh</b></div>
</div>
</div>

<!--
[2:30 – 3:15] Ma première approche utilisait CICIDS2017. Elle a échoué par incompatibilité structurelle : les cinq features les plus importantes, 60,9 % du pouvoir de décision, sont des mesures de trafic réseau qui n'existent pas dans une alerte Wazuh. Le modèle prend donc tout pour du trafic bénin : 2 436 exemples LOW classés BENIGN. J'ai changé d'approche.
-->

---

<div class="kicker">Conception</div>

# Architecture en cinq couches

<div class="arch" style="margin-top:6px">
<div class="layer sim"><div class="n">Couche 1</div><div class="t">Simulation</div><div class="tech">simulate_attacks.py</div><div class="d">4 types d'attaques</div></div>
<div class="link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 6l6 6-6 6"/></svg></div>
<div class="layer siem"><div class="n">Couche 2</div><div class="t">SIEM</div><div class="tech">Wazuh 4.9.2</div><div class="d">Détecte et envoie en webhook</div></div>
<div class="link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 6l6 6-6 6"/></svg></div>
<div class="layer soar"><div class="n">Couche 3</div><div class="t">SOAR</div><div class="tech">Shuffle 2.2.0</div><div class="d">Orchestre le flux</div></div>
<div class="link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 6l6 6-6 6"/></svg></div>
<div class="layer ia"><div class="n">Couche 4</div><div class="t">IA</div><div class="tech">Flask + Random Forest</div><div class="d">Label et score</div></div>
<div class="link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 6l6 6-6 6"/></svg></div>
<div class="layer rep"><div class="n">Couche 5</div><div class="t">Réponse</div><div class="tech">Actions auto</div><div class="d">Blocage, Telegram, e-mail, journal</div></div>
</div>

<div class="row" style="gap:20px; margin-top:26px; align-items:stretch">
<div class="col" style="flex:1.25"><div class="code-box" style="font-size:22px; padding:18px 22px; height:100%; box-sizing:border-box; white-space:normal"><span class="c">// réponse de POST /predict</span><br>{ <span class="s">"label"</span>: <span class="s">"HIGH"</span>,<br>&nbsp;&nbsp;<span class="s">"confidence"</span>: 0.88,<br>&nbsp;&nbsp;<span class="s">"action"</span>: <span class="s">"BLOCK_AND_ALERT"</span> }</div></div>
<div class="col" style="flex:1"><div class="banner" style="font-size:26px; height:100%; box-sizing:border-box; display:flex; align-items:center"><span>Couches reliées en <b>JSON</b> : chacune est remplaçable</span></div></div>
</div>

<!--
[3:15 – 4:00] Cinq couches. On simule des attaques, Wazuh les détecte, Shuffle orchestre, mon API classe l'alerte avec un Random Forest, puis la couche réponse agit. Les couches échangent uniquement du JSON, comme cette réponse de l'API : on peut remplacer le modèle ou la plateforme SOAR sans toucher au reste.
-->

---
class: dense
---

<div class="kicker">Conception</div>

# Le parcours d'une alerte HIGH

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

<div class="banner green" style="margin-top:6px; display:flex; justify-content:space-between; align-items:center; font-size:25px"><span>Brute force SSH, règle Wazuh 5712</span><span style="font-size:34px; font-weight:800">1,231&nbsp;s &nbsp;<span style="font-size:22px; font-weight:500">mesuré, objectif &lt; 2&nbsp;s</span></span></div>

<!--
[4:00 – 4:50] Prenons une attaque par force brute SSH. Un : Wazuh détecte la règle 5712 et envoie l'alerte à Shuffle. Deux : Shuffle appelle l'API. Trois et quatre : l'API interroge AbuseIPDB et calcule les 11 features. Cinq et six : le Random Forest renvoie le label avec un score, ici HIGH à 88 %. Sept : blocage de l'IP, Telegram et e-mail. Le tout en 1,231 seconde, sous la limite de deux secondes.
-->

---
class: sparse2
---

<div class="kicker">Réalisation</div>

# Le dataset : 3&nbsp;945 alertes natives

<div class="row" style="gap:34px">
<div class="col" style="flex:1">
<div class="card accent" style="margin-bottom:14px"><h3>1. Organiques</h3><p class="small">simulate_attacks.py</p></div>
<div class="card blue" style="margin-bottom:14px"><h3>2. Injectées</h3><p class="small">niveaux 10 et 12</p></div>
<div class="card orange"><h3>3. IP malveillantes</h3><p class="small">score AbuseIPDB</p></div>
</div>
<div class="col" style="flex:1.15; padding-top:6px">
<div class="bar-row"><div class="lab" style="width:120px">HIGH</div><div class="track"><div class="fill" style="width:44.5%; background:var(--red)"></div></div><div class="val" style="width:210px; white-space:nowrap">1&nbsp;756 · 44,5&nbsp;%</div></div>
<div class="bar-row"><div class="lab" style="width:120px">LOW</div><div class="track"><div class="fill" style="width:31.9%; background:var(--green)"></div></div><div class="val" style="width:210px; white-space:nowrap">1&nbsp;258 · 31,9&nbsp;%</div></div>
<div class="bar-row"><div class="lab" style="width:120px">MEDIUM</div><div class="track"><div class="fill" style="width:23.6%; background:var(--orange)"></div></div><div class="val" style="width:210px; white-space:nowrap">931 · 23,6&nbsp;%</div></div>
<p class="small" style="margin-top:20px">Découpage 80 / 20 stratifié : 789 alertes de test</p>
</div>
</div>

<!--
[4:50 – 5:20] Le dataset compte 3 945 alertes, construit en trois couches : des alertes organiques générées par le simulateur, des alertes injectées pour les niveaux 10 et 12 difficiles à déclencher naturellement, et des alertes avec des IP publiques malveillantes pour entraîner la feature de réputation. Sans injection, HIGH ne représenterait que 5 %. Les 5 342 alertes du dashboard incluent les événements système, exclus du dataset.
-->

---

<div class="kicker">Réalisation</div>

# Les 11 features

<div class="row" style="gap:20px; align-items:stretch">
<div class="col card" style="border-top:7px solid var(--blue)">
<h3>Natives Wazuh <span class="small">(6)</span></h3>
<div class="frow" style="margin-top:8px"><code>rule_id_enc</code></div><div class="frow"><code>rule_level</code><b>26,85&nbsp;%</b></div><div class="frow"><code>groups_count</code></div><div class="frow"><code>has_mitre</code></div><div class="frow"><code>src_ip_private</code><span>1,13&nbsp;%</span></div><div class="frow"><code>fired_times</code><span>5,17&nbsp;%</span></div>
</div>
<div class="col card" style="border-top:7px solid var(--orange); background:#fffaf2">
<h3>Comportementales <span class="small">(4)</span></h3>
<div class="frow" style="margin-top:8px"><code>alert_frequency_5min</code><b>13,10&nbsp;%</b></div><div class="frow"><code>repeat_rule_10min</code><b>13,84&nbsp;%</b></div><div class="frow"><code>hour_of_day</code></div><div class="frow"><code>is_business_hours</code><span>1,78&nbsp;%</span></div>
</div>
<div class="col card" style="border-top:7px solid var(--red)">
<h3>Threat intel <span class="small">(1)</span></h3>
<div class="frow" style="margin-top:8px"><code>ip_abuse_score</code><b>8,32&nbsp;%</b></div>
<p class="small" style="margin-top:14px">AbuseIPDB, 0 si IP privée</p>
</div>
</div>

<!--
[5:20 – 6:00] Onze features en trois familles. Six sont natives, lues dans l'alerte. Quatre sont calculées en temps réel à partir d'un historique en mémoire thread-safe : la fréquence sur cinq minutes, les répétitions de la même règle sur dix minutes, l'heure et les heures ouvrées. Une est de la threat intelligence : le score AbuseIPDB. On calcule avant de mettre à jour l'historique, pour ne pas compter l'alerte dans sa propre fréquence.
-->

---
class: sparse
---

<div class="kicker">Réalisation</div>

# Labellisation comportementale

<div class="row" style="gap:28px">
<div class="col" style="flex:1.6">
<table><tbody>
<tr><th style="width:170px">Niveau Wazuh</th><th>Label</th><th>Escalade si…</th></tr>
<tr><td><b>7 et plus</b></td><td><span class="chip r">HIGH</span></td><td class="small" style="font-size:21px">toujours</td></tr>
<tr><td><b>5 – 6</b></td><td><span class="chip o">MEDIUM</span></td><td style="font-size:21px">fréq ≥ 10, rép ≥ 8 ou abuse ≥ 80 : <span class="chip r">HIGH</span></td></tr>
<tr><td><b>3 – 4</b></td><td><span class="chip g">LOW</span></td><td style="font-size:21px">fréq ≥ 15, rép ≥ 10 ou abuse ≥ 80 : <span class="chip o">MEDIUM</span></td></tr>
</tbody></table>
</div>
<div class="col" style="flex:1">
<div class="card accent" style="margin-bottom:14px"><h3>Même niveau, labels différents</h3></div>
<div class="card warn"><h3>Labels corrélés aux features</h3><p class="small">voir limites</p></div>
</div>
</div>

<!--
[6:00 – 6:30] Pour entraîner le modèle il faut des labels. Le niveau Wazuh donne le label de base, et la fréquence, la répétition ou la réputation de l'IP peuvent l'escalader. Résultat : deux alertes de même niveau reçoivent des labels différents. Je précise que ces critères sont corrélés aux features : j'y reviens dans les limites. Le code de make_label est dans le rapport, annexe A.
-->

---

<div class="kicker">Réalisation</div>

# Random Forest et API Flask

<div class="row" style="gap:28px">
<div class="col" style="flex:1">
<div class="card accent" style="margin-bottom:14px"><h3>Déséquilibre géré</h3><p class="small">class_weight balanced, 200 arbres</p></div>
<div class="card accent" style="margin-bottom:14px"><h3>Interprétable</h3><p class="small">feature_importances_</p></div>
<div class="card accent"><h3>Portable</h3><p class="small">CPU et GPU</p></div>
</div>
<div class="col" style="flex:1.25">
<table><tbody>
<tr><th style="width:90px">HTTP</th><th>Endpoint</th></tr>
<tr><td>POST</td><td><code>/predict</code></td></tr>
<tr><td>POST</td><td><code>/respond/high</code></td></tr>
<tr><td>POST</td><td><code>/respond/medium</code></td></tr>
<tr><td>POST</td><td><code>/respond/low</code></td></tr>
<tr><td>GET</td><td><code>/health</code> · <code>/stats</code></td></tr>
</tbody></table>
</div>
</div>
<div class="banner" style="margin-top:22px; font-size:25px"><b>Un seul appel</b> depuis Shuffle : <code style="background:#26446f;color:#fff">/predict</code> déclenche la bonne réponse</div>

<!--
[6:30 – 7:00] Random Forest pour trois raisons : il gère le déséquilibre des classes, il est interprétable, et il est portable entre CPU et GPU, contrairement à XGBoost avec device cuda. L'API Flask expose six endpoints. Le point clé : Shuffle fait un seul appel à /predict, et c'est l'API qui déclenche la bonne réponse.
-->

---
class: sparse
---

<div class="kicker">Réalisation</div>

# Workflow Shuffle et actions

<div style="display:flex; align-items:center; gap:10px; margin-bottom:24px">
<div class="card violet" style="padding:12px 18px; font-size:22px"><b>Webhook</b></div>
<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#10233f" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 6l6 6-6 6"/></svg>
<div class="card violet" style="padding:12px 18px; font-size:22px"><b>POST /predict</b></div>
<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#10233f" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 6l6 6-6 6"/></svg>
<div class="card violet" style="padding:12px 18px; font-size:22px"><b>Extraction du label</b></div>
<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#10233f" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 6l6 6-6 6"/></svg>
<div class="card" style="padding:12px 18px; font-size:22px"><b>3 branches</b></div>
</div>

<div class="cards c3">
<div class="card" style="border-top:8px solid var(--red)"><span class="chip r">HIGH</span><p style="margin-top:14px"><b>Blocage IP</b></p><p class="small" style="margin-top:6px">Telegram enrichi, e-mail</p></div>
<div class="card" style="border-top:8px solid var(--orange)"><span class="chip o">MEDIUM</span><p style="margin-top:14px"><b>Notification</b></p><p class="small" style="margin-top:6px">Telegram compact, e-mail</p></div>
<div class="card" style="border-top:8px solid var(--green)"><span class="chip g">LOW</span><p style="margin-top:14px"><b>Journal</b></p><p class="small" style="margin-top:6px">incidents.json</p></div>
</div>

<!--
[7:00 – 7:30] Côté Shuffle : un webhook, un bloc HTTP, une extraction du label, puis trois branches avec une condition sur chaque flèche. HIGH : blocage de l'IP par Wazuh Active Response, Telegram enrichi et e-mail avec le statut du blocage. MEDIUM : notification compacte à l'analyste. LOW : simple journal. L'analyste reçoit donc une alerte avec l'action déjà prise.
-->

---

<div class="kicker">Résultats</div>

# Résultats du modèle V2

<div class="row" style="gap:30px">
<div class="col" style="flex:.8">
<div class="card dark" style="margin-bottom:16px"><div class="big" style="font-size:64px">100&nbsp;%</div><div class="cap">accuracy, 789 alertes de test</div></div>
<table><tbody>
<tr><th>Classe</th><th>F1</th><th>Support</th></tr>
<tr><td>HIGH</td><td>1,00</td><td>352</td></tr>
<tr><td>LOW</td><td>1,00</td><td>302</td></tr>
<tr><td>MEDIUM</td><td>1,00</td><td>135</td></tr>
</tbody></table>
</div>
<div class="col" style="flex:1.2">
<div style="font-size:18px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); margin-bottom:10px">Importance des features</div>
<div class="bar-row"><div class="lab" style="width:230px">rule_level</div><div class="track"><div class="fill" style="width:26.85%"></div></div><div class="val">26,85&nbsp;%</div></div>
<div class="bar-row"><div class="lab" style="width:230px">repeat_rule_10min</div><div class="track"><div class="fill" style="width:13.84%; background:var(--orange)"></div></div><div class="val">13,84&nbsp;%</div></div>
<div class="bar-row"><div class="lab" style="width:230px">alert_frequency_5min</div><div class="track"><div class="fill" style="width:13.1%; background:var(--orange)"></div></div><div class="val">13,10&nbsp;%</div></div>
<div class="bar-row"><div class="lab" style="width:230px">ip_abuse_score</div><div class="track"><div class="fill" style="width:8.32%; background:var(--red)"></div></div><div class="val">8,32&nbsp;%</div></div>
<div class="bar-row"><div class="lab" style="width:230px">fired_times</div><div class="track"><div class="fill" style="width:5.17%"></div></div><div class="val">5,17&nbsp;%</div></div>
</div>
</div>
<div class="banner" style="margin-top:20px; font-size:25px"><code style="background:#26446f;color:#fff">rule_level</code> : <b>39,74&nbsp;% (V1) à 26,85&nbsp;% (V2)</b></div>

<!--
[7:30 – 8:15] Le modèle V2 atteint 100 % sur 789 alertes de test, avec un F1 de 1,00 sur les trois classes : j'y reviens dans les limites. Ce qui est intéressant, c'est l'importance des features : rule_level descend de 39,74 % à 26,85 %, et les features comportementales plus la réputation d'IP pèsent environ 35 % de la décision. Les features mineures, is_business_hours à 1,78 % et src_ip_private à 1,13 %, sont peu actives sur un dataset de laboratoire.
-->

---

<div class="kicker">Résultat clé</div>

# Escalade comportementale

<p style="margin-bottom:10px; font-size:23px; color:var(--muted)">Même alerte, <code>rule.level = 5</code>, répétée 9 fois depuis la même source</p>

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



<div class="row" style="gap:20px; margin-top:24px">
<div class="col card accent"><p>9<sup>e</sup> alerte : <b>HIGH (58&nbsp;%)</b>. Un seuil sur le niveau ne le peut pas.</p></div>
<div class="col card warn"><p>IP publique, AbuseIPDB 100 : <b>HIGH</b> malgré un niveau faible.</p></div>
</div>

<!--
[8:15 – 9:15] C'est la démonstration centrale. Une même alerte de niveau 5, répétée neuf fois. Un seuil Shuffle sur le niveau la classerait MEDIUM à chaque fois. Mon modèle la garde en MEDIUM, entre 49 et 53 % de confiance, pendant huit répétitions, puis la bascule en HIGH à la neuvième, à 58 %, quand le compteur atteint huit. Même chose pour une IP publique malveillante : score AbuseIPDB de 100, classée HIGH malgré un niveau faible.
-->

---
class: sparse
---

<div class="kicker">Validation</div>

# Tests de bout en bout

<div class="cards c3" style="margin-top:4px">
<div class="card" style="border-top:8px solid var(--green)"><span class="chip g">LOW</span><div class="big" style="margin-top:14px; font-size:48px; color:var(--navy)">98&nbsp;%</div><p class="cap">Règle 5715</p><p style="margin-top:6px">Journal</p></div>
<div class="card" style="border-top:8px solid var(--orange)"><span class="chip o">MEDIUM</span><div class="big" style="margin-top:14px; font-size:48px; color:var(--navy)">63&nbsp;%</div><p class="cap">Règle 31103 (XSS)</p><p style="margin-top:6px">Notification</p></div>
<div class="card" style="border-top:8px solid var(--red)"><span class="chip r">HIGH</span><div class="big" style="margin-top:14px; font-size:48px; color:var(--navy)">94&nbsp;%</div><p class="cap">Règle 5712 (SSH)</p><p style="margin-top:6px">Blocage + alertes</p></div>
</div>
<div class="row" style="gap:20px; margin-top:22px">
<div class="col card dark"><h3>Réponse HIGH</h3><p style="font-size:24px"><code style="background:#26446f;color:#fff">blocked</code> <code style="background:#26446f;color:#fff">telegram_sent</code> <code style="background:#26446f;color:#fff">email_sent</code> : <b>true</b></p></div>
<div class="col card dark" style="flex:.7"><div class="big" style="font-size:52px">1,231&nbsp;s</div><div class="cap">objectif &lt; 2&nbsp;s</div></div>
</div>

<!--
[9:15 – 10:00] Trois scénarios testés de bout en bout, avec les scores de confiance du modèle. LOW : une authentification SSH réussie, règle 5715, simplement journalisée. MEDIUM : une attaque XSS, règle 31103, notification à l'analyste. HIGH : un brute force SSH, règle 5712, avec blocage de l'IP, Telegram et e-mail exécutés en parallèle, vérifié avec l'IP 185.220.101.1 et un score AbuseIPDB de 100. Temps de réponse mesuré : 1,231 seconde.
-->

---
class: sparse2
---

<div class="kicker">Bilan</div>

# Mes contributions

<div class="cards c3" style="margin-top:2px">
<div class="card accent"><h3>Problème et idée</h3><p>Triage avant le SOAR</p></div>
<div class="card accent"><h3>Diagnostic CICIDS</h3><p>Changement d'approche</p></div>
<div class="card accent"><h3>Features</h3><p>Temporelles et AbuseIPDB</p></div>
<div class="card accent"><h3>Labellisation</h3><p>Escalade comportementale</p></div>
<div class="card accent"><h3>API Flask V2</h3><p>6 endpoints, Active Response</p></div>
<div class="card accent"><h3>Infrastructure</h3><p>Docker, LVM, Orborus</p></div>
</div>

<!--
[10:00 – 10:30] Mes contributions : identifier le problème et proposer la solution, diagnostiquer l'échec de CICIDS, concevoir les features et la labellisation, développer l'API avec le blocage par Active Response, et résoudre les difficultés d'infrastructure. Difficultés rencontrées, si le jury demande : XGBoost cuda non portable, timeouts Orborus (SWARM=off), ossec.conf écrasé à chaque redémarrage, /home plein deux fois (extension LVM), Docker « too many open files ».
-->

---
class: sparse
---

<div class="kicker">Discussion</div>

# Limites et perspectives

<div class="row" style="gap:26px">
<div class="col card warn" style="padding:22px 26px">
<h3 style="font-size:28px">Limites</h3>
<ul style="margin-top:12px">
<li>100&nbsp;% = cohérence interne</li>
<li>Dataset de laboratoire</li>
<li>IP simulées (score = 0)</li>
<li>Blocage : agent Wazuh requis</li>
<li>API en mode développement</li>
</ul>
</div>
<div class="col card accent" style="padding:22px 26px">
<h3 style="font-size:28px">Perspectives</h3>
<ul style="margin-top:12px">
<li>Données de production OCP</li>
<li>Agents Wazuh sur les serveurs</li>
<li>Docker + Gunicorn</li>
<li>LSTM sur séquences d'alertes</li>
<li>Mesures de latence (50+)</li>
</ul>
</div>
</div>

<!--
[10:30 – 11:15] Soyons honnêtes sur les 100 %. Ils reflètent la cohérence entre les labels et les features, pas une capacité de généralisation : rule_id_enc encode indirectement rule_level, et le modèle atteint 100 % même sans rule_level. Ce qui le distingue d'un seuil, c'est la décision dans un espace à 11 dimensions, avec un score gradué et une escalade comportementale. Autres limites : dataset de laboratoire, IP simulées donc ip_abuse_score à zéro, blocage réel conditionné à un agent Wazuh, API en mode développement. Perspectives : données de production OCP, agents Wazuh, conteneurisation avec Gunicorn, LSTM sur séquences d'alertes, mesures de latence robustes.
-->

---
class: sparse2
---

<div class="kicker">Conclusion</div>

# Ce qu'il faut retenir

<div class="cards c3" style="margin-top:4px">
<div class="card" style="border-top:8px solid var(--red)"><h3>Problème</h3><p>100 alertes/s, SOAR saturé</p></div>
<div class="card" style="border-top:8px solid var(--blue)"><h3>Solution</h3><p>Random Forest entre Wazuh et Shuffle</p></div>
<div class="card" style="border-top:8px solid var(--green)"><h3>Résultat</h3><p>Pipeline complet en 1,231&nbsp;s</p></div>
</div>
<div class="banner green" style="margin-top:26px; font-size:27px"><b>Apport central :</b> même niveau Wazuh, criticités différentes selon le comportement</div>

<!--
[11:15 – 12:00] En conclusion : le problème, la solution, le résultat. L'apport central est la démonstration que deux alertes de même niveau peuvent avoir des criticités différentes selon leur comportement : une alerte de niveau 5 devient HIGH après huit répétitions. Le système est opérationnel de bout en bout, avec des limites assumées et des perspectives claires. Merci.
-->

---
layout: end
---

# Merci de votre attention

<p>Place à vos questions</p>
