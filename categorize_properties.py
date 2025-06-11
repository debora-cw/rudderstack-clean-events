import json
from collections import defaultdict, Counter
import re

class PropertyCategorizer:
    def __init__(self):
        self.categories = {
            # ESSENCIAIS - NÃO REMOVER
            'essential_tracking': {
                'description': 'Propriedades essenciais para funcionamento do RudderStack',
                'patterns': ['messageId', 'rudderId', 'type', 'event', 'userId', 'anonymousId', 'channel'],
                'action': 'MANTER',
                'priority': 'ESSENCIAL'
            },

            'essential_timestamps': {
                'description': 'Timestamps essenciais para análise temporal',
                'patterns': ['sentAt', 'originalTimestamp', 'receivedAt', 'timestamp'],
                'action': 'MANTER',
                'priority': 'ESSENCIAL'
            },

            # CONTEXTO ÚTIL - AVALIAR
            'context_app': {
                'description': 'Informações sobre o aplicativo',
                'patterns': ['context.app.', 'context.library.'],
                'action': 'AVALIAR',
                'priority': 'ÚTIL'
            },

            'context_device': {
                'description': 'Informações sobre dispositivo e sistema',
                'patterns': ['context.os.', 'context.device.', 'context.screen.', 'context.network.'],
                'action': 'AVALIAR',
                'priority': 'ÚTIL'
            },

            'context_location': {
                'description': 'Informações de localização e idioma',
                'patterns': ['context.locale', 'context.timezone', 'context.ip'],
                'action': 'AVALIAR',
                'priority': 'ÚTIL'
            },

            # DADOS PESSOAIS - CRÍTICO
            'personal_data_critical': {
                'description': 'Dados pessoais sensíveis (LGPD/GDPR)',
                'patterns': ['email', 'phone', 'cpf', 'cnpj', 'document', 'password'],
                'action': 'REMOVER_URGENTE',
                'priority': 'CRÍTICO'
            },

            'personal_data_address': {
                'description': 'Dados de endereço e localização',
                'patterns': ['cep', 'address', 'street', 'city', 'state', 'country', 'zipcode', 'postal'],
                'action': 'REMOVER_RECOMENDADO',
                'priority': 'ALTO'
            },

            'personal_data_location': {
                'description': 'Coordenadas GPS e localização precisa',
                'patterns': ['latitude', 'longitude', 'location', 'geolocation', 'coordinates'],
                'action': 'REMOVER_RECOMENDADO',
                'priority': 'ALTO'
            },

            # DADOS TÉCNICOS - LIMPAR
            'technical_debug': {
                'description': 'Dados de debug e desenvolvimento',
                'patterns': ['debug', 'test', 'dev', 'staging', 'temp', 'tmp'],
                'action': 'REMOVER_OPCIONAL',
                'priority': 'MÉDIO'
            },

            'technical_deprecated': {
                'description': 'Propriedades antigas ou depreciadas',
                'patterns': ['old_', 'legacy_', 'deprecated_', '_old', '_legacy', 'unused_'],
                'action': 'REMOVER_RECOMENDADO',
                'priority': 'ALTO'
            },

            'technical_internal': {
                'description': 'IDs internos e dados técnicos desnecessários',
                'patterns': ['internal_', 'system_', 'db_', 'row_id', '_id', 'fingerprint'],
                'action': 'REMOVER_OPCIONAL',
                'priority': 'MÉDIO'
            },

            # INTEGRAÇÃO - AVALIAR
            'integration_data': {
                'description': 'Dados específicos de integrações',
                'patterns': ['integrations.', 'facebook', 'google', 'amplitude', 'mixpanel'],
                'action': 'AVALIAR',
                'priority': 'ÚTIL'
            },

            # ERROS - LIMPAR
            'error_data': {
                'description': 'Dados de erro e exceções',
                'patterns': ['error', 'exception', 'stack', 'trace'],
                'action': 'REMOVER_OPCIONAL',
                'priority': 'MÉDIO'
            },

            # BUSINESS DATA - MANTER
            'business_data': {
                'description': 'Dados de negócio importantes',
                'patterns': ['properties.', 'traits.', 'revenue', 'price', 'product', 'order'],
                'action': 'AVALIAR_NEGÓCIO',
                'priority': 'IMPORTANTE'
            }
        }

    def categorize_property(self, property_name):
        """Categoriza uma propriedade baseada nos padrões definidos"""
        prop_lower = property_name.lower()

        # Verificar cada categoria
        for category_name, category_info in self.categories.items():
            for pattern in category_info['patterns']:
                if pattern.lower() in prop_lower:
                    return category_name, category_info

        # Se não encontrou categoria específica
        return 'uncategorized', {
            'description': 'Propriedade não categorizada',
            'action': 'REVISAR_MANUAL',
            'priority': 'BAIXO'
        }

    def analyze_properties(self, analysis_data):
        """Analisa e categoriza todas as propriedades"""

        # Obter propriedades do top_properties
        top_properties = analysis_data.get('top_properties', {})

        categorized = defaultdict(list)
        category_stats = defaultdict(lambda: {'count': 0, 'total_occurrences': 0})

        print("CATEGORIZANDO PROPRIEDADES...")
        print("=" * 60)

        for prop_name, occurrences in top_properties.items():
            category_name, category_info = self.categorize_property(prop_name)

            categorized[category_name].append({
                'property': prop_name,
                'occurrences': occurrences,
                'action': category_info['action'],
                'priority': category_info['priority'],
                'description': category_info['description']
            })

            category_stats[category_name]['count'] += 1
            category_stats[category_name]['total_occurrences'] += occurrences

        return categorized, category_stats

    def generate_recommendations(self, categorized, category_stats):
        """Gera recomendações baseadas na categorização"""

        recommendations = {
            'immediate_action': [],
            'high_priority': [],
            'medium_priority': [],
            'review_needed': [],
            'keep_essential': []
        }

        for category_name, properties in categorized.items():
            category_info = self.categories.get(category_name, {})
            action = category_info.get('action', 'REVISAR_MANUAL')
            priority = category_info.get('priority', 'BAIXO')

            if action == 'REMOVER_URGENTE':
                recommendations['immediate_action'].extend(properties)
            elif action == 'REMOVER_RECOMENDADO':
                recommendations['high_priority'].extend(properties)
            elif action == 'REMOVER_OPCIONAL':
                recommendations['medium_priority'].extend(properties)
            elif action in ['AVALIAR', 'AVALIAR_NEGÓCIO', 'REVISAR_MANUAL']:
                recommendations['review_needed'].extend(properties)
            elif action == 'MANTER':
                recommendations['keep_essential'].extend(properties)

        return recommendations

    def print_analysis_report(self, categorized, category_stats, recommendations):
        """Imprime relatório detalhado da análise"""

        print("\n" + "="*80)
        print("RELATÓRIO DE CATEGORIZAÇÃO DE PROPRIEDADES")
        print("="*80)

        # Resumo por categoria
        print(f"\nRESUMO POR CATEGORIA:")
        print("-" * 50)

        # Ordenar categorias por prioridade
        priority_order = {'CRÍTICO': 1, 'ALTO': 2, 'IMPORTANTE': 3, 'ÚTIL': 4, 'MÉDIO': 5, 'BAIXO': 6, 'ESSENCIAL': 0}

        sorted_categories = sorted(categorized.items(),
                                 key=lambda x: priority_order.get(
                                     self.categories.get(x[0], {}).get('priority', 'BAIXO'), 6))

        for category_name, properties in sorted_categories:
            category_info = self.categories.get(category_name, {})
            stats = category_stats[category_name]

            print(f"\n[{category_name.upper().replace('_', ' ')}]")
            print(f"   Descrição: {category_info.get('description', 'N/A')}")
            print(f"   Prioridade: {category_info.get('priority', 'N/A')}")
            print(f"   Ação: {category_info.get('action', 'N/A')}")
            print(f"   Propriedades: {stats['count']} ({stats['total_occurrences']:,} ocorrências)")

            # Mostrar top 5 propriedades da categoria
            top_props = sorted(properties, key=lambda x: x['occurrences'], reverse=True)[:5]
            for prop in top_props:
                print(f"     - {prop['property']} ({prop['occurrences']:,}x)")

            if len(properties) > 5:
                print(f"     ... e mais {len(properties) - 5} propriedades")

        # Recomendações de ação
        print(f"\nRECOMENDAÇÕES DE AÇÃO:")
        print("-" * 50)

        if recommendations['immediate_action']:
            print(f"\n[AÇÃO IMEDIATA - CRÍTICO] - {len(recommendations['immediate_action'])} propriedades")
            print("   Dados pessoais sensíveis que DEVEM ser removidos por compliance:")
            for prop in recommendations['immediate_action'][:10]:
                print(f"     REMOVER: {prop['property']} ({prop['occurrences']:,}x)")

        if recommendations['high_priority']:
            print(f"\n[ALTA PRIORIDADE] - {len(recommendations['high_priority'])} propriedades")
            print("   Propriedades que devem ser removidas ou generalizadas:")
            for prop in recommendations['high_priority'][:10]:
                print(f"     AVALIAR: {prop['property']} ({prop['occurrences']:,}x)")

        if recommendations['medium_priority']:
            print(f"\n[MÉDIA PRIORIDADE] - {len(recommendations['medium_priority'])} propriedades")
            print("   Propriedades que podem ser removidas para otimização:")
            for prop in recommendations['medium_priority'][:10]:
                print(f"     OPCIONAL: {prop['property']} ({prop['occurrences']:,}x)")

        if recommendations['review_needed']:
            print(f"\n[REVISÃO NECESSÁRIA] - {len(recommendations['review_needed'])} propriedades")
            print("   Propriedades que precisam de análise de negócio:")
            for prop in recommendations['review_needed'][:10]:
                print(f"     REVISAR: {prop['property']} ({prop['occurrences']:,}x)")

        if recommendations['keep_essential']:
            print(f"\n[MANTER - ESSENCIAL] - {len(recommendations['keep_essential'])} propriedades")
            print("   Propriedades essenciais que NÃO devem ser removidas:")
            for prop in recommendations['keep_essential'][:10]:
                print(f"     MANTER: {prop['property']} ({prop['occurrences']:,}x)")

    def save_detailed_report(self, categorized, category_stats, recommendations):
        """Salva relatório detalhado em arquivo JSON"""

        report = {
            'timestamp': '2025-06-10T16:50:00',
            'summary': {
                'total_categories': len(categorized),
                'total_properties_analyzed': sum(len(props) for props in categorized.values()),
                'immediate_action_needed': len(recommendations['immediate_action']),
                'high_priority': len(recommendations['high_priority']),
                'medium_priority': len(recommendations['medium_priority']),
                'review_needed': len(recommendations['review_needed']),
                'keep_essential': len(recommendations['keep_essential'])
            },
            'categories': {},
            'recommendations': recommendations
        }

        # Adicionar detalhes das categorias
        for category_name, properties in categorized.items():
            category_info = self.categories.get(category_name, {})
            report['categories'][category_name] = {
                'description': category_info.get('description', ''),
                'action': category_info.get('action', ''),
                'priority': category_info.get('priority', ''),
                'stats': dict(category_stats[category_name]),
                'properties': properties
            }

        with open('property_categorization_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\nRelatório detalhado salvo em 'property_categorization_report.json'")

def main():
    print("ANÁLISE E CATEGORIZAÇÃO DE PROPRIEDADES")
    print("=" * 60)

    # Carregar dados da análise
    try:
        with open('event_audit_analysis.json', 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
    except FileNotFoundError:
        print("Erro: Arquivo 'event_audit_analysis.json' não encontrado!")
        print("Execute primeiro: python analyze_events_properties.py")
        return

    # Inicializar categorizador
    categorizer = PropertyCategorizer()

    # Analisar e categorizar propriedades
    categorized, category_stats = categorizer.analyze_properties(analysis_data)

    # Gerar recomendações
    recommendations = categorizer.generate_recommendations(categorized, category_stats)

    # Imprimir relatório
    categorizer.print_analysis_report(categorized, category_stats, recommendations)

    # Salvar relatório detalhado
    categorizer.save_detailed_report(categorized, category_stats, recommendations)

    print(f"\nPRÓXIMOS PASSOS RECOMENDADOS:")
    print("1. Revisar propriedades críticas e implementar remoção urgente")
    print("2. Analisar propriedades de alta prioridade com time de negócio")
    print("3. Planejar remoção gradual das propriedades de média prioridade")
    print("4. Criar rotina de monitoramento para novas propriedades suspeitas")

if __name__ == "__main__":
    main() 