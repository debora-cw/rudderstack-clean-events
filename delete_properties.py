import json
import requests
import time
from typing import List, Dict

# Configurações
API_TOKEN = "SUA_API_KEY"  
BASE_URL = "https://api.rudderstack.com/v2"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Novo arquivo de entrada
INPUT_FILE = "all_cep_properties.json"

# Função para carregar propriedades do arquivo JSON
def load_properties(file_path: str) -> List[Dict]:
    try:
        with open(file_path, 'r') as f:
            properties = json.load(f)
        print(f"Propriedades carregadas de '{file_path}': {len(properties)}")
        return properties
    except Exception as e:
        print(f"Erro ao ler o arquivo {file_path}: {str(e)}")
        return []

def delete_property(property_id: str) -> bool:
    url = f"{BASE_URL}/catalog/properties/{property_id}"
    try:
        response = requests.delete(url, headers=HEADERS)
        if response.status_code in (200, 204):
            print(f"Propriedade excluída com sucesso! (ID: {property_id})")
            return True
        else:
            print(f"Falha ao excluir {property_id}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Erro ao excluir {property_id}: {str(e)}")
        return False

def main():
    properties = load_properties(INPUT_FILE)
    if not properties:
        print("Nenhuma propriedade para excluir.")
        return
    success = 0
    failed = 0
    for idx, prop in enumerate(properties, 1):
        prop_id = prop.get('id')
        prop_name = prop.get('name')
        print(f"[{idx}/{len(properties)}] Excluindo propriedade: {prop_name} (ID: {prop_id})...")
        if prop_id and delete_property(prop_id):
            print(f"Sucesso ao excluir {prop_name} (ID: {prop_id})")
            success += 1
        else:
            print(f"Falha ao excluir {prop_name} (ID: {prop_id})")
            failed += 1
        time.sleep(0.2)  # Pequeno delay para evitar rate limit
    print(f"\nResumo:")
    print(f"Total processadas: {len(properties)}")
    print(f"Sucesso: {success}")
    print(f"Falha: {failed}")

if __name__ == "__main__":
    main() 