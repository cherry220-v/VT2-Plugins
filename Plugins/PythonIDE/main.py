pathFile = open("pythonpath", "a+")

def pythonPath():
    return pathFile.read().split("\n")[0]

def initAPI(api):
    global vtapi, platform, sys, os, CustomDialog, QtWidgets, QtCore
    vtapi = api
    m = vtapi.FSys
    os = m.osModule()
    sys = m.sysModule()
    QtWidgets = vtapi.FSys.importModule("PyQt6.QtWidgets")
    QtCore = vtapi.FSys.importModule("PyQt6.QtCore")

    class CustomDialog(QtWidgets.QDialog):
        def __init__(self, vtapi):
            super().__init__()
            self.vtapi = vtapi
            self.platform = self.vtapi.FSys.platformModule()
            self.os = self.vtapi.FSys.osModule()
            self.platform = self.vtapi.FSys.platformModule()
            self.subprocess = self.vtapi.FSys.sprModule()
            self.setupUi()
        def setupUi(self):
            self.setObjectName("self")
            self.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
            self.resize(400, 111)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
            self.setSizePolicy(sizePolicy)
            self.setMaximumSize(QtCore.QSize(400, 111))
            self.setWindowFilePath("")
            self.setModal(True)
            self.verticalLayout = QtWidgets.QVBoxLayout(self)
            self.verticalLayout.setObjectName("verticalLayout")
            self.frame = QtWidgets.QFrame(parent=self)
            self.frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
            self.frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
            self.frame.setObjectName("frame")
            self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
            self.verticalLayout_2.setObjectName("verticalLayout_2")
            self.label = QtWidgets.QLabel(parent=self.frame)
            self.label.setObjectName("label")
            self.verticalLayout_2.addWidget(self.label)
            self.horizontalLayout = QtWidgets.QHBoxLayout()
            self.horizontalLayout.setObjectName("horizontalLayout")
            self.lineEdit = QtWidgets.QLineEdit(parent=self.frame)
            self.lineEdit.setObjectName("comboBox")
            self.lineEdit.insert(pathFile.read().split("\n")[0] if self.os.path.isfile(pathFile.read().split("\n")[0]) else self.findPython()[0])
            self.horizontalLayout.addWidget(self.lineEdit)
            self.pushButton = QtWidgets.QPushButton(parent=self.frame)
            self.pushButton.setMaximumSize(QtCore.QSize(50, 16777215))
            self.pushButton.clicked.connect(self.customPythonPath)
            self.pushButton.setObjectName("pushButton")
            self.horizontalLayout.addWidget(self.pushButton)
            self.verticalLayout_2.addLayout(self.horizontalLayout)
            self.pushButton_2 = QtWidgets.QPushButton(parent=self.frame)
            self.pushButton_2.clicked.connect(self.savePath)
            self.pushButton_2.setObjectName("pushButton_2")
            self.verticalLayout_2.addWidget(self.pushButton_2)
            self.verticalLayout.addWidget(self.frame)

            self.retranslateUi()
            QtCore.QMetaObject.connectSlotsByName(self)

        def retranslateUi(self):
            _translate = QtCore.QCoreApplication.translate
            self.setWindowTitle(_translate("self", "Choose Python path - "))
            self.label.setText(_translate("self", "Choose Python path"))
            self.pushButton.setText(_translate("self", "Add"))
            self.pushButton_2.setText(_translate("self", "Save"))

        def customPythonPath(self):
            path = self.vtapi.App.openFileDialog()
            if path[0]:
                self.lineEdit.clear()
                self.lineEdit.insert(path[0][0])

        def savePath(self):
            t = self.lineEdit.text()
            if t:
                pathFile.write(t)
            self.close()

        def findPython(self):
            system_type = self.platform.system()

            if system_type == "Windows":
                return self.find_python_windows()
            elif system_type in ("Linux", "Darwin"):  # macOS == Darwin
                return self.find_python_unix()
            else:
                return "", ""

        def find_python_windows(self):
            paths = self.os.environ["PATH"].split(self.os.pathsep)
            for path in paths:
                python_exe = self.os.path.join(path, "python.exe")
                if self.os.path.exists(python_exe):
                    try:
                        version = self.subprocess.check_output([python_exe, "--version"],
                                                        stderr=self.subprocess.STDOUT).decode().strip()
                        return python_exe, version
                    except self.subprocess.SubprocessError:
                        continue
            return "", ""

        def find_python_unix(self):
            try:
                python_path = self.subprocess.check_output(["which", "python3"]).decode().strip()
                if python_path:
                    version = self.subprocess.check_output([python_path, "--version"]).decode().strip()
                    return python_path, version
            except self.subprocess.CalledProcessError:
                pass

            try:
                python_path = self.subprocess.check_output(["which", "python"]).decode().strip()
                if python_path:
                    version = self.subprocess.check_output([python_path, "--version"]).decode().strip()
                    return python_path, version
            except self.subprocess.CalledProcessError:
                pass

            return "", ""

def runFile():
    tab = vtapi.Tab.currentTabIndex()
    process = QtCore.QProcess()

    script_path = vtapi.Tab.getTabFile(tab)
    sys.path.insert(0, pythonPath())

    if os.name == 'nt':  # Если Windows
        cmd_command = f"start cmd.exe /k python {script_path} & timeout /t -1"
        process.start("cmd.exe", ["/c", cmd_command])
    else:  # Если Linux или другие ОС
        bash_command = f"bash -c \"python3 {script_path}; read -p 'Press Enter to continue...'\""
        process.start("x-terminal-emulator", ["-e", bash_command])

    process.waitForFinished()

def showPythonPath():
    d = CustomDialog(vtapi)
    d.exec()