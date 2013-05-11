__all__ = ['api', 'data']

def fqcn(obj):
    return obj.__class__.__module__ + '.' + obj.__class__.__name__
