import re

# Przykładowa lista słów zakazanych/obelżywych (heurystyka pod moderację AI)
FORBIDDEN_WORDS = ['scam', 'oszust', 'spam', 'kurwa', 'chuj', 'jebac', 'debil']

def analyze_text_content(text):
    """
    Analizuje treść wiadomości/komentarza.
    Zwraca krotkę: (is_approved, flag_reason)
    """
    text_lower = text.lower()
    
    # 1. Wykrywanie zabronionych słów
    for word in FORBIDDEN_WORDS:
        if word in text_lower:
            return False, f"Wykryto niedozwolone słowo: '{word}'"

    # 2. Wykrywanie prób wyłudzeń (np. numerów kart płatniczych)
    card_pattern = r'\b(?:\d[ -]*?){13,16}\b'
    if re.search(card_pattern, text):
        return False, "Wykryto potencjalny numer karty płatniczej (ryzyko oszustwa)."

    # Jeśli treść jest czysta:
    return True, None