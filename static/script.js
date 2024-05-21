document.addEventListener("DOMContentLoaded", function() {
    const pdfForm = document.getElementById("pdf-form");
    const queryForm = document.getElementById("query-form");
    const resultDiv = document.getElementById("result");

    pdfForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const pdfFile = document.getElementById("pdf-file").files[0];
        const formData = new FormData();
        formData.append("pdfFile", pdfFile);

        try {
            const response = await fetch("/pdf", {
                method: "POST",
                body: formData
            });
            const data = await response.json();
            console.log(data);
        } catch (error) {
            console.error("Error uploading PDF:", error);
        }
    });

    queryForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const query = document.getElementById("query").value;
        try {
            const response = await fetch("/similar_text", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ question: query })
            });
            const data = await response.json();
            resultDiv.textContent = data.result;
        } catch (error) {
            console.error("Error fetching similar text:", error);
        }
    });
});