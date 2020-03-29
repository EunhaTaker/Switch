'''文件类型'''
# 图像
img_fmat = ['png', 'jpg', 'jepg', 'bmp', 'gif', 'svg']
# 视频
video_fmat = ['avi', 'mp4', 'flv', 'wmv', 'mpeg', 'rmvb']

'''文件大小单位'''
size_unit = ['B', 'KB', 'MB', 'GB', 'TB']

'''全部命令'''
cmds = ['ls','cd','pwd','cp','mv','rm','mkdir','newtag', 'ct', 'settag','modtag','rmtag','help','clear','alias', 'open', 'unfold']

'''错误信息'''
errors = {
    'Partly_Failed': 100,

    'Error_Permission': (102, '权限不足'),
    'Error_Command_Not_Found': (103, '命令%s不存在'),
    'Error_Lack_Arg': (104, '缺少参数'),
    'Alias_Not_Found': (105, '别名%s不存在'),
    'Error_Lack_Option': (106, '尝试使用%s选项%s'),

    'ERROR_PATH_NOTEXIST': (301, '路径%s不存在'),
    'ERROR_ALREADY_EXIST': (302, '路径%s已存在'),
    'Error_Cannot_Overwrite': (304, '无法用文件夹%s覆盖非文件夹%s'),
    'Error_Not_Folder': (305, '%s不是一个文件夹'),
    'Error_Unknown_Fmat': (306, '未知格式'),

    'Error_Tag_Not_Exist': (401, '标签%s不存在'),
    'Error_Tag_Already_Exist': (402, '标签%s已存在'),
    'Error_Tag_Invaild_Name': (403, '标签名含有非法字符：%s'),
}
def pack_error(key, *targets):
    code, msg = errors(key)
    return code, msg % targets
def pack_warning(key, *target):
    _, msg = pack_error(key, *target)
    return errors['Partly_Failed'], msg

'''K'''
K = 1024

