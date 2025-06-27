import requests
import os
import json

API_TOKEN = os.getenv("RUDDERSTACK_API_KEY")
BASE_URL = "https://api.rudderstack.com/v2"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def fetch_all_events():
    url = f"{BASE_URL}/schemas"
    all_events = []
    page = 1
    page_size = 50
    while True:
        params = {"page": page}
        print(f"Buscando página {page} de eventos...")
        try:
            response = requests.get(url, headers=HEADERS, params=params)
            response.raise_for_status()
            response_data = response.json()
            results = response_data.get('results', [])
            if not results:
                break
            all_events.extend(results)
            print(f"Página {page}: {len(results)} eventos encontrados.")
            page += 1
        except Exception as e:
            print(f"Erro ao buscar eventos na página {page}: {str(e)}")
            break
    print(f"Total de eventos encontrados: {len(all_events)}")
    return all_events

# Regras de taxonomia para eventos
def is_standard_event_name(name: str) -> (bool, list):
    reasons = []
    # Regra 1: Deve conter pelo menos um pipe (|)
    if '|' not in name:
        reasons.append('Não contém separador | (pipe)')
    # Regra 2: Deve ter mais de uma palavra (evitar nomes genéricos)
    if len(name.split()) <= 1 and '|' not in name:
        reasons.append('Nome muito curto ou genérico')
    # Regra 3: Evitar nomes genéricos comuns
    genericos = {'success', 'done', 'click', 'ok', 'yes', 'no', 'true', 'false', 'event', 'data'}
    if name.lower() in genericos:
        reasons.append('Nome genérico demais')
    # Regra 4: Deve ser descritivo (mínimo 6 caracteres)
    if len(name) < 6:
        reasons.append('Nome muito curto')
    # Regra 5: Opcional - deve seguir formato App | Contexto | Ação
    if name.count('|') < 1:
        reasons.append('Não segue formato mínimo com pipe')
    return (len(reasons) == 0, reasons)

def main():
    print('Buscando todos os eventos via API...')
    all_events = fetch_all_events()
    print('\nSalvando todos os eventos em all_events.json...')
    with open('all_events.json', 'w', encoding='utf-8') as f:
        json.dump(all_events, f, indent=2, ensure_ascii=False)

    print('Auditando nomes de eventos...')
    not_standard = []
    for event in all_events:
        name = event.get('eventIdentifier', '')
        is_ok, reasons = is_standard_event_name(name)
        if not is_ok:
            event_copy = event.copy()
            event_copy['reasons'] = reasons
            not_standard.append(event_copy)
    print(f"\nTotal de eventos fora do padrão: {len(not_standard)}\n")
    with open('not_standard_events.json', 'w', encoding='utf-8') as f:
        json.dump(not_standard, f, indent=2, ensure_ascii=False)
    for item in not_standard:
        print(f"- {item.get('eventIdentifier', '')} (ID: {item.get('uid', '')}) -> Motivos: {', '.join(item['reasons'])}")
    if not not_standard:
        print('Todos os eventos seguem o padrão!')
    print('\nArquivos gerados: all_events.json, not_standard_events.json')

    # Print resumo final
    print("\n================ RESUMO =================")
    print(f"Total de eventos: {len(all_events)}")
    print(f"Total fora do padrão: {len(not_standard)}")
    print(f"Eventos dentro do padrão: {len(all_events) - len(not_standard)}")
    print("========================================\n")

if __name__ == "__main__":
    main() 