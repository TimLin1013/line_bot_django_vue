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
Vue.prototype.$apiUrl = 'https://4afb-2401-e180-8910-1b9-a8a2-228a-7467-3d23.ngrok-free.app';
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