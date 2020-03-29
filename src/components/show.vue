<template>
	<div id='show-page'
		ref='show_page'
		@contextmenu.prevent = "onMenu"
		@click = "onDirClick"
	>
		<dirMenu ref = 'dir_menu'></dirMenu>
		<div v-for='line of martix'
			style="width: 100%"
		> 
			<div id='display-content' v-for='content of line'
				:style="{width: 100/ele_width(content)+'%',
						 height: 100/(content.type=='img'?img_std[1]:icon_std[1])+'%'}"
				:fullname = 'content.path || content.name'
				:type = 'content.type'
				onselectstart="return false;"
				@dblclick.stop="onDblclick($event, content)"
				@click.stop='onClick($event, content)'
			>
				<div class='icon' v-if='/^back/.test(content.type)'>
					<img class="icon-icon" :src = '"../assets/image/back.png"'/>
					<!-- <div class="text icon-text"><-</div> -->
				</div>
				<div class='disk' v-else-if='content.type == "disk"'>
					<progress class='disk-progress'
						:value= 'content.usage.percent' :max='100'></progress>
					<div class='text disk-text'>
						{{content.name}} 已用{{content.size}}
					</div>
				</div>
				<div class='tag' v-else-if='content.type == "tag"'>
					<div>{{content.name}}</div>
				</div>
				<div class='img' v-else-if='content.type == "img"'>
					<img :src = 'conf.host+conf.read_file+"?"+conf.read_file_args[0]+"="+ content.path +"&opts=--thumb"'
						:alt = 'content.path'
						/>
				</div>
				<div class='icon' v-else
					style="width: 100%"
					>
					<img class="icon-icon" :src = '"../assets/image/"+(content.type=="dir"?"folder":"file")+".png"'/>
					<div class="text icon-text">{{content.name}}</div>
				</div>
			</div>
		</div>
	</div>
</template>


<script>
	import dirMenu from './show-menu.vue'
	import { mapGetters } from 'vuex'
	import handle from '../logic/handle_operate.js'
// import func from '../../vue-temp/vue-editor-bridge'
	export default {
		name: 'show-page',
		computed: {
			...mapGetters(['martix', 'pwd', "conf", "select_list"]),
			icon_width: function(){
				alert(this.$refs.show_page.offsetWidth/8)
				return this.$refs.show_page.offsetWidth/8
			},
			icon_std: function(){
				return this.$store.state.icon_std
			},
			img_std: function(){
				return this.$store.state.img_std
			},
		},
		data: function(){
			return {
				menu_content: ''
			}
		},
		beforeMount: function(){},
		methods:{
			ele_width: function(content){
				switch(content.type){
					case 'img': return this.img_std[0];
					case 'disk': return 5;
					default: return this.icon_std[0];
				}
			},
			onMenu: function(key, content){
				const state = this.$store.state
				// 设置菜单位置
				const dir_menu = this.$refs.dir_menu['$el']
				dir_menu.style.visibility = 'visible'
				dir_menu.style.left = key.clientX + 'px'
				dir_menu.style.top = key.clientY + 'px'
				// 获取元素
				const selectColl = document.getElementsByClassName('for-select')
				const singleColl = document.getElementsByClassName('for-single')
				const pathColl = document.getElementsByClassName('for-path')
				const curfolderColl = document.getElementsByClassName('for-curfolder')
				const curtagColl = document.getElementsByClassName('for-curtag')
				let itemsSet = []	// 待显示列表
				if(state.select_list.length == 0){
					if(state.mode === 'tag'){
						itemsSet.push(...Array.from(curtagColl))
					}else{
						itemsSet.push(...Array.from(curfolderColl))
						const pasteNode = document.getElementById('paste')
						if(state.clipboard.length == 0){	// 处理粘贴项显示效果
							pasteNode.style.color = '#EEEEEE'
							pasteNode.style['pointer-events'] = 'none';
						}else{
							pasteNode.style.color = 'black'
							pasteNode.style['pointer-events'] = 'all';
						}
					}
				}else{
					itemsSet.push(...Array.from(selectColl))
					if(state.select_list.length == 1) itemsSet.push(...Array.from(singleColl))
					if(state.select_type === 'path') itemsSet.push(...Array.from(pathColl))
				}
				// 显示上述节点，隐藏其他菜单项
				let itemsExclude = Array.from(document.getElementsByClassName('menu-item'))	// 待隐藏列表
				for(const item of itemsSet){
					item.style.display = 'block'
					window.arrRemove(itemsExclude, item)
				}
				// 隐藏菜单项
				for(const item of itemsExclude){
					item.style.display = 'none'
				}
				// only-path项在标签模式下需隐藏，反之亦然
				if(state.mode !== 'path'){
					const onlypathmodeColl = document.getElementsByClassName('only-pathmode')
					for(let item of Array.from(onlypathmodeColl)){
						item.style.display = 'none'
					}
				}else if(state.mode !== 'tag'){
					const onlytagmodeColl = document.getElementsByClassName('only-tagmode')
					for(let item of Array.from(onlytagmodeColl)){
						item.style.display = 'none'
					}
				}
				// 仅限选中标签有效
				if(state.select_type !== 'tag'){
					const onlytagColl = document.getElementsByClassName('only-tag')
					for(let item of Array.from(onlytagColl)){
						item.style.display = 'none'
					}
				}
			},
			onClick: function(key, content){
				/* 左击内容（文件、文件夹、标签夹） */
				if(/^back/.test(content.type)) return
				this.$refs.dir_menu['$el'].style.visibility = 'hidden'
				const selects = this.$store.state.select_list
				const node = key.originalTarget.parentNode.parentNode
				// 若点击了已选中内容，则标记为取消选中
				const needCancel = (selects.indexOf(node) != -1)
				if(!key.ctrlKey){
					// 单击，清空原有选中效果
					this.$emit('clear-selects')
				}else if(needCancel){
					// ctrl单击已选中内容，取消选中
					window.arrRemove(selects, node)
					node.style.backgroundColor = ''
				}
				if(!needCancel){	// 若非取消选中，则选中之
					let type = content.type=='tag'? 'tag': 'path'
					if(key.ctrlKey && this.$store.state.select_list.length>0 && this.$store.state.select_type != type)
						// 不同类型(path与tag)的内容不可同时选中
						return
					this.$store.state.select_type = type
					node.style.backgroundColor = '#cce8ff'
					selects.push(node)
				}
			},
			onDirClick: function(){
				this.$refs.dir_menu['$el'].style.visibility = 'hidden'
				// 清空所有选中
				this.$emit('clear-selects')
				// Swal.fire('asdf')
			},
			onDblclick: function(key, content){
				if(/dir|disk|back-fol/.test(content.type)){
					handle.cd(content.path, function(res){
						if(res.code > 100) dirMenu.packs.alertError(res.msg)
					})
				}else if(/tag|back-tag/.test(content.type)){
					handle.opentag(content.name, function(res){
						if(res.code > 100) dirMenu.packs.alertError(res.msg)
					})
				}else if(/img/.test(content.type)){
					// dirMenu.onClickOpen(content.fullname, content.type)
					const conf = this.$store.state.conf
					handle.openImg(content.path, conf)
				}else{
					handle.open(content.path)
				}
			}
		},
		
		mounted: function(){
			// 初始化store
			this.$store.dispatch('init', this)
		},
		components: {
			dirMenu
		}
	}
</script>

<style src='../assets/style/show.css'></style>
