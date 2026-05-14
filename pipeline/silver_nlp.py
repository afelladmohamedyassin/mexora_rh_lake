# Extraction de compétences depuis texte
import pandas as pd
import json
import re

def extraire_competences(df: pd.DataFrame, referentiel_path: str) -> pd.DataFrame:
    """
    Extrait les compétences IT depuis le texte libre en faisant un matching 
    sur le référentiel fourni.
    """
    with open(referentiel_path, 'r', encoding='utf-8') as f:
        referentiel = json.load(f)

    # 1. Construire un dictionnaire plat: alias -> nom_normalise, famille
    dict_competences = {}
    for famille, competences in referentiel.get('familles', {}).items():
        for nom_normalise, aliases in competences.items():
            for alias in aliases:
                dict_competences[alias.lower()] = {
                    'competence': nom_normalise,
                    'famille': famille
                }

    # Trier par longueur décroissante pour éviter les faux positifs 
    # (ex: matcher "react native" avant "react")
    aliases_tries = sorted(dict_competences.keys(), key=len, reverse=True)
    
    resultats = []

    for _, offre in df.iterrows():
        # Concaténer 'competences_brut' et 'description' pour maximiser la recherche
        texte_complet = ' '.join(filter(None, [
            str(offre.get('competences_brut', '') or ''),
            str(offre.get('description', '') or '')
        ])).lower()

        competences_trouvees = set()
        
        for alias in aliases_tries:
            # Recherche en tant que mot entier (word boundary)
            pattern = r'\b' + re.escape(alias) + r'\b'
            
            if re.search(pattern, texte_complet):
                info = dict_competences[alias]
                cle = info['competence']

                if cle not in competences_trouvees:
                    competences_trouvees.add(cle)
                    
                    # On standardise la ville à la volée pour les agrégations futures
                    ville_brute = str(offre.get('ville', '')).capitalize()
                    
                    resultats.append({
                        'id_offre': offre['id_offre'],
                        'profil': offre.get('profil_normalise', 'Autre IT'),
                        'ville': ville_brute,
                        'competence': info['competence'],
                        'famille': info['famille'],
                        'date_pub': offre.get('date_publication'),
                        'annee': str(offre.get('date_publication', ''))[:4],
                        'mois': str(offre.get('date_publication', ''))[5:7]
                    })

        # Si aucune compétence n'est trouvée, on garde une trace
        if not competences_trouvees:
            ville_brute = str(offre.get('ville', '')).capitalize()
            resultats.append({
                'id_offre': offre['id_offre'],
                'profil': offre.get('profil_normalise', 'Autre IT'),
                'ville': ville_brute,
                'competence': 'non_détecté',
                'famille': 'inconnu',
                'date_pub': offre.get('date_publication'),
                'annee': str(offre.get('date_publication', ''))[:4],
                'mois': str(offre.get('date_publication', ''))[5:7]
            })

    df_competences = pd.DataFrame(resultats)
    nb_offres_avec = df_competences[df_competences['competence'] != 'non_détecté']['id_offre'].nunique()
    
    print(f"[SILVER NLP] {len(df_competences)} lignes compétences extraites")
    print(f"[SILVER NLP] {nb_offres_avec}/{len(df)} offres ont au moins 1 compétence détectée")
    
    return df_competences