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


def read_file_as_text(path):
    with open(path, 'r') as content_file:
        file_content = content_file.read()
    return file_content


def read_file_as_binary(path):
    with open(path, 'rb') as content_file:
        file_content = content_file.read()
    return file_content
