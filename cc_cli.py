#!/usr/bin/python
import os
import sys
import readline,rlcompleter
import json
import copy
from argParse import ArgParser

def dolog(msg):
    fp = open('/tmp/cli_log','a+')
    fp.write(msg+'\n')
    fp.close()

history_log='/tmp/cc_command_history'
#cc_conf_file='/tmp/cc_conf'
cc_conf_path ='/tmp/cc_conf/'
policy_file_engine = '/tmp/cc_python_out'


g_json_dict = {'sys':{},'policy':{}} 

g_commit_add_set = set()
g_commit_chg_set = set()
g_commit_del_set = set()

g_del_all_policy = False
g_sys_chg = False

#default policy
default_policy_dict = {'domain':'default','cc_level':'low','threshold_url':10000,'threshold_srcip':100,'qos':[],'trust_list':[],'block_list':[]}
default_qos_dict = {'srcip':'','url':'','https':False,'each_srcip':False,'each_url':False,'speed':0}
default_trust_dict = {'srcip':'','url':''}

#readline
readline.parse_and_bind("tab: complete")

class VolcabCompleter:
    def __init__(self,volcab):
        self.volcab = volcab

    def complete(self,text,state):
        results = [x+" " for x in self.volcab if x.startswith(text)] + [None]
        return results[state]


#words = ['help','sysconf set','sysconf show','policy add','policy set','policy del','policy load','policy save','policy show','qos add','qos set','qos del','trust-table add','trust-table del','black-table add ','black-table del','commit','quit']
words = ['help','sysconf','policy','qos','trust-table','black-table','commit','quit']
completer = VolcabCompleter(words)

readline.set_completer(completer.complete)

def record_command(command_line):
    print 'record command'
    fp = open(history_log,'a+')
    fp.write(command_line+'\n')
    fp.close()

def fun_quit(msg):
	sys.exit(0)

def fun_help(msg):
    print 'fun_help'
    msg = '''
    usage:
       sysconf {set|show} [-l ] [-t ] [-enable {y|n}]
       policy {add|set}  <domain> [-l {high|mid|low}] [-t_url] [-t_sip] [-enable {y|n}]   
       policy del <-a|domain>
       policy {load|save} [path]
       qos {add|set} <domain> -sip -url [-eIP {y|n}] [-eURL {y|n}] [-S {y|n}] -s <speed> 
       qos del <-a|-sip -url>
       trust-table {add|del} -sip -url
       black-table {add|del} -sip -url
       commit [-a] 
       '''
    print msg

def tellEngineCommit():
    print "TODO: tell engine commit"
    if 1:
        return True
    else:
        return False

def sysConf(msg):
    #set-sys -l -t 
    global g_sys_chg
    dolog('sysConf')

    argpaser = ArgParser()
    arg_dict = {'-l':False,'-t':False,'-enable':False}
    argpaser.init_arg(arg_dict)
    argpaser.parse(msg)
    log_level = argpaser.get_arg('-l')
    log_timer = argpaser.get_arg('-t')
    enable    = argpaser.get_arg('-enable')
    if log_level != '':
        g_json_dict['sys']['log_level'] = log_level
    if log_timer != '':
        g_json_dict['sys']['log_timer'] = log_timer
    if enable != '':
        if enable=='y':
            g_json_dict['sys']['enable'] = True
        elif enable=='n':
            g_json_dict['sys']['enable'] = False 

    g_sys_chg = True

def addPolicy(msg):
    #add-policy <domain> [-l {high|mid|low}] [-t_ip] [-t_sip] 
    global g_json_dict
    dolog('addPolicy')
    if len(msg)<2:
        print 'Invalid parameters:too short'
        return

    domainName = msg[2]
    if domainName in g_json_dict['policy']:
        print 'this policy already exists!'
        return
    argpaser = ArgParser()
    arg_dict={'-l':False,'-t_url':False,'-t_sip':False,'-enable':False}
    argpaser.init_arg(arg_dict)
    argpaser.parse(msg)
    cc_level = argpaser.get_arg('-l')
    threshold_srcip = argpaser.get_arg('-t_ip')
    threshold_url = argpaser.get_arg('-t_url')
    enable = argpaser.get_arg('-enable')
    new_policy = copy.deepcopy(default_policy_dict)
    new_policy['domain'] = domainName
    log_msg = 'new policy: domain:'+domainName+' cc_level:'+cc_level+' threshold_srcip:'+threshold_srcip\
            +' threshold_url:'+threshold_url+' enable:'+enable
    dolog(log_msg)
    if cc_level != '':
        new_policy['cc_levlel'] = cc_level
    if threshold_srcip != '':
        new_policy['threshold_srcip'] = threshold_srcip
    if threshold_url != '':
        new_policy['threshold_url'] = threshold_url
    if enable != '':
        if enable=='y':
            new_policy['enable'] = True
        elif enable=='n':
            new_policy['enable'] = False

    #add to g_json_dict
    g_json_dict['policy'][domainName] = new_policy

    log_msg = 'add to g_json_dict:'+domainName
    dolog(log_msg)

    #add to g_commit_set for commit opt
    g_commit_add_set.add(domainName)

    log_msg = 'add to g_commit_add_set:'+domainName
    dolog(log_msg)

def setPolicy(msg):
    print 'setPolicy'
    #set-policy <domain> [-l {high|mid|low}] [-t_url] [-t_sip] 
    domainName = msg[2]
    if not domainName in g_json_dict['policy']:
        print 'This policy not exists, check it'
        return
    argpaser = ArgParser()
    arg_dict={'-l':False,'-t_url':False,'-t_sip':False,'-enable':False}
    argpaser.init_arg(arg_dict)
    argpaser.parse(msg)
    cc_level = argpaser.get_arg('-l')
    threshold_srcip = argpaser.get_arg('-t_sip')
    threshold_url = argpaser.get_arg('-t_url')
    enable = argpaser.get_arg('-enable')

    log_msg = 'set policy: domain:'+domainName+' cc_level:'+cc_level+' threshold_srcip:'+threshold_srcip\
            +' threshold_url:'+threshold_url+' enable:'+enable
    dolog(log_msg)

    new_policy = g_json_dict['policy'][domainName] 
    #new_policy['domain'] = domainName
    if cc_level != '':
        new_policy['cc_level'] = cc_level
    if threshold_srcip != '':
        new_policy['threshold_srcip'] = threshold_srcip
    if threshold_url != '':
        new_policy['threshold_url'] = threshold_url
    if enable != '':
        if enable=='y':
            new_policy['enable'] = True
        elif enable=='n':
            new_policy['enable'] = False

    #add to g_commit_set for commit opt
    if not domainName in g_commit_add_set:
        g_commit_chg_set.add(domainName)
        log_msg = 'add to g_commit_chg_set:'+domainName
        dolog(log_msg)

def delPolicy(msg):
    dolog('delPolicy')
    global g_del_all_policy
    if len(msg)<2 or msg[1]=='':
        print 'Invalide parameters'
        return
    if msg[2]=='-a':
        g_json_dict['policy'].clear()
        g_del_all_policy = True
        g_commit_add_set.clear()
        g_commit_chg_set.clear()
        g_commit_del_set.clear()
        return
    domainName = msg[2]
    if domainName in g_json_dict['policy']:
        g_json_dict['policy'].pop(domainName)
        if domainName in g_commit_add_set:
            g_commit_add_set.remove(domainName)
            dolog('remove from g_commit_add_set:'+domainName)
            # need not tell engine
        else:
            if domainName in g_commit_chg_set:
                g_commit_chg_set.remove(domainName)
                dolog('remove from g_commit_chg_set:'+domainName)
            g_commit_del_set.add(domainName)
            dolog('add to g_commit_chg_set:'+domainName)

def addQos(msg):
    print 'addQos'
    #add-qos <domain> -sip -url [-eIP {y|n}] [-eURL {y|n}] [-S {y|n}] -s <speed> 
    if len(msg)<6:
        print 'Invalid parameters: too short'
    domainName = msg[2]
    if not domainName in g_json_dict['policy']:
        print 'This policy not exists, check it'
        return
    argpaser = ArgParser()
    arg_dict={'-sip':False,'-url':False,'-s':False, '-S':False,'-eIP':False,'-eURL':False}
    argpaser.init_arg(arg_dict)
    argpaser.parse(msg)
    srcip = argpaser.get_arg('-sip')
    url = argpaser.get_arg('-url')
    speed = argpaser.get_arg('-s')
    each_srcip = argpaser.get_arg('-eIP')
    each_url = argpaser.get_arg('-eURL')
    https = argpaser.get_arg('-S')

    log_msg = 'new qos domain:'+domainName+' srcip:'+srcip+' url:'+url+' speed:'+speed+' each_srcip:'+each_srcip+' each_url:'+each_url
    dolog(log_msg)

    find_flag = False
    for item in g_json_dict['policy'][domainName]['qos']:
        if item['srcip']== srcip and item['url']==url:
            find_flag = True

    if find_flag==True:
        print 'the some srcip and url already exists!'
        return
    new_qos = copy.deepcopy(default_qos_dict)
    new_qos['srcip'] = srcip
    new_qos['url'] = url
    new_qos['speed'] = speed
    if each_url == 'y':
        new_qos['each_url'] = True
    if each_srcip == 'y':
        new_qos['each_srcip'] = True
    if https == 'y':
        new_qos['https'] = True

    #add to g_json_dict
    g_json_dict['policy'][domainName]['qos'].append(new_qos)

    dolog('add to qos list :'+domainName)

    #add to g_commit_* 
    if not domainName in g_commit_add_set:
        g_commit_chg_set.add(domainName)
        dolog('add to g_commit_chg_set:'+domainName)

def setQos(msg):
    print 'setQos'
    #set-qos <domain> -sip -url [-eIP {y|n}] [-eURL {y|n}] [-S {y|n}] -s <speed> 
    if len(msg)<6:
        print 'Invalid parameters: too short'
    domainName = msg[2]
    if not domainName in g_json_dict['policy']:
        print 'This policy not exists, check it'
        return
    #parse
    argpaser = ArgParser()
    arg_dict={'-sip':False,'-url':False,'-s':False, '-S':False,'-eIP':False,'-eURL':False}
    argpaser.init_arg(arg_dict)
    argpaser.parse(msg)
    srcip = argpaser.get_arg('-sip')
    url = argpaser.get_arg('-url')
    speed = argpaser.get_arg('-s')
    each_srcip = argpaser.get_arg('-eIP')
    each_url = argpaser.get_arg('-eURL')
    https = argpaser.get_arg('-S')


    log_msg = 'set qos domain:'+domainName+' srcip:'+srcip+' url:'+url+' speed:'+speed+' each_srcip:'+each_srcip+' each_url:'+each_url
    dolog(log_msg)

    #find the qos item
    find_flag = False
    for item in g_json_dict['policy'][domainName]['qos']:
        if item['srcip']== srcip and item['url']==url:
            item['srcip'] = srcip
            item['url'] = url
            item['speed'] = speed
            if each_url != '':
                item['each_url'] = (True if each_url=='y' else  False)
            if each_srcip != '':
                item['each_srcip'] = (True if each_srcip=='y' else False)
            if https != '':
                item['https'] = (True if https=='y' else False)
            find_flag = True
            break

    if find_flag==False:
        print 'This qos item not exists,check it'
        return
    #add to g_commit_* 
    if not domainName in g_commit_add_set:
        g_commit_chg_set.add(domainName)
        dolog('add to g_commit_chg_set:'+domainName)

def delQos(msg):
    print 'delQos'
    #del-qos <domain> -sip -url  
    if len(msg)<4:
        print 'Invalid parameters: too short'
    domainName = msg[2]
    if not domainName in g_json_dict['policy']:
        print 'This policy not exists, check it'
        return
    #parse
    argpaser = ArgParser()
    arg_dict={'-sip':False,'-url':False,'-a':True}
    argpaser.init_arg(arg_dict)
    argpaser.parse(msg)
    srcip = argpaser.get_arg('-sip')
    url = argpaser.get_arg('-url')
    delall = argpaser.get_arg('-a')

    dolog('delQos srcip:'+srcip+' url:'+url+' -a:'+delall)

    find_flag = False
    #find the qos item
    if delall:
        g_json_dict['policy'][domainName]['qos'].clear()
        find_flag = True
    else:
        for item in g_json_dict['policy'][domainName]['qos']:
            if item['srcip']== srcip and item['url']==url:
                g_json_dict['policy'][domainName]['qos'].remove(item)
                find_flag = True
                break

    if find_flag==False:
        print 'this qos item not exists,check it'
        return
    #add to g_commit_* 
    if not domainName in g_commit_add_set:
        g_commit_chg_set.add(domainName)
        dolog('add to g_commit_chg_set:'+domainName)

def addTrust(msg):
    print 'addTrust'
    #add-trust <domain> -sip -url
    if len(msg)<4:
        print 'Invalid parameters: too short'
    domainName = msg[2]
    if not domainName in g_json_dict['policy']:
        print 'This policy not exists, check it'
        return
    argpaser = ArgParser()
    arg_dict={'-sip':False,'-url':False}
    argpaser.init_arg(arg_dict)
    argpaser.parse(msg)
    srcip = argpaser.get_arg('-sip')
    url = argpaser.get_arg('-url')
    new_trust = copy.deepcopy(default_trust_dict)
    new_trust['srcip'] = srcip
    new_trust['url'] = url

    find_flag = False
    for item in g_json_dict['policy'][domainName]['trust_list']:
        if item['srcip']== srcip and item['url']==url:
            find_flag = True

    if find_flag==True:
        print 'This trust item already exists'
        return

    dolog('addTrust srcip:'+srcip+' url:'+url)
    #add to g_json_dict
    g_json_dict['policy'][domainName]['trust_list'].append(new_trust)

    #add to g_commit_* 
    if not domainName in g_commit_add_set:
        g_commit_chg_set.add(domainName)
        dolog('add to g_commit_chg_set:'+domainName)


def delTrust(msg):
    print 'delTrust'
    if len(msg)<4:
        print 'Invalid parameters: too short'
    domainName = msg[1]
    if not domainName in g_json_dict['policy']:
        print 'This policy not exists, check it'
        return
    #parse
    argpaser = ArgParser()
    arg_dict={'-sip':False,'-url':False,'-a':True}
    argpaser.init_arg(arg_dict)
    argpaser.parse(msg)
    srcip = argpaser.get_arg('-sip')
    url = argpaser.get_arg('-url')
    delall = argpaser.get_arg('-a')

    dolog('delTrust srcip:'+srcip+' url:'+url+' -a:'+delall)

    #find the qos item
    find_flag = False
    if delall:
        g_json_dict['policy'][domainName]['trust_list'].clear()
        find_flag = True
    else:
        for item in g_json_dict['policy'][domainName]['trust_list']:
            if item['srcip']== srcip and item['url']==url:
                g_json_dict['policy'][domainName]['trust_list'].remove(item)
                find_flag = True

    if find_flag==False:
        print 'this trust item not exists,check it'
        return
    #add to g_commit_* 
    if not domainName in g_commit_add_set:
        g_commit_chg_set.add(domainName)
        dolog('add to g_commit_chg_set:'+domainName)


def addBlock(msg):
    print 'addBlock'
    if len(msg)<4:
        print 'Invalid parameters: too short'
    domainName = msg[2]
    if not domainName in g_json_dict['policy']:
        print 'This policy not exists, check it'
        return
    argpaser = ArgParser()
    arg_dict={'-sip':False,'-url':False}
    argpaser.init_arg(arg_dict)
    argpaser.parse(msg)
    srcip = argpaser.get_arg('-sip')
    url = argpaser.get_arg('-url')
    new_block = copy.deepcopy(default_trust_dict)
    new_block['srcip'] = srcip
    new_block['url'] = url

    find_flag = False
    for item in g_json_dict['policy'][domainName]['block_list']:
        if item['srcip']== srcip and item['url']==url:
            find_flag = True

    if find_flag==True:
        print 'This block item already exists'
        return


    dolog('addBlock srcip:'+srcip+' url:'+url)
    #add to g_json_dict
    g_json_dict['policy'][domainName]['block_list'].append(new_block)

    #add to g_commit_* 
    if not domainName in g_commit_add_set:
        g_commit_chg_set.add(domainName)
        dolog('add to g_commit_chg_set:'+domainName)

def delBlock(msg):
    print 'delBlock'
    if len(msg)<4:
        print 'Invalid parameters: too short'
    domainName = msg[2]
    if not domainName in g_json_dict['policy']:
        print 'This policy not exists, check it'
        return
    #parse
    argpaser = ArgParser()
    arg_dict={'-sip':False,'-url':False,'-a':True}
    argpaser.init_arg(arg_dict)
    argpaser.parse(msg)
    srcip = argpaser.get_arg('-sip')
    url = argpaser.get_arg('-url')
    delall = argpaser.get_arg('-a')

    dolog('delBlock srcip:'+srcip+' url:'+url+' -a:'+delall)

    #find the qos item
    find_flag = False
    if delall:
        g_json_dict['policy'][domainName]['block_list'].remove(item)
        find_flag = True
    else:
        for item in g_json_dict['policy'][domainName]['block_list']:
            if item['srcip']== srcip and item['url']==url:
                g_json_dict['policy'][domainName]['block_list'].remove(item)
                find_flag = True

    if find_flag==False:
        print 'this block item not exists,check it'
        return
    #add to g_commit_* 
    if not domainName in g_commit_add_set:
        g_commit_chg_set.add(domainName)
        dolog('add to g_commit_chg_set:'+domainName)


def loadPolicy(msg):
    print 'loadPolicy'
    global g_json_dict
    if msg[2]=='':
        confPath= cc_conf_file
    else:
        confPath = msg[2]
    dolog('load file from :'+confPath)
    if not os.path.exists(confPath):
        print 'No default policy file'
        return
    for fn in os.listdir(confPath):
        cur_file = os.path.join(confPath,fn)
        with open(cur_file,'r') as f:
            try:
                json_dict = json.load(f)
                if fn == '_sys':
                    g_json_dict['sys'] = json_dict
                else:
                    g_json_dict['policy'][fn] = json_dict
                print g_json_dict
            except Exception,e:
                print 'load def conf file failed:',e


def loadPolicyDef():
    print 'loadPolicyDef'
    global g_json_dict
    confPath = cc_conf_path
    dolog('load file from :'+confPath)
    if not os.path.exists(confPath):
        print 'No default policy file'
        return
    for fn in os.listdir(confPath):
        cur_file = os.path.join(confPath,fn)
        with open(cur_file,'r') as f:
            try:
                json_dict = json.load(f)
                if fn == '_sys':
                    g_json_dict['sys'] = json_dict
                else:
                    g_json_dict['policy'][fn] = json_dict
                print g_json_dict
            except Exception,e:
                print 'load def conf file failed:',e

def outAdd2Engine(fp,domain_set):
    if fp==None:
        print 'out put file open failed'
        return
    for policy_item in domain_set:
        if policy_item in g_json_dict['policy']:
            item = g_json_dict['policy'][policy_item]
            msg =''
            msg = 'AddPolicy{\n    domain="'+item['domain']+'",\n    cc_level="'+item['cc_level']+'",\n    '\
                 +'threshold_srcip='+str(item['threshold_srcip'])+',\n    threshold_srcip='+str(item['threshold_srcip']) \
                 +',\n    enable='+str(item['enable'])+',\n    qos={\n        '
            fp.write(msg)
            msg = ''
            first_f = True
            for qos_item in item['qos']:
                if first_f==True:
                    msg = '{\n        srcip="'+qos_item['srcip']+'",\n        url="'+qos_item['url']+'",\n        '\
                        +'https='+ ('True' if qos_item['https']=='y' else 'False')+',\n        each_srcip='\
                        +('True' if qos_item['each_srcip'] else 'False')+',\n        each_url='\
                        +('True' if qos_item['each_url'] else 'False')+',\n        speed='+str(qos_item['speed'])+'\n        }\n        '
                    first_f = False
                else:
                    msg = ',{\n        srcip="'+qos_item['srcip']+'",\n        url="'+qos_item['url']+'",\n        '\
                        +'https='+ ('True' if qos_item['https']=='y' else 'False')+',\n        each_srcip='\
                        +('True' if qos_item['each_srcip'] else 'False')+',\n        each_url='\
                        +('True' if qos_item['each_url'] else 'False')+',\n        speed='+str(qos_item['speed'])+'\n        }\n        '
                fp.write(msg)
            msg = '},\n    '
            fp.write(msg)
    
            first_f = True
            msg = ''
            msg = 'trust_list={\n        ' 
            fp.write(msg)
            for trust_item in item['trust_list']:
                if first_f==True:
                    msg = '{\n        srcip="'+trust_item['srcip']+'",\n        url="'+trust_item['url']+'"\n        }\n        '
                    first_f = False
                else:
    
                    msg = ',{\n        srcip="'+trust_item['srcip']+'",\n        url="'+trust_item['url']+'"\n        }\n        '
                fp.write(msg)
    
            msg = '},\n    '
            fp.write(msg)
    
            first_f = True
            msg = ''
            msg = 'block_list={\n        ' 
            fp.write(msg)
            for trust_item in item['block_list']:
                if first_f==True:
                    msg = '{\n        srcip="'+trust_item['srcip']+'",\n        url="'+trust_item['url']+'"\n        }\n        '
                    first_f = False
                else:
    
                    msg = ',{\n        srcip="'+trust_item['srcip']+'",\n        url="'+trust_item['url']+'"\n        }\n        '
                fp.write(msg)
    
            msg = '}\n }\n\n'
            fp.write(msg)
        
def outDel2Engine(fp,domain_set):
    for domainName in domain_set:
        msg = 'DelPolicy{\n    domain="'+domainName+'\n}\n\n'
        fp.write(msg)

def outDelAll2Engine(fp):
    global g_del_all_policy
    if g_del_all_policy:
        fp.write('DelAllPolicy{\n    }\n\n')
        g_del_all_policy = False
        if tellEngineCommit():
            return True
    return False

def outSys2Engine(fp):
    global g_sys_chg
    if g_sys_chg:
        fp.write('AddSys{\n    log_level="'+str(g_json_dict['sys']['log_level'])+'",\n    log_timer='+str(g_json_dict['sys']['log_timer'])+',\n     enable='+str(g_json_dict['sys']['enable'])+'\n     }\n\n')
        g_sys_chg = False

def commit(msg):
    print msg 
    global g_sys_chg
    if len(msg)==2:
        if msg[1]!='-a':
            print 'Invalide parameters'
            return
        else:
            # add all policy to g_commit_add_set
            
            #clear chg set first
            g_commit_chg_set.clear()
            g_sys_chg = True
            for domainName in g_json_dict['policy']:
                g_commit_add_set.add(domainName)


    # find all item in g_commit_add_set
    fp = open(policy_file_engine,'w')
    if outDelAll2Engine(fp):
        fp.close()
        if tellEngineCommit():
            fp = open(policy_file_engine,'w')
        else:
            print 'Del all commit  failed,need redo del-policy -a'
            return
    outSys2Engine(fp)
    outAdd2Engine(fp,g_commit_add_set)
    outAdd2Engine(fp,g_commit_chg_set)
    outDel2Engine(fp,g_commit_del_set)
    fp.close()
    # tell engine to commit
    if tellEngineCommit():
        g_commit_add_set.clear()
        g_commit_chg_set.clear()
        g_commit_del_set.clear()
        print 'commit success!'
    else:
        print 'commit failed,need redo'
    

def savePolicy(msg):
    print 'savePolicy'
    global g_json_dict
    if msg[2]=='':
        filePath = cc_conf_path
    else:
        filePath = msg[1]

    if not os.path.exists(filePath):
        os.mkdir(filePath)
    #sys output 
    print filePath
    sysFile = os.path.join(filePath,'_sys')
    with open(sysFile,'w') as f:
        json.dump(g_json_dict['sys'],f,indent=4)

    for domain in g_json_dict['policy']:
        curFile = os.path.join(filePath,domain)
        with open(curFile,'w') as f:
            json.dump(g_json_dict['policy'][domain],f,indent=4)

def showPolicy(msg):
    print 'showPolicy'
    global g_json_dict
    if len(msg)<2:
        print 'Invalid parameters:too short'
        return
    elif len(msg)==3:
        if msg[2]=='-a':
            print json.dumps(g_json_dict,indent=4)
        else:
            print 'Invalid parameters:',msg[1]
    elif len(msg)==4:
        if msg[2]=='-name':
            policy_name = msg[3]
            print policy_name
            print g_json_dict['policy'].keys()
            if policy_name in g_json_dict['policy']:
                print json.dumps(g_json_dict['policy'][policy_name],indent=4)
            else:
                print 'No this policy'
        else:
            print 'Invalid parameters:',msg[2]
    else:
        print 'Invalid parameters'

def showSys(msg):
    print 'showSys'
    global g_json_dict
    if 'sys' in g_json_dict:
        print json.dumps(g_json_dict['sys'],indent=4)
    else:
        print 'pleae load-policy first'



def blockHandle(msg):
    if len(msg)<2:
        print 'Invalid parameters'
        return
    if msg[1]=='add':
        addBlock(msg)
    elif msg[1]=='del':
        delBlock(msg)
    elif msg[1]=='help':
        msg = '''
    usage:
       black-table {add|del} -sip -url
       '''
        print msg
    else:
        print 'Invalid parameters'

def trustHandle(msg):
    if len(msg)<2:
        print 'Invalid parameters'
        return
    if msg[1]=='add':
        addTrust(msg)
    elif msg[1]=='del':
        delTrust(msg)
    elif msg[1]=='help':
        msg = '''
    usage:
       trust-table {add|del} -sip -url
       '''
        print msg
    else:
        print 'Invalid parameters'

def qosHandle(msg):
    if len(msg)<2:
        print 'Invalid parameters'
        return
    if msg[1]=='add':
        addQos(msg)
    elif msg[1]=='set':
        setQos(msg)
    elif msg[1]=='del':
        delQos(msg)
    elif msg[1]=='help':
        msg = '''
    usage:
       qos {add|set} <domain> -sip -url [-eIP {y|n}] [-eURL {y|n}] [-S {y|n}] -s <speed> 
       qos del <-a|-sip -url>
       '''
        print msg
    else:
        print 'Invalid parameters'
def policyHandle(msg):
    if len(msg)<2:
        print 'Invalid parameters'
        return
    if msg[1]=='add':
        addPolicy(msg)
    elif msg[1]=='set':
        setPolicy(msg)
    elif msg[1]=='del':
        delPolicy(msg)
    elif msg[1]=='load':
        loadPolicy(msg)
    elif msg[1]=='save':
        savePolicy(msg)
    elif msg[1]=='show':
        showPolicy(msg)
    elif msg[1]=='help':
        msg = '''
    usage:
       policy {add|set}  <domain> [-l {high|mid|low}] [-t_url] [-t_sip] [-enable {y|n}]   
       policy del <-a|domain>
       policy {load|save} [path]
       '''
        print msg
    else:
        print 'Invalid parameters'
def sysconfHandle(msg):
    if len(msg)<2:
        print 'Invalid parameters'
        return
    if msg[1] == 'set':
        sysConf(msg)
    elif msg[1] == 'show':
        showSys(msg)
    elif msg[1] == 'help':
        msg = '''
    usage:
       sysconf {set|show} [-l ] [-t ] [-enable {y|n}]
       '''
        print msg
    else:
        print 'Invalid parameters'

#str map to fun
com_fun = {
		'help'        :fun_help,
        'sysconf'     :sysconfHandle,#{'set':sysConf,'show':showSys},
        'policy'      :policyHandle,#{'add':addPolicy,'set':setPolicy,'del':delPolicy,'load':loadPolicy,'save':savePolicy,'show':showPolicy},
#		'set-policy'  :setPolicy,
#		'del-policy'  :delPolicy,
        'qos'         :qosHandle,#{'add':addQos,'set':setQos,'del':delQos},
#		'set-qos'     :setQos,
#		'del-qos'     :delQos,
        'trust-table' :trustHandle,#{'add':addTrust,'del':delTrust},
#		'del-trust'   :delTrust,
        'black-table' :blockHandle,#{'add':addBlock,'del':delBlock},
#		'del-block'   :delBlock,
#        'load-policy' :loadPolicy,
        'commit'      :commit,
#        'save-policy' :savePolicy,
#        'show-policy' :showPolicy,
#        'show-sys'    :showSys,
		'q'           :fun_quit
		}
        
def handle_command(command_line):
    print command_line
    com_list = command_line.split()
    print com_list
    if len(com_list)<1:
        return
    if com_list[0] in com_fun:
        record_command(command_line)
        com_fun[com_list[0]](com_list)
    else:
        print "Error command, type help to get usage "

if __name__=='__main__':
    loadPolicyDef()
    while(1):
        line = raw_input('cc_cli>')
        print 'line:',line
        handle_command(line.strip())
