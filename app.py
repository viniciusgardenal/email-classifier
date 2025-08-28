from flask import Flask, request, jsonify, render_template
from transformers import pipeline
import os

app = Flask(__name__)

try:
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    generator = pipeline("text2text-generation", model="google/flan-t5-small")
except Exception as e:
    print(f"Erro ao carregar os modelos: {e}")
    classifier = None
    generator = None

@app.route('/')
def home():
    return render_template('index.html')

# Rota da API para processar o email
@app.route('/process-email', methods=['POST'])
def process_email():
    if not classifier or not generator:
        return jsonify({"error": "Modelos de IA não estão disponíveis."}), 500

    data = request.get_json()
    if 'email_text' not in data or not data['email_text'].strip():
        return jsonify({"error": "O texto do email não pode estar vazio."}), 400

    email_text = data['email_text']
    
    # --- 1. Classificação ---
    candidate_labels = ["Produtivo", "Improdutivo"]
    classification_result = classifier(email_text, candidate_labels)
    top_category = classification_result['labels'][0]
    
    # --- 2. Geração de Resposta ---
    prompt = ""
    if top_category == "Produtivo":
        prompt = f"""INSTRUÇÃO: Com base no email abaixo, escreva uma resposta profissional e curta em português confirmando o recebimento da solicitação e informando que a equipe irá processá-la.

EMAIL ORIGINAL:
---
{email_text[:600]}
---

RESPOSTA SUGERIDA:"""
    else: # Improdutivo
        prompt = f"""INSTRUÇÃO: Com base na mensagem amigável abaixo, escreva uma resposta extremamente curta e cordial em português, como "Obrigado!" ou "Agradecemos a mensagem!".

MENSAGEM ORIGINAL:
---
{email_text[:400]}
---

RESPOSTA SUGERIDA:"""

    generated_text = generator(prompt, max_new_tokens=300, num_return_sequences=1)
    full_output = generated_text[0]['generated_text']

    anchor = "RESPOSTA SUGERIDA:"
    anchor_position = full_output.find(anchor)

    if anchor_position != -1:
        start_of_response = anchor_position + len(anchor)
        suggested_response = full_output[start_of_response:].strip()
    else:
        suggested_response = full_output.strip()

    return jsonify({
        "category": top_category,
        "suggested_response": suggested_response
    })

if __name__ == '__main__':
    # A porta é definida pela variável de ambiente PORT, útil para a hospedagem
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)