import os
import re
import socket
import threading
import requests

def init(self, sock=None):
    if sock is None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else:
        self.sock = sock

def connect(self, host, port):
    self.sock.connect((host, port))

def myclose(self):
    self.sock.close()

def mysend(self, msg, debug=False):
    if debug:
        print("MESSAGE SENT")
        print(msg.decode())
    self.sock.sendall(msg)

def myreceive(self, debug=False):
    received = b''
    buffer = 1
    while True:
        part = self.sock.recv(buffer)
        received += part
        if part == b'':
            break
    if debug:
        print("Received...")
        print(received)
    return received

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as mysocket:
    mysocket.connect(("me.utm.md", 80))
    mysocket.sendall(b"GET / HTTP/1.1\r\n"
                     b"Host: me.utm.md\r\n\r\n")

    print(str(mysocket.recv(52), 'utf-8'))

def get_url_images_in_text(text):
    urls = []
    results = re.findall("[^\"']*\\.(?:png|jpg|gif)", text)

    for a in results:
        if 'http://' not in a:
            a = 'http://me.utm.md/' + a
        urls.append(a)
    urls = list(set(urls))
    print('Links of images: ' + str(len(urls)))
    return urls


def get_images_from_url(url):
    resp = requests.get(url)
    urls = get_url_images_in_text(resp.text)
    print('\nUrls:\n', urls)
    return urls


def download_images(path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as mysocket:
        mysocket.connect(("me.utm.md", 80))
        mysocket.sendall("GET {0} HTTP/1.1\r\nHost: me.utm.md\r\n"
                         "Connection: close\r\n\r\n".format(path).encode("latin1"))


        images = b''

        while True:

            data = mysocket.recv(1024)
            if not data:
                images = images.split(b"\r\n\r\n")
                if "200" not in images[0].decode("latin1"):
                    print(path)
                image_path = os.path.join(os.getcwd(), "images", path.rpartition("/")[-1])
                with open(image_path, "wb") as fcont:
                    fcont.write(images[-1])
                break

            images += data

img_list = get_images_from_url('http://me.utm.md/')

thread_list = []
threads = 2

for i in img_list:
    t = threading.Thread(target=download_images, args=(i,))
    thread_list.append(t)
    t.start()


for i in thread_list:
    i.join()




print("Download Done")