#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
see : https://www.cnblogs.com/liuzhipenglove/p/7063808.html
@author:   wswenyue
@date:     2022/9/7 
"""
import os
import subprocess
import shutil
import comm_tools
from comm_tools import is_windows_os, is_exe, cmd_run_iter, is_empty, get_str


class AdbCmd(object):
    _adb = None

    @staticmethod
    def find_adb(adb_path: str = None) -> str:
        if comm_tools.is_not_empty(AdbCmd._adb):
            return AdbCmd._adb

        def check_adb_path(path):
            if os.path.exists(path) and is_exe(path):
                return path
            return None

        # Check if a custom adb_path is provided
        if comm_tools.is_not_empty(adb_path):
            resolved_path = check_adb_path(adb_path)
            if resolved_path:
                AdbCmd._adb = resolved_path
                return AdbCmd._adb
            raise ValueError(f"The specified adb path '{adb_path}' is not valid or not executable.")

        # Check system PATH for adb
        adb_in_path = shutil.which("adb")
        if adb_in_path:
            AdbCmd._adb = adb_in_path
            return AdbCmd._adb

        # Check ANDROID_HOME environment variable
        android_home = os.environ.get("ANDROID_HOME")
        if android_home:
            adb_exe_name = "adb.exe" if is_windows_os() else "adb"
            platform_tools_path = os.path.join(android_home, "platform-tools", adb_exe_name)
            resolved_path = check_adb_path(platform_tools_path)
            if resolved_path:
                AdbCmd._adb = resolved_path
                return AdbCmd._adb
            raise EnvironmentError(f"Adb not found in ANDROID_HOME path: {android_home}.")
        
        raise EnvironmentError(
            "Adb could not be found. Ensure adb is in the system PATH or ANDROID_HOME is correctly set."
        )


class AdbHelper(object):

    def __init__(self, adb_path=None, open_log=False):
        self._open_log = open_log
        self._adb = AdbCmd.find_adb(adb_path)

    def __check_adb_connect(self):
        _cmd = f"{self._adb} devices"
        for line in cmd_run_iter(_cmd):
            if is_empty(line):
                continue
            if line.startswith("List of devices attached"):
                continue
            devices = line.split()
            if len(devices) != 2:
                raise ValueError(f"run {_cmd} ;; devices result error!!!")
            if devices[1] == "device":
                return True
        return False

    def __restart_adb_connect(self):
        _cmd = f"{self._adb} kill-server && {self._adb} server && {self._adb} devices"
        os.system(_cmd)

    def check_connect(self):
        if self.__check_adb_connect():
            return True
        self.__restart_adb_connect()
        if self.__check_adb_connect():
            return True
        raise ValueError("adb not connection!!! Please check!!!")

    def run_cmd_result_code(self, cmd):
        self.check_connect()
        _cmd = f"{self._adb} {cmd}"
        if self._open_log:
            print(f"run {_cmd}")
        process = subprocess.Popen(str(_cmd).split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        return process.returncode, out, err

    def run_cmd(self, cmd) -> str:
        code, out, err = self.run_cmd_result_code(cmd)
        if code:
            if self._open_log:
                print(f"error: {err}")
            raise subprocess.CalledProcessError(code, cmd)
        return get_str(out)

    def cmd_run_iter(self, cmd):
        self.check_connect()
        popen = self.popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ""):
            yield get_str(stdout_line)
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

    def popen(self, cmd, buf_size=None,
              stdout=None, stderr=None,
              universal_newlines=None) -> subprocess.Popen:
        _cmd = f"{self._adb} {cmd}"
        if self._open_log:
            print(f"run {_cmd}")
        return subprocess.Popen(str(_cmd).split(), bufsize=buf_size, stdout=stdout, stderr=stderr,
                                universal_newlines=universal_newlines)
