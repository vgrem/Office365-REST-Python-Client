def read_file_as_text(path):
    with open(path, 'r') as content_file:
        file_content = content_file.read()
    return file_content


def read_file_as_binary(path):
    with open(path, 'rb') as content_file:
        file_content = content_file.read()
    return file_content


def ensure_list(web, list_properties):
    ctx = web.context
    lists = web.lists.filter("Title eq '{0}'".format(list_properties.Title))
    ctx.load(lists)
    ctx.execute_query()
    if len(lists) == 1:
        return lists[0]
    return create_list(web, list_properties)


def create_list(web, list_properties):
    ctx = web.context
    list_obj = web.lists.add(list_properties)
    ctx.execute_query()
    return list_obj
