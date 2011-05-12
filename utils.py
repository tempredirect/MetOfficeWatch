import re

def snake_case(input):
    return "_".join(map(lambda s: s.lower(),filter(lambda s: s != '',re.split("([A-Z][a-z]+)",input))))

def chunks(l, n):
    """Returns a list chunked into n sized blocks
    """
    return [l[i:i+n] for i in range(0, len(l), n)]


def first(collection):
    if collection is not None and len(collection) > 0:
        return collection[0]
    return None

def last(collection):
    if collection is not None and len(collection) > 0:
        return collection[len(collection)-1]
    return None

# http://stackoverflow.com/questions/1857780/sparse-assignment-list-in-python/1857860#1857860
class SparseList(list):
  def __setitem__(self, index, value):
    missing = index - len(self) + 1
    if missing > 0:
      self.extend([None] * missing)
    list.__setitem__(self, index, value)
  def __getitem__(self, index):
    try: return list.__getitem__(self, index)
    except IndexError: return None

