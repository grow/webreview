from . import messages
from ..buildbot import buildbot
from ..translations import translations
from babel.messages import pofile
import cStringIO


class Error(Exception):
  pass


class Catalog(object):

  def __init__(self, project, locale, ref='master'):
    self.project = project
    self.locale = locale
    self.ref = ref

  @property
  def path(self):
    return '/translations/{}/LC_MESSAGES/messages.po'.format(self.locale)

  @property
  def content(self):
    bot = buildbot.Buildbot()
    return bot.read_file(self.project.buildbot_job_id, path=self.path, ref=self.ref)

  @property
  def babel_catalog(self):
    fp = cStringIO.StringIO()
    fp.write(self.content)
    fp.seek(0)
    return pofile.read_po(fp, self.locale)

  def list_translations(self):
    translation_objs = []
    for message in self.babel_catalog:
      translation = translations.Translation(
          catalog=self,
          msgid=message.id,
          string=message.string)
      translation_objs.append(translation)
    return translation_objs

  def to_message(self):
    message = messages.CatalogMessage()
    message.locale = self.locale
    message.translations = [translation.to_message()
                            for translation in self.list_translations()]
    return message
