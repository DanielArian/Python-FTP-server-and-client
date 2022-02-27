import sys
from socket import *
import os
import traceback

from importlib_metadata import files

BUFFER_SIZE = 1024

if len(sys.argv) != 3:
    print ("Usage: ./prog <server> <port>")
    sys.exit()

sock = socket(AF_INET, SOCK_STREAM)

#To set waiting time of one second for reponse from server
sock.settimeout(1)

try:
    remoteAddr = (sys.argv[1], int(sys.argv[2]))
except Exception:
    print ("Usage: ./prog <server> <port>")
    sys.exit()

sock.connect(remoteAddr)
print (sock)
print ("-----")

# authentification --------------------------------------------
try:
    # Send username
    bin_message = sock.recv(BUFFER_SIZE)
    username = input(bin_message.decode("utf8"))
    sock.send(username.encode('utf8'))

    # send password
    bin_message = sock.recv(BUFFER_SIZE)
    password = input(bin_message.decode("utf8"))
    sock.send(password.encode('utf8'))

    # get response
    bin_message = sock.recv(BUFFER_SIZE)
    message = bin_message.decode('utf8')
    print(message)
    if message[0:3] == "ERR":
        sock.close()

except timeout:
    print ("Timeout")
    print ("")
    sock.close()
    sys.exit()

except Exception as e:
    print ("Exception: {}".format(str(e)))
    print ("")
    sock.close()
    sys.exit()

# FTP command -----------------------------------------------------
try:
    while True:
        # do not decode here in case of string not containing utf8 char
        bin_message = sock.recv(BUFFER_SIZE)

        # if input from user is required......................
        if b'/$ ' in bin_message:
            message = bin_message.decode('utf8')
            response = input(message)

            if len(response) == 0: response = " " # otherwise, there will be a timeout error
            sock.send(response.encode('utf8'))


        elif b'SENDING' in bin_message:  # ============================

            # DOWNLOAD FILE
            # Should receive from the server:
            # SENDING:<filename>__<filesize>:END_METADATA<file_content>:END_SENDING

            bytes_received = bin_message

            # receiving data ...................................
            while b":END_SENDING" not in bytes_received:
                bytes_received += sock.recv(BUFFER_SIZE)
            
            # extract metadata
            idx_end_metadata = bytes_received.find(b":END_METADATA") + len(":END_METADATA")
            metadata = bytes_received[len('SENDING:'):idx_end_metadata - len(':END_METADATA')]
            filename, filesize = metadata.decode("utf8").split('__')
            print(filename, filesize)

            # ectract file content
            data = bytes_received[idx_end_metadata:-len(":END_SENDING")]

            # write file
            f = open(filename, "wb")
            f.write(data)
            f.close()

            # check if file entirely received ....................

            if os.path.getsize(filename) == int(filesize):
                print("File downloaded.")
            else:
                print(os.path.getsize(filename))
                print("An error occured while downloading.")

            # inform the server that operation is complete
            sock.sendall("randomData".encode("utf8"))

        # if server is in receiving mode, we send a file

        elif b'RECEIVING' in bin_message:    # ==========================

            # UPLOAD FILE

            filepath = input("Path to file: ")

            if not os.path.isfile(filepath):
                print("File not found.")
                sock.sendall(b"ERR")
            else:
                # get metadata .............................
                filename = os.path.basename(filepath)
                filesize = os.path.getsize(filepath)

                # get file content ........................
                f = open(filepath, "rb")
                file_content = f.read()
                f.close()

                # construct sending message ................
                metadata = f"SENDING:{filename}__{filesize}:END_METADATA".encode("utf8")
                data = file_content + b":END_SENDING"
                package = metadata + data

                # send to server
                q, r = len(package) // BUFFER_SIZE, len(package) % BUFFER_SIZE
                for i in range(q):
                    sock.sendall(package[i:i+BUFFER_SIZE])
                sock.sendall(package[-r:])

        # Just a message from the server ...........................
        else:
            message = bin_message.decode('utf8')
            print(message)

except timeout:
    print ("Timeout")
    print ("")
    sock.close()

except Exception as e:
    traceback_output = traceback.format_exc()
    print ("Exception: {}".format(str(e)))
    print("Traceback: {}".format(traceback_output))
    sock.close()

sock.close()