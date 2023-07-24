# README

基于`python3.8.0`和`windows11`

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
后期给加密了，所以无法修改...，破解版在`test`分支里
## 数据库

如果你想要用`QtSql`，那问题会像蚂蚁一样多！

### 攻略

如果你发现连接数据库连不上，是因为你没有`mysql`的`dll`文件

我使用的`pyQt5.15.9`，根据自己所配置的`pyqt5`版本下载驱动

驱动在这里[下载](https://github.com/thecodemonkey86/qt_mysql_driver/releases?page=4), 请搭配[教程](https://blog.csdn.net/qq_41264992/article/details/120933623)食用

所以我使用`pymysql`专门对接`mysql`和`python`

不要用它原生的，不然你会掉入问题黑洞......

### 细节

#### 数据库名

`codereview`

#### 数据库表 `user`
```sql
user{
    id: VARCHAR(50),
    username: VARCHAR(100),
    password: VARCHAR(200),
    salt: BINARY(64),
    aes_key: BINARY(32),
}
```
#### 数据库表 `danger_func`
含自增`id`
```sql
danger_func{
    user_id: VARCHAR(50),
    func_name: VARCHAR(100),
    level: VARCHAR(50),
    solution: VARCHAR(300),
    id: auto_increment
}
```
#### 数据库表`files`
含自增`id`

公钥`pubilc_key`用于加密,私钥`private_key`存于`user`表用于解密

`report`有三种形式 : `doc/docx` `pdf` `md`

```sql
files{
    user_id: VARCHAR(50),
    report_type: VARCHAR(10),
    report_path: VARCHAR(200),
    log_path: VARCHAR(200),
    id: auto_increment
}
```
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

## C/C++函数标识、跳转

### AST语法树

通过语法树节点，得到函数声明、函数定义、函数调用、变量声明、变量赋值、运算符，返回....

#### LLVM安装、clang库安装

需要安装`windows64.exe`的`LLVM`，并把`???/???/bin/libclang.dll`加入环境变量里。

[安装链接](https://github.com/llvm/llvm-project/releases/tag/llvmorg-16.0.0)

之后即将封神！看看`python`库有多离谱，安装`pip install clang`安装的是`clang`调用的接口`api`

#### 生成一棵针对某个文件的语法树

调用`clang.index`模块里的多个类:

```python
from clang.cindex import Index, Config
# 真好啊 API!
# 配个环境
libclangPath = r"???\????\bin\libclang.dll"
Config.set_library_file(libclangPath)
# 写你想要分析的路径 c/cpp/hh/cc/h文件
file_path = r"test_no_headers.c"
index = Index.create()
your_father = index.parse(file_path)
AST_Root = your_father.cursor
```
#### 简易分词 
之前分词还看了半天的`flex`, 呵呵T^T, 这里直接`?`句话秒了
```python
cursor_content = ""
for token in AST_Root.get_tokens():
    cursor_content += token.spelling + '\n'
print(cursor_content)
```
#### 分类内容
传入语法树的根，查看`api`接口提炼关键字和内容

`api`: `???/???/???/?????/Lib/site-packages/clang/cindex.py`

```python
def iterAST(cursor):
    from clang.cindex import CursorKind
    for cur in cursor.get_children():
        if cur.kind == CursorKind.FUNCTION_DECL:
            if cur:
                # 函数声明
                print("FUNCTION_DECL: {}".format(cur.spelling))
            for cur_item in cur.get_children():
                if cur_item.kind == CursorKind.CALL_EXPR:
                    # 函数调用
                    print("CALL_EXPR: {}".formate(cur_item.spelling))
        elif cur.kind == CursorKind.VAR_DECL:
            if cur:
                # 变量声明
                print("VAR_DECL: {}".format(cur.spelling))
        elif cur.kind == CursorKind.FIELD_DECL:
            if cur:
                # 字段声明
                print("FIELD_DECL: {}".format(cur.spelling))
        elif cur.kind == CursorKind.TYPEDEF_DECL:
            if cur:
                # 类型定义
                print("TYPEDEF_DECL: {}".format(cur.spelling))
        else:
            pass
            # done??
        # 递归调用
        iterAST(cur)
# 入口
iterAST(AST_Root)
```
### 初级跳转

对，没错，依旧是通过绝对位置硬算坐标TVT~~~

~~但是已经算过很多次了，所以问题不大~~

计算方法大致就是 : 从上面的语法树里获取到关键位置`*position`

`position = (start_line, start_index, end_line, end_index)`
`positions_func = [position_0,position_1,position_2, ...,position_n]`

传入高亮函数`highlight_all_text(positions)`里进行高亮

### 中级跳转
为什么要分初级还是中级?

初级就是只能在同一个文件里跳转声明\定义\调用

中级就是在不同文件里跳转声明\定义\调用,这里只限制头文件\源文件

高级就是在所有项目文件里面跳转,我暂时还不会...
#### 问题根源
因为如果你把函数的声明写到头文件里，再引用头文件，那么你需要跳转这个函数的时候就会在原来的位置找不到声明...

如果在文件里存在标准头文件，就会把里面的函数一起分析了，这就会分析上千行......

#### 初级解决方案

在文本编辑器里面显示源文件带头文件的内容，但是我实际上分析的时候，传入的内容是含注释掉头文件的源文件内容.

这样之后文本编辑器上的文本位置不会乱，而分析器也不会分析头文件，但是这样会生成临时文件，所以在分析结束之后把它删掉，看起来就是分析了源文件的内容.(๑•̀ㅂ•́)و✧)

对于分析的时候先查一轮源文件里自定义的头文件集合，再对头文件筛选一遍函数声明\定义.

接着对临时文件内容筛选一遍函数声明\定义\调用,在函数声明里查没有在源文件列表里出现的目标

再到头文件函数声明列表里查一遍，查到就输出其信息.

```python
filename = r'???/????/???/test.cpp'

def get_headers(filename):
    import re
    with open(filename, 'r', encoding='utf-8') as file:
        contents = file.readlines()
    headers = []
    # 正则表达式筛选所有 #include"???.h" / #include "???.h" 自定义头文件
    pattern = r'#include\s*["]\s*(\w+\.h)\s*["]'
    for item in contents:
        match = re.search(pattern, item)
        if match:
            dependency = match.group(1)
            headers.append(dependency)
    return headers

# 对所有自定义引用的头文件分析
def headerAnalyzer(filename):
    # 伪代码 FunctionDump是存储过滤结果的类
    headers_path = get_headers(filename)
    headers_analyzers_list = []
    for item in headers_path:
        analyzer_obj = FunctionDump(filename)
        analyzer_obj.Launcher()
        analyzer_obj.show_details()
        headers_analyzers_list.append((item, analyzer_obj))
    return headers_analyzers_list

# 除去头文件的源代码分析
def excludeHeaderAnalyzer(filename):
    # 伪代码 FunctionDump是存储过滤结果的类
    analyzer_obj = FunctionDump(filename)
    analyzer_obj.Launcher()
    analyzer_obj.show_details()
    return analyzer_obj

def preProcessTools(filename, keyword):
    # 伪代码 举声明函数查找例子
    header_objs = headerAnalyzer(filename)
    exclude_header_objs = excludeHeaderAnalyzer(filename)
    # 先把所有名字存起来 之后筛选
    exclude_declaration_name_list = [item.function_name for item in exclude_header_objs.function_declaration_list]
    # 设置声明标志位
    declared_flag = True
    target_function_name = keyword
    if target_function_name not in exclude_declaration_name_list:
        declared_flag = False
    # 根据标志位开始判断是哪个集合里的函数声明 是头文件里的就查头文件 否则查源文件
    if not declared_flag:
        for item in header_objs:
            path, header_obj = item
            for function_obj in header_obj.function_declaration_list:
                if target_function_name == function_obj.function_name and function_obj.declared_contents is not None:
                    print(function_obj.declared_contents)
                    print(function_obj.declared_location)
    elif declared_flag:
        for item in exclude_header_objs.function_declaration_list:
            if target_function_name == item.function_name and item.declared_contents is not None:
                print(item.declared_contents)
                print(item.declared_location)
    # ... 基本照猫画虎 大致思路如上 看具体代码的时候能更清楚地明白我在说什么??0-<我自己写的时候都蒙圈好几次
```

#### 中级解决方案
优化函数调用，加上三种类型判断

1. 只有一个源文件 `>> ???.c/???.cpp`

    函数声明、定义、调用都在同一个源文件里

2. 只有一个源文件和多个头文件 `>> ???.c/???.cpp + (??.h,???.h,????.h)`

    函数声明/定义在头文件,源文件可能含声明、定义、调用

3. 多个源文件和多个头文件，但只有一个源文件含`main`函数 `>> ???.cpp/????.cpp/main.cpp +  (??.h,???.h,????.h)`

    函数声明/定义在头文件,除`main`函数以外的源文件可能包含声明、定义,含`main`的源文件可能包含声明、定义、调用

把所有源文件的内容拼接在一起，最后拼接`main`函数的内容...组合器问世！
```python
# 组合器
class DefinitionCallExpressCombiner:
    def __init__(self, file_path):
        self.file_path = file_path
        self.headers = []
        self.main_sign = None
        self.definition_contents = []
        self.mix_contents = []
        self.main_length = 0
        self.offset_length = 0

    def find_all_files(self, filepath):
        directory, _ = os.path.split(filepath)
        file_list = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.c') or file.endswith('.cpp'):
                    file_list.append(os.path.abspath(os.path.join(root, file)))
        return file_list

    def has_main_function(self, file_path):
        with open(file_path, "r") as file:
            content = file.read()
            return "int main(" in content

    def getDefinitionCodes(self):
        source_files = self.find_all_files(self.file_path)
        for file_path in source_files:
            with open(file_path, "r") as file:
                content = file.readlines()
                if self.has_main_function(file_path):
                    if self.main_sign is None:
                        self.main_sign = file_path
                    else:
                        # print('main function is None.')
                        pass
                else:
                    self.definition_contents += content

    def Combiner(self):
        self.getDefinitionCodes()
        path, name = split(self.main_sign)
        name = '.' + name
        temp_path = os.path.join(path, name)
        with open(self.main_sign, "r", encoding='utf-8') as main_file:
            main_file_content = main_file.readlines()
            self.main_length = len(main_file_content)
        last_line = self.definition_contents[-1]
        if last_line == '}\n':
            pass
        elif last_line == '}':
            self.definition_contents[-1] = '}\n'
        if main_file_content:
            self.mix_contents = self.definition_contents + main_file_content

        new_data = ["//" + line if line.startswith("#include") else line for line in self.mix_contents]
        with open(temp_path, 'w', encoding='utf-8') as temp_obj:
            temp_obj.writelines(new_data)
        self.offset_length = len(new_data) - self.main_length
        return temp_path
```
调用这个函数计算真正的`main`函数声明、定义、调用函数的位置坐标，覆盖临时文件的数据，返回数据
```python
def multiCallExpressCombiner(self, filepath):
    combiner = DefinitionCallExpressCombiner(filepath)
    temp_filepath = combiner.Combiner()
    call_analyzer = FunctionDump(temp_filepath)
    call_analyzer.analyseLauncher()
    os.remove(temp_filepath)

    offset = combiner.offset_length
    function_declaration_list = []
    function_definition_list = []
    function_call_express_list = []
    for item in call_analyzer.function_declaration_list:
        if item.declared_location[0] > offset:
            start_line, start_index, end_line, end_index = item.declared_location
            item.declared_location = (start_line - offset, start_index, end_line - offset, end_index)
            function_declaration_list.append(item)
        else:
            continue
    for item in call_analyzer.function_definition_list:
        if item.definition_location[0] > offset:
            start_line, start_index, end_line, end_index = item.definition_location
            item.definition_location = (start_line - offset, start_index, end_line - offset, end_index)
            function_definition_list.append(item)
        else:
            continue
    for item in call_analyzer.function_callexpress_list:
        if item.call_express_location[0] > offset:
            start_line, start_index, end_line, end_index = item.call_express_location
            item.call_express_location = (start_line - offset, start_index, end_line - offset, end_index)
            function_call_express_list.append(item)
        else:
            continue
    # 覆盖原文
    call_analyzer.function_declaration_list = function_declaration_list
    call_analyzer.function_definition_list = function_definition_list
    call_analyzer.function_callexpress_list = function_call_express_list
    return call_analyzer
```
## 下载文件

登录之后的用户进主页面 进行代码审计之后生成的报告文件

生成的报告是即时审计结果 数据库里存储的是用户自己添加的危险函数数据

饼子图也是即时审计结果

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