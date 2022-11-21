#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by zhangwanxin on 2018/11/4.
from typing import Optional

import color_print
import comm_tools
from app_info import AppInfoHelper
from format_content import IFormatContent


class LogLevelHelper(object):
    VERBOSE = 2
    DEBUG = 3
    INFO = 4
    WARN = 5
    ERROR = 6
    UNKNOWN = 0

    @staticmethod
    def level_code(priority: str) -> int:
        if comm_tools.is_empty(priority):
            return LogLevelHelper.UNKNOWN

        priority = priority.strip()
        if priority == '2' or priority.upper() == 'V':
            # VERBOSE
            level = LogLevelHelper.VERBOSE
        elif priority == '3' or priority.upper() == 'D':
            # DEBUG
            level = LogLevelHelper.DEBUG
        elif priority == '4' or priority.upper() == 'I':
            # INFO
            level = LogLevelHelper.INFO
        elif priority == '5' or priority.upper() == 'W':
            # WARN
            level = LogLevelHelper.WARN
        elif priority == '6' or priority.upper() == 'E':
            # ERROR
            level = LogLevelHelper.ERROR
        else:
            level = LogLevelHelper.UNKNOWN
        return level

    @staticmethod
    def level_name(code: int) -> str:
        if code == 2:
            priority = "V"
        elif code == 3:
            priority = "D"
        elif code == 4:
            priority = "I"
        elif code == 5:
            priority = "W"
        elif code == 6:
            priority = "E"
        else:
            priority = "UnKnown"

        return priority


class LogInfo(object):

    def __init__(self, _date: str, _time: str, _pid: str, _tid: str, _priority: str, _tag: str):
        self._date = _date
        self._time = _time
        self._pid = _pid
        self._tid = _pid
        self._priority = _priority
        self._tag = _tag
        self._msg = None
        self._msg_format: Optional[IFormatContent] = None

    @property
    def tag(self) -> str:
        return self._tag

    @property
    def msg_format(self) -> Optional[IFormatContent]:
        return self._msg_format

    @msg_format.setter
    def msg_format(self, _format: Optional[IFormatContent]):
        self._msg_format = _format

    def append_msg_content(self, _content: str):
        if comm_tools.is_empty(_content):
            return
        if not self._msg:
            self._msg = []
        self._msg.append(comm_tools.get_str(_content).strip())

    def get_msg_content(self):
        if not self._msg:
            return ""
        _content = ""
        for index, line in enumerate(self._msg):
            if comm_tools.is_empty(line):
                continue
            if index == 0:
                _content += line
            else:
                _content += ("\n\t\t" + line)
        return _content.strip()

    def get_format_msg_content(self):
        if self.msg_format:
            return self.msg_format.format_content(self.get_msg_content())
        else:
            return self.get_msg_content()

    def get_process_name(self):
        name = AppInfoHelper.found_name_by_pid(self._pid)
        if not name:
            return self._pid
        return name

    def get_show_name(self):
        name = AppInfoHelper.found_name_by_pid(self._pid)
        if not name:
            return self._pid
        if ":" in name:
            # 子进程
            _s = name.split(":")
            return _s[0].split(".")[-1] + "@" + _s[1]
        else:
            # 主进程
            return name.split(".")[-1] + "@main"

    def get_level(self):
        return LogLevelHelper.level_code(self._priority)

    def print_log(self):
        msg_content = self.get_format_msg_content()
        if comm_tools.is_empty(msg_content):
            return
        if self._pid == self._tid:
            tid_msg = self._tid
        else:
            tid_msg = f"{self._tid}❗"
        msg = "{0}#{1}#{2}#{3}#{4}#{5}".format(self._time, self.get_show_name(),
                                               tid_msg, self._priority, self._tag,
                                               msg_content)
        if self._priority == 'D':
            color_print.green(msg)
        elif self._priority == 'E':
            color_print.red(msg)
        elif self._priority == 'W':
            color_print.yellow(msg)
        elif self._priority == 'I':
            color_print.light_blue(msg)
        else:
            print(msg)
