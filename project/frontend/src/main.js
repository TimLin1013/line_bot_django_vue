import Vue from 'vue'
import App from './App'
import router from './router'
import Calendar from 'vue-mobile-calendar'
import axios from 'axios';
import VueApexCharts from 'vue-apexcharts'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
Vue.use(VueApexCharts)
Vue.use(BootstrapVue)
Vue.use(IconsPlugin)
Vue.component('apexchart', VueApexCharts)
Vue.prototype.$apiUrl = 'https://4d51-2402-7500-5e7-3d41-99d3-971e-35c6-a609.ngrok-free.app';
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