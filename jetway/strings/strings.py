from google.appengine.ext import ndb


class Locale(ndb.Model):
  lang = ndb.StringProperty()
  region = ndb.StringProperty()


class Flags(ndb.Model):
  fuzzy = ndb.BooleanProperty()


class (ndb.Expando):
  en = ndb.StringProperty()
  lang = ndb.StringProperty()
  translator_comments = ndb.TextProperty()
  extracted_comments = ndb.TextProperty()
  reference = ndb.TextProperty()
  flags = ndb.StructuredProperty(Flags)
  previous_untranslated_string = ndb.StringProperty()


class String(ndb.Model):
  locale = ndb.StructuredProperty(Locale)
  source = ndb.StructuredProperty(Translation)
  created = ndb.DateTimeProperty(auto_now_add=True)
  modified = ndb.DateTimeProperty(auto_now=True)
  memory_key = ndb.KeyProperty()

  def search(cls, query_message):
    query = cls.query()
    query.fetch()
    query = query.filter(cls.form.agree_to_share_with_fulfiller == True)
    per_page = query_message.per_page if query_message else 50
    results, next_cursor, has_more = query.fetch_page(per_page, start_cursor=cursor)
    return (results, next_cursor, has_more)
