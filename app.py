'''

Project Orzo

Flask Python app to create stories and corresponding media.

For authentication, I'm using personal account ADC.
So run command 'gcloud auth application-default login' on machine to generate credentials file.

Other useful notes:
 - if running from local, don't forget to run ". venv/bin/activate" at file level above story_generator
 - don't forget to enable text-to-speech API
 - run application by running 'flask run'


'''

import os
import openai
from flask import Flask, redirect, render_template, request, url_for
from google.cloud import texttospeech

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":

        # Generate story
        name = request.form["name"]
        emotion = request.form["emotion"]
        response_story = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(name, emotion),
            temperature=0.6,
            max_tokens=500,)
        story_text = response_story.choices[0].text

        # Generate image description
        response_image_description = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_image_description(story_text),
            temperature=0.6,
            max_tokens=500,)
        response_image_description_text = response_image_description.choices[0].text

        # Generate image
        #image_url = generate_image(response_image_description_text, emotion)
        image_url = 'https://media.sproutsocial.com/uploads/2017/02/10x-featured-social-media-image-size.png'

        # Generate audio file
        story_audio = generate_speech(story_text)

        return redirect(url_for("index", result=story_text, image_url=image_url, audio_url=story_audio))

    result = request.args.get("result")
    image_url = request.args.get("image_url")
    story_audio = request.args.get("story_audio")
    return render_template("index.html", result=result, image_url=image_url, audio_url=story_audio)

def name_validator(name):
    # trim name input to only 5 words or 50 characters (whichever is less)
    # advanced validation can be added later
    if len(str(name)) > 50:
        name = str(name)[:50]
    else:
        name = ' '.join(str(name).split()[:5])
    return name

def generate_prompt(name, emotion):
    return f"Write a 3 sentence {emotion} story about a main character called {name.capitalize()}."

def generate_image_description(story):
    return f"Here is a short story- {story}. \nBriefly describe a moment in time from this story. The moment chosen " \
           f"should make for a good visual image. The description should be only one line and descriptive enough " \
           f"to create an image."

def generate_image(scene_description, emotion):
    response = openai.Image.create(
        prompt=f'Draw a picture using the following description of a scene from a {emotion} story- {scene_description}',
        n=1,
        size="256x256"
    )
    return response['data'][0]['url']

def generate_speech(story, project_id="data-playground-357315"):

    # Set the environment variable to specify the project ID
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id

    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=story)

    # Build the voice request, select the language code ("en-US") and the ssml voice gender ("neutral")
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-GB",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request on the text input
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    # The response's audio_content is binary.
    with open("static/story_audio.mp3", "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print('Audio content written to file "static/story_audio.mp3"')

    return "static/story_audio.mp3"
