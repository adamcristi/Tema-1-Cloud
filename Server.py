import http.server
from http.server import HTTPServer
from io import BytesIO
import requests
import urllib.request
import base64
import json
from datetime import datetime
import time
from configparser import ConfigParser

PORT = 8080


def get_dogs_images():
    # First request
    first_image_request = requests.get("https://dog.ceo/api/breeds/image/random")
    print(first_image_request.json())
    first_image = first_image_request.json().get('message')
    while (first_image.endswith('.jpg') == False and first_image.endswith('.png') == False) or ' ' in first_image:
        first_image_request = requests.get("https://dog.ceo/api/breeds/image/random")
        print(first_image_request.json())
        first_image = first_image_request.json().get('message')
    # Second request
    second_image_request = requests.get("https://api.thedogapi.com/v1/images/search",
                                        params={'limit': 1, 'mime_types': 'static'},
                                        headers={'x-api-key': cat_dog_x_api_key})
    print(second_image_request.json())
    second_image = second_image_request.json()[0].get('url')

    return first_image, second_image


def get_cats_images():
    # First request
    first_image_request = requests.get("https://api.thecatapi.com/v1/images/search",
                                       params={'limit': 1},
                                       headers={'x-api-key': cat_dog_x_api_key})
    print(first_image_request.json())
    first_image = first_image_request.json()[0].get('url')
    # Second request
    second_image_request = requests.get("https://api.thecatapi.com/v1/images/search",
                                        params={'limit': 1},
                                        headers={'x-api-key': cat_dog_x_api_key})
    print(second_image_request.json())
    second_image = second_image_request.json()[0].get('url')

    return first_image, second_image


def process_request(type):
    first_image = None
    second_image = None
    if type == 'dog':
        first_image, second_image = get_dogs_images()
    elif type == 'cat':
        first_image, second_image = get_cats_images()

    # Third request
    distance_images = 0
    if first_image is not None and second_image is not None:
        difference_request = requests.post("https://api.deepai.org/api/image-similarity",
                                           data={
                                               'image1': first_image,
                                               'image2': second_image,
                                           },
                                           headers={'api-key': similarity_api_key})
        print(difference_request.json())
        distance_images = difference_request.json().get('output').get('distance')

    return first_image, second_image, distance_images


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        elif self.path == '/metrics?' or self.path == '/metrics':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(logging_dicts).encode())

    def do_POST(self):
        log_request = dict()
        log_request["Request Index"] = len(logging_dicts) + 1
        log_request["Request Date"] = datetime.now().strftime("%-d.%B.%Y - %H:%M:%S")
        start_time = time.time()

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = body.decode().split('&')

        first_image, second_image, difference = process_request(type=data[1].split("=")[-1])

        if data[0].split("=")[-1] == 'true':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            first_image_data_request = urllib.request.Request(first_image, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(first_image_data_request) as url:
                first_image_data = BytesIO(url.read())
            second_image_data_request = urllib.request.Request(second_image, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(second_image_data_request) as url:
                second_image_data = BytesIO(url.read())

            if first_image_data is not None and second_image_data is not None and difference is not None:
                response = BytesIO()
                response.write(b'<h3>First image:</h3>')
                response.write(b'<img style="width:500px; height: 500px;" src="data:image/jpg;base64,')
                response.write(base64.b64encode(first_image_data.getvalue()))
                response.write(b'" />')
                response.write(b'<h3>Second image:</h3>')
                response.write(b'<img style="width:500px; height: 500px;" src="data:image/jpg;base64,')
                response.write(base64.b64encode(second_image_data.getvalue()))
                response.write(b'" />')
                response.write(b'<h3>Difference between images: ' + str(difference).encode() + b'</h3>')
                self.wfile.write(response.getvalue())
            else:
                self.wfile.write(b'Something went wrong!')
        elif data[0].split("=")[-1] == 'false':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Request processed! Difference between images: ' + str(difference).encode())

        response_time = time.time() - start_time
        log_request["Request"] = {"Show": data[0].split("=")[-1], "Animal": data[1].split("=")[-1]}
        log_request["Response"] = {"Difference": difference}
        log_request["Latency"] = response_time
        logging_dicts.append(log_request)


if __name__ == "__main__":
    config = ConfigParser()
    config.read('config.ini')
    cat_dog_x_api_key = config.get('auth', 'cat_dog_x_api_key')
    similarity_api_key = config.get('auth', 'similarity_api_key')

    logging_dicts = []
    with HTTPServer(('localhost', PORT), Handler) as httpd:
        print("Serving at port", PORT)
        httpd.serve_forever()
