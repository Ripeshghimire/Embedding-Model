document.getElementById('pdfForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const pdfFile = document.getElementById('pdfFile').files[0];
    if (!pdfFile) {
        alert('Please upload a PDF file');
        return;
    }

    const formData = new FormData();
    formData.append('pdfFile', pdfFile);

    try {
        const response = await fetch('/pdf', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        alert('PDF uploaded and processed successfully');
    } catch (error) {
        alert('Failed to upload PDF');
        console.error('Error:', error);
    }
});

document.getElementById('queryForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const question = document.getElementById('question').value;
    if (!question) {
        alert('Please enter a question');
        return;
    }

    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });
        const data = await response.json();
        document.getElementById('result').innerText = 'Result: ' + JSON.stringify(data.results);
    } catch (error) {
        alert('Failed to retrieve similar text');
        console.error('Error:', error);
    }
});
