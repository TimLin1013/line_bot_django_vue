import Vue from 'vue'
import App from './App'
import router from './router'
import Calendar from 'vue-mobile-calendar'
import axios from 'axios';
Vue.prototype.$apiUrl = 'https://9122-27-52-158-61.ngrok-free.app';
Vue.prototype.$axios = axios;
Vue.prototype.$userId = null;
Vue.prototype.$userName = null;// 6/2
Vue.prototype.$personal_id = null;
Vue.use(Calendar);  
Vue.config.productionTip = false
/* eslint-disable no-new */

new Vue({
  el: '#app',
  router,
  render: h => h(App)
})