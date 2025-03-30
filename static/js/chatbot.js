document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('qa-form');
    const questionInput = document.getElementById('question');
    const responseDiv = document.getElementById('response');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const question = questionInput.value.trim();
        if (!question) return;

        // Show loading state
        responseDiv.innerHTML = '<p>Processing your question...</p>';
        
        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question })
            });

            const data = await response.json();
            
            if (response.ok) {
                responseDiv.innerHTML = `<div class="response">${data.answer}</div>`;
            } else {
                responseDiv.innerHTML = `<div class="error">Error: ${data.error}</div>`;
            }
        } catch (error) {
            responseDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
        }
    });
}); 