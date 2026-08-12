# 🗺️ DealScout — Guide Complet de Construction

> M&A Intelligence Platform : Sources (APIs/Scraping/News) → Kafka → Bronze → Silver (Spark) → Gold (dbt) → Scoring Engine → ML/SHAP → FastAPI → React Dashboard

---

## Philosophie de construction

Même logique que LedgerLake et CreditPulse : on construit **en paliers testables**, on ne branche pas 15 technologies en même temps.

```
Palier A — Sources + Ingestion Kafka + Bronze
   → Collecte de données réelles/simulées sur des entreprises, stockage brut

Palier B — Silver (Spark)
   → Nettoyage, standardisation, premières variables dérivées

Palier C — Gold (dbt)
   → company_360, investment_targets, market_analysis

Palier D — Scoring Engine v1 (règles métier)
   → Formule pondérée simple, sans ML — donne déjà des résultats démontrables

Palier E — Machine Learning (Palier avancé)
   → XGBoost prédictif + SHAP, remplace/complète les règles

Palier F — Backend FastAPI
   → Expose les scores et les données au frontend

Palier G — Frontend React
   → Dashboard, classement, fiche entreprise

Palier H — Orchestration, Data Quality, Gouvernance, Observabilité, Docker
   → Industrialisation complète (mêmes briques que LedgerLake/CreditPulse)
```

**Astuce clé pour ce projet** : commence le Scoring Engine avec des **règles métier simples** (Palier D) avant le Machine Learning (Palier E). Contrairement à CreditPulse où le ML est le cœur dès le départ, ici la formule pondérée donne déjà un produit démontrable, et le ML vient ensuite l'améliorer — c'est aussi une meilleure histoire à raconter en entretien ("j'ai d'abord validé la logique métier avec des règles, puis je l'ai remplacée par un modèle prédictif quand j'ai eu assez de données historiques").

---

## PALIER A — Sources, Ingestion Kafka, Bronze

### But
Collecter des données d'entreprises depuis plusieurs sources hétérogènes et les faire transiter par Kafka jusqu'au data lake brut.

### A.1 — Connecteurs de sources (`ingestion/connectors/`)
- `financial_api_connector.py` : appelle une API financière (Alpha Vantage, Financial Modeling Prep — versions gratuites suffisent pour un POC) pour récupérer revenue, market cap, croissance, marge
- `company_db_connector.py` : récupère des métadonnées d'entreprise (secteur, pays, effectifs, levées de fonds) — via une API comme OpenCorporates, ou **génère des données simulées réalistes** si tu veux éviter les limites de quota d'API gratuites pendant le développement
- `news_connector.py` : NewsAPI ou flux RSS, récupère les actualités mentionnant une entreprise
- `web_scraper.py` : BeautifulSoup/Playwright pour extraire des infos publiques du site d'une entreprise (produits, technologie) — **à faire en dernier**, c'est le plus fragile (structure des sites qui change)

**Conseil réaliste** : pour un projet portfolio, ne te bats pas contre des APIs payantes ou des quotas restrictifs. Génère un dataset simulé de 500-1000 entreprises réalistes (via `faker` + règles métier cohérentes) pour Palier A à D, et branche 1-2 vraies APIs gratuites en complément pour prouver que tu sais le faire.

### A.2 — Producers Kafka (`ingestion/producers/`)
- `companies_producer.py` → topic `companies-events`
- `financial_producer.py` → topic `financial-events`
- `news_producer.py` → topic `news-events`

### A.3 — Bronze Writer
- Même principe que LedgerLake : un consumer qui écrit brut, sans transformation, partitionné par date, dans MinIO (`bronze/companies/`, `bronze/financial/`, `bronze/news/`, `bronze/funding/`)

### ✅ Checkpoint Palier A
Tu as un flux de données (simulé ou réel) qui transite par Kafka et atterrit brut dans le data lake, correctement partitionné.

---

## PALIER B — Silver (Spark)

### But
Nettoyer et enrichir les données pour qu'elles soient exploitables.

### B.1 — Jobs Spark (`spark_jobs/`)
- `bronze_to_silver_companies.py` : dédoublonnage (une entreprise peut apparaître plusieurs fois sous des variantes de nom — "ABC", "ABC Inc", "ABC Inc."), standardisation des pays/secteurs
- `bronze_to_silver_financial.py` : typage des montants, gestion des devises, calcul de ratios (marge, croissance YoY)
- `bronze_to_silver_news.py` : agrégation des mentions par entreprise, calcul d'un score de sentiment simple (positif/négatif/neutre — tu peux utiliser une librairie légère comme `textblob` ou un modèle HuggingFace pré-entraîné)

### B.2 — Variables dérivées (feature engineering précoce)
- `growth_score`, `market_score`, `innovation_score`, `financial_health_score` — chacune calculée à partir de règles simples au début (ex: `financial_health_score` = fonction de la marge et de la dette)

### ✅ Checkpoint Palier B
Les fichiers Parquet de Silver contiennent des données dédupliquées, standardisées, avec les scores intermédiaires calculés.

---

## PALIER C — Gold (dbt)

### But
Construire les tables métier finales, celles que les analystes et le scoring engine vont utiliser.

### C.1 — Modèles dbt (`dbt_project/models/gold/`)
- **`company_360.sql`** : vue complète — `company_id`, `name`, `sector`, `country`, `revenue`, `growth`, `employees`, `funding`, `financial_health`, `news_sentiment`
- **`investment_targets.sql`** : la table principale — `company`, `m&a_score`, `ranking`, `recommendation`, `risk_level` (alimentée par le Scoring Engine du Palier D)
- **`market_analysis.sql`** : analyse sectorielle — `sector`, `number_of_companies`, `average_growth`, `investment_volume`

### ✅ Checkpoint Palier C
`dbt run` + `dbt test` passent, et `company_360` contient une vue cohérente et complète par entreprise.

---

## PALIER D — Scoring Engine v1 (règles métier)

### But
Calculer un score M&A entre 0 et 100, sans Machine Learning pour commencer — c'est déjà un produit démontrable.

### D.1 — Formule pondérée (`scoring_engine/rules_scoring.py`)
```
M&A Score = Growth × 30% + Revenue × 20% + Profitability × 20%
          + Market Opportunity × 15% + Innovation × 10%
          + International Presence × 5%
```
- Chaque composante est normalisée entre 0 et 100 avant pondération
- Le script lit `company_360` (Gold), calcule le score, écrit dans `investment_targets`

### D.2 — Classement
- Trie les entreprises par score décroissant, assigne un `ranking`
- Ajoute une `recommendation` textuelle simple selon des seuils (`score >= 85` → "Cible prioritaire", `score >= 60` → "À surveiller", sinon "Faible priorité")

### ✅ Checkpoint Palier D
Tu obtiens un classement Top 50 d'entreprises avec un score cohérent — **tu as déjà un produit démontrable de bout en bout à ce stade**, même sans ML ni frontend fini.

---

## PALIER E — Machine Learning (score prédictif + SHAP)

### But
Remplacer/enrichir les règles métier par un modèle qui apprend depuis des données historiques d'acquisitions réelles ou simulées.

### E.1 — Données d'entraînement (`ml/train.py`)
- Dataset avec une colonne cible `acquired` (0/1) — historique simulé de type "entreprise X a été acquise en (date)" avec ses caractéristiques au moment de l'acquisition
- Features : les mêmes que `company_360` (growth, revenue, profitability, market_score, innovation_score, international_presence)

### E.2 — Entraînement
- `XGBClassifier` (cohérent avec CreditPulse, tu réutilises la même expertise), évalué en AUC-ROC/précision/rappel
- Sortie : `acquisition_probability` (0-100%), à ne pas confondre avec le `m&a_score` de règles — tu peux garder les deux et les comparer dans le dashboard (bon argument de storytelling en entretien)

### E.3 — Explicabilité (`ml/explain.py`)
- SHAP, même logique que CreditPulse : pour chaque entreprise, identifie les facteurs qui poussent la probabilité d'acquisition vers le haut ou le bas (ex : "+ forte croissance", "+ financement récent", "- dette élevée")

### ✅ Checkpoint Palier E
Pour une entreprise donnée, tu obtiens une probabilité d'acquisition ET une explication SHAP lisible.

---

## PALIER F — Backend FastAPI

### But
Exposer les données et scores au frontend.

### F.1 — Endpoints (`backend/app/routers/`)
- `GET /companies` — liste paginée, filtrable
- `GET /companies/{id}/score` — score, ranking, explication SHAP
- `GET /companies/{id}` — fiche complète (company_360)
- `GET /search?sector=FinTech&min_growth=20` — recherche multi-critères (le cas d'usage du fonds d'investissement décrit dans la vision du projet)

### ✅ Checkpoint Palier F
Via Swagger UI (`/docs`), tu peux chercher "FinTech Maroc croissance > 20%" et récupérer une liste triée par score.

---

## PALIER G — Frontend React

### But
Dashboard décisionnel pour l'analyste M&A.

### G.1 — Pages (`frontend/src/pages/`)
- **Dashboard principal** : KPIs (entreprises analysées, cibles à fort potentiel, score moyen), Top Opportunities (classement)
- **CompanyProfile** : données financières, évolution de croissance, score, graphique SHAP
- **Search** : formulaire de recherche multi-critères connecté à `/search`

### ✅ Checkpoint Palier G
Un utilisateur peut chercher "FinTech, croissance > 20%, Maroc" et voir un classement visuel avec explication, 100% depuis l'interface.

---

## PALIER H — Industrialisation (Orchestration, Qualité, Gouvernance, Observabilité, Docker)

Mêmes briques que LedgerLake, appliquées à DealScout :

- **Airflow** (`orchestration/dags/dealscout_daily_pipeline.py`) : pipeline quotidien complet (extraction → Kafka → Spark → dbt → scoring → refresh dashboard), avec un planning explicite (ex: 02:00 extraction, 06:00 calcul des scores, 07:00 refresh dashboard)
- **Great Expectations** (`data_quality/`) : `revenue > 0`, `employees > 0`, `score entre 0 et 100`, `company name not null`
- **OpenMetadata** (`governance/`) : lignée complète Crunchbase/API → Kafka → Bronze → Spark → Silver → dbt → `investment_targets`
- **Prometheus/Grafana** (`observability/`) : Kafka lag, durée des jobs Spark, latence API, échecs de pipeline
- **Docker Compose** : tous les services orchestrés ensemble

### ✅ Checkpoint Palier H
`docker-compose up` lance toute la plateforme, le DAG Airflow tourne quotidiennement, les dashboards Grafana affichent l'état du pipeline en direct.

---

## 🏗️ Architecture proposée (vue d'ensemble)

```
                    DATA SOURCES
                         │
        ─────────────────────────────────────
        │              │                    │
     APIs          Scraping              Files
   (Financial,    (BeautifulSoup,      (CSV/exports
   Company DB,      Playwright)          historiques)
     News)             │                    │
        └──────────────┴────────────────────┘
                         │
                 Data Ingestion Layer
                         │
                    Apache Kafka
        (topics: companies / financial / news)
                         │
        ═══════════════════════════════════════
                     BRONZE LAYER
              Raw Data Lake — MinIO/S3
              JSON, partitionné year/month/day
        ═══════════════════════════════════════
                         │
                    Apache Spark
      (nettoyage, dédup, standardisation, enrichissement)
                         │
        ═══════════════════════════════════════
                     SILVER LAYER
              Clean & Enriched — Parquet
        ═══════════════════════════════════════
                         │
                       dbt
                         │
        ═══════════════════════════════════════
                     GOLD LAYER
        company_360 / investment_targets /
              market_analysis
        ═══════════════════════════════════════
                         │
        ═══════════════════════════════════════
                 INTELLIGENCE LAYER
        ┌─────────────────┬────────────────────┐
   Scoring Engine     ML Prediction      Recommendation
   (règles v1)        (XGBoost + SHAP)      Engine
        └─────────────────┴────────────────────┘
                         │
                  FastAPI Backend
              (/companies, /score, /search)
                         │
                 React Dashboard
        (KPIs, Top Opportunities, Company Profile)

   Transverse :
   Airflow (orchestration quotidienne)
   Great Expectations (data quality)
   OpenMetadata (gouvernance, lineage)
   Prometheus/Grafana (monitoring)
   Docker Compose (déploiement)
```

## 📋 Table de suivi

| Palier | Contenu | Différenciant | Durée réaliste |
|---|---|---|---|
| A | Sources + Kafka + Bronze | ⭐⭐ Base solide | 1-2 semaines |
| B | Spark + Silver | ⭐⭐⭐ Très fort | 2 semaines |
| C | dbt + Gold | ⭐⭐⭐ Très fort | 1-2 semaines |
| D | Scoring règles v1 | ⭐⭐ Produit démontrable rapidement | 1 semaine |
| E | ML + SHAP | ⭐⭐⭐ Différenciant majeur (cas d'usage inédit vs CreditPulse) | 2 semaines |
| F | Backend FastAPI | ⭐⭐ Attendu | 1-2 semaines |
| G | Frontend React | ⭐⭐ Attendu, mais fort impact visuel en entretien | 2 semaines |
| H | Industrialisation | ⭐⭐ Cohérence avec LedgerLake/CreditPulse | 2 semaines |

---

## Positionnement dans ta suite portfolio

```
FINTECH INTELLIGENCE PLATFORM

LedgerLake   → Data Foundation (plateforme de données financières)
CreditPulse  → Credit Risk Decision Engine (scoring crédit)
DealScout    → Investment & M&A Intelligence Engine (scoring d'opportunités)
```

Les trois partagent le même socle technique (Kafka, Spark/dbt, Airflow, Great Expectations, OpenMetadata) mais résolvent des problèmes métier différents — c'est exactement l'argument qui démontre une **compréhension transversale de la donnée en finance**, pas juste trois projets isolés.

---

## Comment on travaille ensemble à partir de maintenant

Comme pour les deux autres projets, chaque fichier du zip contient un commentaire d'en-tête expliquant précisément ce qu'il doit faire. Dis-moi quand tu veux démarrer le **Palier A.1** (connecteurs de sources + génération du dataset d'entreprises simulées) et on code ensemble.
