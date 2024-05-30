import Vue from 'vue'
import App from './App'
import router from './router'
import Calendar from 'vue-mobile-calendar'
import axios from 'axios';
Vue.prototype.$apiUrl = 'https://b2bd-2401-e180-8841-3a0e-c93c-e11a-fe96-1ff9.ngrok-free.app';
Vue.prototype.$axios = axios;
Vue.prototype.$userId = null;
Vue.use(Calendar);
Vue.config.productionTip = false
/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  render: h => h(App)
})
