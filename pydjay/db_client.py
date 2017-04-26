import zmq
import sys
import json

port = "9999"


context = zmq.Context()
print "Connecting to server..."
socket = context.socket(zmq.REQ)
socket.connect ("tcp://127.0.0.1:%s" % port)
#if len(sys.argv) > 2:
#    socket.connect ("tcp://localhost:%s" % port1)


#for request in range (1,10):
#    print "Sending request ", request,"..."
socket.send (json.dumps({'name': 'play',
                        'args': (sys.argv[1],),
                        'kwargs':{}}))
    #  Get the reply.
message = socket.recv()
print "Received reply [", message, "]"

consumer_receiver = context.socket(zmq.PULL)
consumer_receiver.connect("tcp://127.0.0.1:5557")
# send work
#onsumer_sender = context.socket(zmq.PUSH)
#consumer_sender.connect("tcp://127.0.0.1:5558")

while True:
    work = consumer_receiver.recv_json()
    #data = work['type']
    #value = work['value']
    #result = { 'consumer' : consumer_id, 'num' : data}
    #if data%2 == 0:
#        consumer_sender.send_json(result)
    print work
