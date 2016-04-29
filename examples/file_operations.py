listTitle = "Documents"


def readFolder(ctx):
    "Read a folder example"
    list = ctx.web.lists.get_by_title(listTitle)
    folder = list.root_folder
    ctx.load(folder)
    ctx.execute_query()

    print "List url: {0}".format(folder.properties["ServerRelativeUrl"])

    files = folder.files
    ctx.load(files)
    ctx.execute_query()
    for file in files:
        print "File name: {0}".format(file.properties["Name"])

    folders = ctx.web.folders
    ctx.load(folders)
    ctx.execute_query()
    for folder in folders:
        print "Folder name: {0}".format(folder.properties["Name"])
