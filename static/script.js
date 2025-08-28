document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('email-form');
    const emailTextInput = document.getElementById('email-text');
    const submitBtn = document.getElementById('submit-btn');
    const resultsContainer = document.getElementById('results-container');
    const resultsContent = document.getElementById('results-content');
    const loader = document.getElementById('loader');
    
    const categorySpan = document.getElementById('category');
    const responseDiv = document.getElementById('suggested-response');

    form.addEventListener('submit', async (event) => {
        event.preventDefault(); // Impede o recarregamento da página

        const emailText = emailTextInput.value.trim();
        if (!emailText) {
            alert('Por favor, insira o texto do email.');
            return;
        }

        // Mostra o loader e esconde resultados antigos
        resultsContainer.classList.remove('hidden');
        resultsContent.classList.add('hidden');
        loader.classList.remove('hidden');
        submitBtn.disabled = true;
        submitBtn.innerText = 'Analisando...';

        try {
            const response = await fetch('/process-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email_text: emailText }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Ocorreu um erro no servidor.');
            }

            const data = await response.json();

            // Exibe os resultados
            categorySpan.textContent = data.category;
            responseDiv.textContent = data.suggested_response;
            
            resultsContent.classList.remove('hidden');

        } catch (error) {
            alert(`Erro: ${error.message}`);
            resultsContainer.classList.add('hidden'); // Esconde o container se der erro
        } finally {
            // Esconde o loader e reativa o botão
            loader.classList.add('hidden');
            submitBtn.disabled = false;
            submitBtn.innerText = 'Analisar Email';
        }
    });
});