from flask import Flask, request, jsonify
from importlib.resources import path
from google.cloud import vision
import requests, json, os, io, openai

app = Flask(__name__)

# Load the credentials from the json file
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'macro-outpost-393714-a5aaeaa4013e.json'

openai.api_key = "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"

# Authenticate client
client = vision.ImageAnnotatorClient()

# Prepare image
def prepare_image(image_path):
    try:
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        return image
    except Exception as e:
        print(e)
        return None

# Object detection
def detect_object_name(image_path):
    image = prepare_image(image_path)
    objects = client.object_localization(image=image).localized_object_annotations
    if objects:
        result = []
        for object_ in objects:
            result.append(object_.name)
        return result
    else:
        return None

# Generate the output
def generate_recycling_response(object_name):
    URL = "https://api.openai.com/v1/chat/completions"

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": f"Summarize in 50 words the best way to recycle {object_name}?"}],
        "temperature" : 1.0,
        "top_p": 1.0,
        "n" : 1,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 0,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    response = requests.post(URL, headers=headers, json=payload, stream=False)

    # Check if the response status code is 200 (OK)
    if response.status_code == 200:
        # Parse the response JSON
        parsed_response = json.loads(response.text)

        # Extract and beautify the content
        content = parsed_response['choices'][0]['message']['content']
        beautified_response = content.replace("\n\n", "\n")

        return beautified_response
    else:
        return f"Error: Kindly retake the picture."
    
@app.route('/')
def home():
    return 'Hello, this is the root URL!'


@app.route('/detect_recycle', methods=['POST'])
def detect_recycle():
    try:
        # Get the image from the request
        image = request.files.get('image')

        if not image:
            return jsonify({'error': 'No image file provided'})

        # Save the image to a temporary file
        image_path = 'temp_image.jpg'
        image.save(image_path)

        # Detect object name
        object_name = detect_object_name(image_path)

        if object_name:
            object_name = object_name[0]
            # Generate recycling response
            recycling_response = generate_recycling_response(object_name)

            # Delete the temporary image file
            os.remove(image_path)

            return jsonify({'object_name': object_name, 'recycling_response': recycling_response})

        else:
            return jsonify({'error': 'No object detected in the image'})

    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
