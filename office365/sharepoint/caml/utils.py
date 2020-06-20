def to_camel(snake_str):
    return ''.join(x.title() for x in snake_str.split('_'))
