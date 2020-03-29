

def move(srclist, dest, opts=[]):
    # 先复制
    result = copy(srclist, dest, opts)
    ext = result.get('ext', {})
    # 再删除
    rmlist = set(srclist) - set(ext.keys())
    remove(rmlist, opts)

def get_tag(path):
    '''根据标签路径，获取标签、文件、文件夹
    path示例：/人物>家人>姐姐>10月24日/102401.jpg
    '''
    cur = tagtrees
    # 若路径有效，路径首字符必为'/'
    path = path[1:]
    # 按>或》分隔
    parts = re.split('[>》]', path)
    tail = parts[-1]
    # 处理前n-1段
    try:
        for part in parts[: -1]:
            cur = cur[part]
    except KeyError:
        result = {'code': -1}
    else:
        # 最后一段有多种情况
        if cur.get(tail, None):
            # 标签 TODO 文件夹名与标签名、内置键名两两不能相同
            cur = cur[tail]
            result = {'code': cfg.pack_error('LIST_TAG'], 'resource': [], 'files': [], 'msg': 'tag'}
            for key in cur.keys():
                if key[0] != '$':   # '$'开头的是内置键
                    result['resource'].append({'name': key, 'type': 'tag'})
            for p in cur.get('$path', {}).keys():
                if os.path.isdir(p):
                    files = rec_get_folder(p, list_folder(p))
                    result['resource'].append({'name': os.path.basename(p), 'size': len(os.listdir(p)), 'type': 'dir', 'tags': cur['$path'][p]})
                else:
                    file = list_file(p)
                    result['resource'].append(file)
                    result['files'].append(file)
        else 
            tail_parts = tail.split('/')
            if -1 < tail.find('/') < len(tail)-1:
                # 末端可能是多级路径
                tail_head = tail_parts[0]
            else:
                # 单级路径
                tail_head = tail
            for p in cur.get('$path', {}).keys():
                if os.path.basename(p) == tail_head:
                    break
            else:
                result = {'code': -1}
            # 转换为磁盘路径
            path = f'{p}/{'/'.join(tail_parts[1:])}'
            if os.path.exists(path):
                result = None
    finally:
        return path, result


def get_parent(tagpath):
    parts = re.split('[>》]', tagpath[1:])
    cur = tagtrees
    try:
        for part in parts:
            cur = cur[part]
    except:
        return None
    else:
        return cur

def bWindows():
    '''是否是Windows'''
    return platform.system() == 'Windows'

def get_recycle(path):
    '''获取path所在盘的回收站目录'''
    if not bWindows():
        return None
    recy = path[: 3]+'$RECYCLE.BIN/'
    t = os.listdir(recy)
    for d in t:
        try:
            os.listdir(recy + d)
        except:
            # 拒绝访问
            pass
        else:
            # 能够访问的便是回收站了
            return recy + d
    return None
