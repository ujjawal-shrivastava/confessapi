from django.contrib import admin
from .models import Page, Confession

class ConfessionInlineAdmin(admin.TabularInline):
    model = Confession
    ordering=['-dateAdded']
    readonly_fields =['dateAdded','page','confId']
    extra = 1
    
class PageAdmin(admin.ModelAdmin):
     ordering = ['pk']
     inlines = [ConfessionInlineAdmin]
     readonly_fields = ['totalConfessions','pageId','pin']

class ConfessionAdmin(admin.ModelAdmin):
    ordering =['pk']
    readonly_fields = ['dateAdded','page','confId']

admin.site.register(Page, PageAdmin)
#admin.site.register(Confession, ConfessionAdmin)




