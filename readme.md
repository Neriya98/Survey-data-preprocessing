# 1. Méthodologie

Nous avons utilisé la bibliothèque pandas de Python pour automatiser le processus d'intégration. Deux ensembles de données ont été utilisés : l'un contenant les réponses structurées des enquêtes et l'autre contenant les transcriptions correspondantes d'entretiens approfondis. Notre méthode comprend trois étapes principales :

1. Chargement des données

Les ensembles de données de l'enquête et des transcriptions sont chargés à l'aide de la fonction pd.read_excel(), en supposant que les fichiers sont au format Excel.

```python
survey_data = pd.read_excel(survey_data_path)
transcript_data = pd.read_excel(transcript_data_path)
```

2. Définition des variables d'intérêt
Les principales variables relatives aux obstacles et stratégies autour des événements clés de la vie (naissance, décès, mariage) ont été identifiées dans les données d'enquête. Ce sont les variables à utiliser pour l'appariement avec les transcriptions.

```python
interview_variables = ["principaux_obstacles_naissances", "principaux_obstacles_deces", "principaux_obstacles_mariage",\
                       "Strategie_promotion_service_naissance", "Strategie_promotion_service_deces", "Strategie_promotion_service_mariage",\
                       "Strategie_promotion_service_general", "principaux_obstacles_anip_naissances", "principaux_obstacles_anip_deces",\
                       "principaux_obstacles_anip_mariage", "stategies_en_place_service", "stategies_en_place_deces", "stategies_en_place_naissance",\
                       "strategies_en_place_mariage", "poposition_strategies", "non_beneficiaire_services_anip"]
```

3. Création de nouvelles colonnes pour les transcriptions
Pour chaque variable liée aux entretiens dans les données d'enquête, une colonne vide est créée pour stocker la transcription correspondante.

```python
for var in interview_variables:
    var_position = survey_data.columns.get_loc(var) + 1
    survey_data.insert(var_position, f"{var}_transcription", "")
```

4. Nettoyage et recodage des données de transcription
Les noms de colonnes et les variables de code dans l'ensemble de données de transcription ont été standardisés pour garantir la cohérence lors du processus de fusion. Une attention particulière a été portée à la modification des informations de chemin dans la variable CODE.

```python
transcript_data["CODE"] = transcript_data["CODE"].apply(lambda x: "media\\" + str(x).replace("\n", "").replace(" ", "") if not pd.isna(x) else x)
```

5. Appariement automatisé des transcriptions
Pour chaque code dans les données de transcription, l'algorithme parcourt les variables des données d'enquête et attribue la transcription correspondante à l'enregistrement correspondant de l'enquête.

```python
for code_transcript in transcript_data["CODE"]:
    if pd.notna(code_transcript):
        for interview_variable in interview_variables:
            for variable_code in survey_data[interview_variable]:
                if code_transcript == str(variable_code)[:-4]:
                    code_transcript_index = transcript_data[transcript_data["CODE"] == code_transcript].index
                    variable_code_index = survey_data[survey_data[interview_variable] == variable_code].index
                    survey_data.loc[variable_code_index, f"{interview_variable}_transcription"] = transcript_data.loc[code_transcript_index, "TRANSCRIPTIONS"].values[0]
```

6. Nettoyage final des colonnes de transcription
Les transcriptions sont converties au format texte, et tous les symboles de formatage superflus, tels que les sauts de ligne, sont supprimés.

```python
for variable in [var for var in survey_data.columns if "transcription" in var]:
    survey_data[variable] = survey_data[variable].astype(str).str.replace("\n", "")
```