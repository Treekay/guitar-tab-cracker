"""Windows kernel-owned child lifetime; close/crash kills the agent process tree."""
import os


class ProcessScope:
    def __init__(self,process):
        self.handle=None
        if os.name!='nt':return
        import ctypes as c
        from ctypes import wintypes as w
        class Basic(c.Structure):
            _fields_=[('ProcessTime',c.c_longlong),('JobTime',c.c_longlong),('Flags',w.DWORD),
                ('MinimumWorkingSet',c.c_size_t),('MaximumWorkingSet',c.c_size_t),
                ('ActiveProcessLimit',w.DWORD),('Affinity',c.c_size_t),('Priority',w.DWORD),('Scheduling',w.DWORD)]
        class IO(c.Structure):
            _fields_=[(name,c.c_ulonglong) for name in ['ReadOps','WriteOps','OtherOps','ReadBytes','WriteBytes','OtherBytes']]
        class Limits(c.Structure):
            _fields_=[('Basic',Basic),('IO',IO),('ProcessMemory',c.c_size_t),('JobMemory',c.c_size_t),
                ('PeakProcessMemory',c.c_size_t),('PeakJobMemory',c.c_size_t)]
        self.kernel=c.WinDLL('kernel32',use_last_error=True)
        self.kernel.CreateJobObjectW.argtypes=[c.c_void_p,w.LPCWSTR];self.kernel.CreateJobObjectW.restype=w.HANDLE
        self.kernel.SetInformationJobObject.argtypes=[w.HANDLE,c.c_int,c.c_void_p,w.DWORD];self.kernel.SetInformationJobObject.restype=w.BOOL
        self.kernel.AssignProcessToJobObject.argtypes=[w.HANDLE,w.HANDLE];self.kernel.AssignProcessToJobObject.restype=w.BOOL
        self.kernel.CloseHandle.argtypes=[w.HANDLE];self.kernel.CloseHandle.restype=w.BOOL
        handle=self.kernel.CreateJobObjectW(None,None)
        if not handle:raise OSError('Cannot create agent process scope')
        self.handle=handle;limits=Limits();limits.Basic.Flags=0x2000 # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.kernel.SetInformationJobObject(handle,9,c.byref(limits),c.sizeof(limits)) or not self.kernel.AssignProcessToJobObject(handle,w.HANDLE(int(process._handle))):
            self.close();raise OSError('Cannot contain agent process tree')
    def close(self):
        if self.handle:self.kernel.CloseHandle(self.handle);self.handle=None
