import xml.sax
import sys, traceback
import cStringIO

class Node(object):
    def __init__(self, tag, attributes = None):
        self._tag = tag
        if attributes:
            for attribute in attributes.getNames():
                setattr(self, attribute, attributes.getValue(attribute))
        self._children = []
        #self._text = text

    def __getattr__(self, key):
        try:
            object.__getattr__(self, key)
        except:
            return None

    def append(self, child):
        self._children.append(child)

    @property 
    def tag(self):
        return self._tag

    @property
    def children(self):
        return self._children

    @property
    def text(self):
        return self._text

    @property
    def xml(self):
        stringIO = cStringIO.StringIO()
        stringIO.write('<%s>'%self.type)
        for c in self.children:
            stringIO.write(c.xml)
        stringIO.write('</%s>'%self.type)
        return stringIO.getvalue()

class RootNode(Node):
    def __init__(self):
        Node.__init__(self, 'root')

class CharacterDataNode(Node):
    def __init__(self, text):
        Node.__init__(self, 'charData')
        self._text = text

    @property
    def text(self):
        return self._text    

    @property
    def xml(self):
        return self.text

class InstructionNode(Node):
    def __init__(self, target, data):
        Node.__init__(self, 'instruction')
        self._text = data

    @property
    def data(self):
        return self._text

class BasicContentHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.currentNode = RootNode()
        self.nodeStack   = []
    
    def startElement (self, name, attrs):
        if name == 'root':
            return
        self.nodeStack.append(self.currentNode)
        self.currentNode = Node(name, attrs)
        #print name, attrs
    
    def endElement (self, name):
        if name == 'root':
            return
        parentNode = self.nodeStack.pop()
        parentNode.append(self.currentNode)
        self.currentNode = parentNode

    def processingInstruction(self, target, data):
        self.currentNode.append(InstructionNode(target, data))

    def characters (self, chunk):
        self.currentNode.append(CharacterDataNode(chunk))
        
class XMLParseError(Exception):
    pass

class ErrorHandler(xml.sax.ErrorHandler):
    def error(self, exception):
        print 'Some error occured', exception.getMessage()
        raise XMLParseError()

    def fatalError(self, exception):
        print 'Some fatal error occured', exception.getMessage()
        raise XMLParseError()
        #raise XMLParseError()
    def warning(self, exception):
        print 'Some warning occured', exception.getMessage()
        

def parse(string):
    #print 'PARSING', string
    contentHandler = BasicContentHandler()
    ss = string
    try:
        xml.sax.parseString(ss, contentHandler, ErrorHandler())
    except Exception, details:
        print details
    return contentHandler.currentNode.children

#def parseLines(string):
#    return parse(string)
#
if __name__ == '__main__':
    xmlData = """123<list>
#This is a list of elements
#<define name="foo">123</define>
#<t></t>
#</list><b></b>123<list>
#This is a list of elements
#<define name="foo">123</define>
#<t></t>
#</list><b></b>123<list>
#This is a list of elements
#<define name="foo">123</define>
#<t></t>
#</list><b></b>123<list>
#This is a list of elements
#<define name="foo">123</define>
#<t></t>
#</list><b></b>123<list>
#This is a list of elements
#<define name="foo">123</define>
#<t></t>
#</list><b></b>123<list>
#This is a list of elements
#<define name="foo">123</define>
#<t></t>
#</list><b></b>123<list>
#This is a list of elements
#<define name="foo">123</define>
#<t></t>
#</list><b></b>"""
    foo = parse(xmlData)
    print foo
    #for x in foo.children:
    #    print x.type
    #    for t in x.children:
    #        print t.type
