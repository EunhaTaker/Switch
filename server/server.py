from flask import Flask, request, Response
app = Flask(__name__)
from common_kit import init
init(app)
from common_kit import os, logging, req_conf, help_cmd, tab_cmd, set_alias, parse_args, pack_result
from path_kit import not_exist, list_disks, list_file, list_folder, get_file, list_path, get_paths_property
from path_kit import copy, move, remove, newdir, open_file
from tag_kit import list_tagroots, new_tag, set_tag, unfold_tag, mod_tag, rm_tag, change_tag, get_tags_property

@app.route(req_conf['list_path'], methods=['GET'])
def listPath():
    res = list_path(
        *parse_args('list_path')
    )
    return pack_result(res)
    
@app.route(req_conf['change_folder'], methods=['GET'])
def cd():
    res = list_path(
        *parse_args('list_path'), cd=True
    )
    return pack_result(res)

@app.route(req_conf['open_file'], methods=['GET'])
def open():
    res = open_file(
        *parse_args('open_file')
    )
    return pack_result(res)

@app.route(req_conf['read_file'], methods=['GET'])
def readfile():
    '''读取文件内容'''
    data, response_type = get_file(
        *parse_args('read_file')
    )
    # if type_ == 'file':
    #     response = pack_result({})
    return pack_result(data, response_type)


@app.route(req_conf['tree'], methods=['GET'])
def tree():
    '''按标签路径访问'''
    path = request.args.get(req_conf['copy_args'][0])
    res = newdir(path, opts)
    return pack_result(res)

@app.route(req_conf['alias'], methods=['GET'])
def alias():
    '''设置别名'''
    res = set_alias(
        *parse_args('alias')
    )
    return pack_result(res)

@app.route(req_conf['help'], methods=['GET'])
def help():
    '''获取命令行帮助信息'''
    return pack_result(
        help_cmd(
            *parse_args('help')
        )
    )

@app.route(req_conf['tab_cmd'], methods=['GET'])
def tab():
    '''获取命令行帮助信息'''
    return pack_result(
        tab_cmd(
            *parse_args('tab_cmd')
        )
    )


@app.route(req_conf['remove'], methods=['GET'])
def rm():
    '''删除文件'''
    res = remove(
        *parse_args('remove')
    )
    return pack_result(res)

@app.route(req_conf['copy'], methods=['GET'])
def cp():
    res = copy(
        *parse_args('copy')
    )
    return pack_result(res)


@app.route(req_conf['move'], methods=['GET'])
def mv():
    res = move(
        *parse_args('move')
    )
    return pack_result(res)


@app.route(req_conf['new_dir'], methods=['GET'])
def mkdir():
    res = newdir(
        *parse_args('new_dir')
    )
    return pack_result(res)

@app.route(req_conf['new_tag'], methods=['GET'])
def newtag():
    result = new_tag(
        *parse_args('new_tag')
    )
    return pack_result(result)

@app.route(req_conf['set_tag'], methods=['GET'])
def settag():
    result = set_tag(
        *parse_args('set_tag')
    )
    return pack_result(result)

@app.route(req_conf['mod_tag'], methods=['GET'])
def modtag():
    res = mod_tag(
        *parse_args('mod_tag')
    )
    return pack_result(res)

@app.route(req_conf['unfold'], methods=['GET'])
def unfold():
    res = unfold_tag(
        *parse_args('unfold')
    )
    return pack_result(res)

@app.route(req_conf['rm_tag'], methods=['GET'])
def rmtag():
    return pack_result(
        rm_tag(
            *parse_args('rm_tag')
        )
    )

@app.route(req_conf['change_tag'], methods=['GET'])
def changetag():
    return pack_result(
        change_tag(
            *parse_args('change_tag')
        )
    )

@app.route(req_conf['get_detail'], methods=['GET'])
def detail():
    targets, type_ = parse_args('get_detail')
    if type_ == 'tag':
        res = get_tags_property(targets)
    else:
        res = get_paths_property(targets)
    return pack_result(res)

if __name__ == "__main__":
    app.run(port=3999)

