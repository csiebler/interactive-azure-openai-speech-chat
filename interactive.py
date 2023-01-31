import os
import json
import openai
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

load_dotenv()

language = os.getenv("LOCALE", "de-DE")
speech_voice = os.getenv("SPEECH_VOICE_NAME", "de-DE-AmalaNeural")
include_history = os.getenv("INCLUDE_HISTORY", True)

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base =  os.getenv("OPENAI_BASE_URL")
openai.api_type = 'azure'
openai.api_version = '2022-12-01'

deployment_id=os.getenv("OPENAI_DEPLOYMENT_NAME")

speech_config = speechsdk.SpeechConfig(subscription=os.getenv("SPEECH_API_KEY"),
                                       region=os.getenv("SPEECH_REGION"),
                                       speech_recognition_language=language)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)


audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
speech_config.speech_synthesis_language = language 
speech_config.speech_synthesis_voice_name = speech_voice
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)


def create_answer_with_openai(question):
    prompt = f"{question}. Antworte in einem Satz."
    response = openai.Completion.create(engine=deployment_id, prompt=prompt, max_tokens=250)
    completion = response['choices'][0]['text'].replace('\n', '').replace(' .', '.').strip()
    print(f"OpenAI replied: {completion}")
    return completion

def recognize_speech_once():
    print("Waiting for speech input...")
    result = speech_recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized")
        return "No speech recognized"
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))


def synthesize_speech(text):
    ssml = f"""
<speak version="1.0" xmlns="https://www.w3.org/2001/10/synthesis" xml:lang="en-US">
  <voice name="{speech_voice}">
    <prosody rate="+10.00%">
        {text}
    </prosody>
  </voice>
</speak>
    """
    speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml).get()
    
    # speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
                

history = ""

while (True):
    question = recognize_speech_once()
    if (question.startswith("No speech recognized")):
        continue

    # if question in lowercase starts with "beende die", then exit
    if question.lower().startswith("beende die"):
        synthesize_speech("Ok, bis bald!")
        break
    
    if (include_history):
        history += f"\n\n{question}"
        answer = create_answer_with_openai(history)
        history += f"\n\n{answer}"
        print(f"###\nHISTORY:{history}\n###")
    else:
        answer = create_answer_with_openai(question)

    synthesize_speech(answer)