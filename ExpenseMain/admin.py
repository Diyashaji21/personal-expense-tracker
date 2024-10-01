from django.contrib import admin
from .models import *


# Register your models here.
admin.site.site_header="ExpenseManager"
admin.site.site_title="ExpenseManager"
admin.site.index_title="ExpenseManager"

admin.site.register(UserDetail)
admin.site.register(UserPreference)
admin.site.register(Expense)
# admin.site.register(Category)
admin.site.register(Income)
# admin.site.register(Source)
