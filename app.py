import os

import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        name = request.form["name"]
        emotion = request.form["emotion"]
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(name, emotion),
            temperature=0.6,
            max_tokens=500,
        )

        image_url = generate_image(response.choices[0].text)

        return redirect(url_for("index", result=response.choices[0].text, image_url=image_url))

    result = request.args.get("result")
    image_url = request.args.get("image_url")
    print('result = ',result)
    return render_template("index.html", result=result, image_url=image_url)


def generate_prompt(name, emotion):
    return f"Write a 3 sentence {emotion} story about a main character called {name.capitalize()}."

def generate_image(story):
    response = openai.Image.create(
        prompt=f'Draw a picture for the following short story- {story}',
        n=1,
        size="256x256"
    )
    return response['data'][0]['url']