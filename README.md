# Mexora RH Intelligence - Data Lake Pipeline

Ce dépôt contient le pipeline d'ingestion et de transformation de données pour le projet Mexora RH Intelligence. Il implémente une architecture Medallion (Bronze, Silver, Gold) en utilisant Python, Pandas et DuckDB. L'objectif est d'analyser les offres d'emploi IT au Maroc pour en extraire des insights sur les compétences, les intitulés de postes et les salaires.

## Structure du Projet

- `pipeline/` : Contient les scripts pour chaque couche de l'architecture Medallion.
  - `bronze_ingestion.py` : Ingère et sauvegarde les données brutes.
  - `silver_transform.py` : Nettoie et normalise les données (postes, salaires, expérience).
  - `silver_nlp.py` : Extrait les compétences du texte des offres à l'aide d'un référentiel métier.
  - `gold_aggregation.py` : Crée des vues analytiques agrégées avec DuckDB.
- `data_lake/` : Répertoire cible pour les fichiers de données (fichiers JSON, Parquet, base DuckDB).
- `analysis/` : Scripts d'analyse ou requêtes spécifiques.
- `analyse_marche_it_maroc.ipynb` : Notebook Jupyter pour la visualisation et l'analyse exploratoire des résultats finaux.
- `main.py` : Point d'entrée principal pour exécuter de bout en bout le pipeline.
- `rapport_pipeline.md` : Documentation détaillée détaillant les règles de gestion et de nettoyage appliquées lors du traitement.

## Prérequis

- Python 3.11+
- Les fichiers de données initiaux (`offres_emploi_it_maroc.json` et `referentiel_competences_it.json`) doivent être placés dans le dossier `data_lake/` avant de lancer le pipeline.

## Installation et Exécution

1. **Créer et activer un environnement virtuel :**

   *Sur Windows :*
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
   *Sur Mac/Linux :*
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer le pipeline de données :**
   Assurez-vous que les fichiers sources sont bien présents dans `data_lake/`.
   ```bash
   python main.py
   ```

4. **Explorer les résultats avec Jupyter Notebook :**
   ```bash
   jupyter notebook analyse_marche_it_maroc.ipynb
   ```

## Résultats

Après exécution, le dossier `data_lake/` contiendra :
- **Bronze :** Les données brutes ingérées.
- **Silver :** Les données nettoyées au format `.parquet` (`offres_clean.parquet` et `competences_extract.parquet`).
- **Gold :** La base de données DuckDB (`gold_insights.duckdb`) contenant les tables prêtes pour l'analyse et la visualisation.