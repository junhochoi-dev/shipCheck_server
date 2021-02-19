from django.conf.urls import url
from .views import DetailNormalShipAPI, CreateNormalShipAPI, NormalShipRegister, AllDelete, WasteShipReigster, NormalImageExtraRegit, WasteImageExtraRegit

urlpatterns = [
    url(r'^normalship/(?P<pk>\d+)/$', DetailNormalShipAPI.as_view()),
    url(r'^normalship/create/', CreateNormalShipAPI.as_view()),
    url(r'^regitnormal/', NormalShipRegister.as_view()),
    url(r'^del/', AllDelete.as_view()),
    url(r'regitwaste/', WasteShipReigster.as_view()),
    url(r'regitnoramlimg/', NormalImageExtraRegit.as_view()),
    url(r'regitwasteimg/', WasteImageExtraRegit.as_view()),
]