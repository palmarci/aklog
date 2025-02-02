#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by wswenyue on 2018/11/4.

from typing import Optional, List, Union

import comm_tools


class AsciiColor(object):
    fg_desc = {
        "black": 30, "red": 31, "green": 32, "yellow": 33, "blue": 34,
        "purple": 35, "cyan": 36, "white": 37, "gray": 37,
        "highlight_black": 90, "light_black": 90, "hl_black": 90,
        "highlight_red": 91, "light_red": 91, "hl_red": 91,
        "highlight_green": 92, "light_green": 92, "hl_green": 92,
        "highlight_yellow": 93, "light_yellow": 93, "hl_yellow": 93,
        "highlight_blue": 94, "light_blue": 94, "hl_blue": 94,
        "highlight_purple": 95, "light_purple": 95, "hl_purple": 95,
        "highlight_cyan": 96, "light_cyan": 96, "hl_cyan": 96,
        "highlight_white": 97, "light_white": 97, "hl_white": 97,
        "highlight_gray": 97, "light_gray": 97, "hl_gray": 97,
    }

    bg_desc = {
        "black": 40, "red": 41, "green": 42, "yellow": 43, "blue": 44,
        "purple": 45, "cyan": 46, "white": 47, "gray": 47,
        "highlight_black": 100, "light_black": 100, "hl_black": 100,
        "highlight_red": 101, "light_red": 101, "hl_red": 101,
        "highlight_green": 102, "light_green": 102, "hl_green": 102,
        "highlight_yellow": 103, "light_yellow": 103, "hl_yellow": 103,
        "highlight_blue": 104, "light_blue": 104, "hl_blue": 104,
        "highlight_purple": 105, "light_purple": 105, "hl_purple": 105,
        "highlight_cyan": 106, "light_cyan": 106, "hl_cyan": 106,
        "highlight_white": 107, "light_white": 107, "hl_white": 107,
        "highlight_gray": 107, "light_gray": 107, "hl_gray": 107,
    }

    style_desc = {"normal": 0, "none": 0, "bold": 1, "faint": 2, "italic": 3, "underline": 4,
                  "blink": 5, "blink2": 6, "negative": 7, "concealed": 8, "crossed": 9}

    def __init__(self, style: Optional[Union[int, str]] = None,
                 fg: Optional[Union[int, str]] = None,
                 bg: Optional[Union[int, str]] = None):
        """
         https://gist.github.com/JBlond/2fea43a3049b38287e5e9cefc87b2124
        :param style:
        :param fg:
        :param bg:
        """
        self._highlight_bg = False
        self._highlight_fg = False
        self.style = style
        self.bg = bg
        self.fg = fg

    def __str__(self):
        if self.style and self.fg and self.bg:
            return u'\u001b[' + ";".join([str(self.style), str(self.fg), str(self.bg)]) + 'm'
        if self.fg and self.bg:
            return u'\u001b[' + ";".join(["0", str(self.fg), str(self.bg)]) + 'm'
        if self.fg:
            if self.style:
                return u'\u001b[' + f'{self.style};{self.fg}m'
            else:
                return u'\u001b[' + f'{self.fg}m'
        if self.bg:
            return u'\u001b[' + f'{self.bg}m'

        if self.style:
            return u'\u001b[' + f'{self.style}m'
        return ''

    def format(self, data: str) -> str:
        return str(self) + data + u'\u001b[0m'

    @property
    def style(self) -> int:
        return self._style

    @style.setter
    def style(self, style: Optional[Union[int, str]]):
        code = None
        if isinstance(style, str):
            code = self.style_desc.get(style)
        elif isinstance(style, int):
            code = style

        if code and code in range(10):
            self._style = code
        else:
            self._style = None

    @property
    def bg(self) -> int:
        return self._bg

    @bg.setter
    def bg(self, bg: Optional[Union[int, str]]):
        code = None
        if isinstance(bg, str):
            code = self.bg_desc.get(bg)
        elif isinstance(bg, int):
            code = bg

        if code:
            if code in range(40, 48):
                self._bg = code
                self._highlight_bg = False
            elif code in range(100, 108):
                self._bg = code
                self._highlight_bg = True
            else:
                self._bg = None
        else:
            self._bg = None

    @property
    def fg(self) -> int:
        return self._fg

    @fg.setter
    def fg(self, fg: Optional[Union[int, str]]):
        code = None
        if isinstance(fg, str):
            code = self.fg_desc.get(fg)
        elif isinstance(fg, int):
            code = fg

        if code:
            if code in range(30, 38):
                self._fg = code
                self._highlight_fg = False
            elif code in range(90, 98):
                self._fg = code
                self._highlight_fg = True
            else:
                self._fg = None
        else:
            self._fg = None

    def copy(self):
        return AsciiColor(style=self.style, fg=self.fg, bg=self.bg)


class _ColorNode(object):

    def __init__(self, index: int, color: AsciiColor):
        """
        node for colorable
        :param index:
        :param color:
        """
        self._index = index
        self._color = color

    @property
    def index(self) -> int:
        return self._index

    @property
    def color(self) -> AsciiColor:
        return self._color


class ColorStr(object):

    def __init__(self, source: str, base_color: Optional[AsciiColor] = None):
        self._source = source
        self._invalid = comm_tools.is_empty(source)
        self._base_color = base_color
        self._end_index = len(source)
        self._nodes = [_ColorNode(0, color=self.base_color), _ColorNode(self._end_index, color=self.base_color)]

    @property
    def source(self) -> str:
        return self._source

    @property
    def base_color(self) -> AsciiColor:
        if self._base_color:
            return self._base_color
        else:
            return Colors.NONE

    @base_color.setter
    def base_color(self, color: Optional[AsciiColor]):
        if color:
            self._base_color = color

    def _sort(self):
        self._nodes.sort(key=lambda _node: _node.index)

    def _found_near_left_node(self, _target: int) -> Optional[_ColorNode]:
        """
        找到给定元素靠近的left node
        :param _target:
        :return:
        """
        # 找到列表中 <=_target（最靠近）的Node
        self._sort()
        last = None
        for node in self._nodes:
            if node.index <= _target:
                last = node
            else:
                break
        return last

    def _merge_base_color(self, color: Optional[AsciiColor]) -> Optional[AsciiColor]:
        if not color:
            return color
        if self.base_color.style and (not color.style):
            color.style = self.base_color.style
        if self.base_color.fg and (not color.fg):
            color.fg = self.base_color.fg
        if self.base_color.bg and (not color.bg):
            color.bg = self.base_color.bg
        return color

    def set_color(self, begin: int, end: int, color: AsciiColor):
        if self._invalid:
            return self
        if not color:
            return self
        if begin < 0:
            begin = 0
        if end > self._end_index:
            end = self._end_index
        # 1. 找到列表中 <=end（最靠近）的Node，进行copy，生成endNode
        # 2. 删除[begin,end]段的Node
        # 3. 创建beginNode，并插入，排序
        left = self._found_near_left_node(end)
        if not left:
            raise ValueError("found_near_left_node is null!!!")
        self._nodes: List[_ColorNode] = [_node for _node in self._nodes if
                                         _node.index < begin or _node.index > end]
        # add beginNode
        self._nodes.append(_ColorNode(begin, color))
        # add endNode
        self._nodes.append(_ColorNode(end, left.color))
        self._sort()
        return self

    def _format_sub(self, begin_node: _ColorNode, end: int) -> str:
        if begin_node.index < 0 or end > self._end_index or begin_node.index >= end:
            raise ValueError(f"_format_sub error begin:{begin_node.index};;end:{end}")
        if begin_node.color:
            _color = self._merge_base_color(begin_node.color)
            if not _color:
                raise ValueError(f"_format_sub color is null!!!")
            return _color.format(self.source[begin_node.index: end])
        return self.source[begin_node.index: end]

    def __str__(self) -> str:
        ret = None
        if self._invalid:
            return ''
        node_size = len(self._nodes)
        for idx, node in enumerate(self._nodes):
            if idx <= 0:
                # first
                ret = self._format_sub(node, self._nodes[idx + 1].index)
            elif idx >= node_size - 1:
                # end
                break
            else:
                ret += self._format_sub(node, self._nodes[idx + 1].index)
        return ret


class SimpleColorStr(object):
    def __init__(self, data: str, color: AsciiColor):
        self.data = data
        self.color = color

    def __str__(self):
        return self.color.format(self.data)


class ColorStrArr(object):
    def __init__(self, base_color: Optional[AsciiColor] = None):
        self._base_color = base_color
        self._cs_arr: List[Union[str, ColorStr, SimpleColorStr]] = []

    @property
    def base_color(self) -> Optional[AsciiColor]:
        return self._base_color

    @base_color.setter
    def base_color(self, color: Optional[AsciiColor]):
        if color:
            self._base_color = color

    def add(self, cs: Union[str, ColorStr, SimpleColorStr]):
        if cs:
            self._cs_arr.append(cs)

    def __str__(self) -> str:
        ret = ''
        for cs in self._cs_arr:
            if self.base_color and isinstance(cs, ColorStr):
                cs.base_color = self.base_color
            ret += str(cs)
        return ret


class Colors(object):
    NONE = AsciiColor()
    RED = AsciiColor(fg="red")
    LightRed = AsciiColor(fg="light_red")
    Green = AsciiColor(fg="green")
    LightGreen = AsciiColor(fg="light_green")
    Black = AsciiColor(fg="black")
    Purple = AsciiColor(fg="purple")
    Cyan = AsciiColor(fg="cyan")
    LightCyan = AsciiColor(fg="light_cyan")
    Gray = AsciiColor(fg="gray")
    LightGray = AsciiColor(fg="light_gray")
    Blue = AsciiColor(fg="light_blue")
    LightBlue = AsciiColor(fg="light_blue")
    Yellow = AsciiColor(fg="yellow")
    LightYellow = AsciiColor(fg="light_yellow")

    @staticmethod
    def print_color_table():
        """
        prints table of formatted text format options
        """
        for style in range(10):
            for fg in [*range(30, 38), *range(90, 98)]:
                s1 = ''
                for bg in [*range(40, 48), *range(100, 108)]:
                    _format = ';'.join([str(style), str(fg), str(bg)])
                    s1 += AsciiColor(style=style, fg=fg, bg=bg).format(_format) + " "
                print(s1)
            print('\n')


def red(msg):
    print(Colors.RED.format(msg))


def green(msg):
    print(Colors.Green.format(msg))


def yellow(msg):
    print(Colors.Yellow.format(msg))


def light_blue(msg):
    print(Colors.LightBlue.format(msg))


def purple(msg):
    print(Colors.Purple.format(msg))


def cyan(msg):
    print(Colors.Cyan.format(msg))


def light_gray(msg):
    print(Colors.LightGray.format(msg))


def black(msg):
    print(Colors.Black.format(msg))


if __name__ == '__main__':
    # 打印色表
    # Colors.print_color_table()
    # log()
    target = ColorStr("白日依山尽，黄河入海流。欲穷千里目，更上一层楼。", base_color=Colors.LightCyan)
    target.set_color(3, 10, Colors.Green)
    target.set_color(10, 15, Colors.Blue)
    target.set_color(15, 20, Colors.RED)
    target.set_color(11, 21, Colors.Yellow)
    print(target)
    red("白日依山尽")
    yellow("黄河入海流")
    purple("欲穷千里目")
    light_blue("更上一层楼")
    # 11:01:34.321#bangjob@main#22943❗#D#ZLogDebug(ZCMTraceDataDBMgr) #upload msg list is empty!!!
    print(AsciiColor(fg="light_gray").format("11:01:34.321#bang@main#22943❗#")
          + AsciiColor(fg="green", style="underline").format("D")
          + AsciiColor(fg="light_green").format("#ZLogDebug(TraceDataDBMgr)#")
          + str(ColorStr("upload msg list is empty!!!", base_color=AsciiColor(fg="green", style="italic"))
                .set_color(5, 10, AsciiColor(style="underline", bg="black"))
                .set_color(10, 15, AsciiColor(style="crossed"))
                )
          )
