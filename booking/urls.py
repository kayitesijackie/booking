from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from .import views

urlpatterns = [
  url('^$', views.home, name = 'home'),
  url(r'^search/',views.search_results, name = 'search_results'),
  url(r'^bus-details/(\d+)',views.bus_details, name = 'bus_details'),
  url(r'^delete_schedule/(\d+)',views.delete_schedule,name='delete_schedule'),
  url(r'^schedules', views.schedules, name = 'schedules'),
  url(r'pay/(?P<id>\d+)/$',views.SavePayment,name ='pay'),
  url(r'^response/(?P<id>\d+)/$',views.generate_view, name = 'response'),
  
  
  

]
if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
