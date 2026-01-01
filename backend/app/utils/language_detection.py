"""Language detection utilities."""
from typing import Literal

def detect_language(text: str) -> Literal["en", "fr"]:
    """
    Detect language from text.
    Returns 'fr' for French, 'en' for English (default).
    """
    if not text:
        return "en"
    
    text_lower = text.lower()
    
    # French keywords
    french_keywords = [
        'comment', 'quoi', 'où', 'quand', 'pourquoi', 'combien', 
        'quel', 'quelle', 'quelles', 'quels', 'explique', 'parle',
        'montre', 'liste', 'donne', 'analyse', 'graphique', 'tendance',
        'station', 'carburant', 'véhicule', 'carte', 'transactions',
        'inventaire', 'consommation', 'prix', 'litre', 'essence', 'diesel'
    ]
    
    # Count French keywords
    french_count = sum(1 for keyword in french_keywords if keyword in text_lower)
    
    # If more than 2 French keywords found, likely French
    if french_count >= 2:
        return "fr"
    
    # Check for common French words
    common_french = ['le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'ou', 'avec', 'pour', 'sur', 'dans']
    french_word_count = sum(1 for word in common_french if f' {word} ' in f' {text_lower} ' or text_lower.startswith(f'{word} ') or text_lower.endswith(f' {word}'))
    
    if french_word_count >= 3:
        return "fr"
    
    return "en"

