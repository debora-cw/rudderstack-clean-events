import requests
import os
import re
import json
import openai
import time

API_TOKEN = os.getenv("RUDDERSTACK_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
BASE_URL = "https://api.rudderstack.com/v2"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

openai.api_key = OPENAI_API_KEY

def fetch_all_properties():
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
                break
        except Exception as e:
            print(f"Erro ao buscar propriedades na página {page}: {str(e)}")
            break
    print(f"Total de propriedades encontradas: {len(all_properties)}")
    return all_properties

# Regras básicas para propriedades
def is_basic_property_name(name: str) -> (bool, list):
    reasons = []
    # Não deve conter pipe
    if '|' in name:
        reasons.append('Contém separador | (pipe), o que não é recomendado para propriedades')
    # Evitar nomes genéricos comuns
    genericos = {'success', 'done', 'click', 'ok', 'yes', 'no', 'true', 'false', 'event', 'data'}
    if name.lower() in genericos:
        reasons.append('Nome genérico demais')
    # Nome muito curto
    if len(name) < 3:
        reasons.append('Nome muito curto')
    # Nome só com números
    if re.fullmatch(r'\d+', name):
        reasons.append('Nome é apenas números')
    # Nome sem significado aparente
    if re.fullmatch(r'[a-zA-Z]{1,2}', name):
        reasons.append('Nome muito curto e sem significado')
    return (len(reasons) == 0, reasons)

def analyze_with_openai(properties):
    print("\nEnviando propriedades para análise da OpenAI...")
    results = []
    for prop in properties:
        name = prop.get('name', '')
        prompt = (
            f"Analise o nome da propriedade de evento abaixo e responda em português:\n"
            f"- Nome: '{name}'\n"
            f"Avalie:\n"
            f"1. O nome é descritivo e segue boas práticas?\n"
            f"2. O nome é genérico, confuso ou desnecessário?\n"
            f"3. Você recomendaria manter, renomear ou excluir essa propriedade?\n"
            f"4. Se possível, sugira um nome melhor.\n"
            f"Responda de forma objetiva e curta."
        )
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.2,
            )
            analysis = response.choices[0].message.content.strip()
        except Exception as e:
            analysis = f"Erro na análise OpenAI: {str(e)}"
        prop_result = prop.copy()
        prop_result['openai_analysis'] = analysis
        results.append(prop_result)
        print(f"Analisado: {name}")
        time.sleep(1.2)  # Evita rate limit
    return results

def analyze_with_openai_batch(properties, batch_size=20):
    print(f"\nEnviando propriedades para análise da OpenAI em lotes de {batch_size}...")
    results = []
    for i in range(0, len(properties), batch_size):
        batch = properties[i:i+batch_size]
        prop_list = [
            f"- {p['name']} (motivos: {', '.join(p.get('reasons', []))})" for p in batch
        ]
        prompt = (
            "Você é um especialista em taxonomia de dados. Analise a lista de propriedades de evento abaixo, que estão fora do padrão básico de nomenclatura.\n"
            "Para cada propriedade, avalie se:\n"
            "- O nome é ruim, genérico, confuso ou desnecessário\n"
            "- Se parece desnecessária, apenas diga: 'Parece desnecessária e pode ser excluída.'\n"
            "- Se for possível melhorar, sugira um nome melhor e explique brevemente o porquê\n"
            "- Se houver padrões ruins recorrentes, cite exemplos e sugira boas práticas gerais\n"
            "Responda em português, de forma objetiva e clara.\n\n"
            "Propriedades fora do padrão:\n"
            + "\n".join(prop_list)
        )
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1200,
                temperature=0.2,
            )
            analysis = response.choices[0].message.content.strip()
        except Exception as e:
            analysis = f"Erro na análise OpenAI: {str(e)}"
        # Salva o batch inteiro com a resposta
        batch_result = {
            "batch_start": i,
            "batch_end": i+len(batch)-1,
            "property_names": [p['name'] for p in batch],
            "openai_analysis": analysis
        }
        results.append(batch_result)
        print(f"Analisado lote {i+1} a {i+len(batch)}")
        time.sleep(1.2)
    return results

def main():
    print('Buscando todas as propriedades via API...')
    all_properties = fetch_all_properties()
    print('\nSalvando todas as propriedades em all_properties.json...')
    with open('all_properties.json', 'w', encoding='utf-8') as f:
        json.dump(all_properties, f, indent=2, ensure_ascii=False)

    print('Auditando nomes de propriedades (regras básicas)...')
    not_standard = []
    for prop in all_properties:
        name = prop.get('name', '')
        is_ok, reasons = is_basic_property_name(name)
        if not is_ok:
            prop_copy = prop.copy()
            prop_copy['reasons'] = reasons
            not_standard.append(prop_copy)
    print(f"\nTotal de propriedades fora do padrão básico: {len(not_standard)}\n")
    with open('not_standard_properties.json', 'w', encoding='utf-8') as f:
        json.dump(not_standard, f, indent=2, ensure_ascii=False)

    # Análise OpenAI em lote
    openai_results = analyze_with_openai_batch(not_standard, batch_size=20)
    with open('property_openai_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(openai_results, f, indent=2, ensure_ascii=False)
    print('\nArquivo gerado: property_openai_analysis.json')

    # Print resumo final
    print("\n================ RESUMO =================")
    print(f"Total de propriedades: {len(all_properties)}")
    print(f"Total fora do padrão básico: {len(not_standard)}")
    print(f"Propriedades dentro do padrão básico: {len(all_properties) - len(not_standard)}")
    print(f"Total analisadas pela OpenAI: {len(openai_results)}")
    print("========================================\n")

if __name__ == "__main__":
    main() 