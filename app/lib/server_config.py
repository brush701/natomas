from optparse import OptionParser
import os

parser = OptionParser()
parser.add_option("--environment", dest="environment")
parser.add_option("--dbhost", dest="database")
(OPTIONS, _) = parser.parse_args()

class ServerConfig:

    @staticmethod
    def ENVIRONMENT():
        clflag = OPTIONS.environment
        envar = os.getenv("ENVIRONMENT")
        return clflag or envar or "dev"

    @staticmethod
    def DBHOST():
        clflag = OPTIONS.database
        envar = os.getenv("DBHOST")
        return clflag or envar or "localhost"
