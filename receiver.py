import socket
import sys
from lib import *

recvSize = 4200

if __name__ =="__main__":

    global cltHost, cltRecvPort, servHost, servPort

    servHost = socket.gethostbyname(socket.gethostname())
    servPort = int(sys.argv[1])
    cltHost = sys.argv[2]
    cltRecvPort = int(sys.argv[3])

    servSkt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    servInfo = (servHost, servPort)
    servSkt.bind(servInfo)

    print("Waiting for Client...")
    msg, cltAddr = servSkt.recvfrom(recvSize)
    filename = msg[9:9+len(msg)].decode("utf-8")
    print("Client Connected. File being transfered :", filename)
    file = open("t-" + filename, "wb")

    nextSeqNum = 0

    while True:
        msg, cltAddr = servSkt.recvfrom(recvSize)
        cltInfo = (cltAddr[0], cltRecvPort)

        seg = binToSeg(msg)

        if seg.type == 0:

            if (seg.seqNo == nextSeqNum) and (not isCorruptSeg(seg)):
                file.write(seg.data)
                ack = genACK(nextSeqNum)
                servSkt.sendto(segToBin(ack), cltInfo)
                nextSeqNum += 1
            else:
                ack = genACK(nextSeqNum-1)
                servSkt.sendto(segToBin(ack), cltInfo)

        elif seg.type == 3:
            servSkt.sendto(segToBin(genFIN()), cltInfo)
            file.close()
            break

    print("File Transfer Complete...")
    file = open("t-" + filename, "rb")
    print("Received :", len(file.read()), "bytes")
    file.close()