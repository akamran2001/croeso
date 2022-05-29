from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import path, re_path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

def root_redirect(request:HttpRequest):
  return redirect(reverse_lazy('index'))

urlpatterns = [
	  path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('accounts/profile/', root_redirect),
    path('sites', views.index, name='index'),
    path('sites/<int:site_id>',views.details,name='details'),
		path('sites/<int:site_id>/review/',views.create_review, name='createreview'),
    path('random/image/',views.random_image,name='random_image'),
    path('', root_redirect)
]