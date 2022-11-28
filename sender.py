import threading
import socket
import sys
from lib import *

lock1 = threading.Lock()
lock2 = threading.Lock()
completedTransfer = False

windowSize = 16
recvNewACK = False

timeInterval = 50

segSize = 4096
recvSize = 4200

cumulativeACK = -1

def runClientRecv ():

    global recvNewACK, cumulativeACK
    global cltHost, cltRecvPort, servHost, servPort, servInfo

    cltRecvSkt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cltRecvInfo = (cltHost, cltRecvPort)
    cltRecvSkt.bind(cltRecvInfo)
    servInfo = (servHost, servPort)

    while True:
        msg, servAddr = cltRecvSkt.recvfrom(recvSize) 
        ack = binToSeg(msg)

        if ( ack.type == 1 ):
            if ( not isCorruptACK(ack) ):
                lock1.acquire()
                if ( ack.seqNo >= (cumulativeACK + 1) ):
                    cumulativeACK += (ack.seqNo - cumulativeACK)
                    recvNewACK = True
                lock1.release()

        elif ( ack.type == 3 ):
            return


def runClientSend (segments, cltSendSkt ):

    global recvNewACK, cumulativeACK, timeInterval
    global cltHost, cltRecvPort, servHost, servPort, servInfo

    cltRecv = threading.Thread(target=runClientRecv, args=())
    cltRecv.daemon = True
    cltRecv.start()

    base = 0
    nextSeqNum = 0

    timerActive = True
    startTime = getTime()

    while base < len(segments):

        if (nextSeqNum < len(segments)) and (nextSeqNum < (base + windowSize)):
            cltSendSkt.sendto(segToBin(segments[nextSeqNum]), servInfo)
            nextSeqNum += 1

        lock1.acquire()
        if ( recvNewACK ):
            recvNewACK = False
            base = cumulativeACK+1
            if base == nextSeqNum:
                timerActive = False
            else:
                timerActive = True
                startTime = getTime()
        lock1.release()

        if timerActive and ((getTime() - startTime) > timeInterval):
            startTime = getTime()
            for i in range (base, nextSeqNum):
                cltSendSkt.sendto(segToBin(segments[i]), servInfo)

    cltSendSkt.sendto(segToBin(genFIN()), servInfo)
    cltRecv.join()


if __name__ == "__main__":

    global cltHost, cltRecvPort, servHost, servPort, servInfo

    cltHost = socket.gethostbyname(socket.gethostname())
    cltRecvPort = int(sys.argv[1])
    servHost = sys.argv[2]
    servPort = int(sys.argv[3])
    filename = sys.argv[4]

    servInfo = (servHost, servPort)

    file = open(filename, "rb")
    fileContent = file.read()

    print("File being transfered :", filename)
    print("File Size :", len(fileContent), "bytes")

    noOfSegments = len(fileContent) // segSize
    if len(fileContent) % segSize != 0:
        noOfSegments += 1

    cltSendSkt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cltSendSkt.sendto(segToBin(genSYN(bytes(filename, "utf-8"))), servInfo)

    segments = []

    for i in range(noOfSegments):
        if i == noOfSegments - 1:
            start = i*segSize
            end = len(fileContent)
        else:
            start = i*segSize
            end = start + segSize
        newSeg = genSeg(i, fileContent[start:end])
        segments.append(newSeg)

    print("Total Packets need to be transmitted :", len(segments))
    fileTransferStart = getTime()
    runClientSend(segments, cltSendSkt)
    fileTransferEnd = getTime()
    print("File Transfer Complete...")
    print("Time Taken For File Transfer :", (fileTransferEnd - fileTransferStart), "ms")
    file.close()