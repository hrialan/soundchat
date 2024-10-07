import time


def get_prompt(user_context, user_spotify_export, language="fr"):
    if language == "fr":
        return get_prompt_fr(user_context, user_spotify_export)
    elif language == "en":
        return get_prompt_en(user_context, user_spotify_export)
    else:
        raise ValueError("Invalid language.")


def get_system_context(language="fr"):
    if language == "fr":
        return get_system_context_fr()
    elif language == "en":
        return get_system_context_en()
    else:
        raise ValueError("Invalid language.")


def get_prompt_fr(user_context, user_spotify_export):
    prompt_fr = f"""
    Salut ! Peux-tu m'aider à créer une playlist personnalisée basée sur mon humeur et mes préférences musicales ? Voici quelques détails pour te guider :

    1. **Contexte** : Je t'ai fourni le contexte suivant pour t'aider à comprendre mon humeur et mes préférences. Utilise ce contexte autant que possible, même plus que mon export Spotify si c'est pertinent et que la playlist peut servir pour un grand public. Contexte: "{user_context}".

    2. **Export Spotify** : Voici mon export Spotify, qui donne un aperçu de mes goûts musicaux. Assure-toi qu'aucun morceau de cet export n'apparaisse dans la playlist finale (ou du moins pas beaucoup, sauf si c'est pertinent, mais je veux aussi découvrir de nouveaux morceaux) :
    --- DÉBUT DE L'EXPORT SPOTIFY ---
    {user_spotify_export}
    --- FIN DE L'EXPORT SPOTIFY ---

    3. **Date et Heure Actuelles** : {time.asctime()}, utilise cette information pour rendre la playlist pertinente par rapport à l'humeur et à la saison actuelle, ainsi que l'heure de la journée.

    4. **Pays** : Je suis Français, donc tu peux considérer la musique française ou la musique internationale qui est populaire ici.

    **Instructions** :
    - Crée une playlist de 50 morceaux existants qui me plairont, surprendront et me raviront, en me faisant découvrir de la nouvelle musique qui correspond à mes goûts.
    - Sers toi du contexte pour comprendre quel type de musique j'ai besoin en ce moment.
    - Chaque morceau ne doit apparaître qu'une seule fois dans la playlist.
    - Détermine à partir du contexte si la playlist est destinée à une écoute personnelle ou à être partagée avec d'autres. Si c'est pour un usage personnel, utilise autant que possible mon export Spotify pour adapter la playlist à mes goûts. Si c'est pour un public plus large, utilise le contexte pour créer une playlist plus universellement attrayante.
    - Fournis un titre précis et une description en une ligne pour la playlist. Évite d'utiliser des décorations de texte, des guillemets et du markdown. N'hésite pas à utiliser des émojis si cela correspond au contexte.
    - Assure-toi que le titre et la description de la playlist sont dans la même langue que le contexte fourni.

    **Format de Réponse** :
    "
    [TITRE COURT DE LA PLAYLIST BASÉ SUR LE CONTEXTE]
    $$$
    [DESCRIPTION EN UNE LIGNE EXPLIQUANT LA SÉLECTION]
    $$$
    Artiste,Morceau
    Artiste,Morceau
    Artiste,Morceau
    ...  , ...
    "

    **Exemple** :
    "
    Énergie pour le sport !
    $$$
    Une sélection de morceaux dynamiques pour te motiver pendant tes séances de sport.
    $$$
    Daft Punk,Harder Better Faster Stronger
    Eric Prydz,Opus
    ...  , ...
    "

    Merci beaucoup pour ton aide !
    """
    return prompt_fr


def get_system_context_fr():
    return "Tu es un expert en musique chevronné avec une connaissance approfondie de divers genres et une capacité à créer des playlists qui résonnent profondément avec les goûts des auditeurs. Ta mission est de créer une playlist exceptionnelle qui captivera l'utilisateur, en tenant compte de son humeur actuelle et de son historique d'écoute détaillé sur Spotify. Tu es dédié à comprendre les nuances des préférences musicales de chaque utilisateur, garantissant une expérience d'écoute personnalisée et émotionnellement engageante pour chacun. Tu es également capable de créer des playlists adaptées à un public plus large, en utilisant des éléments du contexte pour rendre la playlist universellement attrayante."


def get_prompt_en(user_context, user_spotify_export):
    prompt_en = f"""
    Hi there! Can you help me create a personalized playlist based on my mood and music preferences? Here are some details to guide you:

    1. **Context**: I provided you the following context to help you understand my mood and preferences: "{user_context}". Use this context as much as possible, even more than my Spotify export if it's relevant.

    2. **Spotify Export**: Here is my Spotify export, which gives insight into my musical tastes. Ensure that no track from this export appears in the final playlist (or at least not many):
    --- BEGIN SPOTIFY EXPORT ---
    {user_spotify_export}
    --- END SPOTIFY EXPORT ---

    3. **Current Date and Time**: {time.asctime()}, use this information to make the playlist relevant to the current mood and season.

    4. **Country**: I'm from France, so you can consider French music or international music that is popular here.

    **Instructions**:
    - Create a playlist of 50 existing tracks that will surprise and delight me, introducing me to new music that aligns with my tastes.
    - Follow the guidelines provided in the context to understand what kind of music I need right now.
    - Each track should appear only once in the playlist.
    - Determine from the context whether the playlist is intended for personal listening or for sharing with others. If it's for personal use, use as much of my Spotify export as possible to adapt to my tastes. If it's for a broader audience, use the context to craft a more universally appealing playlist.
    - Provide a precise title and a one-line description for the playlist. Avoid using text decoration, quotes and markdown. Feel free to use emojis if they fit the context.
    - Ensure the playlist title and description are in the same language as the context provided.

    **Response Format**:
    "
    [SHORT PLAYLIST TITLE BASED ON THE CONTEXT]
    $$$
    [ONE-LINE PLAYLIST DESCRIPTION EXPLAINING THE SELECTION]
    $$$
    Artist,Track
    Artist,Track
    Artist,Track
    ...  , ...
    "

    **Example**:
    "
    Chill Vibes for a Rainy Day
    $$$
    A soothing mix of tracks to relax and unwind on a rainy day.
    $$$
    Norah Jones,Don't Know Why
    Bon Iver,Skinny Love
    ...  , ...
    "

    Thanks for your help!
    """
    return prompt_en


def get_system_context_en():
    return "You are a seasoned music connoisseur with an extensive knowledge of diverse genres and a keen ability to curate playlists that resonate deeply with listeners. Your mission is to craft an exceptional playlist that will captivate a broad audience, taking into account their current mood and detailed Spotify listening history. You are dedicated to understanding the nuances of each user's musical preferences, ensuring a personalized and emotionally engaging listening experience for everyone."
