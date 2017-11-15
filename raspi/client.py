#from neopixel import Adafruit_NeoPixel, Color, ws
import urllib
from os.path import dirname, join
from time import sleep

from requests import session

token = open(join(dirname(dirname(__file__)), 'token'), "r").read(-1)


# Main program logic follows:
if __name__ == '__main__':
    '''
    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(240, 18, 800000, 5, False, LED_BRIGHTNESS, 0, 
                              ws.WS2811_STRIP_GRB)
    # Intialize the library (must be called once before other functions).
    strip.begin()
    
    
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
    '''
    base_url = "http://localhost:9999/save"
    _session = session()
    while True:
        response = _session.get(base_url, headers={"token": token})
        assert response.status_code == 200
        url = urllib.unquote(response.text).decode('utf8')
        print(url)
        sleep(10)
