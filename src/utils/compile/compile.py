import os.path
import re
import subprocess

# 编译
class compile(object):
    def __init__(self, inifile, outfile, clang_path):
        self.inifile = inifile
        self.outfile = outfile
        self.clang_path = clang_path

    def get_all_file(self,filepath):
        list = []
        files = os.listdir(filepath)
        for fi in files:
            if re.match("(\w*)\.c$",fi) != None:
                fi_d = filepath + '/' + fi
                # 如果不目录
                if not os.path.isdir(fi_d):
                    list.append(fi_d)
        return list

    def run_com(self):
        inifile = self.inifile
        path, name = os.path.split(inifile)
        sourfileList = self.get_all_file(path)
        res = ' '.join(sourfileList)
        env = os.environ
        cmdd = self.clang_path + ' -o '+self.outfile + " " + res
        p = subprocess.Popen(cmdd, env=env, stdout=subprocess.PIPE, stderr = subprocess.STDOUT, shell=True)
        return p

class run(object):
    def __init__(self, exefile, arg):
        self.exefile = exefile
        self.arg = arg

    def run_run(self):
        if os.path.exists(self.exefile):
            cmdd = self.exefile
            p = subprocess.Popen(cmdd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            p.stdin.write(self.arg.encode())
            p.stdin.close()
            stdout, stderr = p.communicate()
            return stdout.decode()
        else:
            return False

class comrun(object):
    def __init__(self, inif, outf, clang, arg):
        self.inif = inif
        self.outf = outf
        self.clang = clang
        self.arg = arg
    def com_run(self):
        c = compile(inifile=self.inif, outfile=self.outf, clang_path=self.clang)
        p = c.run_com()
        return_code = p.wait()
        if return_code == 0:
            cmdd = self.outf
            p = subprocess.Popen(cmdd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            p.stdin.write(self.arg.encode())
            p.stdin.close()
            stdout, stderr = p.communicate()
            return stdout.decode()
        else:
            return False

