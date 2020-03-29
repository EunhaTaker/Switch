from path_kit import list_folder, list_file
from common_kit import os, cfg, get_type, save_json, load_tagtree, get_dirmsg, get_tagmsg, \
    check_tagname, get_chain, parse_path, pack_path, check_range, tab_cmd, sort_resource,\
    transByte
from common_kit import tags, path_tags, bWindows
import common_kit

def list_tagroots():
    '''列举根级标签'''
    roots = filter(lambda tag: tag.get('$parent') == '#', tags.values())
    roots_msg = []
    for root in roots:
        roots_msg.append(get_tagmsg(root['$name']))
    return roots_msg

def new_tag(name, parent, color=None):
    parent = '#' if not parent else parent
    check = check_tagname(name)
    if check is not True:
        code, msg = cfg.pack_error('Error_Tag_Invaild_Name', check)
    elif parent != '#' and not tags.get(parent):
        code, msg = cfg.pack_error('Error_Tag_Not_Exist', parent)
    elif tags.get(name):
        code, msg = cfg.pack_error('ERROR_ALREADY_EXIST', name)
    else:
        tags[name] = {
            '$name': name,
            '$parent': parent,
            '$color': color,
            '$paths': [],
            '$subtags': [],
        }
        if parent != '#':
            tags[parent]['$subtags'].append(name)
        code, msg = 0, ''
        common_kit.tags_has_changed = True
    return {'code': code, 'msg': msg}

def set_tag(paths, add_tags, del_tags):
    code, ext = 0, {}
    for path in paths:
        abs_path = parse_path(path)
        if not os.path.exists(abs_path):
            code, ext[path] = cfg.pack_warning('ERROR_PATH_NOTEXIST', path)
            continue
        # # 获得反斜杠的完全小写的路径（仅限Windows）
        # norm_path = os.path.normpath(os.path.normcase(abs_path))
        if add_tags:
            for tagname in add_tags:     # 增加
                if not tags.get(tagname):
                    code, ext[tagname] = cfg.pack_warning('Error_Tag_Not_Exist', tagname)
                    continue
                if abs_path in tags[tagname]['$paths']:    # 标签已与文件配对
                    continue
                # 标签关联文件
                tags[tagname]['$paths'].append(abs_path)
                # 文件关联标签，将标签名加入路径path的标签列表
                path_tags.setdefault(abs_path, []).append(tagname)
                common_kit.tags_has_changed = True
        if del_tags:
            for tagname in del_tags:    # 删除
                if not tags.get(tagname):
                    code, ext[tagname] = cfg.pack_warning('Error_Tag_Not_Exist', tagname)
                    continue
                if tagname in path_tags.get(abs_path, []):
                    tags[tagname]['$paths'].remove(abs_path)
                    path_tags[abs_path].remove(tagname)
                    if not path_tags[abs_path]: # 清理空的 路径-标签列表 字典
                        del path_tags[abs_path]
                    common_kit.tags_has_changed = True
    return {'code': code, 'ext': ext}

def mod_tag(name, destname, color, parent):
    code, msg, ext = 0, '', {}
    if tags.get(name) is None:
        code, msg = cfg.pack_warning('Error_Tag_Not_Exist', name)
        return {'code': code, 'msg': msg}
    if color:
        tags[name]['$color'] = color
        common_kit.tags_has_changed = True
    if parent:
        if not tags.get(parent):    # 检查新父亲是否存在
            code, ext['parent'] = cfg.pack_warning('Error_Tag_Not_Exist', parent)
        else:
            pname = tags[name]['$parent']
            if pname:   # 若该标签有父亲
                # 解除原父亲的孩子
                tags[pname]['$subtags'].remove(name)
            # 成为新父亲的孩子
            tags[parent]['$subtags'].append(name)
            # 承认新父亲
            tags[name]['$parent'] = parent
            common_kit.tags_has_changed = True
    if destname:
        check = check_tagname(destname)
        if check is not True:
            code, ext['destname'] = cfg.pack_warning('Error_Tag_Invaild_Name', check)
        elif tags.get(destname):  # 检查新名称是否已存在
            code, ext['destname'] = cfg.pack_warning('Error_Tag_Already_Exist', destname)
        else:
            # 修改自己
            tags[name]['$name'] = destname
            # 修改tag树
            tags[destname] = tags.pop(name)
            # 调整父标签
            pname = tags[destname]['$parent']
            if pname != '#':   # 若该标签有父亲
                tags[pname]['$subtags'].remove(name)
                tags[pname]['$subtags'].append(destname)
            # 调整子标签
            for subtag in tags[destname]['$subtags']:
                tags[subtag]['$parent'] = destname
            # 修改子文件信息
            for path in tags[destname]['$paths']:
                path_tags[path].remove(name)
                path_tags[path].append(destname)
            common_kit.tags_has_changed = True
    return {'code': code, 'msg': msg, 'ext': ext}

def unfold_tag(names):
    '''取多个标签的交集并展开'''
    code, ext, resource = 0, {}, []

    def rec_unfold(name):
        # 读取标签name的直属文件/文件夹
        for path in tags[name].get('$paths', []):
            if check_range(path) is False:
                continue
            if os.path.isdir(path):
                for dirname, _, filenames in os.walk(path):
                    for filename in filenames:
                        fullname = parse_path(dirname+'/'+filename)

                        if pathsSet.__contains__(fullname):
                            continue
                        pathsSet.add(fullname)

                        file = list_file(fullname)
                        resource.append(file)
            elif os.path.isfile(path):

                if pathsSet.__contains__(path):
                    continue
                pathsSet.add(path)

                file = list_file(path)
                resource.append(file)
        # 读取子标签
        for subtag in tags[name]['$subtags']:
            rec_unfold(subtag)
    
    def is_path_of_tag(tag):
        '''判断文件是否属于tag或tag的子孙标签'''
        def func(file_msg):
            '''生成的func交由filter'''
            for t in file_msg['tags']:
                # 对path的每个标签
                while t:
                    # 上溯至根标签
                    if t == tag:
                        # 途中找到tag即成功
                        return True
                    t = tags[t]['$parent']
            return False
        return func

    resource = None
    pathsSet = set()    # 防止同名路径重复读取
    for name in names:
        if not tags.get(name):
            code, ext['name'] = cfg.pack_warning('Error_Tag_Not_Exist', name)
        elif resource is None:
            # 取一个标签展开之，获得该标签下所有文件
            resource = []
            rec_unfold(name)
        else:
            # 对其余标签，分别带入上面获取的文件，不匹配则移除
            resource = list(filter(is_path_of_tag(name), resource))
    return {'code': 0, 'resource': sort_resource(resource), 'ext': ext}


def change_tag(name):
    '''以文件夹方式打开标签'''
    code, msg, resource = 0, '', []
    if name == '#':
        resource = list_tagroots()
    elif not tags.get(name):
        code, msg = cfg.pack_error('Error_Tag_Not_Exist', name)
    else:
        # 子标签
        for sub in tags[name]['$subtags']:
            resource.append(get_tagmsg(sub))
        # 子路径
        for sub in tags[name]['$paths']:
            if check_range(sub) is False:
                continue
            if os.path.isdir(sub):
                resource.append(get_dirmsg(sub))
            elif os.path.isfile(sub):
                resource.append(list_file(sub))
    return {'code': code, 'msg': msg, 'resource': sort_resource(resource), 'chain': get_chain(name)}


def rm_tag(names, opts):
    def rec_rm_tag(name):
        # 删除有子标签的标签，需要-r选项
        if tags[name]['$subtags'] and (not opts or '-r' not in opts):
            return f'标签"{name}"含有子标签，请使用选项-r或--recursive删除'
        # 先删除子标签
        for tagname in tags[name]['$subtags']:
            rec_rm_tag(tagname)
        # 解除path与标签的关联
        for path in tags[name]['$paths']:
            path_tags[path].remove(name)
            if not path_tags[path]:
                # 删除空内容
                del path_tags[path]
        # 断绝父子关系
        p = tags[name]['$parent']
        if p != '#':   # 父亲存在是前提
            tags[p]['$subtags'].remove(name)
        # 删除自己
        del tags[name]
        return True
    code, ext = 0, {}
    for name in names:
        if not tags.get(name):
            code, ext[name] = cfg.pack_warning('Error_Tag_Not_Exist', name)
        else:
            res = rec_rm_tag(name)
            if res is True:
                common_kit.tags_has_changed = True
            else:
                code, ext[name] = cfg.errors['Partly_Failed'], res
    return {'code': code, 'ext': ext}


def get_tags_property(tagnames):
    '''获取标签下的：标签数、不重复文件数、大小、占用空间'''
    code, msg = 0, {}
    pathsSet = set()
    ntag = 0
    nfile = 0
    total_size = 0
    total_occupation = 0

    def count_file(filename):
        '''统计文件'''
        nonlocal nfile, total_size, total_occupation
        if pathsSet.__contains__(filename):
            return
        pathsSet.add(filename)
        nfile += 1
        total_size += os.path.getsize(filename)
        if not bWindows:
            occu = os.popen(f'du {filename}').read().split('\t')[0]
            total_occupation += int(occu)

    def count_folder(folder):
        '''遍历文件夹'''
        for dirname, _, filenames in os.walk(folder):
            for filename in filenames:
                fullname = parse_path(dirname + '/' + filename)
                count_file(fullname)

    def count_tag(tagname):
        '''遍历标签'''
        nonlocal ntag
        tag = tags.get(tagname)
        for subtag in tag.get('$subtags', []):
            ntag += 1
            count_tag(subtag)
        for subpath in tag.get('$paths', []):
            if not check_range(subpath):
                continue    # 排除root路径之外的路径
            if os.path.isdir(subpath):
                count_folder(subpath)
            elif os.path.isfile(subpath):
                count_file(subpath)
    for tagname in tagnames:
        if tags.get(tagname) is None:
            code, msg[tagname] = cfg.pack_warning('Error_Tag_Not_Exist', tagname)
        else:
            count_tag(tagname)
    return {'code': code, 'msg': msg, 'data':{'ntag': ntag, 'nfile': nfile, \
        'total_size': transByte(total_size), 'total_occupation': transByte(total_occupation) if not bWindows else None}}
