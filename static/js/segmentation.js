document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll(".card");
    const serviceDetails = document.getElementById("service-details");

    cards.forEach(card => {
        card.addEventListener("click", () => {
            const serviceType = card.getAttribute("data-service");
            if (services[serviceType]) {
                serviceDetails.innerHTML = services[serviceType];
                serviceDetails.style.display = "block"; // Show the service details section
            }
        });
    });

    const services = {
        image_conversion: `
            <h2>DICOM to Image Converter</h2>
            <p>This tool converts a folder of DICOM files into standard image formats. Upload your folder and start the conversion process.</p>
            <form action="/service/image_conversion" method="POST" enctype="multipart/form-data">
                <input type="file" name="dicom_file" accept=".dcm,.zip" required>
                <button type="submit">Convert</button>
            </form>
        `,
        segmentation: `
            <h2>Segmentation Service</h2>
            <p>Apply segmentation to a folder of DICOM files, producing processed images.</p>
            <form action="/service/segmentation" method="POST" enctype="multipart/form-data">
                <input type="file" name="dicom_file" accept=".dcm,.zip" required>
                <button type="submit">Segment</button>
            </form>
        `,
        model3D: `
            <h2>3D Model Generator</h2>
            <p>Generate a 3D model from DICOM files and view it in STL format.</p>
            <form action="/service/3d_model" method="POST" enctype="multipart/form-data">
                <input type="file" name="dicom_file" accept=".dcm,.zip" required>
                <button type="submit">Generate</button>
            </form>
        `
    };

    cards.forEach(card => {
        card.addEventListener("click", () => {
            const selectedService = card.dataset.service;
            serviceDetails.innerHTML = services[selectedService];
            serviceDetails.style.display = "block";
        });
    });
});
