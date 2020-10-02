import requests
from pyDes import *
import base64
from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def index():
    return "<h>Welcome to songs</h>"

@app.route("/api/", methods=['GET'])
def api():
    song_name = request.args.get('s')
    des_cipher = des(b"38346591", ECB, b"\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
    search_base_url = "https://www.jiosaavn.com/api.php?__call=autocomplete.get&_format=json&_marker=0&cc=in&includeMetaTags=1&query="
    song_details_base_url = "https://www.jiosaavn.com/api.php?__call=song.getDetails&cc=in&_marker=0%3F_marker%3D0&_format=json&pids="
    url = search_base_url + song_name
    song = requests.get(url).json()
    pid = []
    urls = []
    for i in range(len(song["albums"]["data"])):
        pid = (song["albums"]["data"][i]["more_info"]["song_pids"])
        pid_sep = pid.split(", ")
        url2 = song_details_base_url + pid_sep[0]
        song_info = requests.get(url2).json()
        encrypted_url = song_info[pid_sep[0]]["encrypted_media_url"]
        enc_url = base64.b64decode(encrypted_url.strip())
        dec_url = des_cipher.decrypt(enc_url, padmode=PAD_PKCS5).decode('utf-8')
        urls.append(dec_url)
    songs_list = {}
    for i in range(len(song["albums"]["data"])):
        songs_list["song" + str(i + 1)] = {"Title": song["albums"]["data"][i]["title"],
                                           "Image": song["albums"]["data"][i]["image"],
                                           "Artist": song["albums"]["data"][i]["music"],
                                           "Description": song["albums"]["data"][i]["description"],
                                           "URL": urls[i]}
    return f"<code>{songs_list}</code>"

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5000, use_reloader=True, threaded=True)
