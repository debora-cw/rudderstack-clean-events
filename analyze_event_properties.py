import requests
import json
import re
from collections import Counter, defaultdict
from datetime import datetime

class RudderStackAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.rudderstack.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_data_catalog_events(self):
        """
        Obtém todos os eventos do catálogo de dados
        """
        url = f"{self.base_url}/v2/catalog/events"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro ao obter eventos do catálogo: {response.status_code}")
                print(f"Resposta: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erro na requisição: {str(e)}")
            return None
    
    def get_event_properties(self, event_id):
        """
        Obtém propriedades específicas de um evento
        """
        url = f"{self.base_url}/v2/catalog/events/{event_id}/properties"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro ao obter propriedades do evento {event_id}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erro na requisição: {str(e)}")
            return None
    
    def get_all_properties(self):
        """
        Obtém todas as propriedades do catálogo
        """
        url = f"{self.base_url}/v2/catalog/properties"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro ao obter propriedades: {response.status_code}")
                print(f"Resposta: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erro na requisição: {str(e)}")
            return None

def analyze_property_name(prop_name):
    """
    Analisa o nome de uma propriedade e identifica possíveis problemas
    """
    issues = []
    
    # Verificar zip code
    if re.search(r'zip.*code|postal.*code|cep', prop_name.lower()):
        issues.append("ZIP_CODE")
    
    # Verificar nomes com typos comuns
    typo_patterns = {
        r'adress': 'ADDRESS_TYPO',
        r'recieve': 'RECEIVE_TYPO', 
        r'seperate': 'SEPARATE_TYPO',
        r'occured': 'OCCURRED_TYPO',
        r'sucessful': 'SUCCESSFUL_TYPO',
        r'lenght': 'LENGTH_TYPO'
    }
    
    for pattern, issue_type in typo_patterns.items():
        if re.search(pattern, prop_name.lower()):
            issues.append(issue_type)
    
    # Verificar nomes muito longos
    if len(prop_name) > 50:
        issues.append("TOO_LONG")
    
    # Verificar caracteres especiais problemáticos
    if re.search(r'[^\w\s\-_.]', prop_name):
        issues.append("SPECIAL_CHARS")
    
    # Verificar espaços em branco
    if ' ' in prop_name:
        issues.append("HAS_SPACES")
    
    # Verificar nomes duplicados com case diferentes
    if prop_name != prop_name.lower() and prop_name != prop_name.upper():
        issues.append("MIXED_CASE")
    
    # Verificar propriedades que parecem ser temporárias/debug
    debug_patterns = [r'test', r'debug', r'temp', r'tmp', r'old', r'deprecated']
    for pattern in debug_patterns:
        if re.search(pattern, prop_name.lower()):
            issues.append("DEBUG_TEMP")
    
    return issues

def main():
    print("🔍 Analisando Propriedades dos Eventos - Data Governance")
    print("=" * 70)
    
    API_KEY = "2yHrYtvoMRiQs4nsZ0MrqHrJtsi"
    api = RudderStackAPI(API_KEY)
    
    # 1. Tentar obter propriedades do catálogo
    print("\n📋 Obtendo propriedades do catálogo...")
    properties_data = api.get_all_properties()
    
    if properties_data:
        if 'properties' in properties_data:
            properties = properties_data['properties']
            print(f"✅ Encontradas {len(properties)} propriedades no catálogo")
            
            # Analisar cada propriedade
            problematic_properties = []
            issue_counter = Counter()
            
            print(f"\n🔍 Analisando propriedades...")
            
            for prop in properties:
                prop_name = prop.get('name', '')
                prop_id = prop.get('id', '')
                prop_type = prop.get('dataType', 'unknown')
                
                issues = analyze_property_name(prop_name)
                
                if issues:
                    problematic_properties.append({
                        'name': prop_name,
                        'id': prop_id,
                        'type': prop_type,
                        'issues': issues,
                        'description': prop.get('description', ''),
                        'createdAt': prop.get('createdAt', '')
                    })
                    
                    for issue in issues:
                        issue_counter[issue] += 1
            
            # Mostrar resultados
            print(f"\n{'='*70}")
            print("🚨 PROPRIEDADES PROBLEMÁTICAS ENCONTRADAS:")
            print("=" * 70)
            
            if problematic_properties:
                print(f"Total de propriedades com problemas: {len(problematic_properties)}")
                
                # Agrupar por tipo de problema
                issues_by_type = defaultdict(list)
                for prop in problematic_properties:
                    for issue in prop['issues']:
                        issues_by_type[issue].append(prop)
                
                # Mostrar por categoria
                issue_descriptions = {
                    'ZIP_CODE': '📮 Propriedades relacionadas a ZIP/CEP',
                    'ADDRESS_TYPO': '🔤 Erro de digitação: "adress" → "address"',
                    'RECEIVE_TYPO': '🔤 Erro de digitação: "recieve" → "receive"',
                    'SEPARATE_TYPO': '🔤 Erro de digitação: "seperate" → "separate"',
                    'OCCURRED_TYPO': '🔤 Erro de digitação: "occured" → "occurred"',
                    'SUCCESSFUL_TYPO': '🔤 Erro de digitação: "sucessful" → "successful"',
                    'LENGTH_TYPO': '🔤 Erro de digitação: "lenght" → "length"',
                    'TOO_LONG': '📏 Nomes muito longos (>50 caracteres)',
                    'SPECIAL_CHARS': '🔣 Caracteres especiais problemáticos',
                    'HAS_SPACES': '🔲 Contém espaços em branco',
                    'MIXED_CASE': '🔠 Case inconsistente',
                    'DEBUG_TEMP': '🐛 Propriedades temporárias/debug'
                }
                
                for issue_type, props in issues_by_type.items():
                    print(f"\n{issue_descriptions.get(issue_type, issue_type)} ({len(props)} propriedades):")
                    
                    for prop in props[:10]:  # Mostrar apenas as primeiras 10
                        print(f"   • {prop['name']} (ID: {prop['id'][:20]}...)")
                        if prop['description']:
                            print(f"     Descrição: {prop['description'][:60]}...")
                    
                    if len(props) > 10:
                        print(f"     ... e mais {len(props) - 10} propriedades")
                
                # Resumo estatístico
                print(f"\n{'='*70}")
                print("📊 RESUMO ESTATÍSTICO:")
                print("=" * 70)
                
                for issue_type, count in issue_counter.most_common():
                    print(f"   {issue_descriptions.get(issue_type, issue_type)}: {count}")
                
            else:
                print("✅ Nenhuma propriedade problemática encontrada!")
        
        else:
            print("⚠️  Nenhuma propriedade encontrada no catálogo")
    
    else:
        print("❌ Não foi possível obter propriedades do catálogo")
        print("💡 Isso pode indicar que o catálogo não está sendo usado ou você precisa de permissões específicas")
    
    # 2. Tentar obter eventos para análise alternativa
    print(f"\n{'='*70}")
    print("🔄 Tentativa alternativa: Analisando eventos...")
    
    events_data = api.get_data_catalog_events()
    
    if events_data and 'events' in events_data:
        events = events_data['events']
        print(f"✅ Encontrados {len(events)} eventos para análise")
        
        if events:
            print("\n📋 Primeiros 10 eventos encontrados:")
            for i, event in enumerate(events[:10]):
                print(f"   {i+1}. {event.get('name', 'N/A')} (ID: {event.get('id', 'N/A')[:20]}...)")
        else:
            print("⚠️  Lista de eventos vazia")
    
    print(f"\n{'='*70}")
    print("💡 PRÓXIMOS PASSOS RECOMENDADOS:")
    print("=" * 70)
    print("1. 🔍 Revisar propriedades problemáticas identificadas")
    print("2. 🗑️  Criar script de limpeza para propriedades desnecessárias")
    print("3. 📝 Documentar padrões de nomenclatura corretos")
    print("4. 🤖 Implementar validação automática para novas propriedades")
    print("5. 📊 Criar dashboard de monitoramento de qualidade de dados")

if __name__ == "__main__":
    main() 