Kictor
======

Online dictionary based on the console, 基于控制台的在线词典, 兼容 Python2 和 Python3。

## 功能简介

- 支持有道词典、百度翻译、爱词霸三个 API 接口查词;
- 支持单词发音;
- 支持划词查询;
- 支持输出爱词霸每日一句.

```
-b, --baidu      Select baidu api.
-i, --iciba      Select iciba api.
-d, --daysay     Print daily sentence of iciba.
-o, --resources  Print online web resources.
-s, --speech     Print URL to speech audio.
-r, --read       Read out the word, use festival on Linux.
-x, --selection  Show explaination of current selection.
```

**注：** 有道接口功能相对较全，所以默认的查词接口是有道。百度翻译结果太粗糙，爱词霸不支持句子翻译，但是单词的翻译还是很完美的。可以根据需要选择合适的接口。

## 控制台模式

如果不输入任何查询内容，则默认启动控制台查词模式。在控制台模式下支持执行 shell 命令，但需要加上 `!` 前缀，同时支持切换查词接口：

- `@select_youdao` 切换到有道翻译
- `@select_baidu` 切换到百度翻译
- `@select_iciba` 切换到爱词

当输入 `@exit`、`@quit` 或者 `Ctrl+D` 时退出控制台模式。

## 每日一句

- `kict -d` 输出爱词霸的每日一句，

## 依赖的系统工具

- xclip 用于划词查询
- festival 用于单词发音

Debian/Ubuntu 安装：

> apt-get install xclip
>
> apt-get install festival

## 安装与使用

克隆本项目到本地，然后进入项目目录执行：

> ln -s $PWD/kict.py /usr/bin/kict

或者

> cp $PWD/kict.py /usr/bin/kict

项目依赖第三库 `requests`，可以通过 pip 安装：

> pip install requests

**注：** 使用需保证系统有 Python 环境，且版本大于 2.6。

## 更新日志

#### 2018.01.23

- 使用标准库 cmd 模块重写命令行模式

#### 2018.01.22

- 用 urllib 库代替 requests 库，不再依赖任何第三方库
- 修正部分代码风格

-------------
[Huoty](http://konghy.cn)   2016-10-18
