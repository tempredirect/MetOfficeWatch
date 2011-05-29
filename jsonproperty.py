import copy
import simplejson
from google.appengine.api import datastore_errors
from google.appengine.api import datastore_types
from google.appengine.ext import db

class JsonMixin(object):
  """Simple, stateless json utilities mixin.

  Requires class to implement two methods:
    to_json(self): convert data to json-compatible datastructure (dict,
      list, strings, numbers)
    @classmethod from_json(cls, json): load data from json-compatible structure.
  """

  def to_json_str(self):
    """Convert data to json string representation.

    Returns:
      json representation as string.
    """
    return simplejson.dumps(self.to_json(), sort_keys=True)

  @classmethod
  def from_json_str(cls, json_str):
    """Convert json string representation into class instance.

    Args:
      json_str: json representation as string.

    Returns:
      New instance of the class with data loaded from json string.
    """
    return cls.from_json(simplejson.loads(json_str))


class JsonProperty(db.UnindexedProperty):
  """Property type for storing json representation of data.

  Requires data types to implement two methods:
    to_json(self): convert data to json-compatible datastructure (dict,
      list, strings, numbers)
    @classmethod from_json(cls, json): load data from json-compatible structure.
  """

  def __init__(self, data_type, default=None, **kwargs):
    """Constructor.

    Args:
      data_type: underlying data type as class.
      default: default value for the property. The value is deep copied
        fore each model instance.
      kwargs: remaining arguments.
    """
    kwargs["default"] = default
    super(JsonProperty, self).__init__(**kwargs)
    self.data_type = data_type

  def get_value_for_datastore(self, model_instance):
    """Gets value for datastore.

    Args:
      model_instance: instance of the model class.

    Returns:
      datastore-compatible value.
    """
    value = super(JsonProperty, self).get_value_for_datastore(model_instance)
    if not value:
      return None
    json_value = value.to_json()
    if not json_value:
      return None
    return datastore_types.Text(simplejson.dumps(
        json_value, sort_keys=True))

  def make_value_from_datastore(self, value):
    """Convert value from datastore representation.

    Args:
      value: datastore value.

    Returns:
      value to store in the model.
    """

    if value is None:
      return None
    return self.data_type.from_json(simplejson.loads(value))

  def validate(self, value):
    """Validate value.

    Args:
      value: model value.

    Returns:
      Whether the specified value is valid data type value.

    Raises:
      BadValueError: when value is not of self.data_type type.
    """
    if value is not None and not isinstance(value, self.data_type):
      raise datastore_errors.BadValueError(
          "Property %s must be convertible to a %s instance (%s)" %
          (self.name, self.data_type, value))
    return super(JsonProperty, self).validate(value)

  def empty(self, value):
    """Checks if value is empty.

    Args:
      value: model value.

    Returns:
      True passed value is empty.
    """
    return not value

  def default_value(self):
    """Create default model value.

    If default option was specified, then it will be deeply copied.
    None otherwise.

    Returns:
      default model value.
    """
    if self.default:
      return copy.deepcopy(self.default)
    else:
      return None


