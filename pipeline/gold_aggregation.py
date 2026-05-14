# Calcul des agrégats -> Gold
import duckdb
from pathlib import Path

def construire_gold(data_lake_root: str):
    """Construit toutes les tables Gold depuis les données Silver avec DuckDB."""
    silver_offres = f"{data_lake_root}/silver/offres_clean/offres_clean.parquet"
    silver_comp = f"{data_lake_root}/silver/competences_extraites/competences.parquet"
    
    gold_path = Path(data_lake_root) / 'gold'
    gold_path.mkdir(parents=True, exist_ok=True)
    
    # Connexion à DuckDB (en mémoire)
    con = duckdb.connect()
    
    # ---------------------------------------------------------
    # Table Gold 1 : Top compétences par profil
    # ---------------------------------------------------------
    print("[GOLD] Construction top_competences...")
    df_top_comp = con.execute(f"""
        SELECT 
            profil, 
            famille, 
            competence, 
            COUNT(DISTINCT id_offre) AS nb_offres_mentionnent,
            ROUND(COUNT(DISTINCT id_offre) * 100.0 / 
                (SELECT COUNT(DISTINCT id_offre) FROM '{silver_offres}'), 2) AS pct_offres_total,
            RANK() OVER (PARTITION BY profil ORDER BY COUNT(DISTINCT id_offre) DESC) AS rang_dans_profil
        FROM '{silver_comp}'
        WHERE competence != 'non_détecté'
        GROUP BY profil, famille, competence
        ORDER BY profil, rang_dans_profil
    """).df()
    df_top_comp.to_parquet(gold_path / 'top_competences.parquet', index=False)

    # ---------------------------------------------------------
    # Table Gold 2 : Salaires par profil
    # ---------------------------------------------------------
    print("[GOLD] Construction salaires_par_profil...")
    df_salaires = con.execute(f"""
        SELECT 
            profil_normalise AS profil,
            COUNT(*) AS nb_offres,
            COUNT(*) FILTER (WHERE salaire_connu) AS nb_offres_avec_salaire,
            ROUND(MEDIAN(salaire_median_mad) FILTER (WHERE salaire_connu), 0) AS salaire_median_mad,
            ROUND(AVG(salaire_median_mad) FILTER (WHERE salaire_connu), 0) AS salaire_moyen_mad,
            ROUND(MIN(salaire_min_mad) FILTER (WHERE salaire_connu), 0) AS salaire_min_observe,
            ROUND(MAX(salaire_max_mad) FILTER (WHERE salaire_connu), 0) AS salaire_max_observe
        FROM '{silver_offres}'
        GROUP BY profil_normalise
        HAVING COUNT(*) >= 5
        ORDER BY nb_offres DESC
    """).df()
    df_salaires.to_parquet(gold_path / 'salaires_par_profil.parquet', index=False)

    # ---------------------------------------------------------
    # Table Gold 3 : Volume d'offres par ville
    # ---------------------------------------------------------
    print("[GOLD] Construction offres_par_ville...")
    df_villes = con.execute(f"""
        SELECT 
            UPPER(SUBSTRING(CAST(ville AS VARCHAR), 1, 1)) || LOWER(SUBSTRING(CAST(ville AS VARCHAR), 2)) AS ville,
            profil_normalise AS profil,
            COUNT(*) AS nb_offres,
            COUNT(*) FILTER (WHERE LOWER(CAST(teletravail AS VARCHAR)) LIKE '%télétravail%' 
                                OR LOWER(CAST(teletravail AS VARCHAR)) LIKE '%remote%' 
                                OR LOWER(CAST(teletravail AS VARCHAR)) LIKE '%hybride%') AS nb_offres_remote
        FROM '{silver_offres}'
        WHERE ville IS NOT NULL AND ville != ''
        GROUP BY UPPER(SUBSTRING(CAST(ville AS VARCHAR), 1, 1)) || LOWER(SUBSTRING(CAST(ville AS VARCHAR), 2)), profil_normalise
        ORDER BY nb_offres DESC
    """).df()
    df_villes.to_parquet(gold_path / 'offres_par_ville.parquet', index=False)

    # ---------------------------------------------------------
    # Table Gold 4 : Entreprises les plus recruteuses
    # ---------------------------------------------------------
    print("[GOLD] Construction entreprises_recruteurs...")
    df_entreprises = con.execute(f"""
        SELECT 
            entreprise,
            COUNT(*) AS nb_offres_publiees,
            COUNT(DISTINCT profil_normalise) AS nb_profils_differents,
            ROUND(AVG(salaire_median_mad) FILTER (WHERE salaire_connu), 0) AS salaire_moyen_propose,
            MIN(date_publication) AS premiere_offre,
            MAX(date_publication) AS derniere_offre
        FROM '{silver_offres}'
        WHERE entreprise IS NOT NULL AND entreprise != ''
        GROUP BY entreprise
        HAVING COUNT(*) >= 3
        ORDER BY nb_offres_publiees DESC
        LIMIT 100
    """).df()
    df_entreprises.to_parquet(gold_path / 'entreprises_recruteurs.parquet', index=False)

    # ---------------------------------------------------------
    # Table Gold 5 : Tendances mensuelles
    # ---------------------------------------------------------
    print("[GOLD] Construction tendances_mensuelles...")
    df_tendances = con.execute(f"""
        SELECT 
            SUBSTRING(CAST(date_publication AS VARCHAR), 1, 4) AS annee,
            SUBSTRING(CAST(date_publication AS VARCHAR), 6, 2) AS mois,
            profil_normalise AS profil,
            COUNT(*) AS nb_offres,
            ROUND(AVG(salaire_median_mad) FILTER (WHERE salaire_connu), 0) AS salaire_moyen_mois
        FROM '{silver_offres}'
        WHERE date_publication IS NOT NULL AND date_publication != ''
        GROUP BY SUBSTRING(CAST(date_publication AS VARCHAR), 1, 4), SUBSTRING(CAST(date_publication AS VARCHAR), 6, 2), profil_normalise
        ORDER BY profil_normalise, annee, mois
    """).df()
    df_tendances.to_parquet(gold_path / 'tendances_mensuelles.parquet', index=False)

    con.close()
    print(f"[GOLD] 5 tables analytiques Gold construites avec succès dans : {gold_path}")