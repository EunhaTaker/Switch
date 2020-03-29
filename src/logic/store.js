import Vue from 'vue'
import Vuex from 'vuex'
import conf from '../../configs/request-conf.json'
const setting = require('../../configs/user-setting.json').client
Vue.use(Vuex)

let showComp = null

const state = {
	// 当前目录下的文件数据
	contents: [],
	// 浏览模式：path, tag
	mode: 'path',
	// 当前文件路径
	curfolder: '/',
	// 当前标签路径
	curtagpath: '#',
	// 当前标签
	curtag: null,
	// 图像显示规格[行,列]
	img_std: [5, 5],
	// 图标每行显示数量
	icon_std: [8, 8],
	// 历史命令队列
	history_cmds: [],
	// 历史记录游标
	history_pos: 0,
	// 网络请求配置
	conf: conf,
	// 被选中的文件或标签
	select_list: [],
	// 选中内容类型：path, tag, disk
	select_type: null,
	// 剪贴板
	clipboard: [],
	// 剪贴类型：copy, cut
	clip_type: null,
	
}

const getters = {
	pwd: state => {
		return state.mode==='path'? state.curfolder: state.curtagpath
	},
	conf: state => {
		return state.conf
	},
	martix: state => {
		let i=0
		let martix_ = []
		let subarr = []
		for(let file of state.contents){
			// console.log(file.type)
			subarr.push(file)
			i++
			if((file.type == 'img' && i>=state.img_std[0])
				|| (i>=state.icon_std[0]))
			{
				martix_.push(subarr)
				subarr = []
				i = 0
			}
		}
		if(i > 0) martix_.push(subarr)
		return martix_
	},
}

const actions = {
	init: function({commit}, vm){
		showComp = vm
		commit('init')
	},
	// change_dir: function({commit}, data){
	// 	commit('change_dir', data)
	// },
	// open_tag: function({commit}, data){
	// 	commit('open_tag', data)
	// },
	// unfold_tag: function({commit}, files){
	// 	commit('unfold_tag', files)
	// },
	record_cmd: function({commit}, cmd){
		commit('record_cmd', cmd)
	}
}

const mutations = {
	init(state){
		showComp.$on('clear-selects', function(){
			// 重置选中项的样式
			for(var select of state.select_list){
				select.style.backgroundColor = ''
			}
			// 清空选中列表
			state.select_list.splice(0, state.select_list.length)
		})
		// 设置历史命令条目上限
		state.history_cmds.cap = 20
		// 服务端host
		state.conf.host = setting.server+':'+setting.port
	},
	change_dir(state, data){
		if(data.path.lastIndexOf('/')!==data.path.length-1 && data.path.lastIndexOf('\\') !== data.path.length-1)
			data.path += '/'
		state.mode = 'path'
		state.curfolder = data.path
		state.contents = data.files
		// state.chain = data.chain
		// 重置选中
		showComp.$emit('clear-selects')
		if(data.path != '/'){
			let parts = data.path.split(/\/|\\/)
			parts.splice(parts.length-2, 1)
			// 添加返回上级图标
			state.contents.unshift({name:'<-', type:'back-fol', path:parts.join('/')})
		}
	},
	open_tag(state, data){
		state.mode = 'tag'
		state.curtagpath = data.chain
		state.contents = data.contents
		state.curtag = data.tag
		// 重置选中
		showComp.$emit('clear-selects')
		if(data.tag != '#'){
			let parts = data.chain.split('>')
			parts.pop()
			// 添加返回上级图标
			state.contents.unshift({name:parts.pop(), type:'back-tag'})
		}
	},
	unfold_tag(state, files){
		state.contents = files
	},
	record_cmd(state, cmd){
		'登记命令到历史记录'
		if(state.history_cmds[state.history_cmds.length-1] !== cmd){
			// 与上条历史记录不相同，才记录
			window.enqueue(state.history_cmds, cmd)
		}
		// 游标重置
		state.history_pos = state.history_cmds.length
	},
}

export default new Vuex.Store({
	state,
	actions,
	mutations,
	getters,
})