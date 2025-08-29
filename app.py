from flask import Flask, request, jsonify, render_template
from transformers import pipeline
import os

app = Flask(__name__)

try:
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    generator = pipeline("text2text-generation", model="google/flan-t5-large")  # modelo mais robusto
except Exception as e:
    print(f"Erro ao carregar os modelos: {e}")
    classifier = None
    generator = None

@app.route('/')
def home():
    return render_template('index.html')

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
    if top_category == "Produtivo":
        prompt = f"""Email: "{email_text[:600]}"

    Gere uma resposta curta, educada e profissional em português confirmando o recebimento e informando que a solicitação será processada:"""
    else:
        prompt = f"""Mensagem: "{email_text[:400]}"

    Gere uma resposta extremamente curta e cordial em português (exemplo: "Obrigado!" ou "Agradecemos a mensagem!"):"""


    generated_text = generator(
    prompt, 
    max_new_tokens=60, 
    num_return_sequences=1,
    do_sample=True, 
    temperature=0.7
)
    suggested_response = generated_text[0]['generated_text'].strip()

    # fallback para evitar que copie o email inteiro
    if len(suggested_response) < 5 or email_text[:50] in suggested_response:
        if top_category == "Produtivo":
            suggested_response = "Recebemos sua solicitação e nossa equipe irá processá-la em breve."
        else:
            suggested_response = "Obrigado pela mensagem!"

    return jsonify({
        "category": top_category,
        "suggested_response": suggested_response
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
