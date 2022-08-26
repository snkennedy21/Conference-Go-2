from json import JSONEncoder
from datetime import datetime
from django.db.models import QuerySet

class DateEncoder(JSONEncoder):
  def default(self, obj):
    if isinstance(obj, datetime):
      return obj.isoformat()
    else:
      return super().default(obj)

    
class QuerySetEncoder(JSONEncoder):
  def default(self, obj):
    if isinstance(obj, QuerySet):
      return list(obj)
    else:
      return super().default(obj)


class ModelEncoder(DateEncoder, QuerySetEncoder, JSONEncoder):
  encoders = {}
  def default(self, obj):
    if isinstance(obj, self.model):
      d={}
      if hasattr(obj, 'get_api_url'):
        value = obj.get_api_url()
        d['href'] = value
      for property in self.properties:
        value = getattr(obj, property)
        if property in self.encoders:
          encoder = self.encoders[property]
          value = encoder.default(value)
        d[property] = value
      d.update(self.get_extra_data(obj))
      return d
    
    else:
      return super().default(obj)
  
  def get_extra_data(self, obj):
    return {}