import shutil, re
from common_kit import os, logging, cfg, path_tags, transByte, get_type, get_dirmsg, get_file_size, \
    pack_path, parse_path, check_range, pack_path, parse_path, twist, common_path, sort_resource, bWindows

def not_exist(path):
    code, msg = cfg.pack_error('ERROR_PATH_NOTEXIST', path)
    return {'code': code, 'msg': msg}

def list_folder(path):
    '''获取文件夹'''
    resource = []
    # 列举文件夹
    files = os.listdir(path)
    for file in files:
        fullname = os.path.join(path, file)
        # 获取标签
        tag = None
        if os.path.isdir(fullname):
            # 该文件为文件夹
            resource.append(get_dirmsg(fullname))
        else:
            resource.append( list_file(fullname) )
    return resource

def list_file(path):
    '''
    获取文件信息，包括：文件名，大小，类型，标签
    '''
    size_str = get_file_size(path)
    file = os.path.basename(path)
    type_ = get_type(file)
    return {'name': file, 'path': pack_path(path), 'size': size_str, 'type': type_, 'tags': path_tags.get(path, [])}

def open_file(path):
    '''用系统默认软件打开文件'''
    abs_path = parse_path(path)
    os.system(abs_path)

from common_kit import make_response
from flask import Response
from PIL import Image
from io import BytesIO
import base64
def get_file(path, opts=[]):
    '''获取文件'''
    path = parse_path(path)
    # 判断文件类型
    type_ = get_type(path)
    # 浏览器显示内容类型
    data, response_type = None, None
    if type_ == 'img':
        ext = os.path.splitext(path)[1]
        response_type = 'image/svg+xml' if ext == '.svg' else 'image'
        if ext == '.svg' or '--thumb' not in opts:
            data = open(path, 'rb').read()
        else:
            try:
                # 缩略图
                edge = 328  # 缩略图边长
                im = Image.open(path)
                width, height = im.size
                delta = (width - height)/2
                box = (delta, 0, delta+height, height) if width > height else (0, -delta, width, width-delta)
                region = im.crop(box)
                region = region.resize((edge, edge), Image.ANTIALIAS)
                bytesDate = BytesIO()
                region.save(bytesDate, format='png')
                data = bytesDate.getvalue()
            except IOError as e:
                type_ = 'file'
    if type_ == 'file':
        logging.error(f'{path} is file')
    return data, response_type

import psutil
def list_disks():
    '''获取所有磁盘信息'''
    disks = []
    partitions = psutil.disk_partitions()   # linux未测试TODO
    for part in partitions:
        driver_name = part[0]   # 驱动器名
        total, used, free, percent = psutil.disk_usage(driver_name)
        usage = {'total': total, 'used': used, 'percent': percent}
        total = transByte(total)
        used = transByte(used)
        disks.append({'name': driver_name, 'size': f'{used}/{total}: {percent}%', 'type': 'disk', 'usage': usage, 'path': pack_path(driver_name)})
    return disks

def list_path(path, opts=[], cd=False):
    code, msg, resources = 0, '', []
    abspath = parse_path(path)
    if abspath == '':    # 意味着需要获取所有磁盘信息
        resources = list_disks()
    elif os.path.exists(abspath) is False:
        code, msg = cfg.pack_warning('ERROR_PATH_NOTEXIST', path)
    elif os.path.isdir(abspath):
        resources = list_folder(abspath)
        if '-r' in opts:
            pass
    elif cd:
        code, msg = cfg.pack_error('Error_Not_Folder', path)
    else:
        resources.append(list_file(abspath))
    return {'code': code, 'msg': msg, 'resource': sort_resource(resources)}

def copy(srclist, dest, opts=[]):
    code, msg, ext = 0, '', {}
    abs_dest = parse_path(dest)
    if os.path.isfile(abs_dest):
        if len(srclist) > 1:
            code, msg = cfg.pack_error('Error_Not_Folder', abs_dest)
        elif os.path.isdir(parse_path(srclist[0])):
            code, msg = cfg.pack_error('CANNOT_OVERWRITE', srclist[0], dest)
    if code == 0:
        try:
            for src in srclist:
                abs_src = parse_path(src)
                if not os.path.exists(abs_src):
                    code, ext[src] = cfg.pack_warning('ERROR_PATH_NOTEXIST', src)
                elif os.path.isdir(abs_src):
                    if 'r' not in opts:
                        code, ext[src] = cfg.pack_warning('Error_Lack_Option', '-r', f'复制文件夹{src}')
                    else:
                        shutil.copytree(abs_src, abs_dest)
                else:
                    shutil.copy(abs_src, abs_dest)
        except FileNotFoundError:
            code, msg = cfg.pack_error('ERROR_PATH_NOTEXIST', dest)
    result = {'code': code, 'msg': msg}
    if 'ext' in dir():
        result['ext'] = ext
    return result

def move(srclist, dest, opts=[]):
    code, msg, ext = 0, '', {}
    abs_dest = parse_path(dest)
    rename = not os.path.exists(abs_dest)
    if os.path.isfile(abs_dest):
        if len(srclist) > 1:
            code, msg = cfg.pack_error('Error_Not_Folder', dest)
        elif os.path.isdir(parse_path(srclist[0])):
            code, msg = cfg.pack_error('CANNOT_OVERWRITE', srclist[0], dest)
    if code == 0:
        try:
            for src in srclist:
                abs_src = parse_path(src)
                if not os.path.exists(abs_src):
                    code, ext[src] = cfg.pack_warning('ERROR_PATH_NOTEXIST', src)
                elif os.path.isdir(abs_src) and '-r' not in opts:
                    code, ext[src] = cfg.pack_warning('Error_Lack_Option', src, f'移动文件夹{src}')
                else:
                    shutil.move(abs_src, abs_dest)
                    # 标签信息也要相应修改
                    # 获得反斜杠的完全小写的路径（仅限Windows）
                    # norm_src = os.path.normpath(os.path.normcase(abs_src))
                    # norm_dest = os.path.normpath(os.path.normcase(abs_dest))
                    # 处理标签与norm_src的相互对应
                    # after_path应当是移动后的路径，若为文件夹，需进行转换
                    after_path = abs_dest if rename else os.path.join(abs_dest, os.path.basename(abs_src)).replace('\\', '/')
                    twist(abs_src, after_path, delete=False)
                    # 处理标签与norm_src子路径的相互对应
                    for one_path in path_tags:
                        print(common_path(one_path, abs_src), abs_src)
                        if common_path(one_path, abs_src) == abs_src:
                            # one_path是abs_src的子路径
                            twist(one_path, re.sub(f'^{abs_src}', after_path, one_path), delete=False)
        except FileNotFoundError:
            code, msg = cfg.pack_error('ERROR_PATH_NOTEXIST', dest)
    result = {'code': code, 'msg': msg}
    if 'ext' in dir():
        result['ext'] = ext
    return result

def remove(srclist, opts=[]):
    '''批量删除'''
    code, msg, ext = 0, '', {}
    for src in srclist:
        moveFlag = False
        abs_src = parse_path(src)
        if not os.path.exists(abs_src):
            code, ext[src] = cfg.pack_warning('ERROR_PATH_NOTEXIST', src)
        elif os.path.isfile(abs_src):
            shutil.os.remove(abs_src)
            moveFlag = True
        elif '-r' in opts:
            shutil.rmtree(abs_src)
            moveFlag = True
        else:
            code, ext[src] = cfg.pack_warning('Error_Lack_Option' '-r', f'删除文件夹{src}')
        if moveFlag:
            # 相关标签信息也要相应移除
            twist(abs_src)
            # 移除标签与abs_src的子路径的关系
            for one_path in path_tags:
                if common_path(one_path, abs_src) == abs_src:
                    # one_path是abs_src的子路径
                    twist(one_path, re.sub(f'^{abs_src}', after_path, one_path), delete=False)
    return {'code': code, 'msg': msg, 'ext': ext}

def newdir(path, opts=[]):
    '''新建文件夹'''
    def rec_newdir(path):
        if os.path.exists(path) or os.path.dirname(path) == path:
            return
        else:
            rec_newdir(os.path.dirname(path))
            os.mkdir(path)

    abs_path = parse_path(path)
    code, msg = 0, ''
    try:
        if 'p' in opts or 'parent' in opts:
            # rec_newdir(abs_path)
            os.makedirs(abs_path)
        else:
            os.mkdir(abs_path)
    except FileNotFoundError:
        code, msg = cfg.pack_error('ERROR_PATH_NOTEXIST', os.path.dirname(path))
    except PermissionError:
        code, msg = cfg.pack_error('Error_Permission', os.path.dirname(path))
    except FileExistsError:
        code, msg = cfg.pack_error('ERROR_ALREADY_EXIST', path)
    return {'code': code, 'msg': msg}


def get_paths_property(paths):
    '''获取标签下的：文件夹数、文件数、大小、占用空间'''
    code, msg = 0, {}
    nfile = 0
    nfolder = 0
    total_size = 0
    total_occupation = 0

    def count_file(filename):
        '''统计文件'''
        nonlocal nfile, total_size, total_occupation
        nfile += 1
        total_size += os.path.getsize(filename)
        if not bWindows:
            occu = os.popen(f'du {filename}').read().split('\t')[0]
            total_occupation += int(occu)

    def count_folder(folder):
        '''遍历文件夹'''
        nonlocal nfolder
        for dirname, subdirs, filenames in os.walk(folder):
            nfolder += len(subdirs)
            for filename in filenames:
                fullname = parse_path(dirname + '/' + filename)
                count_file(fullname)

    for path in paths:
        abs_path = parse_path(path)
        if os.path.isdir(abs_path):
            count_folder(abs_path)
        elif os.path.isfile(abs_path):
            count_file(abs_path)
    return {'code': code, 'msg': msg, 'data': {'nfolder': nfolder, 'nfile': nfile, \
        'total_size': transByte(total_size), 'total_occupation': transByte(total_occupation) if not bWindows else None}}
