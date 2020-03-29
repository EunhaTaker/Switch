'''通用组件'''

# 别名数据
all_alias = None
# 网络请求配置
req_conf = None
# 标签树
tags = None
# 路径的标签
path_tags = None
# 为命令、标签提供联想的字典树
tries = None
# 根路径
root = None
# 是否为Windows
bWindows = None
# tags树是否修改过，修改后标记，返回response时，若有变动则更新文件
tags_has_changed = False

import os, json, _thread
import config as cfg

'''------------------------for all--------------------------------'''

def save_json(dict_, filename):
    '''保存dict为json到文件'''
    def func():
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dict_, f)
        print(filename + ' save complete')
    _thread.start_new_thread(func)

from trie import Trie
import time
def load_tries():
    '''将命令、命令别名、标签加入字典树'''
    def func():
        # 等待tags和alias加载完毕
        while not tags or not all_alias:
            time.sleep(0.1)
        cmd_trie, tag_trie = Trie(), Trie()
        cmd_trie.add(cfg.cmds)
        cmd_trie.add(all_alias['cmd'].keys())
        tag_trie.add(tags.keys())
        global tries
        tries = {'cmd': cmd_trie, 'tag': tag_trie}
    _thread.start_new_thread(func, ())

alias_file = os.path.dirname(__file__)+'/data/alias.json'
def load_alias():
    global all_alias
    try:
        with open(alias_file, 'r', encoding='utf-8') as f:
            all_alias = json.load(f)
    except:
        # 默认别名
        all_alias = {
            'opt': {
                '--line': '-l',
                '--recursive': '-r',
                '--parent': '-p',
                '--color': '-c',
                '--name': '-n',
                '--add': '-a',
                '--del': '-d',
                '--list': '-l',
            },
            'cmd': {
                'copy': 'cp',
                'move': 'mv',
                'll': 'ls -l',
            }
        }
        save_json(all_alias, alias_file)

import platform
def load_setting():
    '''加载用户设置'''
    setting_file = os.path.join(os.path.dirname(__file__), '..\\configs\\user-setting.json')
    global root, bWindows
    bWindows = (platform.system() == 'Windows')
    with open(setting_file, 'r', encoding='utf-8') as f:
        setting = json.load(f)
        root = setting['server']['root']
        if (root and root[-1] != '/') or (root == '' and not bWindows):
            # 值为空且不是windows，置为/，值不为空但不以/结尾的，添加/
            root += '/'
        # 将路径转换为全斜杠且完全小写（仅限Windows）
        root = os.path.normcase(root).replace('\\', '/')

def addEscape(pattern):
    '''在字符串的所有正则符号前添加转义符'''
    return re.sub('[\[\]\{\}\(\)]\+\?', lambda match: '\\'+match.group(), pattern)

import logging
def init_logging():
    '''初始化日志写入'''
    logging.basicConfig(filename=os.path.dirname(__file__)+'/sundry/exception.log', filemode='w',format='[%(asctime)s]-%(levelname)s : %(message)s',level=logging.ERROR)

def sort_resource(resources):
    '''排序资源'''
    maping = {'tag':0, 'dir':1, 'img':2, 'video':3}
    resources.sort(key=lambda content: maping.get(content['type'], 10))
    return resources

'''------------------------for request-------------------------------'''

def init(app):
    '''初始化'''
    # 加载网络请求配置
    request_conf_path = os.path.join(os.path.dirname(__file__), '..\\configs\\request-conf.json')
    with open(request_conf_path, 'r') as f:
        global req_conf
        req_conf = json.load(f)
    # 加载标签
    load_tagtree()
    # 加载别名
    load_alias()
    # 加载联想字典树
    load_tries()
    # 根路径
    load_setting()
    # 设置logging
    init_logging()
    # 允许跨域
    def after_request(response):
        '''发送响应前夕'''
        response.headers['Access-Control-Allow-Origin'] = '*'
        global tags_has_changed
        if tags_has_changed:    # 若本次请求后，标签树发生变动
            save_tagtree()
            tags_has_changed = False
        return response
    app.after_request(after_request)

from flask import request
import re
def parse_args(req_name):
    '''解析get参数'''
    args = request.args
    ret = []
    for arg_name in req_conf[req_name + '_args']:
        arg = args.get(arg_name)
        if re.match('.*(files|paths|list|tags|targets)$', arg_name):
            # 数组
            ret.append(arg.split(',') if arg else [])
        elif arg_name == 'opts':
            # 可选项，可能是数组，或空
            ret.append(arg.split(',') if arg else [])
        else:
            ret.append(arg)
    return ret

from flask import make_response
def pack_result(data: dict, response_type="application/json"):
    '''data打包为response'''
    if response_type == "application/json":
        print(data)
        data = json.dumps(data)
    response = make_response(data)
    response.headers['Content-Type'] = response_type
    return response

def help_cmd(cmd):
    if not cmd:
        cmd = 'help'
    if cmd in cfg.cmds:
        with open(f"{os.path.dirname(__file__)}/help-docs/{cmd}.txt", 'r', encoding='utf-8') as f:
            code, msg = 0, ''.join(f.readlines())
    else:
        code, msg = cfg.pack_error('Error_Command_Not_Found', cmd)
    return {'code': code, 'msg': msg}

def set_alias(alias, target, opts):
    code, msg = 0, ''
    if '--init' in opts:
        return {'code': 0, 'content': all_alias}
    elif not alias or not target:
        code, msg = cfg.pack_error('Error_Lack_Arg')
    elif '-d' in opts:
        if all_alias['cmd'].get(alias):
            del all_alias['cmd'][alias]
        else:
            code, msg = cfg.pack_error('Alias_Not_Found', alias)
    else:
        all_alias['cmd'][alias] = target
    if code == 0:
        save_json(all_alias, alias_file)
    return {'code': code, 'msg': msg}

def tab_cmd(target, t):
    '''命令行补全'''
    res, perfix = None, target
    if t == 'cmd':
        res = tries['cmd'].getStartBy(target)
    elif t == 'tag':
        res = tries['tag'].getStartBy(target)
    else:
        # 获取路径
        basename = os.path.basename(target)
        perfix = addEscape(basename)
        target = parse_path(target)
        dirname = os.path.dirname(target)
        if os.path.isdir(dirname):
            paths = os.listdir(dirname)
            if t == 'dir':
                paths = list(filter(lambda path: os.path.isdir(os.path.join(dirname, path)), paths))
            elif t == 'file':
                paths = list(filter(lambda path: os.path.isfile(os.path.join(dirname, path)), paths))
            paths = filter(lambda path: re.match(f'^{addEscape(basename)}', path, re.I), paths)    # 匹配前缀，忽略大小写
            # print(list(paths))
            # print(addEscape(basename))
            path_trie = Trie()
            path_trie.add(paths)
            res = path_trie.getStartBy(basename)
        else:
            res = []
    return {'code': 0, 'res': res, 'perfix': perfix}


'''---------------------for tag----------------------'''

tags_file = os.path.dirname(__file__)+'/data/tags.json'
def load_tagtree():
    '''加载标签树到内存'''
    def load():
        global tags, path_tags
        if os.path.exists(tags_file):
            with open(tags_file, 'r', encoding='utf-8') as f:
                dict_ = json.load(f)
                tags = dict_['tags']
                path_tags = dict_['path_tags']
        else:
            tags = {}
            path_tags = {}
        print('load complete')
    _thread.start_new_thread(load, ())

def save_tagtree():
    '''存储标签树'''
    save_json({'tags': tags, 'path_tags': path_tags}, tags_file)

def get_tagmsg(name):
    '''返回标签的名称、颜色、子标签和子路径数量'''
    nsubtag = len(tags[name]['$subtags'])
    nsubpath = len(tags[name]['$paths'])
    return {'name': name, 'color': tags[name]['$color'], 'size': f'{nsubtag}tags+{nsubpath}paths', 'type': 'tag'}

def check_tagname(name):
    '''检查标签名是否含有不合法字符'''
    matchs = re.findall('[#>/\$]', name)
    return ",".join(matchs) if matchs else True

def get_chain(tagname):
    '''获取标签链'''
    parts = []
    while tagname:
        parts.insert(0, tagname)
        tagname = tags.get(tagname, {}).get('$parent')
    return '>'.join(parts)

def twist(srcpath, destpath=None, delete=True):
    '''将标签树数据中的路径进行修改或移除，默认操作为移除'''
    # 处理标签与norm_src的相互对应
    tagnames = path_tags.get(srcpath)
    if tagnames:
        if delete:
            del path_tags[srcpath]
        else:
            path_tags[destpath] = path_tags.pop(srcpath)
        for tagname in tagnames:
            tags[tagname]['$paths'].remove(srcpath)
            if not delete:
                tags[tagname]['$paths'].append(destpath)
        global tags_has_changed
        tags_has_changed = True

'''---------------------for path-----------------------'''

def check_range(path):
    '''该判断适用于标签模式访问，判断文件是不是自定义根目录的子孙'''
    return path.startswith(root)

def pack_path(path):
    '''绝对路径隐去root部分'''
    return re.sub(f'^{root}', '/', path, flags=re.I if bWindows else 0)

def parse_path(path):
    '''将隐藏root的路径解析为绝对路径'''
    path = os.path.normcase(path).replace('\\', '/')
    return re.sub(f'^/', root, path)

def common_path(path1, path2):
    '''获取最长公共目录'''
    try:
        common = os.path.commonpath((path1, path2)).replace('\\', '/')
    except:
        common = ''
    return common

from fnmatch import fnmatch
def get_type(file):
    '''获取文件类型'''
    types = ['img', 'video']
    for type_ in types:
        if any(fnmatch(file, '*.'+file_fmat) for file_fmat in cfg.__dict__[type_+'_fmat']):
            return type_
    return 'file'

def format_decimal(decimal, prec=2):
    '''按小数点后prec位规范小数'''
    if type(decimal) == str:
        point_pos = decimal.find('.')
        if point_pos != -1:
            decimal = decimal[: point_pos+prec+1]
    else:
        decimal = int(decimal * 10**prec) / 10**prec
    return decimal

def transByte(size):
    '''将大小从Byte往上转化，直到数值介于[1,1024)之间'''
    size_level = 0
    while size >= cfg.K:
        size /= cfg.K
        size_level += 1
    return f'{format_decimal(size)}{cfg.size_unit[size_level]}'

def get_file_size(path):
    '''计算文件大小'''
    size = os.path.getsize(path)
    return transByte(size)

def get_dirmsg(path):
    '''获取文件夹信息'''
    try:
        size = len(os.listdir(path))
    except PermissionError:
        size = 'unknown'
    return {'name': os.path.basename(path), 'path': pack_path(path), 'size': size, 'type': 'dir', 'tags': path_tags.get(path, [])}

def check_path(paths, opt):
    for path in paths:
        if opt == 'exists':
            if os.path.exists:
                return cfg.pack_error('ERROR_PATH_NOTEXIST', path)
        if opt == 'non_recursive':
            if os.path.isdir(path):
                return cfg.pack_error('ERROR_LACK_OPT', path)
    return 0, None
