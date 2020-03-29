<template>
  <div id="app" 
	:style="{width: app_width+'px', height: app_height+'px'}"
	>
    <!-- <HelloWorld msg="Welcome to Your Vue.js App"/> -->
	<show_window :style='{width: w1+"%", float: "left"}'></show_window>
	<terminal :style='{width: w2+"%"}'></terminal>
	<!-- <menutree :tags='dat' style="width:60%"></menutree> -->
	<!-- <editor></editor> -->
  </div>
</template>
 
<script>
	//v-bind:class='{full: full, together: together, empty: empty}'
import show_window from './components/show.vue'
import terminal from './components/terminal.vue'
import menutree from './components/menutree4tags.vue'
require('./logic/init.js')
// import editor from './components/home.vue'
 
export default {
  name: 'app',
  props: {
	  app_width: {
		  type: Number
	  },
	  app_height: {
		  type: Number
	  }
  },
  computed: {
	  app_width: ()=>document.documentElement.clientWidth,
	  app_height: ()=>document.documentElement.clientHeight,
	  dat: function(){
		return [['a',['aa',['aaa']],['ab',['aba']]],['b',['ba'],['bb']]]
	  }
  },
  data() {
	  // console.log(document.documentElement.offsetWidth,document.documentElement.clientHeight)
	  return{
		  w1: 70,
		  w2: 30,
		  // app_width: `${document.documentElement.clientWidth}`,
		  // app_height: document.documentElement.clientHeight,
	  }
  },
  components: {
	  show_window,
	  terminal,
	  menutree
  },
  mounted: function(){
	  if(this.$props.together==true){
		  this.w1 = 70
		  this.w2 = 100 - this.w1
	  }
  }
}
</script>

<style>
	*{
		margin: 0;
		padding: 0;
	}
	#app {
		font-family: 'Avenir', Helvetica, Arial, sans-serif;
		-webkit-font-smoothing: antialiased;
		-moz-osx-font-smoothing: grayscale;
		text-align: center;
		color: #2c3e50;

		position: absolute;
	}
</style>
