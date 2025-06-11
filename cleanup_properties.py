import requests
import json
import re
from datetime import datetime
import time

class RudderStackCleanup:
    def __init__(self, api_key, dry_run=True):
        self.api_key = api_key
        self.base_url = "https://api.rudderstack.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.dry_run = dry_run
        self.deleted_count = 0
        self.error_count = 0
    
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
                return None
                
        except Exception as e:
            print(f"❌ Erro na requisição: {str(e)}")
            return None
    
    def delete_property(self, property_id, property_name):
        """
        Deleta uma propriedade específica
        """
        if self.dry_run:
            print(f"🔍 [DRY RUN] Deletaria propriedade: {property_name} (ID: {property_id})")
            return True
        
        url = f"{self.base_url}/v2/catalog/properties/{property_id}"
        
        try:
            response = requests.delete(url, headers=self.headers)
            
            if response.status_code in [200, 204]:
                print(f"✅ Propriedade deletada: {property_name}")
                self.deleted_count += 1
                return True
            else:
                print(f"❌ Erro ao deletar {property_name}: {response.status_code}")
                print(f"   Resposta: {response.text}")
                self.error_count += 1
                return False
                
        except Exception as e:
            print(f"❌ Erro ao deletar {property_name}: {str(e)}")
            self.error_count += 1
            return False
    
    def should_delete_property(self, prop):
        """
        Determina se uma propriedade deve ser deletada baseado em critérios específicos
        """
        prop_name = prop.get('name', '').lower()
        prop_description = prop.get('description', '').lower()
        
        # Critérios para deleção
        delete_reasons = []
        
        # 1. ZIP Codes e códigos postais
        if re.search(r'zip.*code|postal.*code|cep|zipcode', prop_name):
            delete_reasons.append("ZIP_CODE")
        
        # 2. Propriedades com typos óbvios
        typo_patterns = [
            r'adress',      # address
            r'recieve',     # receive  
            r'seperate',    # separate
            r'occured',     # occurred
            r'sucessful',   # successful
            r'lenght',      # length
            r'widht',       # width
            r'heigth',      # height
            r'colum',       # column
            r'tabel',       # table
        ]
        
        for pattern in typo_patterns:
            if re.search(pattern, prop_name):
                delete_reasons.append(f"TYPO_{pattern.upper()}")
        
        # 3. Propriedades temporárias/debug
        temp_patterns = [
            r'test_',
            r'debug_',
            r'temp_',
            r'tmp_',
            r'old_',
            r'deprecated',
            r'_test$',
            r'_debug$',
            r'_temp$',
            r'_tmp$',
            r'_old$'
        ]
        
        for pattern in temp_patterns:
            if re.search(pattern, prop_name):
                delete_reasons.append("TEMPORARY")
        
        # 4. Propriedades com caracteres especiais problemáticos
        if re.search(r'[^\w\s\-_.]', prop_name):
            delete_reasons.append("SPECIAL_CHARS")
        
        # 5. Propriedades muito longas (provavelmente mal nomeadas)
        if len(prop.get('name', '')) > 80:
            delete_reasons.append("TOO_LONG")
        
        # 6. Propriedades duplicadas (mesmo nome com cases diferentes)
        # Este critério seria implementado em uma segunda passada
        
        # 7. Propriedades que parecem ser dados sensíveis que não deveriam estar trackados
        sensitive_patterns = [
            r'password',
            r'ssn',
            r'social.*security',
            r'credit.*card',
            r'bank.*account',
            r'routing.*number'
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, prop_name) or re.search(pattern, prop_description):
                delete_reasons.append("SENSITIVE_DATA")
        
        return delete_reasons
    
    def cleanup_properties(self, confirm_deletion=False):
        """
        Executa a limpeza das propriedades
        """
        print("🧹 Iniciando limpeza de propriedades...")
        print(f"Modo: {'DRY RUN' if self.dry_run else 'EXECUÇÃO REAL'}")
        print("=" * 70)
        
        # Obter todas as propriedades
        properties_data = self.get_all_properties()
        
        if not properties_data or 'properties' not in properties_data:
            print("❌ Não foi possível obter propriedades para limpeza")
            return
        
        properties = properties_data['properties']
        print(f"📊 Analisando {len(properties)} propriedades...")
        
        # Identificar propriedades para deleção
        properties_to_delete = []
        
        for prop in properties:
            delete_reasons = self.should_delete_property(prop)
            
            if delete_reasons:
                properties_to_delete.append({
                    'property': prop,
                    'reasons': delete_reasons
                })
        
        if not properties_to_delete:
            print("✅ Nenhuma propriedade problemática encontrada!")
            return
        
        print(f"\n🚨 Encontradas {len(properties_to_delete)} propriedades para deleção:")
        print("=" * 70)
        
        # Agrupar por motivo
        by_reason = {}
        for item in properties_to_delete:
            for reason in item['reasons']:
                if reason not in by_reason:
                    by_reason[reason] = []
                by_reason[reason].append(item)
        
        # Mostrar resumo por categoria
        reason_descriptions = {
            'ZIP_CODE': '📮 Códigos postais/ZIP codes',
            'TYPO_ADRESS': '🔤 Typo: "adress" → "address"',
            'TYPO_RECIEVE': '🔤 Typo: "recieve" → "receive"',
            'TYPO_SEPERATE': '🔤 Typo: "seperate" → "separate"',
            'TYPO_OCCURED': '🔤 Typo: "occured" → "occurred"',
            'TYPO_SUCESSFUL': '🔤 Typo: "sucessful" → "successful"',
            'TYPO_LENGHT': '🔤 Typo: "lenght" → "length"',
            'TEMPORARY': '🐛 Propriedades temporárias/debug',
            'SPECIAL_CHARS': '🔣 Caracteres especiais problemáticos',
            'TOO_LONG': '📏 Nomes muito longos',
            'SENSITIVE_DATA': '🔒 Dados sensíveis'
        }
        
        for reason, items in by_reason.items():
            print(f"\n{reason_descriptions.get(reason, reason)} ({len(items)} propriedades):")
            
            for item in items[:5]:  # Mostrar apenas as primeiras 5
                prop = item['property']
                print(f"   • {prop.get('name', 'N/A')} (ID: {prop.get('id', 'N/A')[:20]}...)")
            
            if len(items) > 5:
                print(f"     ... e mais {len(items) - 5} propriedades")
        
        # Confirmação para execução real
        if not self.dry_run:
            if not confirm_deletion:
                print(f"\n⚠️  ATENÇÃO: Você está prestes a deletar {len(properties_to_delete)} propriedades!")
                print("Esta ação é IRREVERSÍVEL!")
                
                response = input("\nDeseja continuar? (digite 'CONFIRMO' para prosseguir): ")
                
                if response != 'CONFIRMO':
                    print("❌ Operação cancelada pelo usuário")
                    return
        
        # Executar deleções
        print(f"\n🗑️  Iniciando deleção de {len(properties_to_delete)} propriedades...")
        
        for i, item in enumerate(properties_to_delete):
            prop = item['property']
            prop_name = prop.get('name', 'N/A')
            prop_id = prop.get('id', '')
            reasons = ', '.join(item['reasons'])
            
            print(f"\n[{i+1}/{len(properties_to_delete)}] {prop_name}")
            print(f"   Motivos: {reasons}")
            
            success = self.delete_property(prop_id, prop_name)
            
            if not success and not self.dry_run:
                # Pequena pausa entre tentativas para evitar rate limiting
                time.sleep(0.5)
        
        # Resumo final
        print(f"\n{'='*70}")
        print("📊 RESUMO DA LIMPEZA:")
        print("=" * 70)
        
        if self.dry_run:
            print(f"🔍 [DRY RUN] {len(properties_to_delete)} propriedades seriam deletadas")
        else:
            print(f"✅ Propriedades deletadas com sucesso: {self.deleted_count}")
            print(f"❌ Erros durante deleção: {self.error_count}")
            
            if self.error_count > 0:
                print(f"⚠️  Taxa de sucesso: {(self.deleted_count/(self.deleted_count + self.error_count))*100:.1f}%")

def main():
    print("🧹 Script de Limpeza de Propriedades - RudderStack")
    print("=" * 70)
    
    API_KEY = "2yHrYtvoMRiQs4nsZ0MrqHrJtsi"
    
    # Primeiro, executar em modo DRY RUN
    print("🔍 FASE 1: Análise (Dry Run)")
    print("-" * 40)
    
    cleanup = RudderStackCleanup(API_KEY, dry_run=True)
    cleanup.cleanup_properties()
    
    # Perguntar se quer executar para valer
    print(f"\n{'='*70}")
    print("⚠️  EXECUÇÃO REAL")
    print("=" * 70)
    
    response = input("Deseja executar a limpeza real? (s/N): ").lower()
    
    if response in ['s', 'sim', 'y', 'yes']:
        print("\n🚨 EXECUTANDO LIMPEZA REAL...")
        cleanup_real = RudderStackCleanup(API_KEY, dry_run=False)
        cleanup_real.cleanup_properties(confirm_deletion=False)
    else:
        print("✅ Operação finalizada em modo de análise apenas")

if __name__ == "__main__":
    main() 