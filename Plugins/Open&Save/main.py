def initAPI(api):
    global vtapi, os, FileReadThread, FileWriteThread, queue
    vtapi = api
    os = vtapi.FSys.osModule()

    from classes import FileReadThread, FileWriteThread, queue
    vtapi.SigSlots.tabClosed.connect(lambda index, file: addToRecent(file))

try:
    recentFiles = (eval(open("recent.f", "a+").read()))
except SyntaxError: recentFiles = []

def apiCommand(n):
    return vtapi.getCommand(n).get("command")

def addToRecent(f):
    recentFiles.append(f)
    recLog = open("recent.f", "w+")
    recLog.truncate(0)
    recLog.write(str(recentFiles))
    recLog.close()

def openRecentFile(e=False):
    i = vtapi.Tab.currentTabIndex()
    if len(recentFiles) > 0:
        openFile([recentFiles[-1]])
        recentFiles.remove(recentFiles[-1])
        recLog = open("recent.f", "w+")
        recLog.truncate(0)
        recLog.write(str(recentFiles))
        recLog.close()

def openFile(filePath=None, encoding=None, used=True):
    if not filePath and used:
        filePath, _ = vtapi.App.openFileDialog()
        if not filePath:
            return
    for file in filePath:
        file = os.path.abspath(file)
        encoding = encoding or 'utf-8'
        apiCommand("addTab")(name=file, canSave=True)
        vtapi.Tab.setTab(-1)
        i = vtapi.Tab.currentTabIndex()
        vtapi.Tab.setTabFile(i, file)
        thread = FileReadThread(vtapi, file)
        thread.chunkRead = queue.Queue()

        thread.start()

        while thread.is_alive():
            try:
                chunk = thread.chunkRead.get(timeout=0.1)
                vtapi.Tab.setTabText(i, chunk)
            except queue.Empty:
                continue

        thread.finished.wait()
        thread.stop()
        vtapi.Tab.setTabTitle(i, os.path.basename(file or "Untitled"))
        vtapi.Tab.setTabSaved(vtapi.Tab.currentTabIndex(), True)

def saveFile(f=None, text=None):
    i = vtapi.Tab.currentTabIndex()
    text = text or vtapi.Tab.getTabText(i)
    if vtapi.Tab.getTabCanSave(i):
        if f:
            vtapi.Tab.setTabFile(i, f)
        if not vtapi.Tab.getTabFile(i):
            vtapi.Tab.setTabFile(i, vtapi.App.saveFileDialog()[0])
        if vtapi.Tab.getTabFile(i):
            thread = FileWriteThread(vtapi, text)
            thread.start()
            thread.finished.wait()
            thread.stop()
            vtapi.Tab.setTabTitle(i, os.path.basename(vtapi.Tab.getTabFile(i) or "Untitled"))
            vtapi.Tab.setTabSaved(i, True)

def saveAsFile():
    saveFile(vtapi.App.saveFileDialog()[0])