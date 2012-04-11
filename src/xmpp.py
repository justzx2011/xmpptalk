from pyxmpp2.interfaces import XMPPFeatureHandler
from pyxmpp2.ext.version import VersionProvider
from pyxmpp2.client import Client

class XMPPClient(XMPPFeatureHandler):
  def __init__(self, settings):
    version_provider = VersionProvider(settings)
    self.client = Client(jid, [self, version_provider], settings)

  def start(self):
    self.client.connect()
    self.client.run()
