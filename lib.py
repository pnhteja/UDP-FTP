import time

def getTime ():
    return int(round(time.time()*1000))

def intToBytes ( num, noOfBytes ):
	return num.to_bytes(length=noOfBytes, byteorder="big")

def bytesToInt ( data, start, end ):
	return int.from_bytes(data[start:end], byteorder="big")

def calcCheckSum (data):

	totalSum = 0
	unitLen = 2
	val = (2**(8*unitLen))

	for i in range (0, len(data), unitLen):
		subUnit = bytesToInt (data, i, i+unitLen)
		totalSum += subUnit

		while ( totalSum > (val - 1)):
			q = totalSum // val
			r = totalSum % val
			totalSum = q+r

	complementSum = val - 1 - totalSum
	return complementSum


def isCorruptSeg (seg):

	recvChkSum = calcCheckSum(seg.data)
	if (recvChkSum == seg.checkSum):
		return False
	else:
		return True

def isCorruptACK (seg):
	
	if ( seg.checkSum == 1 ):
		return True
	else:
		return False


class segment:

	def __init__ (self, type, seqNo, checkSum, payload, data):
		self.type = type
		self.seqNo = seqNo
		self.checkSum = checkSum
		self.payload = payload
		self.data = data

def segToBin (seg):
	bytForm = bytearray()
	bytForm.extend(intToBytes(seg.type, 1))
	bytForm.extend(intToBytes(seg.seqNo, 4))
	bytForm.extend(intToBytes(seg.checkSum, 2))
	bytForm.extend(intToBytes(seg.payload, 2))
	bytForm.extend(seg.data)
	return bytForm

def genSeg (seqNo, data):
	return segment(0, seqNo, calcCheckSum(data), len(data), data)

def genACK (seqNo):
	return segment(1, seqNo, 0, 0, b'0')

def genSYN (fileName):
	return segment(2, 0, 1, 0, fileName)

def genFIN ():
	return segment(3, 0, 0, 0, b'0')

def binToSeg (binForm):
	type = bytesToInt (binForm, 0, 1)
	seqNo = bytesToInt (binForm, 1, 5)
	checkSum = bytesToInt (binForm, 5, 7)
	payload = bytesToInt (binForm, 7, 9)
	data = binForm[9:9+payload]
	return segment(type, seqNo, checkSum, payload, data)