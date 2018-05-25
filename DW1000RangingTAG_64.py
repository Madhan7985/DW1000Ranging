"""
This python script is used to configure the DW1000 chip as a tag for ranging functionalities. It must be used in conjunction with the RangingAnchor script. 
It requires the following modules: DW1000, DW1000Constants and monotonic.
"""


import DW1000
import monotonic
import DW1000Constants as C
import time
import socket

LEN_DATA = 20
data = [0] * LEN_DATA
lastActivity = 0
lastPoll = 0
sentAck = False
receivedAck = False
expectedMsgId = C.POLL_ACK
timePollSentTS = 0
timeRangeSentTS = 0
timePollAckReceivedTS = 0
REPLY_DELAY_TIME_US = 7000
# The polling range frequency defines the time interval between every distance poll in milliseconds. Feel free to change its value. 
POLL_RANGE_FREQ = 50# the distance between the tag and the anchor will be estimated every second.
tagID = 23
anchorID = 1

def millis():
    """
    This function returns the value (in milliseconds) of a clock which never goes backwards. It detects the inactivity of the chip and
    is used to avoid having the chip stuck in an undesirable state.
    """
    return int(round(monotonic.monotonic()*C.MILLISECONDS))


def handleSent():
    """
    This is a callback called from the module's interrupt handler when a transmission was successful. 
    It sets the sentAck variable as True so the loop can continue.
    """        
    global sentAck
    sentAck = True


def handleReceived():
    """
    This is a callback called from the module's interrupt handler when a reception was successful. 
    It sets the received receivedAck as True so the loop can continue.
    """            
    global receivedAck
    receivedAck = True


def receiver():
    """
    This function configures the chip to prepare for a message reception.
    """    
    DW1000.newReceive()
    DW1000.receivePermanently()
    DW1000.startReceive()


def noteActivity():
    """
    This function records the time of the last activity so we can know if the device is inactive or not.
    """    
    global lastActivity
    lastActivity = millis()


def resetInactive():
    """
    This function restarts the default polling operation when the device is deemed inactive.
    """
    global expectedMsgId
    print("Reset inactive")	
    expectedMsgId = C.POLL_ACK
    transmitPoll()
    noteActivity()


def transmitPoll():
    """
    This function sends the polling message which is the first transaction to enable ranging functionalities. 
    It checks if an anchor is operational.
    """    
    global data, lastPoll 
    while (millis() - lastPoll < POLL_RANGE_FREQ):
        pass
    DW1000.newTransmit()
    data[0] = C.POLL
    data[17] = tagID    # Always Sender on 17
    data[18] = anchorID # Always Receiver on 18 
    DW1000.setData(data, LEN_DATA)
    DW1000.startTransmit()
    lastPoll = millis()


def transmitRange():
    """
    This function sends the range message containing the timestamps used to calculate the range between the devices.
    """
    global data, timeRangeSentTS, timePollSentTS
    DW1000.newTransmit()
    data[0] = C.RANGE
    data[17] = tagID    # Always Tag Address on 17
    data[18] = anchorID # Always Anchor address on 18 
    timeRangeSentTS = DW1000.setDelay(REPLY_DELAY_TIME_US, C.MICROSECONDS)
    DW1000.setTimeStamp(data, timePollSentTS, 1)
    DW1000.setTimeStamp(data, timePollAckReceivedTS, 6)
    DW1000.setTimeStamp(data, timeRangeSentTS, 11)
    DW1000.setData(data, LEN_DATA)
    DW1000.startTransmit()


def loop():
    global sentAck, receivedAck, data, timePollAckReceivedTS, timePollSentTS, timeRangeSentTS, expectedMsgId
    if (sentAck == False and receivedAck == False):
        if ((millis() - lastActivity) > C.RESET_PERIOD):
            resetInactive()
        return False

    if sentAck:
        sentAck = False
        msgID = data[0]      
        if msgID == C.POLL:
            timePollSentTS = DW1000.getTransmitTimestamp()
        elif msgID == C.RANGE:
            timeRangeSentTS = DW1000.getTransmitTimestamp()
        noteActivity()

    if receivedAck:
        receivedAck = False
        data = DW1000.getData(LEN_DATA)
        # Dont accept data if sender is a Tag or if data is not for me (TAG ID's starts from 21)
        if data[17] > 20 or data[18] != tagID:
            return
        msgID = data[0]  
        # print "Sender : ", data[17]
        # print "Receiver : ",data[18]  
        if msgID != expectedMsgId:
            print "Unexpected Messege"
            expectedMsgId = C.POLL_ACK
            transmitPoll()
            return
        if msgID == C.POLL_ACK:
            # print "Received poll ack from : ", data[17]
            timePollAckReceivedTS = DW1000.getReceiveTimestamp()
            expectedMsgId = C.RANGE_REPORT
            transmitRange()
            noteActivity()
        elif msgID == C.RANGE_REPORT:
            print "Received range report from : ", data[17]            
            expectedMsgId = C.POLL_ACK
#            time.sleep(0.03) #introduced so that it wont poll immediately after sending range
#            transmitPoll()
            noteActivity()
            return True
        elif msgID == C.RANGE_FAILED:
            # print "Received range failed from : ", data[17]
            expectedMsgId = C.POLL_ACK
            transmitPoll()
            noteActivity()
    return False


try:
    PIN_IRQ = 19
    PIN_SS = 16
    DW1000.begin(PIN_IRQ)
    DW1000.setup(PIN_SS)
    print("DW1000 initialized")
    print("############### TAG ##############")	

    DW1000.generalConfiguration("7D:00:22:EA:82:60:3B:9C", C.MODE_LONGDATA_RANGE_ACCURACY)
    DW1000.registerCallback("handleSent", handleSent)
    DW1000.registerCallback("handleReceived", handleReceived)
    DW1000.setAntennaDelay(C.ANTENNA_DELAY_RASPI)
 
#   # create a socket object
#    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#    # get local machine name
#    host = '10.2.128.65'#socket.gethostname()                           
#    port = 8888
#    # bind to the port
#    serversocket.bind((host, port))
#    # queue up to 5 requests
#    serversocket.listen(5)
#    clientsocket,addr = serversocket.accept()
#    print("Got a connection from %s" % str(addr))

    receiver()
    transmitPoll()
    noteActivity()
    while 1:
        loop()
#        while(True):
#            if(loop()):
#                clientsocket.send("Done")
#                break
#        clientsocket.recv(1024)


except KeyboardInterrupt:
    DW1000.close()














