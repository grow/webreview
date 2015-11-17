#import airlock
from . import sheets


#class SheetsHandler(airlock.Handler):
class SheetsHandler(object):

  def get(self, sheet_id):
    resp = sheets.get_sheet(sheet_id, gid=self.request.GET.get('gid'))
    self.response.headers['Content-Type'] = 'text/csv'
    self.response.out.write(resp)
