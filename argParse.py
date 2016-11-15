#-*- utf-8 -*-

class ArgParser():
    def __init__(self):
        self.flag_list = list()
        self.parse_dict = dict()
    def init_arg(self,arg_dict):
        #arg :init the arg mab be receive
        #flag: true: is flag type no para followed,false:has follwed paras
        for k,v in arg_dict.items():
            if v:
                self.flag_list.append(k)
            self.parse_dict[k]=''

    def parse(self,line):
        maxLen=len(line)
        if maxLen==1:
            return
        i=1
        while(i<maxLen):
            if line[i] in self.parse_dict:
                if line[i] in self.flag_list:
                    self.parse_dict[line[i]]='true'
                else:
                    self.parse_dict[line[i]]=line[i+1]
                    i = i + 1
            i = i + 1
    def get_arg(self,arg):
        if arg in self.parse_dict:
            return self.parse_dict[arg]
        else:
            return null

    def arg_print(self):
        print self.parse_dict
        for k,v in self.parse_dict.items():
            print 'arg:',k
            print 'value:',v


if __name__=='__main__':
    parser = ArgParser()
    parser.init_arg('-a',False)
    parser.init_arg('-b',True)
    parser.parse(['fun','-b','-a','A'])
    parser.arg_print()


