from pytaskgraph.dependency import Dependency

from os.path import abspath, normcase
from hashlib import md5
from base64 import b64encode

class FileDependency(Dependency):

    def __init__(self, file_path):
        self.path = normcase(abspath(file_path))
        Dependency.__init__(self, self.path)


    def calculate_hash(self):
        f = open(self.path, 'r')
        m = md5()
        m.update(f.read())
        f.close()
        digest = m.digest()
        return b64encode(digest).rstrip('=')
