from neopixel import Adafruit_NeoPixel, Color, ws
import urllib
from os.path import dirname, join
from time import sleep
from io import BytesIO
from PIL import Image
from requests import session
from base64 import b64decode

token = open(join(dirname(dirname(__file__)), 'token'), "r").read(-1)

if __name__ == '__main__':
    strip = Adafruit_NeoPixel(240, 18, 800000, 5, False, 3, 0, ws.WS2811_STRIP_GRB)
    strip.begin()
    base_url = "http://localhost:9999/save"
    _session = session()
    while True:
        response = _session.get(base_url, headers={"token": token})
        assert response.status_code == 200
        data = response.text.replace("data:image/png;base64,", "")
        data = b64decode(data)

        fh = open("temp.png", "w")
        fh.write(data)
        fh.close()

        img = Image.open("temp.png")
        img_data = list(img.getdata())
        for i in range(strip.numPixels()):
            color = Color(img_data[i][0], img_data[i][1], img_data[i][2])
            strip.setPixelColor(i, color)
        strip.show()

        sleep(10)
