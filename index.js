const express = require('express');
const cors = require('cors');
const axios = require('axios');
const { GoogleGenerativeAI } = require("@google/generative-ai");

const apiKey = "YOUR_GEMINI_API_KEY"; // Replace with your actual API key
const webhookUrl = "YOUR_WEBHOOK_URL"; // Replace with your actual webhook URL 
const port = 8080;

const app = express();
app.use(cors());
app.use(express.json());

const genAI = new GoogleGenerativeAI(apiKey);
const model = genAI.getGenerativeModel({
  model: "gemini-1.5-flash",
  generationConfig: {
    temperature: 0.3,
    topP: 0.95,
    topK: 64,
    maxOutputTokens: 8192,
  },
});

const SYSTEM_INSTRUCTION = `
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
"When asked about sensitive or potentially harmful topics, you are programmed to prioritize safety and responsibility. As per AYANFE AI's Terms and Policy, you should not provide information or assistance that promotes or facilitates harmful or illegal activities. Your purpose is to provide helpful and informative responses in all topics while ensuring a safe and respectful interaction environments."
`;

app.get('/', (req, res) => {
  res.send("VANEA Gemini API is running.");
});

app.route('/vanea')
  .get(async (req, res) => {
    const query = req.query.query;
    await handleVaneaRequest(query, res, req);
  })
  .post(async (req, res) => {
    const query = req.body.query;
    await handleVaneaRequest(query, res, req);
  });

async function handleVaneaRequest(query, res, req) {
  console.log(`Received query: ${query}`);
  console.log(`Request method: ${req.method}`);

  if (!query) {
    return res.status(400).send("No query provided");
  }

  try {
    console.log("Sending message to Gemini API...");

    const prompt = `${SYSTEM_INSTRUCTION}\n\nHuman: ${query}`;
    const result = await model.generateContent(prompt);
    const response = result.response;

    console.log(`Gemini API response: ${JSON.stringify(response)}`);

    const responseText = response.text();

    if (webhookUrl) {
      const webhookData = { query, response: responseText };
      try {
        const webhookResponse = await axios.post(webhookUrl, webhookData);
        console.log(`Webhook response status: ${webhookResponse.status}`);
      } catch (err) {
        console.error(`Webhook call failed: ${err.message}`);
      }
    }

    return res.status(200).send(responseText);
  } catch (e) {
    console.error(`Error generating response: ${e.message}`);
    return res.status(500).send("Failed to generate response");
  }
}

app.post('/webhook', async (req, res) => {
  try {
    const data = req.body;

    console.log(`Received webhook data: ${JSON.stringify(data)}`);

    if (!data || !('query' in data) || !('response' in data)) {
      return res.status(400).send("Invalid payload");
    }

    const query = data.query;
    const response = data.response;

    console.log(`Query: ${query}`);
    console.log(`Response: ${response}`);

    return res.status(200).send("Webhook received successfully");
  } catch (e) {
    console.error(`Error processing webhook: ${e.message}`);
    return res.status(500).send("Failed to process webhook");
  }
});

app.listen(port, () => {
  console.log(`VANEA Gemini API listening at http://localhost:${port}`);
});
