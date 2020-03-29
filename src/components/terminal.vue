<template>
	<div id='terminal'
		@click.stop="focus_click"
	>
		<div id = 'terminal-bar'>
			<img src="../assets/image/right_arrow.png" />
		</div>
		<div 
			id = 'history-part'
			v-html="history" 
			
		/>
		<div id="input-part"
		>
			<div class='prompt' ref='prompt'>
				>
			</div>
			<div 
				id = 'command-input'
				ref = 'input_text'
				contenteditable = true
				autofocus
				spellcheck = false
				@keydown.tab.enter.stop.prevent = ''
				@keydown = 'onType'
				@keyup.enter = 'onEnter'
				@keyup.up.stop.prevent = 'onUp'
				@keyup.down.stop.prevent = 'onDown'
				@keyup.tab.stop.prevent = 'onTab'
			/>
		</div>
		<div id="advice-part"
			ref = 'advice_part'
			v-html="advice_html"
		></div>
	</div>
</template>

<script>
	import handle from '../logic/handle_cmd.js'
	import { mapActions } from 'vuex'
	export default{
		name: 'command_line',
		props: {},
		data: function(){
			return {
				history: '',	// 历史交互内容
				advice_html: '',	// 候选区内容
				advice_index: -1,	// 候选区当前位置
				advice_list: null,	// 联想列表
			}
		},
		methods:{
			...mapActions(['change_dir', 'unfold_tag', 'record_cmd', 
				'set_advice', 'clear_advice']),
			onEnter: function(i){
				if(this.advice_list){
					// 代表选定联想词，应清空候选区
					this.clear_advice()
					return
				}
				// 输出结果
				// var result = ''
				// 编辑区内容
				let cmd = this.$refs.input_text.innerHTML.replace(/<div>|<\/div>|<br>|<span>|<\/span>/g, '')
				console.log(cmd.replace(/&nbsp;/g, ' ').trim())
				// 输入内容附加到 历史交互
				this.history += '<div>'+this.$refs.prompt.innerHTML.trim()+cmd+'</div>'
				// 清空输入区
				this.$refs.input_text.innerHTML = ''
				if(cmd.replace(/&nbsp;/g, ' ').trim() === '')
					// 忽略空命令
					return
				// 记录到历史命令
				this.record_cmd(cmd)
				// 提交命令
				const self = this
				handle.exe_cmd(cmd.replace(/&nbsp;/g, ' ').trim(), function(errcode, str){
					if(str){
						let color_style = ''
						if(errcode === 1) color_style = 'style="color: #D70022"'
						else if(errcode === 0) color_style = 'style="color: #BE9B00"'
						else if(errcode === -1) color_style = 'style="color: #FEFAD5"'
						// 加上提示符，以及用<div>包围（确保换行）
						self.history += '<div %>%</div>'.format(color_style, str)
					}
				})
				
				
			},
			onTab: function(){
				const self = this
				let focusIndex = getSelection().focusOffset
				if(focusIndex == 1 && getSelection().focusNode.nodeName !== '#text'){
					// 光标又跑div上去了
					focusIndex = this.$refs.input_text.textContent.length
				}
				const cmd = this.$refs.input_text.innerHTML //.replace(/<span>|<\/span>/g, '')
				// 没有前缀，无需补全
				if(cmd === '' || cmd[cmd.length-1] === ' ') return
				let head = cmd.substring(0, focusIndex)
				// console.log('tab::',focusIndex,getSelection().focusNode)
				const tail = cmd.substring(focusIndex)
				// console.error(this.advice_list)
				if(this.advice_list){
					// 已展示候选区，当切换联想词
					if(this.advice_index !== -1){
						// 已进入候选区，恢复上一条联想词颜色
						this.$refs.advice_part.childNodes[this.advice_index].style = null
						this.$refs.advice_part.childNodes[this.advice_index].style = null
						
					}//else{
					// 	this.advice_index += 1
					// 	this.$refs.input_text.innerHTML = '%<span>%</span>%'.format(head, this.advice_list[this.advice_index], tail)
					// }
					this.advice_index += 1
						this.advice_index %= this.advice_list.length
						// 将当前联想词插入命令行
						this.$refs.input_text.innerHTML = this.$refs.input_text.innerHTML.replace(/<span>.*?<\/span>/, function($0){
							return '<span>%</span>'.format(self.advice_list[self.advice_index])
						})
					// 反转当前联想词颜色
					const black = '#002B36'
					const white = '#FFFFFF'
					this.$refs.advice_part.childNodes[this.advice_index].style.color = black
					this.$refs.advice_part.childNodes[this.advice_index].style.backgroundColor = white
					
					// 设置光标
					const span = this.$refs.input_text.getElementsByTagName('span')[0]
					this.focus_in(span, 1)
				}else{
					handle.tab(head, function(res, perfix){
						if(res.length == 0) return
						const pattern = new RegExp(perfix + '$')
						console.warn(res, perfix, pattern)
						if(res.length == 1){
							// 单个联想词直接填充
							head = head.replace(pattern, res[0])
							self.$refs.input_text.innerHTML = head + tail
							console.warn('hj和', head, self.$refs.input_text.innerHTML)
							// 设置光标
							const div = self.$refs.input_text
							self.focus_in(div, 1)
							// self.clear_advice()
						}else{
							// 多个联想词，设置候选区
							self.$refs.input_text.innerHTML = head.replace(pattern, '<span>%</span>'.format(perfix)) + tail
							// 设置光标
							const span = self.$refs.input_text.getElementsByTagName('span')[0]
							self.focus_in(span, 1)
							let str = ''
							for(let adv of res){
								str += '<span>'+adv+'</span>'
							}
							self.advice_list = res
							console.warn('tab_res::',res)
							self.advice_html = str
							self.advice_index = -1
						}
						
					})
				}
			},
			onUp: function(){
				var state = this.$store.state
				if(state.history_pos - 1 >= 0){
					state.history_pos -= 1
					this.$refs.input_text.innerHTML = state.history_cmds[state.history_pos]
					this.focus_click()
				}
				// console.log(state.history_cmds+"  "+state.history_pos)
			},
			onDown: function(){
				var state = this.$store.state
				if(state.history_pos + 1 > state.history_cmds.length){return}
				state.history_pos += 1
				if(state.history_pos == state.history_cmds.length){
					this.$refs.input_text.innerHTML = ''
				}else{
					this.$refs.input_text.innerHTML = state.history_cmds[state.history_pos]
				}
				this.focus_click()
				// console.log(state.history_cmds+"  "+state.history_pos)
			},
			onType: function(key){
				// 语法高亮
				// 字符数量达某个值，新增一个可编辑div
				// float为none
				// 考虑删除情况
				if(this.advice_list && !/Tab|Enter/.test(key.code)){
					this.clear_advice()
				}
			},
			clear_advice: function(){
				// 清空候选区
				this.advice_list = null
				this.advice_html = ''
				// 联想词所在的span和其前面的text的长度之和，用于正确聚焦
				if(this.$refs.input_text.childNodes[0].nodeName === 'SPAN')
					var len = this.$refs.input_text.childNodes[0].textContent.length
				else
					var len = this.$refs.input_text.childNodes[0].textContent.length + this.$refs.input_text.childNodes[1].textContent.length
				// 左右键应当对聚焦位置产生影响
				// if(key.code == 'ArrowLeft');
					// len -= 1
				// else if(key.code == 'ArrowRight' && len < this.$refs.input_text.textContent.length)
					// len += 1
				// 剔除掉<span>，顺便清掉讨厌的<br>
				this.$refs.input_text.innerHTML = this.$refs.input_text.innerHTML.replace(/<span>|<\/span>|<br>/g, '')
				console.warn('clear::',this.$refs.input_text.innerHTML)
				// 聚焦
				this.focus_in(this.$refs.input_text.childNodes[0], len)
			},
			focus_in: function(node, index){
					var s = getSelection()
					var r = document.createRange()
					r.setStart(node, index)
					r.setEnd(node, index)
					s.removeAllRanges()
					s.addRange(r)
			},
			focus_click: function(){
				if(getSelection().anchorNode.nodeName === '#text'
						&& getSelection().anchorNode.nodeValue === this.$refs.input_text.innerHTML)
					return
				var editor = this.$refs.input_text
				if(!editor.innerHTML){
					editor.focus()
				}else{	// 焦点集中到命令末端
					var len = editor.childNodes.length
					this.focus_in(editor, len)
				}
			},
			stringify_cb: function(key, value) {
				// console.log(key+"   ...  ")
				if (typeof value === 'object' && value) {
						if (cache.indexOf(value) !== -1) {
							// Circular reference found, discard key
							return;
						}
						// Store value in our collection
						cache.push(value);
					}
					return value;
			},
				
		},
		mounted: function(){
			// 自动聚焦
			this.$refs.input_text.focus()
			// 初始化：初始界面、别名信息
			handle.init(this)
			console.info('terminal mounted')
		}
		
	}
</script>

<style src='../assets/style/terminal.css'></style>