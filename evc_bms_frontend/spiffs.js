const URL = "http://192.168.1.4/frontend";
const HTML_PATH = path.resolve("../index.html");

import fs from "fs";
import path from "path";
import FormData from "form-data";

async function uploadFile() {
    if (!fs.existsSync(HTML_PATH)) {
        console.error("File not found: index.html");
        return;
    }

    const formData = new FormData();
    formData.append("data", fs.createReadStream(HTML_PATH));

    try {
        const response = await fetch(URL, {
            method: "POST",
            body: formData,
        });

        const text = await response.text();
        console.log(`Upload response: ${text}`);
    } catch (error) {
        console.error("Error uploading file:", error);
    }
}

uploadFile();

