import pandas as pd
import numpy as np

def process_data(survey_data_path:str, transcript_data_path:str, destination_path:str):
    """
    La fonction pour transformer la base de donnée. Elle suite le cheminement suivant:

    1. Créer une colonne vide à la suite de chaque variable dans la grande base de données
    2. Corriger l'absence de "media" et "acc" pour respecter le format suivant `media\code.aac`
    3. Pour chaque code dans CODE (transcript), 
        * Chercher dans la base de donnée la variable dans laquelle il est logé
        * Une fois que la variable est trouvée, aller dans la colonne vide correspondante à cette variable
        * Mettre le texte copié dans TRANSCRIPTIONS à la place de la cellule vide (intersection entre Colonne vide et ligne dans laquelle le CODE a été retrouvé)
    
    parameters : 
    survey_data_path (str) : le chemin d'accès vers la base de données sur l'enquete.
    transcript_data_path (str) : le chemin d'accès vers la base de données des transcriptions.
    destination_path (str) : le chemin du dossier dans lequel veut être sauvergardé la base de donnée finale

    return:
    survey_data (DataFrame) : la base de données modifiée    
    
    """
    # Load the datas
    survey_data = pd.read_excel(survey_data_path)
    transcript_data = pd.read_excel(transcript_data_path)
    
    # Define the variables that are related to the interview reconrds
    interview_variables = ["principaux_obstacles_naissances", "principaux_obstacles_deces", "principaux_obstacles_mariage",\
                           	"Strategie_promotion_service_naissance", "Strategie_promotion_service_deces", "Strategie_promotion_service_mariage",\
                            "Strategie_promotion_service_general",	"principaux_obstacles_anip_naissances", "principaux_obstacles_anip_deces",\
                            "principaux_obstacles_anip_mariage", "stategies_en_place_service",	"stategies_en_place_deces",	"stategies_en_place_naissance",\
                            "strategies_en_place_mariage", "poposition_strategies", "non_beneficiaire_services_anip"]

    # Create the empty columns in the survey_data associated with each variable in the interview variables list
    for var in interview_variables:
        var_position = survey_data.columns.get_loc(var) + 1
        survey_data.insert(var_position, f"{var}_transcription", "")

    # Recode the transcript data to correct the odds behaviours
        ## Correct the names of the colums (especially to correct the `TRANSCRIPTIONS` variable)
    transcript_data.columns = ['TRANSCRIPTEURS', 'ENQUETEURS', 'ENQUETES', 'CODE', 'TRANSCRIPTIONS']
        ## Modifiy the CODE variable in transcript_data
    transcript_data["CODE"] = transcript_data["CODE"].apply(lambda x : "media\\" + str(x).replace("\n", "").replace(" ", "") if not pd.isna(x) else x)

    # Loop to take the comment in the transcript database and assign it to the corresponding column
        ## Take each code in the `CODE` variable in transcript data
    for code_transcript in transcript_data["CODE"]:
        ## Check if the code taken is not null
        if pd.notna(code_transcript):
            ### Now, iterate over each variable in the interview variables list in the survey data
            for interview_variable in interview_variables:
                #### Take each code in the variable over wich we're iterating through
                for variable_code in survey_data[interview_variable]:
                    ##### Check if the code in the interview variable in the survey data is the same as the code taken in the transcript data
                    if code_transcript == str(variable_code)[:-4]:
                        ## Take the index corresponding to the code taken in the transcript data                        
                        code_transcript_index = transcript_data[transcript_data["CODE"]==code_transcript].index
                        ## Take the index corresponding to the code taken in the survey data                        
                        variable_code_index = survey_data[survey_data[interview_variable]==variable_code].index
                        ## Assign the human transcription to the corresponding code in the suervey data
                        survey_data.loc[variable_code_index, f"{interview_variable}_transcription"] = transcript_data.loc[code_transcript_index, "TRANSCRIPTIONS"].values[0]
    
    # Convert to string format and delete any formatting symbols the new columns created
    for variable in [var for var in survey_data.columns if "transcription" in var]:
        survey_data[variable] = survey_data[variable].astype(str).str.replace("\n", "")

    # Save the file
    destination_path = destination_path + "survey_data.xlsx"
    survey_data.to_excel(destination_path)   

    return survey_data
