from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from confessionApp.schema import schema
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('ujjawal/', admin.site.urls),
    url(r'^data$', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
]
