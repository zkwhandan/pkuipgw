#!/usr/bin/python2
#
# pkuipgw: PKU IPGW Client for Linux
# <http://www.linux-wiki.cn/>
# Copyright (c) 2007-2009,2011-2012 Chen Xing <cxcxcxcx@gmail.com>
# Copyright (c) 2014 Casper Ti. Vector <caspervector@gmail.com>

import getopt
import os.path
import re
import sys
import traceback

from configparser import ConfigParser
from http.cookiejar import CookieJar
from urllib.parse import urlencode
from urllib.request import build_opener, HTTPCookieProcessor, URLError

class ArgError(Exception):
    pass

class ConfError(Exception):
    pass

class IPGWError(Exception):
    pass
    
class IPGWManager:
    def __init__(self, username, password, login = True):
        self.username = username
        self.password = password
        self.opener = build_opener(HTTPCookieProcessor(CookieJar()))
        if login:
            self.login()
    
    def login(self):
        data = "username1="+self.username+\
                "&password="+self.password+"&pwd_t=%E5%AF%86%E7%A0%81&fwrd=free"+\
    			"&username="+self.username+"%7C%3BkiDrqvfi7d%24v0p5Fg72Vwbv2%3B%7C"+\
    			self.password+"%7C%3BkiDrqvfi7d%24v0p5Fg72Vwbv2%3B%7C12"
        self.opener.open('https://its.pku.edu.cn/cas/login', bytes(data, 'ASCII'))
        self.opener.open("https://its.pku.edu.cn/netportal/netportal_UTF-8.jsp").read()
        self.opener.open("https://its.pku.edu.cn/netportal/PKUIPGW?cmd=open&type=free&fr=0&sid=432").read()

    def connect(self, all = False):
        url = 'https://its.pku.edu.cn/netportal/ITSipgw?cmd=open&type=fee'
        html = self.opener.open(url).read()
        #url = 'https://its.pku.edu.cn/netportal/ipgwResult.jsp'
        #html = self.opener.open(url).read()
        return self.format(html)

    def disconnect(self, all = False):
        url = 'https://its.pku.edu.cn/netportal/ITSipgw?cmd=close&type='
        if all: url += 'all'
        else: url += 'self'
        html = self.opener.open(url).read()
        return self.format(html)

    def disconnectIP(self):
        url = 'https://its.pku.edu.cn/netportal/ITSipgw?cmd=getconnections'
        html = self.opener.open(url).read()
        print(self.format(html))
        select = ''
        while select not in self.conns: 
            select = input('    断开第几个连接：')
        if select == '0': return self.disconnet(all = False)
        if select == '1': return self.disconnet(all = True)
        url = 'https://its.pku.edu.cn/netportal/ITSipgw?cmd=disconnect&ip=' + self.conns[select]
        html = self.opener.open(url).read()
        return self.format(html)
    
    def format(self, html):
        html = html.decode('utf-8')
        i1 = html.index("<table")
        i2 = html.index("</table>")
        html = html[i1:i2]
        html = html.replace('<br>', '\n\t')
        dr = re.compile(r'<[^>]+>|\r',re.S)
        html = dr.sub('',html)
        dr = re.compile(r'[ \t\n]{2,}',re.S)
        html = dr.sub('\n    ',html)
        if '地理位置' in html:
            html = html.replace('\n', '')
            html = html.replace('    20', '\n         20')
            t = html.split('操作    ')[1].split('断开连接    ')
            self.conns = {'0':'self', '1':'all'}
            html = '\n    0  当前连接\n    1  全部连接\n'
            for i in range(len(t)):
                if len(t[i]) > 10:
                    self.conns[str(i+2)] = t[i].split('    ')[0]
                    html += '    ' + str(i+2) +'  ' + t[i] + '\n'
        return html
        

def tb_exit(retval, verbose = False):
    if verbose:
        traceback.print_exc()
    else:
        typ, val, tb = sys.exc_info()
        sys.stderr.write(typ.__name__ + ': ' + str(val) + '\n')
    sys.exit(retval)

def in_main():
    opts, args = getopt.getopt(sys.argv[1:], 'c:')

    configFiles = []
    for key, val in opts:
        if key == '-c':
            configFiles.append(val)
    if not configFiles:
        configFiles = [
            'pkuipgwrc'
        ]

    if len(args) < 1 or args[0] not in ['connect', 'disconnect', 'disconnectIP']:
        raise ArgError
    elif len(args) == 1:
        all = False
    elif len(args) == 2 and args[1] == 'all':
        all = True
    else:
        raise ArgError

    config = ConfigParser()
    if not config.read(configFiles):
        raise ConfError('No readable config file.')
    elif 'pkuipgw' not in config.sections():
        raise ConfError('Section "pkuipgw" not found in config file.')
    config = dict(config.items('pkuipgw'))
    if 'username' not in config or 'password' not in config:
        raise ConfError('Both "username" and "password" required.')

    ipgw = IPGWManager(config['username'], config['password'])
    os.system('cls')
    if args[0] == 'connect':
        print(ipgw.connect(all = all))
    elif args[0] == 'disconnect':
        print(ipgw.disconnect(all = all))
    elif args[0] == 'disconnectIP':
        print(ipgw.disconnectIP())

def main():
    try:
        in_main()
    except ArgError:
        sys.stderr.write(
            'Usage: pkuipgw [-c cfg_file] [-c ...]'
            ' (connect|disconnect|disconnectIP) [all]\n'
        )
        sys.exit(1)
    except ConfError:
        tb_exit(2)
    except IPGWError:
        tb_exit(3)
    except:
        tb_exit(4, verbose = True)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()

