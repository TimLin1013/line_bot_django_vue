import Vue from 'vue'
import Router from 'vue-router'
import liff_search from '@/components/liff_search'

  Vue.use(Router)

  export default new Router({
    routes: [

      {
        path: '/:queryParam', 
        name: 'liff_search_with_query',
        component: liff_search,
        props: true 
      },
      {
        path: '/',
        name: 'liff_search',
        component: liff_search,
        props: true 
      }
    ]
  })