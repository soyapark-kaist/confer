from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$','server.views.home'),
    url(r'^home$', 'server.views.home'),
    url(r'^team', 'server.views.team'),
    url(r'^credits', 'server.views.credits'),
    
    url(r'^data', 'server.views.data'),
    
    url(r'^like/(\w+)$', 'server.views.like'),
    url(r'^person_like/(\w+)$', 'server.views.person_like'),
    url(r'^log/(\w+)$', 'server.views.log'),

    url(r'^login', 'server.auth.login'),
    url(r'^register', 'server.auth.register'),
    url(r'^logout', 'server.auth.logout'),

    url(r'^forgot', 'server.auth.forgot'),
    url(r'^reset/(\w+)', 'server.auth.reset'),
    url(r'^verify/(\w+)', 'server.auth.verify'),

    #confer apps APIs
    url(r'^api/likes$', 'server.views.likes'),
    url(r'^api/similar_people$', 'server.views.similar_people'),

    #confer developer APIs
    url(r'^developer$', 'server.views.developer'),
    url(r'^developer/apps$', 'server.views.apps'),
    url(r'^developer/register_app$', 'server.views.register_app'),
    url(r'^developer/allow_access$', 'server.views.allow_access'),

    #confer settings
    url(r'^(\w+?)/settings', 'server.views.settings'),

    #move this matching in the end
    url(r'^(\w+?)/visualizations$', 'server.views.visualizations'),
    url(r'^(\w+?)/feed$', 'server.views.feed'),
    url(r'^(\w+?)/network_graph$', 'server.views.network_graph'),
    
    url(r'^(\w+?)/papers$', 'server.views.papers'),
    url(r'^(\w+?)/schedule$', 'server.views.schedule'),
    url(r'^(\w+?)/paper', 'server.views.paper'),
    url(r'^(\w+?)/meetups', 'server.views.meetups'),
    url(r'^(\w+?)/admin$', 'server.views.admin'),
    url(r'^(\w+?)/update_conference$', 'server.views.update_conference'),
    url(r'^(\w+)$', 'server.views.conf'),
    url(r'^(\w+?)/$', 'server.views.conf'),
    url(r'^(\w+?)/anonymized_data_dump$', 'server.views.anonymized_data_dump'),
    url(r'^(\w+?)/all_data_dump$', 'server.views.all_data_dump'),
    
    url(r'^recs', 'server.views.get_recs'),
)