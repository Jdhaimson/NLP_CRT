import json
# from jsonrpc import ServerProxy, JsonRpc20, TransportTcpIp
import jsonrpclib
from pprint import pprint
import sys


class StanfordNLP:
    def __init__(self, port_number=8080):
        self.server = jsonrpclib.Server("http://localhost:%d" % port_number)
        #self.server = ServerProxy(JsonRpc20(), TransportTcpIp(addr=("127.0.0.1", 8080)))

    def parse(self, text):
        return json.loads(self.server.parse(text))

def demo_stanford_parser(sentence):
    nlp = StanfordNLP()
    result = nlp.parse(sentence)
    pprint(result)

    from nltk.tree import ParentedTree
    nlpparsetree = result['sentences'][0]['parsetree']
    parsetree = nlpparsetree[nlpparsetree.index('(ROOT'):]
    tree = ParentedTree.fromstring(parsetree)
    tree.pretty_print()
    pprint(tree)
    pprint(tree.pos())

if __name__ == "__main__":
    sentence = sys.argv[1]
    demo_stanford_parser(sentence)
