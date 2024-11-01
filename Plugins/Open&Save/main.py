def execList(lst):
    try: return eval(lst)
    except: return []

def initAPI(api):
    global OpenFileCommand, SaveFileCommand, OpenRFileCommand, addToRFiles
    VtAPI = api

    class OpenFileCommand(VtAPI.Plugin.WindowCommand):
        def __init__(self, api, window):
            super().__init__(api, window)
            self.QtCore = self.api.importModule("PyQt6.QtCore")
            self.chardet = self.api.importModule("chardet")
            self.os = self.api.importModule("os")
        def run(self, f: list = [], dlg=False):
            if dlg:
                f = self.api.Dialogs.openFileDialog()[0]
            # self.window.openFile(f) | Use command with name 'OpenFileCommand'
            self.initThread()
            for file in f:
                view = self.window.newFile()
                view.setFile(file)
                view.setTitle(self.os.path.basename(file or "Untitled"))
                self.fileReader = FileReadThread(file, self)
                self.fileReader.line_read.connect(view.insert)
                self.fileReader.start()
                self.fileReader.wait()
                view.setSaved(True)
        
        def initThread(self):
            global FileReadThread
            class FileReadThread(VtAPI.Widgets.Thread):
                line_read = self.QtCore.pyqtSignal(str)

                def __init__(self, file_path: str, cclass, buffer_size: int = 1024, parent=None):
                    super().__init__(parent)
                    self.file_path = file_path
                    self.buffer_size = buffer_size
                    self._is_running = True
                    self.cclass = cclass

                def run(self):
                    with open(self.file_path, 'rb') as f:
                        raw_data = f.read(1024)
                        encoding_info = self.cclass.chardet.detect(raw_data)
                        encoding = encoding_info.get('encoding', 'utf-8')

                    with open(self.file_path, 'r', encoding=encoding) as f:
                        while self._is_running:
                            chunk = f.read(self.buffer_size)
                            if not chunk:
                                break
                            self.line_read.emit(chunk)
                            self.msleep(50)

                def stop(self):
                    self._is_running = False

    class SaveFileCommand(VtAPI.Plugin.WindowCommand):
        def __init__(self, api, window):
            super().__init__(api, window)
            self.QtCore = self.api.importModule("PyQt6.QtCore")
            self.os = self.api.importModule("os")
        def run(self, view: VtAPI.View | None = None, dlg=False):
            if not view:
                view = self.window.activeView
            if dlg or not view.getFile():
                f = self.api.Dialogs.saveFileDialog()[0]
            else:
                f = view.getFile()
            # self.window.saveFile(f) | Use command with name 'SaveFileCommand'
            self.initThread()
            text = view.getText()
            view.setFile(f)
            view.setTitle(self.os.path.basename(f))
            writeThread = FileWriteThread(f, text, self)
            writeThread.progress.connect(lambda p: print(f"Progress: {p}%"))
            writeThread.finished.connect(lambda: print("File writing completed"))
            writeThread.error.connect(lambda e: print("Error:", e))

            writeThread.start()
            writeThread.wait()
            view.setSaved(True)
        def initThread(self):
            global FileWriteThread
            class FileWriteThread(VtAPI.Widgets.Thread):
                progress = self.QtCore.pyqtSignal(int)
                finished = self.QtCore.pyqtSignal()
                error = self.QtCore.pyqtSignal(str)

                def __init__(self, file_path, content, api, parent=None, chunk_size=4096):
                    super().__init__(parent)
                    self.file_path = file_path
                    self.content = content
                    self.chunk_size = chunk_size
                    self.QtCore = api.QtCore

                def run(self):
                    try:
                        total_length = len(self.content)
                        written_length = 0

                        with open(self.file_path, 'w', encoding='utf-8') as file:
                            for i in range(0, total_length, self.chunk_size):
                                chunk = self.content[i:i + self.chunk_size]
                                file.write(chunk)
                                written_length += len(chunk)
                                
                                progress_percent = int((written_length / total_length) * 100)
                                self.progress.emit(progress_percent)

                        self.finished.emit()
                    except Exception as e:
                        self.error.emit(str(e))

    class OpenRFileCommand(VtAPI.Plugin.WindowCommand):
        def __init__(self, api, window):
            super().__init__(api, window)
            self.os = self.api.importModule("os")
            self.ast = self.api.importModule("ast")
        def run(self):
            recentFiles = open("recent.f", "r+")
            print(self.os.path.abspath(recentFiles.name))
            fList = self.ast.literal_eval(recentFiles.read())
            print(fList)
            if len(fList) > 0 and self.window.getCommand("OpenFileCommand"):
                if fList[-1]:
                    self.window.runCommand({"command": "OpenFileCommand", "kwargs": {"f": [fList[-1]]}})
                fList.remove(fList[-1])
                recentFiles.seek(0)
                recentFiles.truncate()
                recentFiles.write(str(fList))
                recentFiles.close()
    
    def addToRFiles(view, api):
        if view.getFile():
            ast = api.importModule("ast")
            recentFiles = open("recent.f", "r+")
            fList = ast.literal_eval(recentFiles.read())
            fList.append(view.getFile())
            recentFiles.seek(0)
            recentFiles.truncate()
            recentFiles.write(str(fList))
            recentFiles.close()

    VtAPI.activeWindow.signals.tabClosed.connect(lambda view: addToRFiles(view, VtAPI))
    VtAPI.activeWindow.registerCommandClass({"command": OpenRFileCommand, "shortcut": "ctrl+shift+t"})
