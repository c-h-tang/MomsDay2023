from flask import Flask, jsonify, render_template, request, current_app, send_file
import base64
from PIL import Image
import numpy as np
from scipy.spatial import KDTree
import os

app = Flask(__name__)

# change as necessary
tilesAcross = 200
renderedTileSize = 70
count = 0


@app.route('/', methods=["GET"])
def GET_index():
  '''Route for "/" (frontend)'''
  return render_template("index.html")

@app.route('/makeMosaic', methods=["POST"])
def POST_makeMosaic():
    global tilesAcross
    global renderedTileSize
    global count

    # parse info from app.py
    data = request.files["image"]

    # initialize base image
    base = Image.open(data)
    width, height = base.size

    # determine tile sizes
    baseTileSize = width / tilesAcross
    baseTileFloor = int(baseTileSize)
    baseRemainder = baseTileSize - baseTileFloor

    # determine tilesPerX
    tilesPerRow = tilesAcross
    tilesPerCol = int (height // baseTileSize)

    # determine size of final mosaic
    finalWidth = int(tilesAcross * renderedTileSize)
    finalHeight = int(tilesPerCol * renderedTileSize)

    # crop image height if necessary
    pixels = np.array(base)
    cropped = pixels[:tilesPerCol * baseTileFloor, :]

    # initialize sliding window
    answer1 = Image.new('RGB', (finalWidth, finalHeight))
    botY = 0
    topY = baseTileFloor
    botX = 0
    topX = baseTileFloor

    resBotX = 0
    resTopX = renderedTileSize
    resBotY = 0
    resTopY = renderedTileSize

    # go through all tiles
    tree1 = current_app.tree1
    map1 = current_app.map1
    pics1 = current_app.pics1
    for y in range(tilesPerCol):
        botX = 0
        topX = baseTileFloor
        resBotX = 0
        resTopX = renderedTileSize
        for x in range(tilesPerRow):
            currTile = cropped[botY:topY, botX:topX]
            r = np.mean(currTile[:,:,0])
            g = np.mean(currTile[:,:,1])
            b = np.mean(currTile[:,:,2])
            rgb = (r, g, b)
            if y != tilesPerCol - 1 and x != tilesPerRow - 1 and baseRemainder > 0: # fraction involved
                temp = cropped[botY:topY + 1, botX:topX + 1]
                r2 = np.mean(temp[:,:,0])
                g2 = np.mean(temp[:,:,1])
                b2 = np.mean(temp[:,:,2])
                diff1 = (r2 - r) * baseRemainder
                diff2 = (g2 - g) * baseRemainder
                diff3 = (b2 - b) * baseRemainder
                rgb = (r + diff1, g + diff2, b + diff3)
            index = tree1.query(rgb, k = 1)[1]
            key = map1[pics1[index]]
            region = (int(resBotX), int(resBotY), int(resTopX), int(resTopY))
            answer1.paste(key, region)
            botX = botX + baseTileFloor
            topX = topX + baseTileFloor
            resBotX = resBotX + renderedTileSize
            resTopX = resTopX + renderedTileSize
        botY = botY + baseTileFloor
        topY = topY + baseTileFloor
        resBotY = resBotY + renderedTileSize
        resTopY = resTopY + renderedTileSize

    answer1.save("Mom-Mosaic.png")

    # Example - Prepare a single mosaic response:
    res = []
    with open("Mom-Mosaic.png", "rb") as f:
        buffer = f.read()
    b64 = base64.b64encode(buffer)
    response = {
        "image": "data:image/png;base64," + b64.decode('utf-8')
    }
    res.append(response)
    count = count + 1
    return jsonify(res), 200

@app.before_first_request
def initiate():
    global renderedTileSize
    global tilesAcross

    # process kd-trees
    pokePics = generatePics(renderedTileSize) 
    pics1 = []
    map1 = {}
    for p in pokePics:
        curr = averageRGB(p)
        map1[curr] = p
        pics1.append(curr)

    # insert into kd-trees
    tree1 = KDTree(pics1)
    current_app.tree1 = tree1
    current_app.pics1 = pics1
    current_app.map1 = map1
    return "Pics have been initialized", 200

def averageRGB(image):
  table = np.array(image)
  r = np.mean(table[:,:,0])
  g = np.mean(table[:,:,1])
  b = np.mean(table[:,:,2])
  return (r, g, b)

def generatePics(ts):
  directory = os.getcwd() + "/pictures/"
  allPics = os.listdir(directory)

  images = []
  for pic in allPics:
    path = os.path.join(directory, pic)
    image = Image.open(path)
    resized = image.resize((ts, ts))
    resized = resized.convert("RGB")
    images.append(resized)
  return images

@app.route('/download')
def download():
    if count > 0:
        path = os.getcwd() + '/Mom-Mosaic.png'
        print(path)
        return send_file(path, as_attachment=True)
    return "No mosaic has been created yet\nGo back!", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))