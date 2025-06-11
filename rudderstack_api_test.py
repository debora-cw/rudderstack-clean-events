import requests
import json
from datetime import datetime

class RudderStackAPI:
    def __init__(self, api_key, workspace_id=None):
        self.api_key = api_key
        self.base_url = "https://api.rudderstack.com"
        self.workspace_id = workspace_id
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def get_tracking_plans(self):
        """
        Obtém todos os tracking plans disponíveis
        """
        url = f"{self.base_url}/v2/tracking-plans"

        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                print("Tracking Plans obtidos com sucesso!")
                return response.json()
            else:
                print(f"Erro ao obter tracking plans: {response.status_code}")
                print(f"Resposta: {response.text}")
                return None

        except Exception as e:
            print(f"Erro na requisição: {str(e)}")
            return None

    def get_events_from_tracking_plan(self, tracking_plan_id):
        """
        Obtém eventos de um tracking plan específico
        """
        url = f"{self.base_url}/v2/tracking-plans/{tracking_plan_id}/events"

        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                print(f"Eventos do tracking plan {tracking_plan_id} obtidos com sucesso!")
                return response.json()
            else:
                print(f"Erro ao obter eventos: {response.status_code}")
                print(f"Resposta: {response.text}")
                return None

        except Exception as e:
            print(f"Erro na requisição: {str(e)}")
            return None

    def get_data_catalog_events(self):
        """
        Obtém todos os eventos do catálogo de dados
        """
        url = f"{self.base_url}/v2/catalog/events"

        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                print("Eventos do catálogo obtidos com sucesso!")
                return response.json()
            else:
                print(f"Erro ao obter eventos do catálogo: {response.status_code}")
                print(f"Resposta: {response.text}")
                return None

        except Exception as e:
            print(f"Erro na requisição: {str(e)}")
            return None

    def get_sources(self):
        """
        Obtém todas as sources configuradas
        """
        url = f"{self.base_url}/v2/sources"

        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                print("Sources obtidas com sucesso!")
                return response.json()
            else:
                print(f"Erro ao obter sources: {response.status_code}")
                print(f"Resposta: {response.text}")
                return None

        except Exception as e:
            print(f"Erro na requisição: {str(e)}")
            return None

def main():
    print("🚀 Teste da API RudderStack")
    print("=" * 50)

    # API RudderStack
    API_KEY = "2yHrYtvoMRiQs4nsZ0MrqHrJtsi"  # Sua API key

    # Inicializa a classe da API
    api = RudderStackAPI(API_KEY)

    print("\n1. Obtendo Tracking Plans...")
    tracking_plans = api.get_tracking_plans()
    if tracking_plans:
        print(f"Encontrados {len(tracking_plans.get('trackingPlans', []))} tracking plans")
        for plan in tracking_plans.get('trackingPlans', [])[:3]:  # Mostra apenas os 3 primeiros
            print(f"   - {plan.get('name', 'N/A')} (ID: {plan.get('id', 'N/A')})")

    print("\n2. Obtendo Sources...")
    sources = api.get_sources()
    if sources:
        print(f"Encontradas {len(sources.get('sources', []))} sources")
        for source in sources.get('sources', [])[:3]:  # Mostra apenas as 3 primeiras
            print(f"   - {source.get('name', 'N/A')} (Tipo: {source.get('sourceDefinition', {}).get('name', 'N/A')})")

    print("\n3. Obtendo Eventos do Catálogo...")
    catalog_events = api.get_data_catalog_events()
    if catalog_events:
        events = catalog_events.get('events', [])
        print(f"Encontrados {len(events)} eventos no catálogo")
        for event in events[:5]:  # Mostra apenas os 5 primeiros
            print(f"   - {event.get('name', 'N/A')} (ID: {event.get('id', 'N/A')})")

    # Se tiver tracking plans, pegamos eventos de um deles
    if tracking_plans and tracking_plans.get('trackingPlans'):
        first_plan_id = tracking_plans['trackingPlans'][0].get('id')
        if first_plan_id:
            print(f"\n4. Obtendo eventos do primeiro tracking plan ({first_plan_id})...")
            plan_events = api.get_events_from_tracking_plan(first_plan_id)
            if plan_events:
                events = plan_events.get('events', [])
                print(f"Encontrados {len(events)} eventos no tracking plan")
                for event in events[:3]:  # Mostra apenas os 3 primeiros
                    print(f"   - {event.get('name', 'N/A')}")
                    properties = event.get('properties', {})
                    if properties:
                        print(f"     Propriedades: {list(properties.keys())[:3]}")  # Primeiras 3 propriedades

    print("\n" + "=" * 50)
    print("Teste concluído!")

if __name__ == "__main__":
    main() 