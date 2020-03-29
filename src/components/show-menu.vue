<template>
	<ul ref = 'dir_menu' class = 'menu' @click.stop="onClickMenu">
		<li class="menu-item for-single" @click="onClickOpen">打开</li>
		<li class="menu-item for-curfolder for-curtag" @click="onClickRefresh">刷新</li>
		<li class="menu-item for-curfolder" @click="onClickMkdir">新建文件夹</li>
		<li class="menu-item for-curtag" @click="onClickNewtag">新建标签</li>
		<li class="menu-item for-single only-tag" @click="onClickModtag">修改标签</li>
		<li class="menu-item for-path" @click="onClickSettag($event, 'add')">添加标签</li>
		<li class="menu-item for-path" @click="onClickSettag($event, 'del')">移除标签</li>
		<li class="menu-item for-single" @click="onClickRename">重命名</li>
		<li class="menu-item for-select only-pathmode" @click="onClickCut">剪切</li>
		<li class="menu-item for-select only-pathmode" @click="onClickCopy">复制</li>
		<li class="menu-item for-curfolder" id="paste" @click="onClickPaste">粘贴</li>
		<li class="menu-item for-select only-path" @click="onClickRemove">删除</li>
		<li class="menu-item for-curfolder for-curtag for-select" @click="onClickProperty">属性</li>
	</ul>
</template>

<script>
import handle from '../logic/handle_operate.js'
import Swal from 'sweetalert2'
export default {
	name: 'dir_menu',
	methods: {
		onClickOpen: function(){
			const self = this
			const target = self.$store.state.select_list[0]
			const fullname = target.getAttribute('fullname')
			const type = target.getAttribute('type')
			switch(type){
				case 'dir':
				case 'disk':
					handle.cd(fullname, function(res){
						if(res.code > 100){Swal.fire('', res.msg, 'error')}
					})
					break
				case 'tag':
					handle.opentag(fullname, function(res){
						if(res.code > 100){Swal.fire('', res.msg, 'error')}
					})
					break
				case 'img':
					const conf = self.$store.state.conf
					handle.openImg(fullname, conf)
					break
				default:
					handle.open(fullname)
			}
		},
		onClickMenu: function(){
			this.$refs.dir_menu.style.visibility = 'hidden'
		},
		onClickRefresh: function(){
			const self = this
			handle.refresh(function(res){
				if(res.code === 0) self.packs.alertSuccess('完成')
			})
		},
		onClickMkdir: function(){
			Swal.fire({
				title: '新建文件夹',
				input: 'text',
				showCancelButton: true,
				focusConfirm: true,
				confirmButtonText: '确定',
				confirmButtonAriaLabel: 'Thumbs up, great!',
				cancelButtonText: '取消',
				cancelButtonAriaLabel: 'Thumbs down',
				preConfirm: (dirname) => {
					handle.mkdir(dirname, function(res){
						if(res.code === 0){
							Swal.fire('% 创建完成'.format(dirname), '', 'success')
						}else if(res.code > 100){
							Swal.fire('', res.msg, 'error')
						}
					})
				}
			})
		},
		onClickNewtag: function(){
			const self = this
			Swal.mixin({
				input: 'text',
				confirmButtonText: '下一步&rarr;',
				showCancelButton: true,
				progressSteps: ['名', '色']
			}).queue([
				{
					text: '标签名称'
				},
				{
					text: '颜色（可不填）'
				}
			]).then((result)=>{
				const answers = result.value
				if(!answers[0]) self.packs.alertError('未指定名称')
				else{
					handle.newtag(...answers, self.$store.state.curtag, function(res){
						if(res.code === 0) self.packs.alertSuccess('创建成功')
						else self.packs.alertError(res.msg)
					})
				}
			})
		},
		onClickModtag: function(){
			const self = this
			const tagname = self.$store.state.select_list[0].getAttribute('fullname')
			// const color = self.$store.state.select_list[0].getAttribute('color')
			Swal.fire({
				html: 
					'<input id="name-input" class="swal2-input" placeholder="名称">'+
					'<input id="color-input" class="swal2-input" placeholder="颜色">'+
					'<input id="parent-input" class="swal2-input" placeholder="父标签">',
				text: '无需改变的项可不填',
				showCancelButton: true,
				preConfirm: ()=>{
					let name = document.getElementById('name-input').value || undefined
					let color = document.getElementById('color-input').value || undefined
					let parent = document.getElementById('parent-input').value || undefined
					console.warn(name, color, parent)
					if(name || color || parent){
						handle.modtag(tagname, name, color, parent, function(res){
							if(res.code === 0) self.packs.alertSuccess('完成')
							else if(res.code === 100){
								let ext = []
								for(let k in res.ext) ext.push(res.ext[k])
								self.packs.alertWarning(ext.join('\n'))
							}
						})
					}
				}
			})
		},
		onClickSettag: function(key, type){},
		onClickRename: function(){
			const self = this
			const state = self.$store.state
			const target = state.select_list[0].getAttribute('fullname')
			Swal.fire({
				title: '重命名',
				input: 'text',
				inputValue: target.split(/[\/\\]/).pop(),
				showCancelButton: true,
				focusConfirm: true,
				confirmButtonText: '确定',
				confirmButtonAriaLabel: 'Thumbs up, great!',
				cancelButtonText: '取消',
				cancelButtonAriaLabel: 'Thumbs down',
				preConfirm: (destname) => {
					if(state.select_type === 'path'){
						handle.mv(target, destname, true, function(res){
							if(res.code === 0) self.packs.alertSuccess('完成')
							else if(res.code > 100) self.packs.alertError(res.msg)
						})
					}else if(state.select_type === 'tag'){
						handle.modtag(target, destname, undefined, undefined, function(res){
							if(res.code === 0) self.packs.alertSuccess('完成')
							else if(res.code === 100) self.packs.alertError(res.ext.destname)
							else if(res.code > 100) self.packs.alertError(res.msg)
						})
					}
				}
			})
		},
		onClickCut: function(){
			const state = this.$store.state
			const targetItems = state.select_list
			let srclist = []
			for(let item of targetItems){
				srclist.push(item.getAttribute('fullname'))
			}
			state.clipboard = srclist
			state.clip_type = 'cut'
			this.packs.alertSuccess('已剪切到剪贴板')
		},
		onClickCopy: function(){
			const state = this.$store.state
			const targetItems = state.select_list
			let srclist = []
			for(let item of targetItems){
				srclist.push(item.getAttribute('fullname'))
			}
			state.clipboard = srclist
			state.clip_type = 'copy'
			Swal.fire({
						icon: 'success',
						showConfirmButton: false,
						timer: 600,
						text: '已复制到剪贴板'
					})
		},
		onClickPaste: function(){
			const self = this
			const state = this.$store.state
			if(state.clip_type === 'copy'){
				handle.cp(state.clipboard, function(res){
					if(res.code === 0) self.packs.alertSuccess('复制完成')
				})
			}else if(state.clip_type === 'cut'){
				handle.mv(state.clipboard, null, false, function(res){
					if(res.code === 0) self.packs.alertSuccess('移动完成')
				})
			}
			state.clipboard = []
		},
		onClickRemove: function(){
			let targets = []
			const state = this.$store.state
			for(var node of state.select_list){
				targets.push(node.getAttribute('fullname'))
			}
			Swal.fire({
				title: '确认删除？',
				text: "删除后无法恢复",
				icon: 'warning',
				showCancelButton: true,
				confirmButtonColor: '#d33',
				confirmButtonText: '确定删除',
				cancelButtonText: '取消'
			}).then((result) => {
				if (result.value) {
					handle.rm(targets, state.select_type, function(res){
						if(res.code === 0)
							Swal.fire('已删除!','','success')
					})
				}
			})
		},
		onClickProperty: function(){
			const self = this
			handle.detail(self.$store.state.select_list[0].getAttribute('fullname'), self.$store.state.select_type, function(res){
				if(res.code === 0){
					Swal.fire({
						html: 
							((res.data.ntag)?res.data.ntag + '个标签<br>': '') +
							(res.data.nfolder?res.data.nfolder+'个文件夹<br>':'') +
							res.data.nfile + '个'+ (res.data.ntag?'不重复':'')+'文件<br>'+
							'大小: ' + res.data.total_size + "<br>" +
							((res.data.total_occupation === null)? '': '<br>占用空间: '+res.data.total_occupation),
						icon: 'info',
					})
				}else self.packs.alertError(res.msg)
			})
		}
	},
	data: function(){
		return {
			packs: {
				alertError: function(msg){
					Swal.fire('', msg, 'error')
				},
				alertSuccess: function(msg){
					Swal.fire({
								icon: 'success',
								toast: true,
								position: 'top-right',
								showConfirmButton: false,
								timer: 600,
								text: msg
							})
				},
				alertWarning: function(msg){
					Swal.fire('', msg, 'warning')
				}
			}
		}
	},
}
</script>

<style>
.menu{
    position: fixed;
	overflow: visible;
    border-radius: 5px;
    box-shadow: 10px 10px 20px 10px rgba(50, 50, 50, 0.3);
    visibility: hidden;
    text-align: left;
	background-color: aliceblue;
}
.menu-item{
    height: 20px;
    width: 160px;
    padding-left: 3px;
    padding-right: 3px;
    clear: left;
    display:block;
	overflow: hidden;
}
.menu-item:hover{
    border-radius: 4px;
    background-color: aquamarine
}
</style>
