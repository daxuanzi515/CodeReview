# README

基于`python3.8.0`和`windows11`

其他版本`3.7.0`我在本机测试之后也能使用

数据库：`mysql 8.0.28`

连接方式是`pymysql` 不是`QtSql.QSqlDatabase`

安装依赖 `pip install -r requirements.txt`s

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

搜`QtabBar`，修改成为如下，就是把`text-transform`的`uppercase`修改为`none`
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

驱动在这里[下载](https://github.com/thecodemonkey86/qt_mysql_driver/releases?page=4), 请搭配[教程](https://blog.csdn.net/qq_41264992/article/details/120933623)食用

所以我使用`pymysql`专门对接`mysql`和`python`

不要用它原生的，不然你会掉入问题黑洞......

## 编辑器

使用`QsciScintilla`

自定义文本编辑器动作和配置，只写了`cpp`和`c`的基本筛选器

### 参考文档

`python`的基础`api`官方文档在[这里](https://qscintilla.com),但是只是初级小白版

后续的一系列骚操作请去正规的`Scintilla`官网上看接口是怎么写的

### 光标跳转

光标跳转是我一步步实验出来硬写的，结合大爹`chatgpt`的分析~~(它的唯一作用就是帮我分析了参数含义)~~,再修改的.

### 指定区域查找

硬算出范围，然后暴力，因为`api`比较底层

## 终端模拟

### 基本原理

这里直接让后台开一个子进程，用线程加速，对于特殊操作做区分，重定到`print`操作里输出终端内容

### 切换目录的秘密

其实子进程通过命令行是无法直接切换的，它至始至终都只能在你调用它的地方。

但是可以通过这个`os.chdir(directory)`指定当前工作目录为`directory`，这样就完美解决！

### 清屏

`cls`之后会让输出为空，但因为是模拟，所以直接强制把输出框内容清除就能达到效果

### 自定义颜色

使用的`chatgpt3.5`主页的颜色作为终端配色

背景:`#143113`,字体:`#FF8BFF && Consolas`

## 下载文件

登录之后的用户进主页面 进行代码审计之后生成的报告文件

首先先存在数据库里 下载的时候才会取

## 控制跳转

请按照格式添加窗口, 否则全是`bug`

## 导出依赖 

只会导出项目所使用的依赖 而不是所有依赖

`pip install pipreq`

关闭代理之后再在当前项目文件夹操作, 不然爆代理错误.

要用`utf-8`否则爆`gbk`错误,因为我的主机是`win11`.

`pipreqs ./ --encoding=utf8`

## 文件缺失

`clang.exe` 请自己去下载捏,然后放在`compile`目录下

如果遇到`compile`出现问题，因为不是我负责的部分

我就直说了:

它的最大缺陷就是只能处理有依赖的`.c/cpp`,`.h`文件编译问题

它只能把有依赖关系的文件放在`test\init_data\test_data\test_c`里，因为它强制查含`.c`的文件，没有更新的分析，这里后续是可以修改的

### 举个例子

`test.h`里有函数`int add(int a,int b)`声明
```c++
#include<stdio.h>
#include<stdlib.h>
int add(int a, int b);
```

`test.cpp`里对其进行引用`#include "test.h"`,并调用`add(12,15)`
```c++
#include "test.h"
int sum;
int main()
{
    sum = add(12, 15);
    printf("sum = %d",sum);
    return 0;
}
```
`test2.cpp`里实现了`add`方法
```c++
#include "test.h"
int add(int a,int b)
{
    return a+b;
}
```
放在一个文件夹下用`clang.exe`编译，会自动查找`test.h`只要在同一文件夹下就可以
```bash
clang.exe -o test.exe test.cpp test2.cpp    
```
当你不想在同一文件夹下生成`exe`文件，请指定固定的绝对路径
## 演示视频

在另一分支`test`里,暂不描述内容