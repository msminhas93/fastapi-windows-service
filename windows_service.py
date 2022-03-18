import os
import sys
from multiprocessing import freeze_support
from subprocess import Popen

import psutil
import servicemanager
import win32event
import win32service
import win32serviceutil


def kill_proc_tree(pid):
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    for child in children:
        child.kill()


class PythonWindowsService(win32serviceutil.ServiceFramework):
    _svc_name_ = "FastAPI Uvicorn Server Service"  # service name
    _svc_display_name_ = "FastAPI Uvicorn Server Service"  # service display name
    _svc_description_ = "This service starts up the uvicorn server."  # service description

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        kill_proc_tree(self.process.pid)
        self.process.terminate()
        win32event.SetEvent(self.hWaitStop)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        # Create a separate process to allow server stopping when service
        # is stopped

        server_path = os.path.join(sys._MEIPASS, "server\\server.exe")
        server_cmd = f"call {server_path}"
        self.process = Popen(server_cmd, shell=True)
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)


if __name__ == '__main__':
    freeze_support()  # Needed for pyinstaller for multiprocessing on WindowsOS
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(PythonWindowsService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(PythonWindowsService)
