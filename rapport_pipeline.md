# Rapport de Traitement du Pipeline de Données

Ce document trace les règles appliquées lors du passage de la zone Bronze (données brutes) à la zone Silver (données nettoyées).

## 1. Normalisation des Intitulés de Postes
* **Règle appliquée :** Utilisation d'expressions régulières (Regex) pour mapper les titres non standardisés vers un référentiel de 12 familles de profils métiers.
* **Volumétrie :** 5000 offres ingérées au total. 2443 offres ont été classées dans une catégorie spécifique. 2557 offres n'ayant pas matché ont été classées en "Autre IT".
* **Cas limites rencontrés :** Les titres combinant plusieurs rôles (ex: "Développeur Fullstack / DevOps") sont classés selon la première occurrence détectée par les Regex pour éviter les doublons de comptage au niveau de l'offre.

## 2. Normalisation des Salaires
* **Règle appliquée :** Extraction des valeurs numériques via Regex. Conversion des salaires en format "K" (milliers) et conversion des montants en EUR vers MAD (taux fixe de 10.8). Calcul de la médiane pour les fourchettes.
* **Volumétrie :** 71.5% des offres ont un salaire renseigné et valide après nettoyage.
* **Cas limites rencontrés :** Les mentions "Selon profil" ou "Confidentiel" ont été converties en valeurs nulles (avec un flag booléen `salaire_connu = False`). Les salaires aberrants (inférieurs à 3 000 MAD ou supérieurs à 100 000 MAD par mois) ont été rejetés par précaution.

## 3. Normalisation de l'Expérience
* **Règle appliquée :** Extraction des bornes minimales et maximales depuis le texte ("3-5 ans" -> min:3, max:5). Conversion des mots-clés "Junior" et "Débutant" (0-2 ans) et "Senior" (5+ ans).
* **Cas limites rencontrés :** Si seule la borne minimale est mentionnée ("min 3 ans"), la borne maximale est laissée nulle (None).

## 4. Extraction NLP des Compétences
* **Règle appliquée :** Recherche par mots entiers (`\b`) des alias du dictionnaire dans une concaténation des champs `competences_brut` et `description`. Tri des alias par longueur décroissante pour éviter les conflits (ex: empêcher "node" d'occulter "node.js").
* **Volumétrie :** 4789 offres ont au moins 1 compétence détectée. 12732 lignes générées dans la table des compétences éclatée.
* **Cas limites rencontrés :** Si un alias courant a plusieurs significations hors IT (ex: "Go" ou "R"), la limite des "mots entiers" réduit les faux positifs, bien qu'un nettoyage manuel supplémentaire ou un modèle de contexte serait idéal pour la perfection.

## 5. Sauvegarde et Agrégation (Zones Silver & Gold)
* **Sauvegarde Silver :** `offres_clean.parquet` (443 Ko) et `competences.parquet` (118 Ko) sauvegardés avec succès.
* **Agrégation Gold :** 5 tables analytiques (`top_competences`, `salaires_par_profil`, `offres_par_ville`, `entreprises_recruteurs`, `tendances_mensuelles`) construites avec succès dans la zone `data_lake/gold`.