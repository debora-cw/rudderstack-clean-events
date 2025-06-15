import json
import re
import requests
import os
from typing import List, Dict

API_TOKEN = os.getenv("RUDDERSTACK_API_KEY")
BASE_URL = "https://api.rudderstack.com/v2"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def is_cep(name: str) -> bool:
    cep_pattern = r'^\d{5}-\d{3}$'
    return bool(re.match(cep_pattern, name))

def fetch_all_properties() -> List[Dict]:
    url = f"{BASE_URL}/catalog/properties"
    all_properties = []
    page = 1
    page_size = 50
    while True:
        params = {"page": page, "per_page": page_size}
        print(f"Buscando página {page} de propriedades...")
        try:
            response = requests.get(url, headers=HEADERS, params=params)
            response.raise_for_status()
            response_data = response.json()
            if isinstance(response_data, dict) and 'data' in response_data:
                properties = response_data['data']
                if not properties:
                    break
                all_properties.extend(properties)
                print(f"Página {page}: {len(properties)} propriedades encontradas.")
                page += 1
            else:
                print(f"Formato inesperado da resposta: {type(response_data)}")
                print(f"Resposta: {json.dumps(response_data, indent=2)[:500]}...")
                break
        except Exception as e:
            print(f"Erro ao buscar propriedades na página {page}: {str(e)}")
            break
    print(f"Total de propriedades encontradas: {len(all_properties)}")
    return all_properties

def filter_cep_properties(properties: List[Dict]) -> List[Dict]:
    cep_properties = []
    for prop in properties:
        try:
            if isinstance(prop, dict) and 'name' in prop:
                if is_cep(prop['name']):
                    cep_properties.append(prop)
            else:
                print(f"Propriedade com formato inesperado: {prop}")
        except Exception as e:
            print(f"Erro ao processar propriedade: {str(e)}")
            print(f"Propriedade: {prop}")
    return cep_properties

def main():
    all_properties = fetch_all_properties()
    if not all_properties:
        print("Não foi possível buscar as propriedades. Verifique o token de API.")
        return
    cep_properties = filter_cep_properties(all_properties)
    print(f"\nTotal de propriedades encontradas: {len(all_properties)}")
    print(f"Propriedades com formato de CEP: {len(cep_properties)}")
    output_file = 'all_cep_properties.json'
    with open(output_file, 'w') as f:
        json.dump(cep_properties, f, indent=2)
    print(f"\nLista de todas as propriedades de CEP foi salva em '{output_file}'")
    if cep_properties:
        print("\nExemplos de propriedades de CEP encontradas:")
        for prop in cep_properties[:5]:
            print(f"Nome: {prop['name']}, ID: {prop['id']}")
    else:
        print("\nNenhuma propriedade com formato de CEP foi encontrada.")

if __name__ == "__main__":
    main()
