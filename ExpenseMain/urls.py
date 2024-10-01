from .views import *
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .views import home_view

urlpatterns = [
    # Main paths
    path('', views.index, name="index"),
    path('signup', views.signup, name="signup"),
    path('login', views.login, name='login'),
    path('home',home,name='home'),
    path('account_settings',currency_settings,name='account_settings'),
    path('expense',expense,name='expense'),
    path('addExpense',addExpense,name='addExpense'),
    path('editExpense/<int:id>',editExpense,name='editExpense'),
    path('deleteExpense/<int:id>',deleteExpense,name='deleteExpense'),
    path('searchExpense',csrf_exempt(searchExpense),name='searchExpense'),
    path('validateUserName',csrf_exempt(validateUserName),name='validateUserName'),
    path('validateUserEmail',csrf_exempt(validateUserEmail),name='validateUserEmail'),
    path('income',income,name='income'),
    path('addIncome',addIncome,name='addIncome'),
    path('editIncome/<int:id>',editIncome,name='editIncome'),
    path('deleteIncome/<int:id>',deleteIncome,name='deleteIncome'),
    path('searchIncome',csrf_exempt(searchIncome),name='searchIncome'),
    path('incomeCategorySummary',incomeCategorySummary,name='incomeCategorySummary'),
    # path('customIncomeDate',views.customIncomeDate,name='customIncomeDate'),
    path('expenseCategorySummary',expenseCategorySummary,name='expenseCategorySummary'),
    path('income_stats',incomeStatsView,name='income_stats'),
    path('expense_stats',expenseStatsView,name='expense_stats'),
    path('exportincomeCSV',exportincomeCSV,name='exportincomeCSV'),
    path('exportincomeExcel',exportincomeExcel,name='exportincomeExcel'),
    path('exportincomePdf',exportincomePdf,name='exportincomePdf'),
    path('exportCSV',exportCSV,name='exportCSV'),
    path('exportExcel', views.exportExcel, name='exportExcel'),
    path('exportPdf', views.exportPdf, name='exportPdf'),

    # Profile settings
    path('profile_settings', views.profile_settings, name='profile_settings'),
    path('profileValidateUsername', csrf_exempt(views.profileValidateUsername), name='profileValidateUsername'),

    # Username and email validation
    path('validateUserName', csrf_exempt(views.validateUserName), name='validateUserName'),
    path('validateUserEmail', csrf_exempt(views.validateUserEmail), name='validateUserEmail'),

    # Expense suggestions with AI
    path('expense-suggestions/', views.expense_suggestions, name='expense_suggestions'),
    path('visualization/combined_pie/', combined_expense_income_pie_chart, name='combined_expense_income_pie_chart'),
    path('fetch_expenses_savings/<str:selected_date>/', views.fetch_expenses_savings, name='fetch_expenses_savings'),
    path('savings/', views.savings_view, name='savings'),
    path('category_expense/', views.category_expense_view, name='category_expense'),


    path('visualize-all/', views.visualize_all, name='visualize_all'),

    
    # Logout
    path('logout', views.logout, name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
