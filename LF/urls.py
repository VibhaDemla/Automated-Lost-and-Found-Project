from django.contrib import admin
from django.urls import path , include
from . import views
urlpatterns = [
    path('', views.home , name = "home"),
    path('signup' , views.signup,name = "signup"),
    path('signin' , views.signin,name = "signin"),
    path('signout' , views.signout,name = "signout"),
    path('userDashboard' , views.userDashboard,name = "userDashboard"),
    path('notifications' , views.notifications,name = "notifications"),
    path('uploadImage' , views.uploadImage,name = "uploadImage"),
    path('item_type' , views.item_type,name = "item_type"),
    path('submitItemDetails' , views.submitItemDetails,name = "submitItemDetails"),
    path('getItemType' , views.getItemType,name = "getItemType"),
    path('findItem' , views.findItem,name = "findItem"),
    path('topMatches' , views.topMatches,name = "topMatches"),

]