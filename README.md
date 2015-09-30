# Campanella-rapidfork

Campanella的话题后端

## 依赖

- Python 3.4.2
- Tornado 4.2.1
- ……

## 运行

```shell
./server.py [--port=8080] [--num=4] [--debug]
```
不填写任何参数时，根据settings.py中的设置启动。

- `--debug`
单实例debug模式启动（会即时响应更改，并强制单进程）
- `--port=8080`
指定监听端口
- `--num=4`
指定进程数量

## 目录结构

```
rapidfork [apphome]
|-controllers
    |-__init__.py
    |-...
|-models
    |-__init__.py
    |-...
|-views
    |-__init__.py
    |-...
|-__init__.py
|-urls.py [app路由配置]
applications.py
server.py
settings.py
urls.py
```
