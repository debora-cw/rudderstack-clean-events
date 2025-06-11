import requests
import json
import os
from datetime import datetime, timedelta

# Tenta carregar o arquivo .env se disponível
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("💡 Dica: Instale python-dotenv para carregar automaticamente o arquivo .env")
    print("   pip install python-dotenv")

class RudderStackAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.rudderstack.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def get_transformations(self):
        """
        Obtém todas as transformações configuradas
        """
        url = f"{self.base_url}/v2/transformations"

        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erro ao obter transformações: {response.status_code}")
                print(f"Resposta: {response.text}")
                return None

        except Exception as e:
            print(f"Erro na requisição: {str(e)}")
            return None

    def get_source_details(self, source_id):
        """
        Obtém detalhes específicos de uma source
        """
        url = f"{self.base_url}/v2/sources/{source_id}"

        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erro ao obter detalhes da source: {response.status_code}")
                return None

        except Exception as e:
            print(f"Erro na requisição: {str(e)}")
            return None

    def get_destination_details(self, destination_id):
        """
        Obtém detalhes específicos de uma destination
        """
        url = f"{self.base_url}/v2/destinations/{destination_id}"

        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erro ao obter detalhes da destination: {response.status_code}")
                return None

        except Exception as e:
            print(f"Erro na requisição: {str(e)}")
            return None

    def get_connections(self):
        """
        Obtém todas as conexões (source -> destination)
        """
        url = f"{self.base_url}/v2/connections"

        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erro ao obter conexões: {response.status_code}")
                print(f"Resposta: {response.text}")
                return None

        except Exception as e:
            print(f"Erro na requisição: {str(e)}")
            return None

def main():
    print("Explorando Conexões e Transformações do RudderStack")
    print("=" * 70)

    # Carrega a API key do arquivo de ambiente
    API_KEY = os.getenv('RUDDERSTACK_API_KEY')
    
    if not API_KEY:
        print("❌ Erro: RUDDERSTACK_API_KEY não encontrada nas variáveis de ambiente")
        print("Por favor, configure a variável de ambiente RUDDERSTACK_API_KEY")
        return
    
    api = RudderStackAPI(API_KEY)

    # 1. Obter transformações
    print("\nObtendo Transformações...")
    transformations = api.get_transformations()

    if transformations:
        if 'transformations' in transformations:
            trans_list = transformations['transformations']
            print(f"Encontradas {len(trans_list)} transformações")

            for i, trans in enumerate(trans_list[:5]):  # Primeiras 5
                print(f"\n{i+1}. {trans.get('name', 'N/A')}")
                print(f"   ID: {trans.get('id', 'N/A')}")
                print(f"   Linguagem: {trans.get('language', 'N/A')}")
                print(f"   Ativo: {'✅' if trans.get('enabled', False) else '❌'}")
                print(f"   Criado em: {trans.get('createdAt', 'N/A')}")
        else:
            print("✅ Requisição bem-sucedida, mas nenhuma transformação encontrada")

    # 2. Obter conexões
    print(f"\n{'='*70}")
    print("🔗 Obtendo Conexões (Source -> Destination)...")
    connections = api.get_connections()

    if connections:
        if 'connections' in connections:
            conn_list = connections['connections']
            print(f"Encontradas {len(conn_list)} conexões")

            # Agrupar por source
            source_connections = {}
            for conn in conn_list:
                source_id = conn.get('sourceId', 'N/A')
                if source_id not in source_connections:
                    source_connections[source_id] = []
                source_connections[source_id].append(conn)

            print(f"\nResumo das Conexões:")
            print(f"   Sources com conexões: {len(source_connections)}")

            # Mostrar detalhes das primeiras conexões
            print(f"\nDETALHES DAS PRIMEIRAS 10 CONEXÕES:")
            for i, conn in enumerate(conn_list[:10]):
                print(f"\n{i+1}. Source: {conn.get('sourceName', 'N/A')}")
                print(f"   -> Destination: {conn.get('destinationName', 'N/A')}")
                print(f"   Source ID: {conn.get('sourceId', 'N/A')}")
                print(f"   Destination ID: {conn.get('destinationId', 'N/A')}")
                print(f"   Ativo: {'✅' if conn.get('enabled', False) else '❌'}")

                # Verificar se tem transformações aplicadas
                if 'transformations' in conn and conn['transformations']:
                    print(f"   Transformações aplicadas: {len(conn['transformations'])}")
                    for trans in conn['transformations'][:2]:  # Primeiras 2
                        print(f"     - {trans.get('name', 'N/A')}")
        else:
            print("Requisição bem-sucedida, mas nenhuma conexão encontrada")

    # 3. Analisar uma source específica em detalhes
    print(f"\n{'='*70}")
    print("Analisando Source Específica: 'Production - Mobile'")

    # ID da source Production - Mobile (do resultado anterior)
    mobile_source_id = "2IY4hAaD9ErVZd2qBuR0gQEF0nD"
    source_details = api.get_source_details(mobile_source_id)

    if source_details:
        print("Detalhes da Source 'Production - Mobile':")
        print(f"   Nome: {source_details.get('name', 'N/A')}")
        print(f"   Tipo: {source_details.get('sourceDefinition', {}).get('name', 'N/A')}")
        print(f"   Write Key: {source_details.get('writeKey', 'N/A')[:20]}...")
        print(f"   Ativo: {'✅' if source_details.get('enabled', False) else '❌'}")

        # Verificar configurações específicas
        config = source_details.get('config', {})
        if config:
            print("   Configurações:")
            for key, value in list(config.items())[:5]:  # Primeiras 5 configurações
                print(f"     {key}: {str(value)[:50]}...")

    print(f"\n{'='*70}")
    print("Análise concluída!")
    print("\n Insights importantes:")
    print("   1. Você tem uma infraestrutura robusta com muitas sources e destinations")
    print("   2. Ambiente bem organizado (Production, Staging, Dev)")
    print("   3. Múltiplas integrações com Amplitude para analytics")
    print("   4. Uso de Kafka para streaming de dados")
    print("   5. Transformações disponíveis para processamento de dados")

if __name__ == "__main__":
    main() 