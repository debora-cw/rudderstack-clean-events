import requests
import json
from datetime import datetime
from collections import defaultdict, Counter

class RudderStackAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.rudderstack.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_all_sources(self):
        """Obtém todas as sources"""
        url = f"{self.base_url}/v2/sources"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erro ao obter sources: {response.status_code}")
                return None
        except Exception as e:
            print(f"Erro na requisição: {str(e)}")
            return None
    
    def get_all_event_schemas(self, page=1):
        """Obtém todos os schemas de eventos usando Event Audit API v2"""
        url = f"{self.base_url}/v2/schemas"
        params = {"page": page}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erro ao obter schemas (página {page}): {response.status_code}")
                if response.status_code == 400:
                    print("Possível problema: Event Audit API não habilitada no workspace")
                return None
        except Exception as e:
            print(f"Erro na requisição de schemas: {str(e)}")
            return None
    
    def get_schemas_by_source(self, write_key, page=1):
        """Obtém schemas de eventos filtrados por source (writeKey)"""
        url = f"{self.base_url}/v2/schemas"
        params = {"writeKey": write_key, "page": page}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            return None
    
    def get_schema_details(self, schema_id):
        """Obtém detalhes completos de um schema específico"""
        url = f"{self.base_url}/v2/schemas/{schema_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            return None

def extract_properties_from_schemas(schemas_data):
    """Extrai propriedades dos schemas de eventos"""
    properties = []
    
    if not schemas_data or 'results' not in schemas_data:
        return properties
    
    for schema_item in schemas_data['results']:
        schema = schema_item.get('schema', {})
        write_key = schema_item.get('writeKey', 'unknown')
        event_type = schema_item.get('eventType', 'unknown')
        event_identifier = schema_item.get('eventIdentifier', 'N/A')
        
        for property_path, data_type in schema.items():
            properties.append({
                'property': property_path,
                'data_type': data_type,
                'write_key': write_key,
                'event_type': event_type,
                'event_identifier': event_identifier,
                'schema_id': schema_item.get('uid', 'unknown')
            })
    
    return properties

def identify_unnecessary_properties(properties):
    """Identifica propriedades potencialmente desnecessárias com base nos padrões da documentação"""
    unnecessary_patterns = [
        # Códigos postais e endereços (PRIORIDADE ALTA)
        'zip', 'zipcode', 'zip_code', 'postal', 'postal_code', 'cep',
        'address', 'street', 'city', 'state', 'country', 'location',
        
        # Propriedades antigas/deprecated
        'old_', 'legacy_', 'deprecated_', 'unused_', 'temp_',
        'test_', 'debug_', 'dev_', '_old', '_legacy', '_deprecated',
        
        # Dados sensíveis (PRIORIDADE CRÍTICA)
        'password', 'ssn', 'social_security', 'credit_card', 'cpf', 'cnpj',
        'phone', 'email', 'ip', 'user_agent', 'fingerprint',
        
        # IDs internos desnecessários
        'internal_id', 'system_id', 'db_id', 'row_id', 'rudder_id',
        
        # Timestamps redundantes
        'created_at_timestamp', 'updated_at_timestamp', 'deleted_at',
        '_timestamp', '_time', '_date',
        
        # Propriedades de contexto excessivas
        'context.ip', 'context.userAgent', 'context.library',
        'context.traits.city', 'context.traits.country',
        
        # Propriedades de device muito específicas
        'device_fingerprint', 'browser_fingerprint', 'canvas_fingerprint',
        'screen_', 'viewport_', 'browser_'
    ]
    
    suspicious_properties = []
    
    for prop in properties:
        prop_name = prop['property'].lower()
        
        # Verificar padrões suspeitos
        for pattern in unnecessary_patterns:
            if pattern in prop_name:
                category = get_category_for_pattern(pattern)
                priority = get_priority_for_category(category)
                
                suspicious_properties.append({
                    **prop,
                    'reason': f"Contém padrão suspeito: '{pattern}'",
                    'category': category,
                    'priority': priority
                })
                break
        
        # Verificar propriedades muito longas
        if len(prop_name) > 50:
            suspicious_properties.append({
                **prop,
                'reason': "Nome muito longo (possível dado desnecessário)",
                'category': 'long_name',
                'priority': 'medium'
            })
    
    return suspicious_properties

def get_category_for_pattern(pattern):
    """Categoriza o tipo de propriedade suspeita"""
    categories = {
        # Dados de endereço
        'zip': 'address_data', 'zipcode': 'address_data', 'zip_code': 'address_data',
        'postal': 'address_data', 'postal_code': 'address_data', 'cep': 'address_data',
        'address': 'address_data', 'street': 'address_data', 'city': 'address_data',
        'state': 'address_data', 'country': 'address_data', 'location': 'address_data',
        
        # Dados sensíveis
        'password': 'sensitive_data', 'ssn': 'sensitive_data', 'credit_card': 'sensitive_data',
        'cpf': 'sensitive_data', 'cnpj': 'sensitive_data', 'phone': 'sensitive_data',
        'email': 'sensitive_data', 'ip': 'sensitive_data', 'fingerprint': 'sensitive_data',
        
        # Propriedades antigas
        'old_': 'deprecated', 'legacy_': 'deprecated', 'deprecated_': 'deprecated',
        'unused_': 'deprecated', '_old': 'deprecated', '_legacy': 'deprecated',
        
        # Dados temporários/teste
        'temp_': 'temporary', 'test_': 'test_data', 'debug_': 'debug_data',
        'dev_': 'development',
        
        # Contexto excessivo
        'context.': 'context_data', 'user_agent': 'context_data', 'browser_': 'context_data'
    }
    
    for key, category in categories.items():
        if key in pattern:
            return category
    
    return 'other'

def get_priority_for_category(category):
    """Define prioridade de limpeza por categoria"""
    priorities = {
        'sensitive_data': 'critical',
        'address_data': 'high',
        'deprecated': 'high',
        'test_data': 'medium',
        'debug_data': 'medium',
        'development': 'medium',
        'temporary': 'medium',
        'context_data': 'low',
        'other': 'low'
    }
    return priorities.get(category, 'low')

def main():
    print("ANÁLISE DE PROPRIEDADES DE EVENTOS - RUDDERSTACK")
    print("Usando Event Audit API v2 para análise precisa")
    print("=" * 70)
    
    API_KEY = "2yHrYtvoMRiQs4nsZ0MrqHrJtsi"
    api = RudderStackAPI(API_KEY)
    
    # 1. Verificar se a Event Audit API está habilitada
    print("Verificando acesso à Event Audit API...")
    test_schemas = api.get_all_event_schemas(page=1)
    
    if not test_schemas:
        print("ERRO: Event Audit API não acessível!")
        print("Possíveis causas:")
        print("1. Event Audit API não habilitada no workspace")
        print("2. Token sem permissões adequadas")
        print("3. Plano não suporta Event Audit API (requer Enterprise)")
        return
    
    print(f"Event Audit API acessível! Primeira página retornou dados.")
    
    # 2. Coletar todos os schemas de eventos
    all_properties = []
    page = 1
    total_schemas = 0
    
    print(f"\nColetando schemas de eventos...")
    
    while True:
        print(f"Processando página {page}...")
        schemas_data = api.get_all_event_schemas(page=page)
        
        if not schemas_data or 'results' not in schemas_data:
            break
        
        results = schemas_data['results']
        if not results:
            break
        
        # Extrair propriedades dos schemas
        page_properties = extract_properties_from_schemas(schemas_data)
        all_properties.extend(page_properties)
        total_schemas += len(results)
        
        print(f"   Página {page}: {len(results)} schemas, {len(page_properties)} propriedades")
        
        # Verificar se há mais páginas (padrão é 50 por página)
        if len(results) < 50:
            break
        
        page += 1
        
        # Limite de segurança
        if page > 20:
            print("   Limite de páginas atingido (20 páginas)")
            break
    
    print(f"\nTotal coletado: {total_schemas} schemas, {len(all_properties)} propriedades")
    
    # 3. Análise estatística
    print(f"\n{'='*70}")
    print("ANÁLISE ESTATÍSTICA DAS PROPRIEDADES")
    print("=" * 70)
    
    if all_properties:
        # Contar propriedades por nome
        property_counts = Counter([prop['property'] for prop in all_properties])
        
        print(f"Total de propriedades únicas: {len(property_counts)}")
        print(f"Total de ocorrências: {len(all_properties)}")
        
        print(f"\nTOP 20 PROPRIEDADES MAIS COMUNS:")
        for prop_name, count in property_counts.most_common(20):
            print(f"   • {prop_name}: {count} ocorrências")
        
        # Contar por tipo de dados
        type_counts = Counter([prop['data_type'] for prop in all_properties])
        print(f"\nTIPOS DE DADOS:")
        for data_type, count in type_counts.items():
            print(f"   • {data_type}: {count} propriedades")
        
        # Contar por tipo de evento
        event_type_counts = Counter([prop['event_type'] for prop in all_properties])
        print(f"\nTIPOS DE EVENTOS:")
        for event_type, count in event_type_counts.items():
            print(f"   • {event_type}: {count} propriedades")
    
    # 4. Identificar propriedades desnecessárias
    print(f"\n{'='*70}")
    print("PROPRIEDADES POTENCIALMENTE DESNECESSÁRIAS")
    print("=" * 70)
    
    suspicious_props = identify_unnecessary_properties(all_properties)
    
    if suspicious_props:
        print(f"Encontradas {len(suspicious_props)} propriedades suspeitas!")
        
        # Agrupar por prioridade
        by_priority = defaultdict(list)
        for prop in suspicious_props:
            by_priority[prop['priority']].append(prop)
        
        # Mostrar por prioridade
        priority_order = ['critical', 'high', 'medium', 'low']
        
        for priority in priority_order:
            if priority not in by_priority:
                continue
                
            props = by_priority[priority]
            print(f"\nPRIORIDADE {priority.upper()}: {len(props)} propriedades")
            
            # Agrupar por categoria dentro da prioridade
            by_category = defaultdict(list)
            for prop in props:
                by_category[prop['category']].append(prop)
            
            for category, cat_props in by_category.items():
                print(f"\n  Categoria: {category}")
                print(f"  Quantidade: {len(cat_props)}")
                
                # Mostrar exemplos (máximo 5 por categoria)
                for prop in cat_props[:5]:
                    print(f"    • {prop['property']} ({prop['data_type']})")
                    print(f"      Evento: {prop['event_identifier']}")
                    print(f"      Razão: {prop['reason']}")
                
                if len(cat_props) > 5:
                    print(f"    ... e mais {len(cat_props) - 5} propriedades")
    else:
        print("Nenhuma propriedade suspeita encontrada nos padrões analisados")
    
    # 5. Recomendações específicas
    print(f"\n{'='*70}")
    print("RECOMENDAÇÕES PARA LIMPEZA")
    print("=" * 70)
    
    if suspicious_props:
        critical_props = [p for p in suspicious_props if p['priority'] == 'critical']
        high_props = [p for p in suspicious_props if p['priority'] == 'high']
        
        if critical_props:
            print("🚨 AÇÃO URGENTE - PROPRIEDADES CRÍTICAS:")
            print(f"   {len(critical_props)} propriedades sensíveis encontradas!")
            print("   DEVE ser removido IMEDIATAMENTE por compliance")
            
        if high_props:
            print(f"\n⚠️  ALTA PRIORIDADE:")
            print(f"   {len(high_props)} propriedades desnecessárias")
            print("   Recomenda-se remoção para otimização")
        
        print(f"\n📋 PRÓXIMOS PASSOS:")
        print("1. Revisar lista de propriedades críticas")
        print("2. Criar script de remoção automatizada")
        print("3. Implementar em ambiente de teste primeiro")
        print("4. Monitorar impacto após remoção")
        print("5. Criar rotina de limpeza periódica")
    
    # 6. Salvar resultados
    print(f"\nSalvando resultados...")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_schemas': total_schemas,
        'total_properties': len(all_properties),
        'unique_properties': len(set(prop['property'] for prop in all_properties)),
        'suspicious_properties': len(suspicious_props),
        'by_priority': {
            priority: len([p for p in suspicious_props if p['priority'] == priority])
            for priority in ['critical', 'high', 'medium', 'low']
        },
        'top_properties': dict(property_counts.most_common(50)) if all_properties else {},
        'suspicious_details': suspicious_props
    }
    
    with open('event_audit_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("Resultados salvos em 'event_audit_analysis.json'")
    print(f"\n{'='*70}")
    print("ANÁLISE CONCLUÍDA!")
    print("=" * 70)

if __name__ == "__main__":
    main() 