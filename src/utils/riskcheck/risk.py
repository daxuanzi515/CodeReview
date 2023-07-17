import os
import re
from os.path import split

from src.utils.riskcheck.lex import Run_Lexer
from src.config.config import Config

class Leak(object):
    def __init__(self, fileName='', line='', name='', type=''):
        self.fileName = fileName
        self.line = line
        self.name = name
        self.type = type
        self.flag = 0
        self.apply = False


class RiskReport(object):
    def __init__(self, fileName='', riskName='', line='', riskLev='', solve=''):
        self.fileName = fileName
        self.riskName = riskName
        self.line = line
        self.riskLev = riskLev
        self.solve = solve

class InvalidReport(object):
    def __init__(self, fileName='', line='', name=''):
        self.fileName = fileName
        self.line = line
        self.name = name

class RiskFind(object):
    def __init__(self, funlist, vallist, inifile):
        self.funlist = funlist
        self.vallist = vallist
        self.inifile = inifile
        self.riskfunlist = []
        self.validfun = []
        self.validval = []
        self.invalidfun = []
        self.invalidval = []

        self.leakval = []


    def get_all_file(self, filepath):
        self.filelist = []
        files = os.listdir(filepath)
        for fi in files:
            if self.inifile.endswith(".c"):
                if re.match("(\w*)\.c$", fi) != None:
                    fi_d = filepath + '/' + fi
                    # 如果不目录
                    if not os.path.isdir(fi_d):
                        self.filelist.append(fi_d)
            elif self.inifile.endswith(".cpp"):
                if re.match("(\w*)\.cpp$", fi) != None:
                    fi_d = filepath + '/' + fi
                    # 如果不目录
                    if not os.path.isdir(fi_d):
                        self.filelist.append(fi_d)
    def invalid_find(self, fun, l):
        le = Run_Lexer(inFile=self.inifile)
        le.runLexer()
        code = le.code
        flag = 0
        first = True
        l.append(fun)
        fline = fun.line.split(":")[-1]
        for line in code[int(fline):]:
            if len(line) > 1:
                if line[1] == '{' or line[-1] == '{':
                    flag += 1
                    first = False
                if line[1] == '}' or line[-1] == '}':
                    flag -= 1
            if flag == 0 and first == False:
                break
            for v in self.vallist:
                if v.name in line:
                    index = line.index(v.name)
                    if len(line) > index + 1:
                        if line[index + 1] != "(" and v.line != "line:" + str(line[0]) and v in fun.list:
                            self.validval.append(v)
                    else:
                        if v.line != "line:" + str(line[0]) and v in fun.list:
                            self.validval.append(v)
            for v in self.vallist:
                if v.name in line and v not in self.validval and v.filepath == fun.filepath:
                    if v.father == fun.name or v.father == "":
                        index = line.index(v.name)
                        if len(line) > index + 1:
                            if line[index + 1] != "(" and v.line != "line:" + str(line[0]):
                                self.validval.append(v)
                        else:
                            if v.line != "line:" + str(line[0]):
                                self.validval.append(v)
            for f in self.funlist:
                if f.name in line and f not in self.validfun:
                    index = line.index(f.name)
                    if line[index + 1] == '(' and f.line != "line:" + str(line[0]):
                        self.validfun.append(f)
        if self.validfun != l:
            for f in list(set(self.validfun) - set(l)):
                self.invalid_find(f, l)

    def leak_find(self, fun):
        le = Run_Lexer(inFile=self.inifile)
        le.runLexer()
        code = le.code
        flag = 0
        first = True
        fline = fun.line.split(":")[-1]
        indexLine = []
        # 找到该函数所在行数范围
        for line in code[int(fline):]:
            if len(line) > 1:
                indexLine.append(line[0])
                if line[1] == '{' or line[-1] == '{':
                    flag += 1
                    first = False
                if line[1] == '}' or line[-1] == '}':
                    flag -= 1
            if flag == 0 and first == False:
                break
        for v in self.vallist:
            if v.father == fun.name:
                if v.val_type.endswith("int *") or v.val_type.endswith("char *"):
                    leak = Leak()
                    for l in indexLine:
                        with open(self.inifile) as f:
                            content = f.readlines()[int(l) - 1]
                        if self.inifile.endswith(".c"):
                            if "malloc" in content and v.name in code[int(l)]:
                                leak.flag += 1
                                leak.apply = True
                            if "free(" + v.name + ")" in content:
                                leak.flag -= 1
                        elif self.inifile.endswith(".cpp"):
                            if "new" in content:
                                if v.name in code[int(l)]:
                                    leak.flag += 1
                                    leak.apply = True
                            if "delete " + v.name in content:
                                leak.flag -= 1
                    if leak.flag != 0:
                        leak.fileName = self.inifile
                        leak.name = v.name
                        leak.line = v.line
                        if leak.flag == 1 and leak.apply:
                            leak.type = "指针未释放！"
                        else:
                            leak.type = "指针重复释放"
                        self.leakval.append(leak)
                    elif leak.flag == 0 and leak.apply == False:
                        leak.fileName = self.inifile
                        leak.name = v.name
                        leak.line = v.line
                        leak.type = "野指针"
                        self.leakval.append(leak)


    def risk_fun(self, file_path=None):
        self.fun_name = []
        self.fun_vul = []
        self.fun_sol = []
        config_obj = Config()
        config_ini = config_obj.read_config()
        fun_file = ""
        if file_path == None:
            fun_file = config_ini['main_project']['project_name'] + config_ini['scanner']['common_rule']
        else:
            fun_file = file_path
        f = open(fun_file, "r", encoding='utf-8')
        while True:
            s = f.readline().strip("\n")
            s = s.strip("\r")
            if s:
                self.fun_name.append(s.split('\t')[0])
                self.fun_vul.append(s.split('\t')[1])
                self.fun_sol.append(s.split('\t')[2])
            else:
                break
        f.close()
        path, name = split(self.inifile)
        self.get_all_file(path)
        for fn in self.filelist:
            f = open(fn, "r")
            s = f.readlines()
            f.close()
            for fun in self.fun_name:
                pattern = re.compile("\W" + fun + "[(]")
                for ss in s:
                    if re.search(pattern, ss) != None:
                        report = RiskReport()
                        report.line = s.index(ss) + 1
                        index = self.fun_name.index(fun)
                        report.fileName = fn
                        report.riskName = self.fun_name[index]
                        report.riskLev = self.fun_vul[index]
                        report.solve = self.fun_sol[index]
                        self.riskfunlist.append(report)

        for f in self.funlist:
            if f.name == "main":
                self.validfun.append(f)
            self.invalid_find(f, [])
            if self.inifile.endswith(".c") or self.inifile.endswith(".cpp"):
                self.leak_find(f)

        for f in list(set(self.funlist) - set(self.validfun)):
            inval = InvalidReport()
            inval.fileName = f.filepath
            inval.line = f.line
            inval.name = f.name
            self.invalidfun.append(inval)
        for f in list(set(self.vallist) - set(self.validval)):
            inval = InvalidReport()
            inval.fileName = f.filepath
            inval.line = f.line
            inval.name = f.name
            self.invalidval.append(inval)







