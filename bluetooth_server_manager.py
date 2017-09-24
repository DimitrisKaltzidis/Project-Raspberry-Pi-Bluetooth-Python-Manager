#!/usr/bin/python

from threading import Thread
from time import sleep
import logging
import logging.handlers
import argparse
import sys
import os
import time
from bluetooth import *


def handle_bluetooth_client_async(client_socket, client_info):
    print("Accepted new connection from ", client_info)

    while True:

        try:
            # Read data from client
            byte_data = client_socket.recv(1024)

            # if no data
            if len(byte_data) == 0:
                break

            # Convert from byte to string
            data = byte_data.decode("utf-8")
            data = data[:-1]

            # Implement your logic here!!!
            print("Received [%s] from client:[%s]" % (data, str(client_info)))

            # Handle the request
            if data == "exit":
                print("User [%s] requested Bluetooth communication termination." % (str(client_info)), )
                client_socket.close()
                print("Terminated socket serving clinet: [%s]" % (str(client_info)), )
                break

            client_socket.send("Pi > [%s]" % data)
            print("Sent [%s] to client [%s]" % (data, str(client_info)))
        except:
            print("User left. Bluetooth communication ternination is requested for user [%s]." % (str(client_info)), )
            client_socket.close()
            print("Terminated socket serving clinet: [%s]" % (str(client_info)), )
            break

    print("Killed thread serving client [%s]" % (str(client_info)), )


# Main loop
def main():
    print("Initializing Bluetooth. Please wait...")
    # We need to wait until Bluetooth init is done
    time.sleep(15)
    print("Initializing Bluetooth. Done!")
    # Make device visible
    os.system("sudo hciconfig hci0 piscan")

    # Create a new server socket using RFCOMM protocol
    server_sock = BluetoothSocket(RFCOMM)
    # Bind to any port
    server_sock.bind(("", PORT_ANY))
    # Start listening
    server_sock.listen(1)

    # Get the port the server socket is listening
    port = server_sock.getsockname()[1]

    # The service UUID to advertise android old
    # uuid = "0001101-0000-1000-8000-00805F9B34FB"

    # The service UUID to advertise Python bt rasp
    uuid = "7be1fcb3-5776-42fb-91fd-2ee7b5bbb86d"

    # Start advertising the service
    advertise_service(server_sock, "raspberrypi",
                      service_id=uuid,
                      service_classes=[uuid, SERIAL_PORT_CLASS],
                      profiles=[SERIAL_PORT_PROFILE])

    # The client socket
    client_sock = None

    # Main Bluetooth server loop
    while True:

        print("Waiting for new connections on RFCOMM channel %d" % port)

        try:

            # This will block until we get a new connection
            client_sock, client_info = server_sock.accept()
            print("New Bluetooth connection attempt detected")

            thread = Thread(target=handle_bluetooth_client_async, args=(client_sock, client_info,))
            thread.start()

        except IOError:
            pass

        except KeyboardInterrupt:
            server_sock.close()
            print("Keyboard interruption detected.")
            break


if __name__ == "__main__":
    print("Bluetooth server program started")
    main()
    print("Bluetooth server program finished")

