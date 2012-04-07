import abc
from util import HANDLED, ObjectDict

class ChatBot(metaclass=abc.ABCMeta):
  '''
  *Message handlers* should receive the sender, msg and returns either
  HANDLED to indicate to process no more, a string to be used as the msg, or
  anything else the bot will simply ignore and continue.
  '''
  __version__ = 'pre-alpha'

  def __init__(self, settings, userManager, xmppclient):
    self.settings = ObjectDict(settings)
    self.initSettings()
    self.userManager = userManager(settings)
    self.xmppclient = xmppclient(settings)
    self._message_handlers = []

  def initSettings(self):
    settings = self.settings
    if 'software_name' not in settings:
      settings['software_name'] = self.__class__.__name__
    if 'software_version' not in settings:
      settings['software_version'] = self.__version__

  def on_message(self, sender, msg, timestamp=None):
    for h in self._message_handlers:
      #TODO: message stipper
      ret = h(self, sender, msg)
      if ret is HANDLED:
        break
      elif isinstance(ret, str):
        msg = ret
    else:
      #TODO userManager.speakNotAllowed
      ret = self.userManager.speakNotAllowed(sender)
      if ret:
        self.reply(_('You are not allowed to speak until %s') % ret)
      else:
        #TODO self.userManager.messageSent(sender, msg)
        self.userManager.messageSent(sender, msg)
        smsg = self.formatMsg(sender, msg, timestamp)
        self.dispatchMsg(smsg, exclude={sender})

  @abc.abstractmethod
  def formatMsg(self, sender, msg, timestamp):
    pass

  def dispatchMsg(self, msg, exclude):
    for u in self.getMsgReceivers():
      if u not in exclude:
        #TODO xmppclient.sendMsg
        self.xmppclient.sendMsg(u, msg)
    return True

  def getMsgReceivers(self):
    #TODO self.userManager.getActiveMembers()
    it_all = self.userManager.iterActiveMembers()
    online = self.xmppclient.getOnlineBuddies()
    return [u for u in it_all if u in onlinj]

  def start(self):
    self.xmppclient.start()
