import Vue from 'vue'
import App from './App.vue'
import store from './logic/store.js'

Vue.config.productionTip = false

// import installSweetAlert2 from './libs/vue-sweetalert2.js'
// Vue.use(installSweetAlert2)

new Vue({
	store,
	render: h => h(App),
}).$mount('#app')
