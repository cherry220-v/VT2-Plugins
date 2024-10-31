def initAPI(api):
    global vtapi
    vtapi = api
    vtapi.SigSlots.treeWidgetDoubleClicked.connect(lambda it: onDoubleClick(it))

def openDir(dir=None):
    if not dir:
        dir = vtapi.App.openDirDialog()
    vtapi.App.setTreeWidgetDir(dir)

def onDoubleClick(item):
    openFileCommand = vtapi.getCommand("openFile")
    fp = vtapi.App.getModelElement(item)
    if openFileCommand and fp:
        openFileCommand.get("command")([fp])
    else:
        vtapi.App.setLogMsg("Command 'openFile' not found. Install Open&Save plugin")
    print(item)