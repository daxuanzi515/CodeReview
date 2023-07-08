import os.path


class FunctionValue:
    def __init__(self, filepath = '', name = '', val_type = '', type = "",line = ""):
        self.filepath = filepath
        self.name = name
        self.val_type = val_type
        self.type = type
        self.line = line
        self.list = []
        self.father = ""
        self.flag = 0

    def add(self, value):
        self.list.append(value)


class funvaluefind():
    def __init__(self,filename, tagsfile, ctagspath):
        self.filename = filename
        self.tagsfile = tagsfile
        self.ctagspath = ctagspath
        self.funlist = []
        self.vallist = []

    def get_fun_value(self):
        filename = self.filename
        tagsfile = self.tagsfile
        cmd = self.ctagspath + " --languages=c,c++ -R -I argv --kinds-c=+defglmpstuvx --kinds-c++=+defglmpstuvx --fields=+n -o " + tagsfile + " " + filename
        # cmd = "ctags.exe --languages=c -R -I argv --kinds-c=+defglmpstuvx --fields=+n -o " + tagsfile + " " + filename
        os.system(cmd)
        f = open(self.tagsfile, "r")
        code = f.readlines()
        f.close()
        for line in code:
            if line.startswith("!_TAG"):
                continue
            split_line = line.split('\t')
            # print("split_line:", split_line)
            fun = FunctionValue()
            fun.name = split_line[0]
            # print("funname:", fun.name)
            fun.filepath = split_line[1]
            # print("len:", len(split_line))
            if len(split_line) == 8 or len(split_line) == 6:
                fun.line = split_line[4]
                fun.type = split_line[3]
                if fun.type == 'l':
                    fun.val_type = split_line[6].split(":")[-1]
                    fun.father = split_line[5].split(":")[-1]
                    self.vallist.append(fun)
                else:
                    fun.val_type = split_line[5].strip("\n").split(":")[-1]
                    if fun.type == 'f':
                        self.funlist.append(fun)
                    else:
                        if fun.type == "s":
                            fun.val_type = "struct"
                        self.vallist.append(fun)
            elif len(split_line) == 9:
                fun.line = split_line[5]
                fun.type = split_line[4]
                if fun.type == 'm':
                    fun.val_type = split_line[7].split(":")[-1]
                    fun.father = split_line[6]
                    self.vallist.append(fun)
                elif fun.type == 'l':
                    fun.val_type = split_line[7].split(":")[-2] + ' ' + split_line[7].split(":")[-1]
                    fun.father = split_line[6].split(":")[-1]
                    self.vallist.append(fun)
        for i in self.vallist:
            if i.type == 'm':
                for v in self.vallist:
                    if v.type == 's':
                        self.vallist[self.vallist.index(v)].add(i)
            elif i.type == 'l':
                for f in self.funlist:
                    if i.filepath == f.filepath and i.father == f.name:
                        self.funlist[self.funlist.index(f)].add(i)