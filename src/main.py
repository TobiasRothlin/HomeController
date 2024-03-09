from HomeController import HomeController
import time
import socket

import json
import _thread

homeController = HomeController()
do_logging = False
intervall = 10

def logging_thread():
    global homeController
    global intervall
    global do_logging
    while True:
        if do_logging:
            homeController.log_data()
            time.sleep(intervall)

def main_thread():
    global homeController
    global intervall
    global do_logging

    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen()

    response = """HTTP/1.1 200 OK
Content-Type: application/json

"""
    while True:
        data = {}
        conn, addr = s.accept()  # Accept a connection
        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)  # Receive up to 1024 bytes from the connection
        reqeustString = request.decode('utf-8')
        print(reqeustString)
        if reqeustString.find("GET /set/relais") != -1:
            parsedRequest = reqeustString.split(" ")[1].split("/")
            homeController.set_relais(int(parsedRequest[3]), int(parsedRequest[4]))
            data["status"] = "OK"
            data["data"] = {
                "relaisStates": {
                    "0": homeController.get_relais(0),
                    "1": homeController.get_relais(1),
                    "2": homeController.get_relais(2),
                    "3": homeController.get_relais(3)
                }
            }

        elif reqeustString.find("GET /get/states") != -1:
            data["status"] = "OK"
            data["data"] = {
                "errorStates": {
                    "Yellow": homeController.get_status_led("Yellow"),
                    "Green": homeController.get_status_led("Green"),
                }
            }

        elif reqeustString.find("GET /get/sensors") != -1:
            data["status"] = "OK"
            data["data"] = {
                "temperature": homeController.get_temperature(),
                "humidity": homeController.get_humidity(),
                "light": homeController.get_light()
            }

        elif reqeustString.find("GET /startLogging") != -1:
            if homeController.sd_connected:
                parsedRequest = reqeustString.split(" ")[1].split("/")
                intervall = int(parsedRequest[2])
                do_logging = True
                data["data"] = {
                    "loggingState": "started",
                    "loggingIntervall": intervall
                }
                data["status"] = "OK"
            else:
                data["status"] = "ERROR"
                data["data"] = {
                    "error": "No SD Card connected"
                }

        elif reqeustString.find("GET /stopLogging") != -1:
            do_logging = False
            data["status"] = "OK"
            data["data"] = {
                "loggingState": "stopped"
            }

        else:
            data["status"] = "ERROR"
            data["data"] = {
                "Possible Requests": ["192.168.1.161/set/relais/3/1",
                                    "192.168.1.161/get/states",
                                    "192.168.1.161/get/sensors",
                                    "192.168.1.161/startLogging/10",
                                    "192.168.1.161/stopLogging",]
            }
        # Send the HTTP response
        send_response = response + json.dumps(data)
        print(send_response)
        conn.send(send_response)
        conn.close()
        

second_thread = _thread.start_new_thread(logging_thread, ())
main_thread()




