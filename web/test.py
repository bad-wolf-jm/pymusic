from twisted.web import server, resource
from twisted.web.static import File
from twisted.internet import reactor, endpoints, task
from threading import Thread
import os
#
#os.chdir(os.path.expanduser('~/deep-learning/deeplearn/twitter_sentiment'))
#
from models.byte_cnn import train

i=0

class Simple(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        return b"<html>Hello, world!</html>" + str(i).encode('utf8')

def call_loop():
    global i
    i += 1

thr = Thread(target=train.start_training)
thr.start()
#print('training_started')
#print(os.path.expanduser('~/deep-learning/python/deeplearn/twitter_sentiment/foo.html'))
f = File(os.path.expanduser('~/python/deep-learning/deeplearn/twitter_sentiment'))

site = server.Site(f)
endpoint = endpoints.TCP4ServerEndpoint(reactor, 8080)
endpoint.listen(site)
reactor.run()
