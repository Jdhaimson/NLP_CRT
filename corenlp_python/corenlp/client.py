import json
# from jsonrpc import ServerProxy, JsonRpc20, TransportTcpIp
import jsonrpclib
from pprint import pprint


class StanfordNLP:
    def __init__(self, port_number=8080):
        self.server = jsonrpclib.Server("http://localhost:%d" % port_number)

    def parse(self, text):
        return json.loads(self.server.parse(text))

def demo_stanford_parser():
    nlp = StanfordNLP()
    result = nlp.parse("Hello world!  It is so beautiful.")
    pprint(result)

    from nltk.tree import Tree
    tree = Tree.parse(result['sentences'][0]['parsetree'])
    pprint(tree)


if __name__ == "__main__":
    demo_stanford_parser()
