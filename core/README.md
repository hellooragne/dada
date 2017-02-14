
我先把结构介绍一下

启动是用 python web.py

web.py 里面写着默认端口号（本地测试用）

默认数据库是 meitian，data_structure的所有sql文件，每一个对应一个数据库表


要启动项目，需要python2.7加上一些库，所有的纯python库都已经添加到项目里面去了，只有像 mysql-python, pycurl, PIL这样的含有binary的库需要本地安装

web.py 里面可以找到 url 对应的 controller，每个controller是一个类

static/ 里面放所有的静态文件比如.js .css .swf .jpg .png

template/ 里面是需要渲染的 .html 文件
