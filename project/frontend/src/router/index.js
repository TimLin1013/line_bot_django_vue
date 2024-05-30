import Vue from 'vue'
import Router from 'vue-router'
import liff_search from '@/components/liff_search'
import liff_keep from '@/components/liff_keep'
import liff_personal from '@/components/liff_personal_form'

Vue.use(Router)

  export default new Router({
    mode: 'history',
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
      },
      {
        path: '/keep',
        name: 'liff_keep',
        component: liff_keep,
        props: true
      },
      {
        path: '/personal_form',
        name: 'liff_personal_form',
        component: liff_personal,
        props: true
      },
    ]
    
  })
