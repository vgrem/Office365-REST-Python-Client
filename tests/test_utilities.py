from office365.sharepoint.file_creation_information import FileCreationInformation


class ListExtensions(object):
    """SharePoint List extensions"""

    @classmethod
    def ensure_list(cls, web, list_properties):
        ctx = web.context
        lists = web.lists.filter("Title eq '{0}'".format(list_properties.Title))
        ctx.load(lists)
        ctx.execute_query()
        if len(lists) == 1:
            return lists[0]
        return cls.create_list(web, list_properties)

    @classmethod
    def create_list(cls, web, list_properties):
        ctx = web.context
        list_obj = web.lists.add(list_properties)
        ctx.execute_query()
        return list_obj


class FileExtensions(object):
    @classmethod
    def upload_file(cls, list, url, content):
        info = FileCreationInformation()
        info.content = content
        info.url = url
        info.overwrite = True
        upload_file = list.root_folder.files.add(info)
        list.context.execute_query()
        return upload_file


class WebExtensions(object):
    """SharePoint Web extensions"""

    @classmethod
    def get_all_webs(cls, parent_web, result=None):
        if result is None:
            result = []
        ctx = parent_web.context
        webs = parent_web.webs
        ctx.load(webs)
        ctx.execute_query()
        result = result + list(webs)
        for web in webs:
            return cls.get_all_webs(web, result)
        return result


def read_file_as_text(path):
    with open(path, 'r') as content_file:
        file_content = content_file.read()
    return file_content


def read_file_as_binary(path):
    with open(path, 'rb') as content_file:
        file_content = content_file.read()
    return file_content


def normalize_response(response):
    content = response.decode("utf-8")
    if (content[0] == content[-1]) and content.startswith(("'", '"')):
        return content[1:-1]
    return content
