# interactive-azure-openai-speech-chat

This is a simple example that uses Azure Speech and Azure OpenAI Service to implement a chat-like experience using voice.

Copy `.env.example` to `.env`, and adapt the values:

```dotenv
OPENAI_BASE_URL=https://xxxxxxx.openai.azure.com/ # point to your Azure OpenAI Service URL
OPENAI_API_KEY=xxxxx # fill in your Azure OpenAI Service API key
OPENAI_DEPLOYMENT_NAME=text-davinci-003 # fill in your text-davinci-003 deployment name
SPEECH_API_KEY=xxxx # fill in your Speech API key
SPEECH_REGION=westeurope # adapt to your Speech API Azure region
```

Then install the dependencies and run the script:

```console
pip install -r requirements.txt
python interactive.py
```