# README

基于`python3.8.0`

其他版本`3.7.0`我在本机测试之后也能使用

数据库：`mysql 8.0.28`

连接方式是`pymysql` 不是`QtSql.QSqlDatabase`

安装依赖 `pip install -r requirements.txt`

## 样式

所使用的样式需要下载

```bash
pip install qt_material
```

样式表可以自定义和修改，在安装包的位置找到：

`????\????\???\Lib\site-packages\qt_material`里的`material.css.template`可以直接编辑所有样式，为了把字体调大，搜索`font-size`，修改数字为`16`：

```css
  {% if font_size %}
    font-size: {{font_size|density(density_scale, density_interval=1)}}px;
  {% else %}
    font-size: {{14|density(density_scale, density_interval=1)}}px;
  {% endif %}
```

把标签页名字改小写，也就不应用大写

搜QtabBar，修改成为如下，就是把`text-transform`的`uppercase`修改为`none`
```css
    QTabBar{
      text-transform: none;
      font-weight: bold;
    }
```

## 配置

移植项目需要先修改`config.py`里`config.ini`的绝对路径

```python
self.path = r'???\???\CodeReview\src\config\config.ini'
```

再到`config.ini`里修改如下的值，注意要在project_name这里加上\

```python
[main_project]
project_name = 你项目文件夹所在位置\
[mysql]
db_password = 你的密码
...
```

## 数据库

如果你想要用`QtSql`，那问题会像蚂蚁一样多！

### 攻略

如果你发现连接数据库连不上，是因为你没有`mysql`的`dll`文件

我使用的`pyQt5.15.9`，根据自己所配置的`pyqt5`版本下载驱动

驱动在这里[下载](https://github.com/thecodemonkey86/qt_mysql_driver/releases?page=4), 请搭配[教程](https://blog.csdn.net/qq_41264992/article/details/120933623?spm=1001.2014.3001.5501)食用

所以我使用`pymysql`专门对接`mysql`和`python`

不要用它原生的了，不然你会掉入问题黑洞......

## 编辑器

使用`QsciScintilla`

快速自定义文本编辑器动作和配置

## 下载文件

登录之后的用户进主页面 进行代码审计之后生成的报告文件

首先先存在数据库里 下载的时候才会取

## 控制跳转 controller.py

请按照格式添加窗口, 否则全是bug

## 导出依赖 

只会导出项目所使用的依赖 而不是所有依赖

`pip install pipreq`

关闭代理之后再在当前项目文件夹操作, 不然爆代理错误.

要用`utf-8`否则爆`gbk`错误,因为我的主机是`win11`.

`pipreqs ./ --encoding=utf8`

## 演示视频

在另一分支`test`里,暂不描述内容