Kictor
======

A dictionary based on the console, 一个基于控制台的词典工具, 兼容 Python2 和 Python3。

目前主要接入了有道词典、百度翻译、爱词霸三个开放字典、翻译 API 接口。

## 功能简介

- 支持有道词典、百度翻译、爱词霸三个 API 接口查词;
- 支持单词发音;
- 支持划词查询.

使用帮助：

```
-a {youdao,baidu,iciba}, --dict-api {youdao,baidu,iciba}
                      Specify which dict API to use, default youdao.
-r, --read            Read out the word, use festival on Linux.
-x, --selection       Show explaination of current selection.
-t, --text            Show plain text, without ascii color chars.
--debug               Debug mode.
```

## 控制台模式

如果不输入任何查询内容，则默认启动控制台查词模式。在控制台模式下支持执行 shell 命令，但需要加上 `!` 前缀，同时支持切换查词接口：

- `@youda` 切换到有道翻译
- `@baidu` 切换到百度翻译
- `@iciba` 切换到爱词

当输入 `@exit`、`@quit` 或者 `Ctrl+D` 时退出控制台模式，输入 `@help` 可以查看帮助。


## 配置文件

配置文件主要用于配置各开放平台的 API 地址、AppKey 等。配置内容可参考 [示例配置文件](config.example.ini)。

配置文件名可以 `kictor.ini` 或者 `kictor.conf`，程序会搜索下列目录下的配置文件：

- /etc/
- /usr/local/etc/
- ~/.config/
- ~/.local/etc/
- ~/.kictor/

此外，程序还会搜索 `~/.kictor/` 和程序运行目录下的 `config.ini` 配置文件。


## 依赖的系统工具

- xclip 用于划词查询
- festival 用于单词发音

Debian/Ubuntu 安装：

> apt-get install xclip
>
> apt-get install festival


## 安装与使用

克隆本项目到本地，然后进入项目目录执行：

> pip install .

**注：** 使用需保证系统有 Python 环境，且版本大于 2.6。


## 更新日志

#### 2018.01.23

- 使用标准库 cmd 模块重写控制台模式
- 控制台模式每次查完次之后手动执行一次内存回收

#### 2018.01.22

- 用 urllib 库代替 requests 库，不再依赖任何第三方库
- 修正部分代码风格

-------------
[Huoty](http://konghy.cn)   2016-10-18
