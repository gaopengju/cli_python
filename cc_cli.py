#!/usr/bin/python
import os
import sys
import readline
import json
from argParse import ArgParser

history_log='/tmp/cc_command_history'
cc_conf_file='/tmp/cc_conf'


json_dict = dict()
readline.parse_and_bind("tab: complete")

class VolcabCompleter:
	def __init__(self,volcab):
		self.volcab = volcab

	def complete(self,text,state):
		results = [x+" " for x in self.volcab if x.startswith(text)] + [None]
		return results[state]

words = ['help','add-policy','set-policy','del-policy','add-qos','set-qos','del-qos','add-trust','del-trust','add-block','del-block','show-policy','show-sys','load-policy','save-policy','quit']
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
       add-policy <domain> [-l {high|mid|low}] [-t_ip] [-t_sip] 
       set-policy <domain> [-l {high|mid|low}] [-t_ip] [-t_sip] 
       del-policy <domain>
       add-qos <domain> -sip -url [-eIP_{y|n}] [-eURL {y|n}] -s <speed> 
       set-qos <domain> -sip -url [-eIP_{y|n}] [-eURL {y|n}] -s <speed> 
       del-qos <domain> -sip -url  
       add-trust <domain> -sip -url
       del-trust <domain> -sip -url
       add-block <domain> -sip -url
       del-block <domain> -sip -url
       load-policy [path]  
       save-policy [path]  
       show-policy {-a|-name}\n
       '''
    print msg

def addPolicy(msg):
    #add-policy <domain> [-l {high|mid|low}] [-t_ip] [-t_sip] 
    print 'addPolicy'
    argpaser = ArgParser()
    arg_dict={'-l':False,'-t_ip':False,'-t_sip':False}
    argpaser.init_arg(arg_dict)
    TODO




def setPolicy(msg):
    print 'setPolicy'

def delPolicy(msg):
    print 'setPolicy'

def addQos(msg):
    print 'addQos'

def setQos(msg):
    print 'setQos'

def delQos(msg):
    print 'delQos'

def addTrust(msg):
    print 'addTrust'

def delTrust(msg):
    print 'delTrust'

def addBlock(msg):
    print 'addBlock'

def delBlock(msg):
    print 'delBlock'

def loadPolicy(msg):
    print 'loadPolicy'
    if msg=='':
        f_conf = cc_conf_file
    else:
        f_conf = msg[1]
    print 'load file:',f_conf
    if not os.path.isfile(f_conf):
        print 'policy file not exists'
        return
    with open(f_conf,'r') as f:
        json_dict = json.load(f)

def loadPolicyDef():
    print 'loadPolicyDef'
    global json_dict
    f_conf = cc_conf_file
    print 'load file:',f_conf
    if not os.path.isfile(f_conf):
        print 'No default policy file'
        return
    with open(f_conf,'r') as f:
        try:
            json_dict = json.load(f)
            print json_dict
        except Exception,e:
            print 'load def conf file failed:',e

def savePolicy(msg):
    print 'savePolicy'
    global json_dict
    if len(msg)==1:
        write_f = cc_conf_file
    elif len(msg)==2:
        if msg[1]=='':
            write_f = cc_conf_file
        else:
            write_f = msg[1]
    else:
        print 'Invalid parameters:too many'
        return
    with open(write_f,'w') as f:
        json.dump(json_dict,f,indent=4)

def showPolicy(msg):
    print 'showPolicy'
    global json_dict
    if len(msg)<2:
        print 'Invalid parameters:too short'
        return
    elif len(msg)==2:
        if msg[1]=='-a':
            print json.dumps(json_dict,indent=4)
        else:
            print 'Invalid parameters:',msg[1]
    elif len(msg)==3:
        if msg[1]=='-name':
            policy_name = msg[2]
            if policy_name in json_dict['policy']:
                print json.dumps(json_dict['policy'][policy_name],indent=4)
            else:
                print 'No this policy'
        else:
            print 'Invalid parameters:',msg[1]
    else:
        print 'Invalid parameters'

def showSys(msg):
    print 'showSys'
    global json_dict
    if 'sys' in json_dict:
        print json.dumps(json_dict['sys'],indent=4)
    else:
        print 'pleae load-policy first'

#str map to fun
com_fun = {
		'help'        :fun_help,
		'add-policy'  :addPolicy,
		'set-policy'  :setPolicy,
		'del-policy'  :delPolicy,
		'add-qos'     :addQos,
		'set-qos'     :setQos,
		'del-qos'     :delQos,
		'add-trust'   :addTrust,
		'del-trust'   :delTrust,
		'add-block'   :addBlock,
		'del-block'   :delBlock,
        'load-policy' :loadPolicy,
        'save-policy' :savePolicy,
        'show-policy' :showPolicy,
        'show-sys'    :showSys,
		'q'           :fun_quit
		}

def handle_command(command_line):
    print command_line
    com_list = command_line.split(' ',10)
    print com_list
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
