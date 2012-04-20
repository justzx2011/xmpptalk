#
# (C) Copyright 2012 lilydjwg <lilydjwg@gmail.com>
#
# This file is part of xmpptalk.
#
# xmpptalk is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xmpptalk is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with xmpptalk.  If not, see <http://www.gnu.org/licenses/>.
#
import datetime
from util import HANDLED, ObjectDict

class ChatBot:
  '''
  *Message handlers* should receive the sender, msg and returns either
  HANDLED to indicate to process no more, a string to be used as the msg, or
  anything else the bot will simply ignore and continue.
  '''
  __version__ = 'alpha'

  def __init__(self, settings, dbManager, xmppclient):
    self.settings = ObjectDict(settings)
    self.initSettings()
    self.dbManager = dbManager(settings)
    self.xmppclient = xmppclient(settings)
    self._message_handlers = []
    self.now = datetime.datetime.utcnow()

  def initSettings(self):
    settings = self.settings
    if 'software_name' not in settings:
      settings['software_name'] = self.__class__.__name__
    if 'software_version' not in settings:
      settings['software_version'] = self.__version__

  #TODO: on_message 的 wrapper
  def on_message(self, sender, msg, timestamp=None):
    self.now = datetime.datetime.utcnow()
    for h in self._message_handlers:
      #TODO: message stipper
      ret = h(self, sender, msg)
      if ret is HANDLED:
        break
      elif isinstance(ret, str):
        msg = ret
    else:
      #TODO User.speakNotAllowedUntil
      ret = sender.speakNotAllowedUntil(self.now)
      if ret:
        self.reply(_('You are not allowed to speak until %s') % ret)
      else:
        smsg = self.formatMsg(sender, msg, timestamp)
        #TODO self.dbManager.logMessageSent(sender, msg)
        self.dbManager.logMessageSent(sender, msg)
        self.dispatchMsg(smsg, exclude={sender})

  def formatMsg(self, sender, msg, timestamp):
    if timestamp:
      dt = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
      interval = self.now - dt
      if interval.days == 0:
        #TODO: config
        dt += config.timezoneoffset
        #TODO: timeformat
        msg = '(%s) ' % dt.strftime(timeformat) + msg
    #TODO: User 的属性：nick
    msg = '[%s] ' % sender.nick + msg
    return msg

  def dispatchMsg(self, msg, exclude):
    for u in self.getMsgReceiverJIDs():
      if u not in exclude:
        #TODO xmppclient.sendMsg
        #TODO User.jid
        self.xmppclient.sendMsg(u, msg)
    return True

  def reply(self, msg):
    #TODO: self.current_user
    self.xmppclient.sendMsg(self.current_user, msg)

  def getMsgReceiverJIDs(self):
    #TODO self.dbManager.iterActiveMembers()
    it_all = self.dbManager.iterActiveMembers()
    online = self.xmppclient.getOnlineBuddies()
    #TODO User.getReceiveJID
    return [u.getReceiveJID() for u in it_all if u in online]

  def start(self):
    self.xmppclient.start()
