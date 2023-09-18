import os

import openai
from flask import Flask, redirect, render_template, request, url_for

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
        print(response_image_description_text)

        # Generate image
        image_url = generate_image(response_image_description_text, emotion)

        return redirect(url_for("index", result=story_text, image_url=image_url))

    result = request.args.get("result")
    image_url = request.args.get("image_url")
    return render_template("index.html", result=result, image_url=image_url)

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
