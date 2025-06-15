# RudderStack Clean Events

Scripts para buscar e excluir propriedades de CEP no RudderStack via API.

## Como usar

1. **Configure sua variável de ambiente:**
   - Copie o arquivo `.env.example` para `.env`:
     ```
     cp .env.example .env
     ```
   - Edite o `.env` e coloque sua chave real:
     ```
     RUDDERSTACK_API_KEY=seu_token_aqui
     ```

2. **Instale as dependências:**
   ```
   pip install -r requirements.txt
   ```

3. **Busque todas as propriedades de CEP:**
   ```
   python fetch_all_cep_properties.py
   ```

4. **Exclua todas as propriedades de CEP:**
   ```
   python delete_properties.py
   ```

## Segurança

- **Nunca suba seu token de API para o repositório!**
- O arquivo `.env` está no `.gitignore` por segurança.