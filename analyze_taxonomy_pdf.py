import pdfplumber
import openai
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
PDF_PATH = "CW-Events and Taxonomy-260625-143644.pdf"

# Função para extrair texto do PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Função para resumir usando OpenAI
def summarize_text_with_openai(text, prompt=None):
    if not OPENAI_API_KEY:
        raise Exception("OPENAI_API_KEY não encontrada nas variáveis de ambiente!")
    openai.api_key = OPENAI_API_KEY
    
    if not prompt:
        prompt = (
            "Você é um especialista em taxonomia de eventos de produto digital. "
            "Resuma o artigo abaixo, focando em explicar qual é o padrão de nomenclatura sugerido para eventos e propriedades. "
            "Se possível, cite exemplos e regras.\n\nARTIGO:\n" + text[:6000]  # Limite de tokens para contexto
        )
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def main():
    print("Lendo PDF...")
    text = extract_text_from_pdf(PDF_PATH)
    print(f"Texto extraído com {len(text)} caracteres. Enviando para OpenAI...")
    resumo = summarize_text_with_openai(text)
    print("\n===== RESUMO DO ARTIGO (PADRÃO DE NOMENCLATURA) =====\n")
    print(resumo)

if __name__ == "__main__":
    main() 