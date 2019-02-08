from keras.applications import ResNet50
from keras.preprocessing.image import img_to_array
from keras.applications import imagenet_utils
from PIL import Image
import numpy as np
import flask
import io
import tensorflow as tf

app = flask.Flask(__name__)
model = None

def load_model():
    global model
    model = ResNet50(weights="imagenet")
    global graph
    graph = tf.get_default_graph()

def prepare_image(image,target):
    if image.mode!="RGB":
        image = image.convert("RGB")
    
    # resize the input image and preprocess it
    image = image.resize(target)
    image = img_to_array(image)
    image = np.expand_dims(image,axis=0)
    image = imagenet_utils.preprocess_input(image)

    return image

@app.route("/predict",methods=["POST"])
def predict():
    data = {"success":False}
    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            image = flask.request.files["image"].read()
            image = Image.open(io.BytesIO(image))
            image = prepare_image(image,target=(224,224))

            with graph.as_default():
                preds = model.predict(image)
                results = imagenet_utils.decode_predictions(preds)
                data["predictions"] = []

                for (imagenetID,label,prob) in results[0]:
                    r = {"label":label,"probability":float(prob)}
                    data["predictions"].append(r)
                
                data["Success"] = True
            
    return flask.jsonify(data)

if __name__ == "__main__":
    print(("* Loading Keras model and Flask starting server..."
		"please wait until server has fully started"))
    load_model()
    app.run(host='0.0.0.0',debug=False)