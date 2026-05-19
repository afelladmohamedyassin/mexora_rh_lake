import os
from pipeline.bronze_ingestion import ingerer_bronze
from pipeline.silver_transform import (
    charger_depuis_bronze, 
    nettoyer_titres_postes, 
    normaliser_salaires, 
    normaliser_experience,
    sauvegarder_silver
)
from pipeline.silver_nlp import extraire_competences
from pipeline.gold_aggregation import construire_gold

def main():
    DATA_LAKE_ROOT = 'data_lake'
    SOURCE_JSON_PATH = os.path.join(DATA_LAKE_ROOT, 'offres_emploi_it_maroc.json')
    REF_COMPETENCES_PATH = os.path.join(DATA_LAKE_ROOT, 'referentiel_competences_it.json')

    print("=== DÉMARRAGE DU PIPELINE DATA LAKE MEXORA RH ===\n")

    print("--- Phase 1: Ingestion vers Bronze (Raw) ---")
    if os.path.exists(SOURCE_JSON_PATH):
        ingerer_bronze(filepath_source=SOURCE_JSON_PATH, data_lake_root=DATA_LAKE_ROOT)
    else:
        print(f"ERREUR: Fichier source introuvable : {SOURCE_JSON_PATH}")
        return

    print("\n--- Phase 2: Nettoyage vers Silver (Cleaned) ---")
    df_brut = charger_depuis_bronze(data_lake_root=DATA_LAKE_ROOT)
    
    if not df_brut.empty:
        # Nettoyage
        df_clean = nettoyer_titres_postes(df_brut)
        df_clean = normaliser_salaires(df_clean)
        df_clean = normaliser_experience(df_clean)
        
        # NLP Extraction
        print("\n--- Phase 3: Extraction NLP des compétences ---")
        df_competences = extraire_competences(df_clean, REF_COMPETENCES_PATH)
        
        # Sauvegarde Parquet (Silver)
        print("\n--- Phase 4: Sauvegarde en zone Silver (Parquet) ---")
        sauvegarder_silver(df_clean, df_competences, DATA_LAKE_ROOT)
        
        # Agrégation DuckDB (Gold)
        print("\n--- Phase 5: Agrégation vers zone Gold (Curated) ---")
        construire_gold(data_lake_root=DATA_LAKE_ROOT)
        
        print("\n=== PIPELINE TERMINÉ AVEC SUCCÈS ===")
        
    else:
        print("ERREUR: Aucune donnée chargée depuis la zone Bronze.")

if __name__ == "__main__":
    main()