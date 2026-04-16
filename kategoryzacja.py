import json
import os
from google import genai
from dotenv import load_dotenv

# --- 1. KONFIGURACJA API ---
load_dotenv()
klucz = os.getenv("GOOGLE_API_KEY")

# zwracanie błędu, jeśli klucz nie został znaleziony
if not klucz:
    print("404: API Key not found!")
    exit()

# nowe połączenie z Google Gemini przy użyciu nowego SDK
client = genai.Client(api_key=klucz)

# --- 2. FUNKCJA KATEGORYZACJI ZGŁOSZENIA PRZY POMOCY AI ---
def zapytaj_prawdziwe_ai_o_kategorie(tekst_uzytkownika):
    prompt = f"""
    Jesteś analitykiem pierwszej linii wsparcia technicznego w sieci sklepów Żabka.
    Franczyzobiorca zgłasza następujący problem: "{tekst_uzytkownika}"
    
    Twoim zadaniem jest skategoryzowanie tego problemu. 
    WYBIERZ JEDNĄ KATEGORIĘ GŁÓWNĄ Z TEJ LISTY:
    - Sprzęt IT > Komputer Kasowy
    - Sprzęt IT > Komputer Zapleczowy
    - Sprzęt IT > Monitor Kasowy
    - Sprzęt IT > Monitor Zapleczowy
    - Sieć > Switch Kasowy
    - Sieć > Switch Zapleczowy
    - Inne
    
    WYBIERZ JEDNĄ PODKATEGORIĘ Z TEJ LISTY:
    - Nie włącza się
    - Brak internetu
    - Inne
    
    ZASADY: 
    1. Jeśli mowa o "kasie", "posie" z reguły chodzi o "Komputer Kasowy".
    2. Zwróć wynik DOKŁADNIE w formacie: KATEGORIA_GŁÓWNA | PODKATEGORIA
    3. Nie dodawaj absolutnie żadnych innych słów, znaków ani przywitań.
    """
    
    try:
        # Wywołanie modelu przy użyciu nowego SDK
        odpowiedz = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt
        )
        wynik = odpowiedz.text.strip()
        
        if "|" in wynik:
            kategoria, podkategoria = wynik.split("|")
            return kategoria.strip(), podkategoria.strip()
        else:
            return "Inne", "Inne"
            
    except Exception as e:
        print(f"[Błąd API: {e}]")
        return "Inne", "Inne"

# --- 3. NUMERATOR ZGŁOSZEŃ (cw-0000X) ---
def pobierz_nastepny_numer_zgloszenia(nazwa_pliku):
    if not os.path.exists(nazwa_pliku):
        return 1
    with open(nazwa_pliku, "r", encoding="utf-8") as plik:
        baza = json.load(plik)
        if not baza:
            return 1
        
        ostatnie_id_tekst = baza[-1]["id_numer"]
        ostatnie_id_liczba = int(str(ostatnie_id_tekst).replace("cw-", ""))
        return ostatnie_id_liczba + 1

# --- 4. START PROGRAMU ---
print("--- INTELIGENTNY SYSTEM WSPARCIA ---")
baza_file = "baza_ticketow.json"

while True:
    problem = input("\nUżytkownik: ")
    if problem.lower() == 'wyjscie': break

    print("System: [Sztuczna Inteligencja analizuje zgłoszenie...]")
    kategoria, podkategoria = zapytaj_prawdziwe_ai_o_kategorie(problem)
    
    print(f"[AI rozpoznało: {kategoria} | {podkategoria}]")
    
    ma_podpowiedzi = False
    
    if podkategoria == "Nie włącza się":
        print("System: Zanim utworzymy zgłoszenie, sprawdź proszę:")
        print("-> Dociśnij kable zasilające przy urządzeniu.")
        print("-> Sprawdź, czy w gniazdku jest prąd (np. czy działa inne urządzenie).")
        ma_podpowiedzi = True
    elif "Sieć" in kategoria or podkategoria == "Brak internetu":
        print("System: Zanim utworzymy zgłoszenie, sprawdź proszę:")
        print("-> Zrestartuj switch/router (wyciągnij wtyczkę zasilania na 10 sekund).")
        print("-> Sprawdź, czy kable sieciowe są wpięte i czy migają diody.")
        ma_podpowiedzi = True

    if ma_podpowiedzi:
        decyzja = input("Czy to pomogło? (tak / nie): ").lower()
        if decyzja == "tak":
            print("System: Super! Cieszę się, że pomogłem.")
            continue

    print("System: Tworzę zgłoszenie do technika...")
    
    nr_liczba = pobierz_nastepny_numer_zgloszenia(baza_file)
    nr_sformatowany = f"cw-{nr_liczba:05d}"
    
    nowy_ticket = {
        "id_numer": nr_sformatowany,
        "kategoria": kategoria,
        "podkategoria": podkategoria,
        "opis": problem,
        "status": "OTWARTE"
    }

    baza = []
    if os.path.exists(baza_file):
        with open(baza_file, "r", encoding="utf-8") as f:
            baza = json.load(f)
    
    baza.append(nowy_ticket)
    with open(baza_file, "w", encoding="utf-8") as f:
        json.dump(baza, f, indent=4, ensure_ascii=False)

    print(f"System: GOTOWE! Twoje zgłoszenie to: {nr_sformatowany}")