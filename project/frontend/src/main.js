import Vue from 'vue'
import App from './App'
import router from './router'
import Calendar from 'vue-mobile-calendar'
import axios from 'axios';
Vue.prototype.$apiUrl = 'https://63ee-2402-7500-487-fd17-d195-f126-5a02-1378.ngrok-free.app';
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