import requests
from concurrent.futures import ThreadPoolExecutor
import time

number_batches = 1  # 10


def post_request(url, data):
    time.sleep(0.01)
    response = requests.post(url=url, data=data).text
    return response


if __name__ == "__main__":
    for index in range(number_batches):
        urls = ["http://localhost:8080/"] * 50
        data = [{'show': 'false', 'animal': 'dog'}] * 50
        start_time = time.time()
        # Concurent
        with ThreadPoolExecutor(max_workers=4) as executor:
            for data in executor.map(post_request, urls, data):
                print(data)
        # Iterativ
        # for url in urls:
        #    print(post_request(url=url,data=data[0]))
        print("Time to finish batch {}: {} seconds".format(str(index + 1), str(time.time() - start_time)))
