from django.contrib import admin
from . import models

# Register your models here.
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title',)
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(models.Item, ItemAdmin)
admin.site.register(models.Order)
admin.site.register(models.OrderItem)
admin.site.register(models.Address)