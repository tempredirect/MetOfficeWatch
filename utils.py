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