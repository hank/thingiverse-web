import logging, os, sys, pprint, json, arrow
from flask import Flask, render_template, send_from_directory, abort
app = Flask(__name__)

BASE_PATH="../with_api/thingiverse"
THINGZIP_PATH=os.path.join(BASE_PATH, "files")
THINGJSON_PATH=os.path.join(BASE_PATH, "thing_json")
IMAGEJSON_PATH=os.path.join(BASE_PATH, "image_json")
IMAGE_PATH=os.path.join(BASE_PATH, "images")
AVATAR_PATH=os.path.join(BASE_PATH, "user_avatars")
THINGCOMMENTSJSON_PATH=os.path.join(BASE_PATH, "thing_comments_json")

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(os.path.basename(__file__))
PP = pprint.PrettyPrinter(indent=4)

def _ipath(id_):
    """Makes a path from the input ID. This includes the subdir from the padded
       integer"""
    newfdr = str(id_).zfill(8)[0:4]
    return newfdr

@app.route('/')
def index():
    return 'Index Page'

@app.route('/thing/<int:thing>')
def get_thing(thing):
    #_logger.debug('Getting thing {}'.format(thing))
    try:
        with open(os.path.join(THINGJSON_PATH, _ipath(thing), f"{thing}.json"), "r") as thing_json:
            thing_j = json.load(thing_json)
        # Validate type
        if not isinstance(thing_j, dict):
            f_name = os.path.join(THINGZIP_PATH, _ipath(thing), f"{thing}.zip")
            if os.path.exists(f_name):
                thing_file = f"/zip/{thing}"
            else:
                thing_file = None
            return render_template('404.html', error=133800, message=f"Thing {thing} not valid!", thing_file=thing_file), 404
    except IOError:
        f_name = os.path.join(THINGZIP_PATH, _ipath(thing), f"{thing}.zip")
        if os.path.exists(f_name):
            thing_file = f"/zip/{thing}"
        else:
            thing_file = None
        return render_template('404.html', error=133704, message=f"Thing {thing} not found!", thing_file=thing_file), 404


    try:
        with open(os.path.join(IMAGEJSON_PATH, _ipath(thing), f"{thing}.json"), "r") as image_json:
            images = json.load(image_json)
    except IOError:
        images = {}
    try:
        with open(os.path.join(THINGCOMMENTSJSON_PATH, _ipath(thing), f"{thing}.json"), "r") as comment_json:
            comments = json.load(comment_json)
    except IOError:
        comments = {'comments':[]}
    # _logger.debug('thing {}'.format(repr(thing_j)))
    thing_j['added'] = arrow.get(thing_j['added'])
    ppcontent = PP.pformat(thing_j)
    ppimages = PP.pformat(images)
    ppcomments = PP.pformat(comments)
    # Grab image paths for all existing
    images_resolved = []
    for i in images:
        id_ = i['id']
        images_resolved.append(f"/images/{id_}")

    return render_template('thing.html', thing=thing_j, 
                           images=images, images_resolved=images_resolved,
                           comments=comments,
                           ppcontent=ppcontent, ppimages=ppimages, ppcomments=ppcomments)

@app.route('/images/<int:imgid>')
def send_image(imgid):
    exts = ['jpg', 'jpeg', 'gif', 'png']
    img = None
    for e in exts:
        f_name = os.path.join(IMAGE_PATH, _ipath(imgid), f"{imgid}.{e}")
        if os.path.exists(f_name):
            img = f"{imgid}.{e}"
            break
    if img:
        return send_from_directory(os.path.join(IMAGE_PATH, _ipath(imgid)), img)

@app.route('/avatars/<int:imgid>')
def send_avatar(imgid):
    exts = ['jpg', 'jpeg', 'gif', 'png']
    img = None
    for e in exts:
        f_name = os.path.join(AVATAR_PATH, _ipath(imgid), f"{imgid}.{e}")
        if os.path.exists(f_name):
            img = f"{imgid}.{e}"
            break
    if img:
        return send_from_directory(os.path.join(AVATAR_PATH, _ipath(imgid)), img)
    else:
        abort(404)

@app.route('/zip/<int:tid>')
def send_zip(tid):
    f_name = os.path.join(THINGZIP_PATH, _ipath(tid), f"{tid}.zip")
    if os.path.exists(f_name):
        return send_from_directory(os.path.join(THINGZIP_PATH, _ipath(tid)), f"{tid}.zip")
    else:
        return "File not found"

@app.route('/favicon.ico')
def favicon():
    if os.path.exists("static/favicon.ico"):
        return send_from_directory("static", "favicon.ico")

@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', error=404), 404
