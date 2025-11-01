from django.contrib import admin
from .models import CarMake, CarModel

# class CarModelInline(admin.StackedInline):
#     model = CarModel
#     extra = 1  

# class CarModelAdmin(admin.ModelAdmin):
#     list_display = ("name", "car_make", "type", "year", "dealer_id")
#     list_filter = ("car_make", "type", "year")
#     search_fields = ("name", "car_make__name", "dealer_id")

# class CarMakeAdmin(admin.ModelAdmin):
#     list_display = ("name", "description", "country")
#     search_fields = ("name", "country")
#     inlines = [CarModelInline]

admin.site.register(CarMake)
admin.site.register(CarModel)