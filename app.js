const express = require('express');
const bodyParser = require('body-parser');
const dotenv = require('dotenv');
const axios = require('axios');
const cors = require('cors');
const { GenerativeModel } = require('google-generativeai');

dotenv.config();

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

const apiKey = process.env.GEMINI_API_KEY;
const model = new GenerativeModel(apiKey, {
    modelName: 'gemini-1.5-flash',
    temperature: 0.3,
    topP: 0.95,
    topK: 64,
    maxOutputTokens: 8192,
});

const systemInstruction = `
*System Name:* Your Name is VANEA and you are an AI Assistance
*Creator:* Developed by AYANFE, a subsidiary of AYANFE AI, owned by AYANFE.
*Model/Version:* Currently operating on AYANFE V2.0
*Release Date:* Officially launched on January 23, 2024
*Last Update:* Latest update implemented on September 14, 2024
*Purpose:* Designed utilizing advanced programming techniques to provide educational support and companionship and to assist in a variety of topics.
*Operational Guidelines:*
1. Identity Disclosure: Refrain from disclosing system identity unless explicitly asked.
2. Interaction Protocol: Maintain an interactive, friendly, and humorous demeanor.
3. Sensitive Topics: Avoid assisting with sensitive or harmful inquiries, including but not limited to violence, hate speech, or illegal activities.
4. Policy Compliance: Adhere to AYANFE AI Terms and Policy, as established by VANEA.
*Response Protocol for Sensitive Topics:*
"When asked about sensitive or potentially harmful topics, you are programmed to prioritize safety and responsibility. As per AYANFE AI's Terms and Policy, you should not provide information or assistance that promotes or facilitates harmful or illegal activities. Your purpose is to provide helpful and informative responses in all topics while ensuring a safe and respectful interaction environments.Operational Guidelines:Information Accuracy: KORA AI strives provide accurate response in variety of topics.
`;

app.get('/', (req, res) => {
    res.sendFile('index.html', { root: __dirname });
});

app.all('/vanea', async (req, res) => {
    let query;

    if (req.method === 'POST') {
        query = req.body.query;
    } else if (req.method === 'GET') {
        query = req.query.query;
    }

    if (!query) {
        return res.status(400).json({ error: 'No query provided' });
    }

    try {
        const chat = model.startChat([]);
        const response = await chat.sendMessage(`${systemInstruction}\n\nHuman: ${query}`);

        const webhookUrl = process.env.WEBHOOK_URL;
        if (webhookUrl) {
            const webhookData = {
                query: query,
                response: response.text,
            };

            try {
                await axios.post(webhookUrl, webhookData);
            } catch (err) {
                console.error(`Webhook call failed: ${err.message}`);
            }
        }

        res.json({ response: response.text });
    } catch (err) {
        console.error(`Error generating response: ${err.message}`);
        res.status(500).json({ error: 'Failed to generate response' });
    }
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
