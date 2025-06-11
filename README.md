# RudderStack Events Explorer

Este script permite explorar conexões e transformações do RudderStack através da API.

## Configuração

### 1. Instalar dependências
```bash
pip install requests
```

### 2. Configurar variáveis de ambiente

1. Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

2. Edite o arquivo `.env` e adicione sua chave da API do RudderStack:
```
RUDDERSTACK_API_KEY=sua_chave_api_real_aqui
```

### 3. Executar o script

#### Opção 1: Usando arquivo .env (recomendado)
```bash
# Instale python-dotenv se ainda não tiver
pip install python-dotenv

# Execute o script
python get_events_from_source.py
```

#### Opção 2: Definindo a variável diretamente
```bash
export RUDDERSTACK_API_KEY="sua_chave_api_aqui"
python get_events_from_source.py
```

## Segurança

⚠️ **IMPORTANTE**: Nunca commite o arquivo `.env` no repositório! Ele já está incluído no `.gitignore` para sua proteção.

## Funcionalidades

O script explora:
- ✅ Transformações configuradas
- ✅ Conexões entre sources e destinations  
- ✅ Detalhes específicos de sources
- ✅ Análise de configurações 