import Vue from 'vue'
import App from './App'
import router from './router'
import Calendar from 'vue-mobile-calendar'
import axios from 'axios';
import VueApexCharts from 'vue-apexcharts'
Vue.use(VueApexCharts)

Vue.component('apexchart', VueApexCharts)
Vue.prototype.$apiUrl = 'https://8dec-2401-e180-8940-6dd-a5e2-a8a7-477e-5295.ngrok-free.app';
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