from . import messages
from ..buildbot import buildbot
from ..translations import translations
from babel.messages import pofile
import babel
import io
import cStringIO


class Error(Exception):
  pass


class Catalog(object):

  def __init__(self, project, locale, ref='master'):
    self.project = project
    self.locale = locale
    self.babel_locale = babel.Locale.parse(self.locale)
    self.ref = ref
    self._bot = buildbot.Buildbot()
    self.num_translated = 0
    self.num_fuzzy = 0
    self.num_messages = 0
    self.percent_translated = 0
    self.sha = None
    self.content = None
    self.load()

  @property
  def path(self):
    return '/translations/{}/LC_MESSAGES/messages.po'.format(self.locale)

  @property
  def ident(self):
    return '{}{}'.format(self.project.name, self.path)

  def load(self):
    data = self._bot.get_contents(
        self.project.buildbot_job_id,
        path=self.path,
        ref=self.ref)
    self.content = data['content'].encode('utf-8')
    self.sha = data['sha']

  @property
  def babel_catalog(self):
#    fp = cStringIO.StringIO()
    fp = io.BytesIO()
    fp.write(self.content)
    fp.seek(0)
    return pofile.read_po(fp, self.locale)

  @property
  def name(self):
    return self.babel_locale.get_display_name('en_US')

  def list_translations(self):
    translation_objs = []
    for message in list(self.babel_catalog)[1:]:
      translation = translations.Translation(
          catalog=self,
          msgid=message.id,
          string=message.string)
      translation_objs.append(translation)
    return translation_objs

  def _generate_stats(self):
    for message in list(self.babel_catalog)[1:]:
      self.num_messages += 1
      if message.string:
        self.num_translated += 1
      if 'fuzzy' in message.flags:
        self.num_fuzzy += 1
    self.percent_translated = self.num_translated * 100 // self.num_messages

  def to_message(self, included=None):
    self._generate_stats()
    message = messages.CatalogMessage()
    message.name = self.name
    message.ident = self.ident
    message.locale = self.locale
    message.sha = self.sha
    message.ref = self.ref
    if included is None or 'translations' in included:
      message.translations = [translation.to_message()
                              for translation in self.list_translations()]
    message.num_messages = self.num_messages
    message.num_translated = self.num_translated
    message.num_fuzzy = self.num_fuzzy
    message.percent_translated = self.percent_translated
    return message

  def update_translations(self, translation_messages, ref, sha, committer, author):
    for message in translation_messages:
      self.babel_catalog[message.msgid] = message.string
    fp = io.BytesIO()
    pofile.write_po(fp, self.locale)
    content = fp.getvalue()
    return self._bot.write_file(
        self.project.buildbot_job_id,
        path=self.path,
        contents=content,
        ref=ref,
        sha=sha,
        committer=committer,
        author=author)
