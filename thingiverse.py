import logging, os, sys, pprint, json, arrow
from flask import Flask, render_template, send_from_directory
app = Flask(__name__)

BASE_PATH="../with_api/thingiverse"
THINGZIP_PATH=os.path.join(BASE_PATH, "files")
THINGJSON_PATH=os.path.join(BASE_PATH, "thing_json")
IMAGEJSON_PATH=os.path.join(BASE_PATH, "image_json")
IMAGE_PATH=os.path.join(BASE_PATH, "images")
THINGCOMMENTSJSON_PATH=os.path.join(BASE_PATH, "thing_comments_json")

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(os.path.basename(__file__))
PP = pprint.PrettyPrinter(indent=4)

@app.route('/')
def index():
    return 'Index Page'

@app.route('/thing/<int:thing>')
def get_thing(thing):
    #_logger.debug('Getting thing {}'.format(thing))
    with open(os.path.join(THINGJSON_PATH, f"{thing}.json"), "r") as thing_json:
        thing_j = json.load(thing_json)
    try:
        with open(os.path.join(IMAGEJSON_PATH, f"{thing}.json"), "r") as image_json:
            images = json.load(image_json)
    except IOError:
        images = {}
    # _logger.debug('thing {}'.format(repr(thing_j)))
    thing_j['added'] = arrow.get(thing_j['added'])
    ppcontent = PP.pformat(thing_j)
    ppimages = PP.pformat(images)
    # Grab image paths for all existing
    images_resolved = []
    for i in images:
        id_ = i['id']
        images_resolved.append(f"/images/{id_}")

    return render_template('thing.html', thing=thing_j, 
                           images=images, images_resolved=images_resolved,
                           ppcontent=ppcontent, ppimages=ppimages)

@app.route('/images/<int:imgid>')
def send_image(imgid):
    exts = ['jpg', 'jpeg', 'gif', 'png']
    img = None
    for e in exts:
        f_name = os.path.join(IMAGE_PATH, f"{imgid}.{e}")
        if os.path.exists(f_name):
            img = f"{imgid}.{e}"
            break
    if img:
        return send_from_directory(IMAGE_PATH, img)

@app.route('/zip/<int:tid>')
def send_zip(tid):
    f_name = os.path.join(THINGZIP_PATH, f"{tid}.zip")
    if os.path.exists(f_name):
        return send_from_directory(THINGZIP_PATH, f"{tid}.zip")
    else:
        return "File not found"
