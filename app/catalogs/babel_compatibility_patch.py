from babel import localedata
import pickle
import os

# NOTE: Babel does not support "fuzzy" locales. A locale is considered "fuzzy"
# when a corresponding "localedata" file that matches a given locale's full
# identifier (e.g. "en_US") does not exist. Here's one example: "en_BD". CLDR
# does not have a localedata file matching "en_BD" (English in Bangladesh), but
# it does have individual files for "en" and also "bn_BD". As it turns
# out, localedata files that correspond to a locale's full identifier (e.g.
# "bn_BD.dat") are actually pretty light on the content (largely containing
# things like start-of-week information) and most of the "meat" of the data is
# contained in the main localedata file, e.g. "en.dat".
#
# Users may need to generate pages corresponding to locales that we don't
# have full localedata for, and until Babel supports fuzzy locales, we'll
# monkeypatch two Babel functions to provide partial support for fuzzy locales.
#
# With this monkeypatch, locales will be valid even if Babel doesn't have a
# localedata file matching a locale's full identifier, but locales will still
# fail with a ValueError if the user specifies a territory that does not exist.
# With this patch, a user can, however, specify an invalid language. Obviously,
# this patch should be removed when/if Babel adds support for fuzzy locales.
# Optionally, we may want to provide users with more control over whether a
# locale is valid or invalid, but we can revisit that later.

# See: https://github.com/grow/pygrow/issues/93


def fuzzy_load(name, merge_inherited=True):
  localedata._cache_lock.acquire()
  try:
    data = localedata._cache.get(name)
    if not data:
      # Load inherited data
      if name == 'root' or not merge_inherited:
        data = {}
      else:
        parts = name.split('_')
        if len(parts) == 1:
          parent = 'root'
        else:
          parent = '_'.join(parts[:-1])
        data = fuzzy_load(parent).copy()
      filename = os.path.join(localedata._dirname, '%s.dat' % name)
      try:
        fileobj = open(filename, 'rb')
        try:
          if name != 'root' and merge_inherited:
            localedata.merge(data, pickle.load(fileobj))
          else:
            data = pickle.load(fileobj)
          localedata._cache[name] = data
        finally:
          fileobj.close()
      except IOError:
        pass
    return data
  finally:
    localedata._cache_lock.release()


localedata.exists = lambda name: True
localedata.load = fuzzy_load
