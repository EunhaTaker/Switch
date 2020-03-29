import req from './request.js'
// import alias from '../../server/alias.json'

let context = null
let alias = {cmd: [], opt: []}

const cli_cb = function(res, cb){
	if(cb){
		if(res.code === 100) cb(0, Object.values(res.ext).join('<br>'))
		else if(res.code > 100) cb(1, res.msg)
		else cb()
	}
}

const check_targets = function(targets, narg=[], type='path'){
	// narg限制参数数量,空表示无限制,1个元素限制最低参数数量,2个元素限制最低和最高参数数量
	if(narg.length > 0){
		if(targets.length < narg[0]){
			return '参数过少,至少需要'+narg[0]+'个参数'
		}
		if(narg.length == 2 && targets.length > narg[1]){
			return '参数过多,最多只能有'+narg[1]+'个参数'
		}
	}
	if(type === 'path'){
		for(let i in targets){
			let tar = targets[i]
			const dir = (context.$store.state.mode === 'path')? context.$store.state.curfolder: context.$store.state.curtagpath
			if(tar == '.'){
				if(context.$store.state.mode === 'tag')
					return '标签模式暂不支持此操作'
				tar = context.$store.state.curfolder
			}else if(tar[0] !== '/'){
				if(context.$store.state.mode === 'tag')
					return '标签模式暂不支持此操作'
				// 相对路径转绝对路径
				tar = context.$store.state.curfolder + tar
			}
			let parts = tar.split(/[\\\/]/)	// 按斜杠或反斜杠拆分
			let j = 0
			while(j < parts.length){
				if(/^\.+$/.test(parts[j])){	// parts[i]是....的格式
					let nback = parts[j].length - 1	// x个点将回退x-1级
					if(nback > j)	// 回退过多
						return targets[i] + ' 路径错误'
					parts.splice(j-nback, nback+1)	// 删除时包括parts[i]
					j -= nback+1
				}else{
					j ++
				}
			}
			targets[i] = parts.join('/')
			if(targets[i] === ''){
				// 相对路径回退到底
				targets[i] = '/'
			}
			if(/.*:$/.test(targets[i]))
				// 路径以冒号结尾，如c:，转换为c:/
				targets[i] += '/'
		}
	}
	return true
}

const preprocess = function(cmdline){
	'预处理：解析别名、清除不必要的空格、保护必要的空格'
	// do-while处理嵌套别名
	// record数组记录解嵌套过程中出现的所有别名，防止出现环路
	let record = []
	do{
		var tmpcmd = cmdline	// tmpcmd===cmdline意味指代到头
		cmdline = cmdline.replace(/^\s*(\S+)/, function($0, $1){
			if(record.indexOf($1) != -1){
				// 环路出现，将record标记为null
				record = null
				return $1
			}else{
				record.push($1)
			}
			return alias.cmd[$1]? alias.cmd[$1]: $1
		})
	}while(record !== null && cmdline !== tmpcmd)
	// 保护空格转义
	cmdline = cmdline.replace(/\\ /g, '@#$')
	// 保护每对引号之间的空格，消除引号本身
	cmdline = cmdline.replace(/[\'\"].*?[\'\"]/g, function(a,b,c){
		return a.replace(/ /g, '@#$').replace(/[\'\"]/g, '')
	})
	// 消除=和,周围的空白
	cmdline = cmdline.split(/ *, *(?!\s*-)/).join(',').split(/ *= */).join('=')
	return cmdline
}

const split_cmd = function(cmdline){
	'分解命令行，并恢复受保护的空格'
	let parts = cmdline.split(/ +/)
	let command = parts.shift()
	let targets = []
	let setting = {}
	let options = []
	let tmparr
	for(let part of parts){
		// "命令 -h"转换为"help 命令"
		if(part==='-h' || part==='--help'){
			targets = [command]
			command = 'help'
			break
		}
		// 恢复空格转义
		part = part.replace(/@#\$/g, ' ')
		if(/^-/.test(part)){	// 选项
			tmparr = part.split('=')
			if(/^--/.test(part)){	// 长选项(长选项将通过alias替换为短选项)
				if(tmparr.length == 1){	// 未指定值
					if(alias.opt[part]) part = alias.opt[part]
					options.push(part)
				}else{	// 指定值
					if(alias.opt[tmparr[0]])
						setting[alias.opt[tmparr[0]]] = tmparr[1]
				}
			}else for(let opt of part.substring(1).split('')){	// 短选项
				if(tmparr.length == 1){	// 未指定值
					options.push('-'+opt)
				}else if(tmparr[0].length > 2){
					if(cb) cb(1, part + '：无法为多个选项指定值')
					return
				}else	// 指定值
					setting[tmparr[0]] = tmparr[1]
			}
		}else{
			targets.push(part)
		}
	}
	return [command, targets, setting, options]
}


const parse_cmd = function(cmdline){
	'解析命令'
	// console.log(cmd+ ' cmd is ')
	// 命令行预处理
	cmdline = preprocess(cmdline)
	// 分解命令行
	return split_cmd(cmdline)
}

export default{
	init(ctx){
		context = ctx
		req.init_store(ctx.$store)
		let self = this
		// 获取别名信息
		this.exe_cmd('alias --init')
		this.exe_cmd('cd /')
	},
	
	exe_cmd(cmdline, cb){
		// console.log('cmdline:', cmdline)
		let command, targets, setting, options
		[command, targets, setting, options] = parse_cmd(cmdline)
		// console.log('exe::', command, targets, setting, options)
		switch(command){
			case 'cd': {
				let result = check_targets(targets, [1, 1])
				if(result === true){
					req.change_dir(targets[0], function(res){
						if(res.code === 0 && cb) cb()
						else if(cb) cb(1, res.msg)
					})
				}else{
					if(cb) cb(1, result)
				}
				break
			}
			case 'ls': {
				if(cb){
					// ls <==> ls .
					if(targets.length == 0)
						targets.push('.')
					// 参数检查与调整
					const result = check_targets(targets)
					if(result !== true){
						cb(1, result)
						break
					}
					for(let path of targets){
						let str = ''
						req.list_dir(path, options, function(res){
							if(res.code === 100) cb(0, Object.values(res.ext).join('<br>'))	// 部分失败
							else if(res.code > 100) {return cb(1, res.msg) }
							// 多路径
							else if(targets.length > 1) str += '<br>'+path+':<br><br>'
							// 拼接信息
							const {resource = []} = res || {}
							for(let file of resource){
								if(options.indexOf('-l') != -1 || options.indexOf('--line') != -1){
									if(file.type === 'tag')
										str += [file.type, file.name, 'c:'+file.color, '<br>'].join('  ')
									else
										str += [file.type, file.name, file.size, file.tag, '<br>'].join('  ')
								}else{
									str += file.name + '  '
								}
							}
							if(!setting.line && targets.length>1) str += "<br>"
							cb(-1, str)
						})
					}
				}
				break
			}
			case 'open':{
				const result = check_targets(targets)
				if(result !== true){
					cb(1, result)
				}else
					req.open_file(targets[0])
				break
			}
			case 'rm':{
				let result = check_targets(targets, [1])
				if(result !== true){
					if(cb) cb(1, result)
				}else {
					req.remove(targets, options, function(res){
						cli_cb(res, cb)
					})
				}
				break
			}
			case 'cp':{
				let result = check_targets(targets, [2])
				if(result === true){
					let dest = targets.pop()
					req.copy(targets, dest, options, function(res){cli_cb(res, cb)})
				}else if(cb) cb(1, result)
				break
			}
			case 'mv':{
				let result = check_targets(targets, [2])
				if(result === true){
					let dest = targets.pop()
					req.move(targets, dest, options, function(res){cli_cb(res, cb)})
				}else if(cb) cb(1, result)
				break
			}
			case 'mkdir': {
				let result = check_targets(targets, [1, 1])
				if(result === true){
					let path = targets[0]
					req.new_dir(path, options, function(res){cli_cb(res, cb)})
				}else if(cb) cb(1, result)
				break
			}
			case 'pwd':{
				req.pwd(function(pwd){if(cb)cb(-1, pwd)})
				break
			}
			case 'newtag': {
				let result = check_targets(targets, [1, 3], 'other')
				if(result){
					name = targets.shift()
					req.new_tag(name, setting['-c'], setting['-p'], function(res){
						cli_cb(res, cb)
					})
				}else{
					if(cb) cb(1, result)
				}
				break
			}
			case 'settag': {
				// 检查参数数量
				let result = check_targets(targets, [1], 'none')
				// 检查路径
				if(result===true) result = check_targets(targets)
				if(result===true){
					req.set_tag(targets, setting['-a'], setting['-d'], function(res){cli_cb(res, cb)})
				}else if(cb){
					cb(1, result)
				}
				break
			}
			case 'modtag': {	// 修改标签
				let name = targets.shift()
				req.mod_tag(name, setting['-n'], setting['-c'], setting['-p'], function(res){cli_cb(res, cb)})
				break
			}
			case 'rmtag': {
				req.rm_tag(targets, options, function(res){cli_cb(res, cb)})
				break
			}
			case 'ct': {
				let result = check_targets(targets, [1, 1], 'tag')
				if(result === true){
					req.change_tag(targets[0], function(res){cli_cb(res, cb)})
				}else if(cb) cb(result)
				break
			}
			case 'unfold': {
				let result = check_targets(targets, [1], 'tag')
				if(result === true){
					req.unfold(targets, function(res){cli_cb(res, cb)})
				}else if(cb) cb(result)
				break
			}
			case 'clear': {
				context.history = ''
				if(cb) cb()
				break
			}
			case 'help': {
				req.help(targets[0], function(res){
					if(cb) cb(res.code>100?1:-1, res.msg.replace(/\n/g, '<br>'))
				})
				break
			}
			case 'alias': {
				let a, c
				[a, c] = targets
				if(options.indexOf('-l') != -1){
					// 查看别名
					if(cb){
						if(a){	// 查看cmd
							if(alias.cmd[a]) cb(-1, '%:  %'.format(a, alias.cmd[a]) )
						}else{	// 查看所有别名
							let str = ''
							for(let name in alias.cmd){
								str += '%:  %<br>'.format(name, alias.cmd[name])
							}
							cb(-1, str)
						}
					}
				}else{
					req.alias(a, c, options, function(res){
						if(res.code === 0){
							if(options.indexOf('--init') != -1){
								alias = res.content
								if(cb)cb()
							}else if(options.indexOf('-d') != -1){
								delete alias.cmd[a]
							}else{
								alias.cmd[a] = c
							}
						}else{
							if(cb) cb(1, res.msg)
						}
					})
				}
				break
			}
			default: {
				if(cb) cb(1, 'command "' + command + '" not found')
				break
			}
		}
	},
	tab: function(cmdline, cb){
		// console.log('tab cmdline:', cmdline)
		// 预处理命令行
		cmdline = preprocess(cmdline)
		// console.log('tab cmdline:', cmdline)
		// 按空格分隔
		let parts = cmdline.split(/ +/)
		// console.log('tab cmdline:', parts)
		var type, target, command
		if(parts.length == 1){
			// 只有1个部分，需补全指令
			target = parts[0]
			type = 'cmd'
		}else{
			// 否则，关注最后一部分
			target = parts.pop()
			command = parts[0]
			if(target.indexOf('=') != -1){
				[type, target] = target.split('=')
			}
		}
		if(type !== 'cmd'){
			if(type){
				type = type.replace(/^-(p|a|d)$/, 'tag')
			}else{
				if(/^(ls|mv|cp|rm|mkdir|settag|open)$/.test(command))
					type = 'path'
				else if(/^(cd|mkdir)$/.test(command))
					type = 'dir'
				else if(/^(newtag|modtag|ct|rmtag|unfold)$/.test(command))
					type = 'tag'
				else if(command === 'help')
					type = 'cmd'
			}
			if(/(path|dir|file)/.test(type)){
				// 确保target是绝对路径
				target = [target]
				check_targets(target)
				target = target[0]
			}
		}
		// 恢复空格转义
		target = target.replace(/@#\$/g, ' ')
		if(type) req.tab_cmd(target, type, function(res, perfix){
			// 对返回结果，将左边没有反斜杠的空格加上反斜杠
			perfix = perfix.replace(/[^\\] /g, function($0){
				return $0.replace(/ /g, '\\\\ ')	// 4个反斜杠匹配一个反斜杠
			})
			// for(let i in res){
			// 	res[i] = res[i].replace(/[^\\] /g, function($0){
			// 		return $0.replace(/ /g, '\\ ')
			// 	})
			// }
			cb(res, perfix)
		})
		
	}
}