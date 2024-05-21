document.addEventListener("DOMContentLoaded", () => {
    const pdfUploadForm = document.getElementById("pdf-upload-form");
    const similarityCheckerForm = document.getElementById("similarity-checker-form");dxc

    pdfUploadForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const formData = new FormData();
        const pdfFile = document.getElementById("pdfFile").files[0];
        formData.append("pdfFile", pdfFile);

        const response = await fetch("/pdf", {
            method: "POST",
            body: formData,
        });

        if (response.ok) {
            const result = await response.json();
            document.getElementById("upload-result").innerText = JSON.stringify(result, null, 2);
        } else {
            document.getElementById("upload-result").innerText = "Failed to upload PDF.";
        }     
    });

    similarityCheckerForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const question = document.getElementById("question").value;

        const response = await fetch("/similaritychecker", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ question }),
        });

        if (response.ok) {
            const result = await response.json();
            document.getElementById("similarity-result").innerText = JSON.stringify(result, null, 2);
        } else {
            document.getElementById("similarity-result").innerText = "Failed to check similarity.";
        }
    });
});
