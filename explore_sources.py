import requests
import json
from datetime import datetime

class RudderStackAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.rudderstack.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def get_sources_detailed(self):
        """
        Obtém informações detalhadas de todas as sources
        """
        url = f"{self.base_url}/v2/sources"

        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erro ao obter sources: {response.status_code}")
                print(f"Resposta: {response.text}")
                return None

        except Exception as e:
            print(f"Erro na requisição: {str(e)}")
            return None

    def get_source_by_id(self, source_id):
        """
        Obtém informações detalhadas de uma source específica
        """
        url = f"{self.base_url}/v2/sources/{source_id}"

        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erro ao obter source {source_id}: {response.status_code}")
                return None

        except Exception as e:
            print(f"Erro na requisição: {str(e)}")
            return None

    def get_destinations(self):
        """
        Obtém todas as destinations configuradas
        """
        url = f"{self.base_url}/v2/destinations"

        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erro ao obter destinations: {response.status_code}")
                return None

        except Exception as e:
            print(f"Erro na requisição: {str(e)}")
            return None

def main():
    print("Explorando Sources do RudderStack em Detalhes")
    print("=" * 60)

    API_KEY = "2yHrYtvoMRiQs4nsZ0MrqHrJtsi"
    api = RudderStackAPI(API_KEY)

    # 1. Obter todas as sources
    print("\nObtendo informações detalhadas das Sources...")
    sources_data = api.get_sources_detailed()

    if sources_data and 'sources' in sources_data:
        sources = sources_data['sources']
        print(f"Total de {len(sources)} sources encontradas\n")

        # Categorizar sources por tipo
        source_types = {}
        for source in sources:
            source_def = source.get('sourceDefinition', {})
            source_type = source_def.get('name', 'Desconhecido')

            if source_type not in source_types:
                source_types[source_type] = []
            source_types[source_type].append(source)

        print("Sources por Tipo:")
        for source_type, type_sources in source_types.items():
            print(f"   {source_type}: {len(type_sources)} sources")

        print("\n" + "="*60)
        print("DETALHES DAS PRIMEIRAS 10 SOURCES:")
        print("="*60)

        for i, source in enumerate(sources[:10]):
            print(f"\n{i+1}. {source.get('name', 'N/A')}")
            print(f"   ID: {source.get('id', 'N/A')}")
            print(f"   Tipo: {source.get('sourceDefinition', {}).get('name', 'N/A')}")
            print(f"   Ativo: {'✅' if source.get('enabled', False) else '❌'}")
            print(f"   Criado em: {source.get('createdAt', 'N/A')}")

            # Verificar se tem destinations conectadas
            destinations = source.get('destinations', [])
            if destinations:
                print(f"   Destinations conectadas: {len(destinations)}")
                for dest in destinations[:3]:  # Mostrar apenas as 3 primeiras
                    dest_name = dest.get('name', 'N/A')
                    dest_type = dest.get('destinationDefinition', {}).get('name', 'N/A')
                    print(f"     - {dest_name} ({dest_type})")
            else:
                print("   Destinations conectadas: 0")

    # 2. Obter destinations
    print(f"\n{'='*60}")
    print("Obtendo Destinations...")
    destinations_data = api.get_destinations()

    if destinations_data and 'destinations' in destinations_data:
        destinations = destinations_data['destinations']
        print(f"Total de {len(destinations)} destinations encontradas")

        # Categorizar destinations por tipo
        dest_types = {}
        for dest in destinations:
            dest_def = dest.get('destinationDefinition', {})
            dest_type = dest_def.get('name', 'Desconhecido')

            if dest_type not in dest_types:
                dest_types[dest_type] = []
            dest_types[dest_type].append(dest)

        print("\nDestinations por Tipo:")
        for dest_type, type_dests in dest_types.items():
            print(f"   {dest_type}: {len(type_dests)} destinations")

        print(f"\n🔍 PRIMEIRAS 5 DESTINATIONS:")
        for i, dest in enumerate(destinations[:5]):
            print(f"\n{i+1}. {dest.get('name', 'N/A')}")
            print(f"   Tipo: {dest.get('destinationDefinition', {}).get('name', 'N/A')}")
            print(f"   Ativo: {'✅' if dest.get('enabled', False) else '❌'}")

    print(f"\n{'='*60}")
    print("Exploração concluída!")
    print("Próximos passos sugeridos:")
    print("   1. Escolher uma source específica para analisar eventos")
    print("   2. Verificar transformações aplicadas")
    print("   3. Analisar fluxo de dados entre sources e destinations")

if __name__ == "__main__":
    main() 