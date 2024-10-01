from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import *
from dateutil.parser import parse
from django.utils import timezone
import json
from django.template.defaultfilters import date as django_date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse,HttpResponse
import csv
import datetime
import xlwt

from django.views.decorators.cache import cache_control
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import re
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent



# Create your views here.
def index(request):
    return render(request,'index.html')


def signup(request):
    if request.method=='GET':
        return render(request,'signup.html')
    else:
        name=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        if UserDetail.objects.filter(email=email) or UserDetail.objects.filter(name=name):
            msg = {'msg1' : 'Username or Email already exists!'}
            return render(request, 'signup.html', msg)
        else:
            userData=UserDetail(name=name,email=email,password=password)
            userData.save()
            return render(request,'index.html')
    

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from .models import UserDetail  # Import your UserDetail model

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Log the user in
            auth_login(request, user)
            # Save user details in session
            request.session['email'] = email
            request.session['user_id'] = user.id
            request.session['user_name'] = user.get_full_name()
            return redirect('/home')
        else:
            messages.error(request, 'Invalid Username or password!')
    
    return render(request, 'login.html')

from django.http import JsonResponse
from .models import Income, Expense 


def home(request):
    context = {}
    if 'user_id' in request.session:
        user_name = UserDetail.objects.get(email=request.session['email']).name
        context = {'user_name': user_name if request.session['user_id'] != '' else ''}
        return render(request, 'home.html', context)
    else:
        return redirect('/login')

from django.utils.timezone import localdate

def incomeCalendarView(request):
    income_events = []
    incomes = Income.objects.filter(owner=request.user)  # Fetch incomes for the logged-in user
    for income in incomes:
        income_events.append({
            'title': f"Income: ₹{income.amount}",
            'start': str(income.date),
            'color': '#4caf50'  # Customize color for income events
        })
    return JsonResponse(income_events, safe=False)

def expenseCalendarView(request):
    expense_events = []
    expenses = Expense.objects.filter(owner=request.user)  # Fetch expenses for the logged-in user
    for expense in expenses:
        expense_events.append({
            'title': f"Expense: ₹{expense.amount}",
            'start': str(expense.date),
            'color': '#f44336'  # Customize color for expense events
        })
    return JsonResponse(expense_events, safe=False)

def profile_settings(request):
    if 'user_id' in request.session:
        userDetails=UserDetail.objects.get(id=request.session['user_id'])
        if request.method=='GET':
            context={
                'userDetails':userDetails,
                'user_name':request.session['user_name']
            }
            return render(request,'profile.html',context)
        else:
            user_name=request.POST.get('username')
            password=request.POST.get('password')
            userDetails.name=user_name
            userDetails.password=password
            userDetails.save()
            return redirect('home')
    else:
        return redirect('/login')



def currency_settings(request):
    if 'user_id' in request.session:

        currency_data=[]
        userDetails=UserDetail.objects.get(id=request.session['user_id'])
        file_path=BASE_DIR/'currencies.json'

        with open(file_path,'r') as json_file:
            print(json_file)
            data=json.load(json_file)
            for k,v in data.items():
                currency_data.append({'name':k,'value':v})
        exists=UserPreference.objects.filter(user=request.session['user_id']).exists()
        user_preference=None
        if exists:
            user_preference=UserPreference.objects.get(user=userDetails)
        if request.method=='GET':
            return render(request,'preferences.html',{'currencies':currency_data,'user_preferences':user_preference,'user_name':request.session['user_name']})
        else:
            currency=request.POST.get('currency')
            #checking if user has already a preference
            if UserPreference.objects.filter(user=userDetails).exists():
                currency=request.POST.get('currency')
                user_preference.currency=currency
                user_preference.save()
                return render(request,'preferences.html',{'currencies':currency_data,'user_preferences':user_preference,'user_name':request.session['user_name']})
            else:
                savePreference=UserPreference.objects.create(user=userDetails,currency=currency)
                savePreference.save()
                return render(request,'preferences.html',{'currencies':currency_data,'user_preferences':user_preference,'user_name':request.session['user_name']})
    else:
        return redirect('/login')

def expense(request):
    if 'user_id' in request.session:

        if request.method=='GET':
            userDetails=UserDetail.objects.get(id=request.session['user_id'])
            currency=''
            if UserPreference.objects.filter(user=userDetails).exists():
                currency=UserPreference.objects.get(user=userDetails).currency
            expenses=Expense.objects.filter(owner=userDetails)
            paginator=Paginator(expenses,5)
            page_number=request.GET.get('page')
            page_obj=Paginator.get_page(paginator,page_number)
            context={
                'expenses':expenses,
                'currency':currency,
                'page_obj':page_obj,
                'user_name':request.session['user_name']
            }
            return render(request,'expenses.html',context)
    else:
        return redirect('/login')
    
from django.contrib import messages

def addExpense(request):
    userDetails = UserDetail.objects.get(id=request.session['user_id'])
    if request.method == 'GET':
        context = {
            'user_name': request.session['user_name']
        }
        return render(request, 'add_expense.html', context)
    else:
        amount = float(request.POST.get('amount'))
        description = request.POST.get('description')
        category = request.POST.get('category')
        date = request.POST.get('date_of_expense')
        
        # Calculate total income
        total_income = Income.objects.filter(owner=userDetails).aggregate(Sum('amount'))['amount__sum'] or 0
        
        if amount > total_income:
            # Set a message for alert
            messages.error(request, 'Expense cannot exceed your total income!')
            return redirect('add_expense')  # Redirect back to add expense page
        
        # If the expense is valid, save it
        expense = Expense.objects.create(
            amount=amount,
            description=description,
            category=category.upper(),
            date=date,
            owner=userDetails
        )
        expense.save()
        return redirect('expense')

    

def editExpense(request,id):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    expense=Expense.objects.get(pk=id)
    # categories=Category.objects.all()
    if request.method=='GET':
        context={
            'expense':expense,
            # 'categories':categories,
            'user_name':request.session['user_name']

        }
        return render(request,'edit_expense.html',context)
    else:
        amount=request.POST.get('amount')
        description=request.POST.get('description')
        category=request.POST.get('category')
        date=request.POST.get('date_of_expense')
        print(amount,description,category,date)
        expense.amount=amount
        expense.description=description
        expense.category=category.upper()
        expense.date=date
        expense.owner=userDetails
        expense.save()
        return redirect('expense')
    

def deleteExpense(request,id):
    expense=Expense.objects.get(pk=id)
    expense.delete()
    return redirect('expense')
        


def searchExpense(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    if request.method=='POST':
        search_str=json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=userDetails) | Expense.objects.filter(
            date__istartswith=search_str, owner=userDetails) | Expense.objects.filter(
            description__icontains=search_str, owner=userDetails) | Expense.objects.filter(
            category__icontains=search_str, owner=userDetails)
        data=expenses.values()
        return JsonResponse(list(data),safe=False)
    


def income(request):
    if 'user_id' in request.session:

        if request.method=='GET':
            userDetails=UserDetail.objects.get(id=request.session['user_id'])
            currency=''
            if UserPreference.objects.filter(user=userDetails).exists():
                currency=UserPreference.objects.get(user=userDetails).currency
            incomes=Income.objects.filter(owner=userDetails)
            paginator=Paginator(incomes,5)
            page_number=request.GET.get('page')
            page_obj=Paginator.get_page(paginator,page_number)
            context={
                'incomes':incomes,
                'currency':currency,
                'page_obj':page_obj,
                'user_name':request.session['user_name']

            }
            return render(request,'incomes.html',context)
    else:
        return redirect('/login')
    

def addIncome(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    if request.method=='GET':
        # sources=Source.objects.all()
        context={
            # 'sources':sources,
            'user_name':request.session['user_name']

        }
        return render(request,'add_income.html',context)
    else:
        amount=request.POST.get('amount')
        description=request.POST.get('description')
        source=request.POST.get('category')
        date=request.POST.get('date_of_expense')
        income=Income.objects.create(amount=amount,description=description,source=source.upper(),date=date,owner=userDetails)
        income.save()
        return redirect('income')
    

def editIncome(request,id):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    income=Income.objects.get(pk=id)
    # sources=Source.objects.all()
    if request.method=='GET':
        context={
            'income':income,
            # 'categories':sources,
            'user_name':request.session['user_name']

        }
        return render(request,'edit_income.html',context)
    else:
        amount=request.POST.get('amount')
        description=request.POST.get('description')
        source=request.POST.get('category')
        date=request.POST.get('date_of_expense')
        income.amount=amount
        income.description=description
        income.category=source.upper()
        income.date=date
        income.owner=userDetails
        income.save()
        return redirect('income')
    

def deleteIncome(request,id):
    income=Income.objects.get(pk=id)
    income.delete()
    return redirect('income')
        


def searchIncome(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    if request.method=='POST':
        search_str=json.loads(request.body).get('searchText')
        # income=Income.objects.filter(amount_istarts_with=search_str,owner=userDetails) | Income.objects.filter(date_istarts_with=search_str,owner=userDetails)| Income.objects.filter(description_icontains=search_str,owner=userDetails)| Income.objects.filter(category_icontains=search_str,owner=userDetails)
        income = Income.objects.filter(
            amount__istartswith=search_str, owner=userDetails) | Income.objects.filter(
            date__istartswith=search_str, owner=userDetails) | Income.objects.filter(
            description__icontains=search_str, owner=userDetails) | Income.objects.filter(
            source__icontains=search_str, owner=userDetails)
        data=income.values()
        return JsonResponse(list(data),safe=False)
    

def expenseCategorySummary(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    todaysDate=datetime.date.today()
    sixMonthsAgo=todaysDate-datetime.timedelta(days=30*6)
    expenses=Expense.objects.filter(owner=userDetails,date_gte=sixMonthsAgo,date_lte=todaysDate)
    finalRepresentation={

    }

    def getCategory(expense):
        return expense.category
    categoryList=list(set(map(getCategory,expenses)))

    def getExpenseCategoryAmount(category):
        amount=0
        filtered_by_category=expenses.filter(category=category)
        for item in filtered_by_category:
            amount+=item.amount
        return amount

    for x in expenses:
        for y in categoryList:
            finalRepresentation[y]=getExpenseCategoryAmount(y)
    return JsonResponse({'expense_category_data':finalRepresentation},safe=False)

# def incomeStatsView(request):
#     if 'user_id' in request.session :
#         todaysDate=datetime.date.today()
#         sixMonthsAgo=todaysDate-datetime.timedelta(days=30*6)
#         context={'user_name':request.session['user_name'],'from':sixMonthsAgo,'to':todaysDate}
#         return render(request,'incomeStats.html',context)
#     else:
#         return redirect('/login')

def incomeStatsView(request):
    if 'user_id' in request.session :
        todaysDate=timezone.localdate()
        sixMonthsAgo=todaysDate-datetime.timedelta(days=30*6)
        context={'user_name':request.session['user_name'],'from':sixMonthsAgo,'to':todaysDate}
        return render(request,'incomeStats.html',context)
    else:
        return redirect('/login')


def expenseStatsView(request):
    if 'user_id' in request.session:
        context={'user_name':request.session['user_name']}
        return render(request,'expenseStats.html',context)
    else:
        return redirect('/login')


def exportincomeCSV(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename=Expenses'+str(datetime.datetime.now())+'.csv'
    writer=csv.writer(response)
    writer.writerow(['Amount','Description','Source','Date'])
    incomes=Income.objects.filter(owner=userDetails)
    for income in incomes:
        writer.writerow([income.amount,income.description,income.source,income.date])
    return response


def exportCSV(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename=Expenses'+str(datetime.datetime.now())+'.csv'
    writer=csv.writer(response)
    writer.writerow(['Amount','Description','Category','Date'])
    expenses=Expense.objects.filter(owner=userDetails)
    for expense in expenses:
        writer.writerow([expense.amount,expense.description,expense.category,expense.date])
    return response


def exportincomeExcel(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    response=HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition']='attachment; filename=Expenses'+str(datetime.datetime.now())+'.xls'
    wb=xlwt.Workbook(encoding='utf-8')
    ws=wb.add_sheet('Expenses')
    row_num=0
    font_style=xlwt.XFStyle()
    font_style.font.bold=True
    columns=['Amount','Description','Source','Date']
    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num],font_style)

    font_style=xlwt.XFStyle()
    rows=Income.objects.filter(owner=userDetails).values_list('amount','description','source','date')

    for row in rows:
        row_num+=1
        for col_num in range(len(row)):
            ws.write(row_num,col_num,str(row[col_num]),font_style)
    wb.save(response)
    return response

def exportExcel(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    response=HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition']='attachment; filename=Expenses'+str(datetime.datetime.now())+'.xls'
    wb=xlwt.Workbook(encoding='utf-8')
    ws=wb.add_sheet('Expenses')
    row_num=0
    font_style=xlwt.XFStyle()
    font_style.font.bold=True
    columns=['Amount','Description','Category','Date']
    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num],font_style)

    font_style=xlwt.XFStyle()
    rows=Expense.objects.filter(owner=userDetails).values_list('amount','description','category','date')

    for row in rows:
        row_num+=1
        for col_num in range(len(row)):
            ws.write(row_num,col_num,str(row[col_num]),font_style)
    wb.save(response)
    return response


def exportincomePdf(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    incomes=Income.objects.filter(owner=userDetails)
    response=HttpResponse(content_type='application/pdf')
    response['Content-Disposition']='attachment;filename="expense.pdf"'
    doc=SimpleDocTemplate(response,pagesize=letter)
    elements=[]

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ])

    data=[['Amount','Date','Source','Description']]
    for income in incomes:
        data.append([income.amount,income.date,income.source,income.description])
    table=Table(data)
    table.setStyle(style)
    elements.append(table)
    doc.build(elements)
    return response

def exportPdf(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    expenses=Expense.objects.filter(owner=userDetails)
    response=HttpResponse(content_type='application/pdf')
    response['Content-Disposition']='attachment;filename="expense.pdf"'
    doc=SimpleDocTemplate(response,pagesize=letter)
    elements=[]

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ])

    data=[['Amount','Date','Category','Description']]
    for expense in expenses:
        data.append([expense.amount,expense.date,expense.category,expense.description])
    table=Table(data)
    table.setStyle(style)
    elements.append(table)
    doc.build(elements)
    return response


def profileValidateUsername(request):
        if request.method=='POST':
            data=json.loads(request.body)
            search_str=data['username']
            if not str(search_str).isalnum():
                return JsonResponse({'username_error': 'username should only contain alphanumeric characters'}, status=400)
            if UserDetail.objects.filter(name=search_str).exists():
                 return JsonResponse({'username_error': 'sorry username is in use,choose another one '}, status=409)
        return JsonResponse({'username_valid': True})


def validateUserName(request):
    if request.method=='POST':
        data=json.loads(request.body)
        search_str=data['username']
        if not str(search_str).isalnum():
            return JsonResponse({'username_error': 'username should only contain alphanumeric characters'}, status=400)
        if UserDetail.objects.filter(name=search_str).exists():
                return JsonResponse({'username_error': 'sorry username is in use,choose another one '}, status=409)
    return JsonResponse({'username_valid': True})


def validateUserEmail(request):
    if request.method=='POST':
        data=json.loads(request.body)
        email=data['email']
        if not validate_email(email):
                return JsonResponse({'email_error':'Email is invalid'},status=400)
        if UserDetail.objects.filter(email=email).exists():
                return JsonResponse({'email_error':'Email already exists. please choose another name.'},status=400)
    return JsonResponse({'email_valid':True})


def logout(request):
        if 'user_id' not in request.session or 'user_name' not in request.session :
            return redirect('/login')
   
        del request.session['user_name']

        del request.session['user_id']
    # except:
    #     return index(request)
    
        return redirect('login')


from django.shortcuts import render
import google.generativeai as genai

# Configure API key
genai.configure(api_key="AIzaSyDMWgpRHcRIFEt-spI7fq5AlstIUO5pBKo")

# Create the model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the generative AI model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# View to handle form input and display suggestions
def expense_suggestions(request):
    if request.method == 'POST':
        income = request.POST.get('income')
        expense = request.POST.get('expense')
        date = request.POST.get('date')
        category = request.POST.get('category')
        location = request.POST.get('location')

        # Validate user input
        if not (income and expense and date and category and location):
            return render(request, 'input_form.html', {'error': 'Please provide all input details.'})

        # Combine user input into a single prompt
        user_input = f"Income: {income}, Expense: {expense}, Date: {date}, Category: {category}, Location: {location}."

        try:
            # Create chat session with Google Generative AI
            chat_session = model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [
                            "Give suggestions for controlling expenses from your earnings with fields: income, expense, date, category, and location. Provide a rough idea for saving money from the given details.",
                        ],
                    },
                ]
            )

            # Get response from AI model
            response = chat_session.send_message(user_input)

            # Remove asterisks from the response
            cleaned_response = response.text.replace('*', '')

            # Check if response is valid
            if cleaned_response:
                return render(request, 'suggestions.html', {'response': cleaned_response})
            else:
                return render(request, 'input_form.html', {'error': 'No response from the AI model. Please try again.'})

        except Exception as e:
            # Handle potential errors
            return render(request, 'input_form.html', {'error': f"An error occurred: {str(e)}"})

    return render(request, 'input_form.html')
from django.shortcuts import render,redirect
from .models import *
from dateutil.parser import parse
from django.utils import timezone
import json
from django.template.defaultfilters import date as django_date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse,HttpResponse
import csv
import datetime
import xlwt

from django.views.decorators.cache import cache_control
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import re
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent



# Create your views here.
def index(request):
    return render(request,'index.html')


def signup(request):
    if request.method=='GET':
        return render(request,'signup.html')
    else:
        name=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        if UserDetail.objects.filter(email=email) or UserDetail.objects.filter(name=name):
            msg = {'msg1' : 'Username or Email already exists!'}
            return render(request, 'signup.html', msg)
        else:
            userData=UserDetail(name=name,email=email,password=password)
            userData.save()
            return render(request,'index.html')
    

def login(request):
    if request.method=='GET':
        return render(request,'login.html')
    else:
        email=request.POST.get('email')
        password=request.POST.get('password')
        userData=UserDetail.objects.filter(email=email,password=password)
        print(userData)
        if userData.filter(email=email,password=password).exists():
            request.session['email']=userData[0].email
            request.session['user_id']=userData[0].id
            request.session['user_name']=userData[0].name
            return redirect("/home")
        else:
            msg={'msg1':"Invalid Username or password!"}
            return render(request,'login.html',msg)


def home(request):
    context={}
    if 'user_id' in request.session:
        user_name=UserDetail.objects.get(email=request.session['email']).name 
        if request.session['user_id']!='':
            context={'user_name':user_name}
        else:
            context={'user_name':''}
        return render(request,'home.html',context)
    else:
        return redirect('/login')

def incomeCalendarView(request):
    incomes=Income.objects.filter(owner=request.session['user_id'])
    event_list=[]
    for income in incomes:
        event_list.append({
            'title':income.description,
            'start':income.date.isoformat(),
            'end':income.date.isoformat(),
        })
    return JsonResponse(event_list,safe=False)


def expenseCalendarView(request):
    expenses=Expense.objects.filter(owner=request.session['user_id'])
    event_list=[]
    for expense in expenses:
        event_list.append({
            'title':expense.description,
            'start':expense.date.isoformat(),
            'end':expense.date.isoformat()
        })
    return JsonResponse(event_list,safe=False)


def profile_settings(request):
    if 'user_id' in request.session:
        userDetails=UserDetail.objects.get(id=request.session['user_id'])
        if request.method=='GET':
            context={
                'userDetails':userDetails,
                'user_name':request.session['user_name']
            }
            return render(request,'profile.html',context)
        else:
            user_name=request.POST.get('username')
            password=request.POST.get('password')
            userDetails.name=user_name
            userDetails.password=password
            userDetails.save()
            return redirect('home')
    else:
        return redirect('/login')



def currency_settings(request):
    if 'user_id' in request.session:

        currency_data=[]
        userDetails=UserDetail.objects.get(id=request.session['user_id'])
        file_path=BASE_DIR/'currencies.json'

        with open(file_path,'r') as json_file:
            print(json_file)
            data=json.load(json_file)
            for k,v in data.items():
                currency_data.append({'name':k,'value':v})
        exists=UserPreference.objects.filter(user=request.session['user_id']).exists()
        user_preference=None
        if exists:
            user_preference=UserPreference.objects.get(user=userDetails)
        if request.method=='GET':
            return render(request,'preferences.html',{'currencies':currency_data,'user_preferences':user_preference,'user_name':request.session['user_name']})
        else:
            currency=request.POST.get('currency')
            #checking if user has already a preference
            if UserPreference.objects.filter(user=userDetails).exists():
                currency=request.POST.get('currency')
                user_preference.currency=currency
                user_preference.save()
                return render(request,'preferences.html',{'currencies':currency_data,'user_preferences':user_preference,'user_name':request.session['user_name']})
            else:
                savePreference=UserPreference.objects.create(user=userDetails,currency=currency)
                savePreference.save()
                return render(request,'preferences.html',{'currencies':currency_data,'user_preferences':user_preference,'user_name':request.session['user_name']})
    else:
        return redirect('/login')


# Expense view
def expense(request):
    if 'user_id' in request.session:
        if request.method == 'GET':
            userDetails = UserDetail.objects.get(id=request.session['user_id'])
            currency = ''
            if UserPreference.objects.filter(user=userDetails).exists():
                currency = UserPreference.objects.get(user=userDetails).currency
            expenses = Expense.objects.filter(owner=userDetails)
            paginator = Paginator(expenses, 5)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'expenses': expenses,
                'currency': currency,
                'page_obj': page_obj,
                'user_name': request.session['user_name']
            }
            return render(request, 'expenses.html', context)
    else:
        return redirect('/login')


# Add Expense view
def addExpense(request):
    if 'user_id' in request.session:
        userDetails = UserDetail.objects.get(id=request.session['user_id'])
        if request.method == 'GET':
            # categories = Category.objects.all()  # Uncomment if categories are being used
            context = {
                # 'categories': categories,  # Uncomment if categories are being used
                'user_name': request.session['user_name']
            }
            return render(request, 'add_expense.html', context)
        else:
            amount = request.POST.get('amount')
            description = request.POST.get('description')
            category = request.POST.get('category')
            date = request.POST.get('date_of_expense')

            print(f"Amount: {amount}, Description: {description}, Category: {category}, Date: {date}")

            expense = Expense.objects.create(
                amount=amount,
                description=description,
                category=category.upper(),
                date=date,
                owner=userDetails
            )
            expense.save()
            return redirect('expense')
    else:
        return redirect('/login')

def editExpense(request,id):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    expense=Expense.objects.get(pk=id)
    # categories=Category.objects.all()
    if request.method=='GET':
        context={
            'expense':expense,
            # 'categories':categories,
            'user_name':request.session['user_name']

        }
        return render(request,'edit_expense.html',context)
    else:
        amount=request.POST.get('amount')
        description=request.POST.get('description')
        category=request.POST.get('category')
        date=request.POST.get('date_of_expense')
        print(amount,description,category,date)
        expense.amount=amount
        expense.description=description
        expense.category=category.upper()
        expense.date=date
        expense.owner=userDetails
        expense.save()
        return redirect('expense')
    

def deleteExpense(request,id):
    expense=Expense.objects.get(pk=id)
    expense.delete()
    return redirect('expense')
        


def searchExpense(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    if request.method=='POST':
        search_str=json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=userDetails) | Expense.objects.filter(
            date__istartswith=search_str, owner=userDetails) | Expense.objects.filter(
            description__icontains=search_str, owner=userDetails) | Expense.objects.filter(
            category__icontains=search_str, owner=userDetails)
        data=expenses.values()
        return JsonResponse(list(data),safe=False)
    

# Income view
def income(request):
    if 'user_id' in request.session:
        if request.method == 'GET':
            userDetails = UserDetail.objects.get(id=request.session['user_id'])
            currency = ''
            if UserPreference.objects.filter(user=userDetails).exists():
                currency = UserPreference.objects.get(user=userDetails).currency
            incomes = Income.objects.filter(owner=userDetails)
            paginator = Paginator(incomes, 5)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'incomes': incomes,
                'currency': currency,
                'page_obj': page_obj,
                'user_name': request.session['user_name']
            }
            return render(request, 'incomes.html', context)
    else:
        return redirect('/login')

def addIncome(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    if request.method=='GET':
        # sources=Source.objects.all()
        context={
            # 'sources':sources,
            'user_name':request.session['user_name']

        }
        return render(request,'add_income.html',context)
    else:
        amount=request.POST.get('amount')
        description=request.POST.get('description')
        source=request.POST.get('category')
        date=request.POST.get('date_of_expense')
        income=Income.objects.create(amount=amount,description=description,source=source.upper(),date=date,owner=userDetails)
        income.save()
        return redirect('income')
    

def editIncome(request,id):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    income=Income.objects.get(pk=id)
    # sources=Source.objects.all()
    if request.method=='GET':
        context={
            'income':income,
            # 'categories':sources,
            'user_name':request.session['user_name']

        }
        return render(request,'edit_income.html',context)
    else:
        amount=request.POST.get('amount')
        description=request.POST.get('description')
        source=request.POST.get('category')
        date=request.POST.get('date_of_expense')
        income.amount=amount
        income.description=description
        income.category=source.upper()
        income.date=date
        income.owner=userDetails
        income.save()
        return redirect('income')
    

def deleteIncome(request,id):
    income=Income.objects.get(pk=id)
    income.delete()
    return redirect('income')
        


def searchIncome(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    if request.method=='POST':
        search_str=json.loads(request.body).get('searchText')
        # income=Income.objects.filter(amount__istarts_with=search_str,owner=userDetails) | Income.objects.filter(date_istarts_with=search_str,owner=userDetails)| Income.objects.filter(description__icontains=search_str,owner=userDetails)| Income.objects.filter(category_icontains=search_str,owner=userDetails)
        income = Income.objects.filter(
            amount__istartswith=search_str, owner=userDetails) | Income.objects.filter(
            date__istartswith=search_str, owner=userDetails) | Income.objects.filter(
            description__icontains=search_str, owner=userDetails) | Income.objects.filter(
            source__icontains=search_str, owner=userDetails)
        data=income.values()
        return JsonResponse(list(data),safe=False)
    

def expenseCategorySummary(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    todaysDate=datetime.date.today()
    sixMonthsAgo=todaysDate-datetime.timedelta(days=30*6)
    expenses=Expense.objects.filter(owner=userDetails,date__gte=sixMonthsAgo,date__lte=todaysDate)
    finalRepresentation={

    }

    def getCategory(expense):
        return expense.category
    categoryList=list(set(map(getCategory,expenses)))

    def getExpenseCategoryAmount(category):
        amount=0
        filtered_by_category=expenses.filter(category=category)
        for item in filtered_by_category:
            amount+=item.amount
        return amount

    for x in expenses:
        for y in categoryList:
            finalRepresentation[y]=getExpenseCategoryAmount(y)
    return JsonResponse({'expense_category_data':finalRepresentation},safe=False)


# def customIncomeDate(request):
#     fromDate=request.POST.get("fromDate")
#     toDate=request.POST.get('toDate')
#     print(fromDate,toDate)
#     incomeCategorySummary(request,fromDate,toDate)
#     return redirect('/income_stats')

def incomeCategorySummary(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    todaysDate=datetime.date.today()
    sixMonthsAgo=todaysDate-datetime.timedelta(days=30*6)
    incomes=Income.objects.filter(owner=userDetails,date__gte=sixMonthsAgo,date__lte=todaysDate)
    finalRepresentation={

    }

    def getCategory(incomes):
        return incomes.source
    categoryList=list(set(map(getCategory,incomes)))


    def getIncomeCategoryAmount(source):
        amount=0
        filtered_by_category=incomes.filter(source=source)
        for item in filtered_by_category:
            amount+=item.amount
        return amount
    for x in incomes:
        for y in categoryList:
            finalRepresentation[y]=getIncomeCategoryAmount(y)
    return JsonResponse({'income_category_data':finalRepresentation},safe=False)

# def incomeStatsView(request):
#     if 'user_id' in request.session :
#         todaysDate=datetime.date.today()
#         sixMonthsAgo=todaysDate-datetime.timedelta(days=30*6)
#         context={'user_name':request.session['user_name'],'from':sixMonthsAgo,'to':todaysDate}
#         return render(request,'incomeStats.html',context)
#     else:
#         return redirect('/login')

def incomeStatsView(request):
    if 'user_id' in request.session :
        todaysDate=timezone.localdate()
        sixMonthsAgo=todaysDate-datetime.timedelta(days=30*6)
        context={'user_name':request.session['user_name'],'from':sixMonthsAgo,'to':todaysDate}
        return render(request,'incomeStats.html',context)
    else:
        return redirect('/login')


def expenseStatsView(request):
    if 'user_id' in request.session:
        context={'user_name':request.session['user_name']}
        return render(request,'expenseStats.html',context)
    else:
        return redirect('/login')


def exportincomeCSV(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename=Expenses'+str(datetime.datetime.now())+'.csv'
    writer=csv.writer(response)
    writer.writerow(['Amount','Description','Source','Date'])
    incomes=Income.objects.filter(owner=userDetails)
    for income in incomes:
        writer.writerow([income.amount,income.description,income.source,income.date])
    return response


def exportCSV(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename=Expenses'+str(datetime.datetime.now())+'.csv'
    writer=csv.writer(response)
    writer.writerow(['Amount','Description','Category','Date'])
    expenses=Expense.objects.filter(owner=userDetails)
    for expense in expenses:
        writer.writerow([expense.amount,expense.description,expense.category,expense.date])
    return response


def exportincomeExcel(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    response=HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition']='attachment; filename=Expenses'+str(datetime.datetime.now())+'.xls'
    wb=xlwt.Workbook(encoding='utf-8')
    ws=wb.add_sheet('Expenses')
    row_num=0
    font_style=xlwt.XFStyle()
    font_style.font.bold=True
    columns=['Amount','Description','Source','Date']
    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num],font_style)

    font_style=xlwt.XFStyle()
    rows=Income.objects.filter(owner=userDetails).values_list('amount','description','source','date')

    for row in rows:
        row_num+=1
        for col_num in range(len(row)):
            ws.write(row_num,col_num,str(row[col_num]),font_style)
    wb.save(response)
    return response

def exportExcel(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    response=HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition']='attachment; filename=Expenses'+str(datetime.datetime.now())+'.xls'
    wb=xlwt.Workbook(encoding='utf-8')
    ws=wb.add_sheet('Expenses')
    row_num=0
    font_style=xlwt.XFStyle()
    font_style.font.bold=True
    columns=['Amount','Description','Category','Date']
    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num],font_style)

    font_style=xlwt.XFStyle()
    rows=Expense.objects.filter(owner=userDetails).values_list('amount','description','category','date')

    for row in rows:
        row_num+=1
        for col_num in range(len(row)):
            ws.write(row_num,col_num,str(row[col_num]),font_style)
    wb.save(response)
    return response


def exportincomePdf(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    incomes=Income.objects.filter(owner=userDetails)
    response=HttpResponse(content_type='application/pdf')
    response['Content-Disposition']='attachment;filename="expense.pdf"'
    doc=SimpleDocTemplate(response,pagesize=letter)
    elements=[]

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ])

    data=[['Amount','Date','Source','Description']]
    for income in incomes:
        data.append([income.amount,income.date,income.source,income.description])
    table=Table(data)
    table.setStyle(style)
    elements.append(table)
    doc.build(elements)
    return response

def exportPdf(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    expenses=Expense.objects.filter(owner=userDetails)
    response=HttpResponse(content_type='application/pdf')
    response['Content-Disposition']='attachment;filename="expense.pdf"'
    doc=SimpleDocTemplate(response,pagesize=letter)
    elements=[]

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ])

    data=[['Amount','Date','Category','Description']]
    for expense in expenses:
        data.append([expense.amount,expense.date,expense.category,expense.description])
    table=Table(data)
    table.setStyle(style)
    elements.append(table)
    doc.build(elements)
    return response


def profileValidateUsername(request):
        if request.method=='POST':
            data=json.loads(request.body)
            search_str=data['username']
            if not str(search_str).isalnum():
                return JsonResponse({'username_error': 'username should only contain alphanumeric characters'}, status=400)
            if UserDetail.objects.filter(name=search_str).exists():
                 return JsonResponse({'username_error': 'sorry username is in use,choose another one '}, status=409)
        return JsonResponse({'username_valid': True})


def validateUserName(request):
    if request.method=='POST':
        data=json.loads(request.body)
        search_str=data['username']
        if not str(search_str).isalnum():
            return JsonResponse({'username_error': 'username should only contain alphanumeric characters'}, status=400)
        if UserDetail.objects.filter(name=search_str).exists():
                return JsonResponse({'username_error': 'sorry username is in use,choose another one '}, status=409)
    return JsonResponse({'username_valid': True})


def validateUserEmail(request):
    if request.method=='POST':
        data=json.loads(request.body)
        email=data['email']
        if not validate_email(email):
                return JsonResponse({'email_error':'Email is invalid'},status=400)
        if UserDetail.objects.filter(email=email).exists():
                return JsonResponse({'email_error':'Email already exists. please choose another name.'},status=400)
    return JsonResponse({'email_valid':True})


def logout(request):
        if 'user_id' not in request.session or 'user_name' not in request.session :
            return redirect('/login')
   
        del request.session['user_name']

        del request.session['user_id']
    # except:
    #     return index(request)
    
        return redirect('login')



from django.shortcuts import render
import google.generativeai as genai

# Configure API key
genai.configure(api_key="AIzaSyDMWgpRHcRIFEt-spI7fq5AlstIUO5pBKo")

# Create the model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the generative AI model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# View to handle form input and display suggestions
def expense_suggestions(request):
    if request.method == 'POST':
        income = request.POST.get('income')
        expense = request.POST.get('expense')
        date = request.POST.get('date')
        category = request.POST.get('category')
        location = request.POST.get('location')

        # Validate user input
        if not (income and expense and date and category and location):
            return render(request, 'input_form.html', {'error': 'Please provide all input details.'})

        # Combine user input into a single prompt
        user_input = f"Income: {income}, Expense: {expense}, Date: {date}, Category: {category}, Location: {location}."

        try:
            # Create chat session with Google Generative AI
            chat_session = model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [
                            "Give suggestions for controlling expenses from your earnings with fields: income, expense, date, category, and location. Provide a rough idea for saving money from the given details.",
                        ],
                    },
                ]
            )

            # Get response from AI model
            response = chat_session.send_message(user_input)

            # Remove asterisks from the response
            cleaned_response = response.text.replace('*', '')

            # Check if response is valid
            if cleaned_response:
                return render(request, 'suggestions.html', {'response': cleaned_response})
            else:
                return render(request, 'input_form.html', {'error': 'No response from the AI model. Please try again.'})

        except Exception as e:
            # Handle potential errors
            return render(request, 'input_form.html', {'error': f"An error occurred: {str(e)}"})

    return render(request, 'input_form.html')





























import matplotlib.pyplot as plt
import io
import urllib, base64
from django.shortcuts import render
from .models import Expense, Income

def combined_expense_income_pie_chart(request):
    # Querying the data from the models
    total_expenses = Expense.objects.aggregate(total=models.Sum('amount'))['total'] or 0
    total_incomes = Income.objects.aggregate(total=models.Sum('amount'))['total'] or 0

    # Data for pie chart
    labels = ['Total Expenses', 'Total Income']
    amounts = [total_expenses, total_incomes]

    # Plotting the combined pie chart
    plt.figure(figsize=(7, 7))
    plt.pie(amounts, labels=labels, autopct='%1.1f%%', startangle=140, colors=['red', 'green'])
    plt.title('Expenses vs Income')

    # Save the plot to a string buffer in order to send it as an image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    # Render the image in the template
    return render(request, 'visualization_combined_pie.html', {'data': uri})

from django.shortcuts import render, redirect
from .models import Income, Expense, UserDetail, UserPreference
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.core.paginator import Paginator

@login_required
def savings_view(request):
    # Get the logged-in user
    user = request.user

    # Debug: Check if the user is fetched correctly
    print(f"Logged-in User: {user.email}")

    # Find the corresponding UserDetail
    try:
        user_detail = UserDetail.objects.get(email=user.email)
        print(f"User Detail found: {user_detail}")
    except UserDetail.DoesNotExist:
        user_detail = None

    # Initialize variables to avoid errors
    total_income = 0
    total_expense = 0
    total_savings = 0

    if user_detail:
        # Fetch all income and expenses for this user
        incomes = Income.objects.filter(owner=user_detail)
        expenses = Expense.objects.filter(owner=user_detail)

        # Debug: Print incomes and expenses
        print(f"Incomes: {incomes}")
        print(f"Expenses: {expenses}")

        # Sum total income and expenses
        total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

        # Calculate savings
        total_savings = total_income - total_expense

        # Debug: Check calculated values
        print(f"Aggregated Total Income: {total_income}")
        print(f"Aggregated Total Expense: {total_expense}")
        print(f"Calculated Total Savings: {total_savings}")

    # Pass the calculated values to the template
    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'total_savings': total_savings,
    }

    print(f"Context Data: {context}")  # Debug context data
    return render(request, 'savings.html', context)

def income(request):
    if 'user_id' in request.session:
        if request.method == 'GET':
            userDetails = UserDetail.objects.get(id=request.session['user_id'])
            currency = ''
            if UserPreference.objects.filter(user=userDetails).exists():
                currency = UserPreference.objects.get(user=userDetails).currency
            incomes = Income.objects.filter(owner=userDetails)
            paginator = Paginator(incomes, 5)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'incomes': incomes,
                'currency': currency,
                'page_obj': page_obj,
                'user_name': request.session['user_name']
            }
            return render(request, 'incomes.html', context)
    else:
        return redirect('/login')

def expense(request):
    if 'user_id' in request.session:
        if request.method == 'GET':
            userDetails = UserDetail.objects.get(id=request.session['user_id'])
            currency = ''
            if UserPreference.objects.filter(user=userDetails).exists():
                currency = UserPreference.objects.get(user=userDetails).currency
            expenses = Expense.objects.filter(owner=userDetails)
            paginator = Paginator(expenses, 5)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'expenses': expenses,
                'currency': currency,
                'page_obj': page_obj,
                'user_name': request.session['user_name']
            }
            return render(request, 'expenses.html', context)
    else:
        return redirect('/login')

def addExpense(request):
    userDetails = UserDetail.objects.get(id=request.session['user_id'])
    if request.method == 'GET':
        context = {
            'user_name': request.session['user_name']
        }
        return render(request, 'add_expense.html', context)
    else:
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        category = request.POST.get('category')
        date = request.POST.get('date_of_expense')
        print(f"Adding Expense - Amount: {amount}, Description: {description}, Category: {category}, Date: {date}")
        expense = Expense.objects.create(amount=amount, description=description, category=category.upper(), date=date, owner=userDetails)
        expense.save()
        return redirect('expense')


@login_required
def home_view(request):
    # Fetch user's expenses
    expenses = Expense.objects.filter(owner=request.user)

    # Prepare events for the calendar
    events = [
        {
            'title': f"₹{expense.amount} - {expense.description}",
            'start': expense.date.isoformat(),  # Convert date to ISO format for FullCalendar
            'description': f"Category: {expense.category}",
        }
        for expense in expenses
    ]

    # Calculate total income, expenses, and savings
    total_income = ...  # Your logic to calculate total income
    total_expenses = sum(exp.amount for exp in expenses)
    savings = total_income - total_expenses

    # Render the home page and pass the events to the template
    return render(request, 'home.html', {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'savings': savings,
        'events': events,  # Pass events to the template
    })


from django.http import JsonResponse
from datetime import datetime

def fetch_expenses_savings(request, selected_date):
    print(f"Selected date received: {selected_date}")  # Debugging the selected date
    if 'user_id' in request.session:
        userDetails = UserDetail.objects.get(id=request.session['user_id'])

        try:
            formatted_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            print(f"Formatted date: {formatted_date}")  # Debugging the formatted date

            expenses = Expense.objects.filter(owner=userDetails, date=formatted_date)
            total_expenses = sum(exp.amount for exp in expenses)

            total_income = 0  # Add logic to fetch income if necessary
            savings = total_income - total_expenses

            return JsonResponse({
                'total_expenses': total_expenses,
                'savings': savings,
            })
        except Exception as e:
            print(f"Error fetching data: {e}")
            return JsonResponse({'error': 'Invalid date format'}, status=400)
    else:
        return JsonResponse({'error': 'Unauthorized'}, status=401)



from django.shortcuts import render
from .models import Expense
from django.db.models import Sum

def category_expense_view(request):
    # Group expenses by category and calculate the total for each
    expenses_by_category = Expense.objects.values('category').annotate(total_amount=Sum('amount')).order_by('-total_amount')
    
    context = {
        'expenses_by_category': expenses_by_category
    }
    return render(request, 'category_expense.html', context)



from django.db.models import Sum
import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from .models import Expense, Income

import plotly.graph_objects as go
import plotly.express as px
from django.shortcuts import render
from django.db.models import Sum

def visualize_all(request):
    # Monthly Expense Trend (Interactive Line Plot)
    monthly_expenses = Expense.objects.values('date__year', 'date__month').annotate(total=Sum('amount')).order_by('date__year', 'date__month')
    months = [f"{entry['date__month']}/{entry['date__year']}" for entry in monthly_expenses]
    totals = [entry['total'] for entry in monthly_expenses]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=totals, mode='lines+markers', line=dict(color='blue', width=2), marker=dict(size=8)))
    fig.update_layout(title='Monthly Expense Trend', xaxis_title='Month', yaxis_title='Total Expenses', xaxis_tickangle=-45)
    monthly_expenses_chart = fig.to_html(full_html=False)

    # Expense Distribution by Category (Interactive Bar Chart)
    expense_distribution = Expense.objects.values('category').annotate(total=Sum('amount')).order_by('category')
    categories = [entry['category'] for entry in expense_distribution]
    totals = [entry['total'] for entry in expense_distribution]

    fig = go.Figure([go.Bar(x=categories, y=totals, marker_color='skyblue')])
    fig.update_layout(title='Expense Distribution by Category', xaxis_title='Category', yaxis_title='Total Expenses', xaxis_tickangle=-45)
    expense_distribution_chart = fig.to_html(full_html=False)

    # Income vs. Expenses Over Time (Interactive Dual-Axis Line Plot)
    income_data = Income.objects.values('date__year', 'date__month').annotate(total_income=Sum('amount')).order_by('date__year', 'date__month')
    expense_data = Expense.objects.values('date__year', 'date__month').annotate(total_expense=Sum('amount')).order_by('date__year', 'date__month')

    months = sorted(set([f"{entry['date__month']}/{entry['date__year']}" for entry in income_data] + [f"{entry['date__month']}/{entry['date__year']}" for entry in expense_data]))

    income_totals = []
    expense_totals = []
    for month in months:
        income_totals.append(next((entry['total_income'] for entry in income_data if f"{entry['date__month']}/{entry['date__year']}" == month), 0))
        expense_totals.append(next((entry['total_expense'] for entry in expense_data if f"{entry['date__month']}/{entry['date__year']}" == month), 0))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=income_totals, mode='lines+markers', name='Income', line=dict(color='green', width=2), marker=dict(size=8)))
    fig.add_trace(go.Scatter(x=months, y=expense_totals, mode='lines+markers', name='Expenses', line=dict(color='red', width=2), marker=dict(size=8)))
    fig.update_layout(title='Income vs. Expenses Over Time', xaxis_title='Month', yaxis_title='Total Amount', xaxis_tickangle=-45)
    income_vs_expenses_chart = fig.to_html(full_html=False)

    # User Spending Patterns (Interactive Horizontal Bar Chart)
    user_spending = Expense.objects.values('owner__name').annotate(total=Sum('amount')).order_by('owner__name')
    users = [entry['owner__name'] for entry in user_spending]
    totals = [entry['total'] for entry in user_spending]

    fig = go.Figure([go.Bar(x=totals, y=users, orientation='h', marker_color='lightcoral')])
    fig.update_layout(title='User Spending Patterns', xaxis_title='Total Expenses', yaxis_title='User')
    user_spending_chart = fig.to_html(full_html=False)

    # Expense vs. Income Ratio (Interactive Pie Chart)
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_income = Income.objects.aggregate(total=Sum('amount'))['total'] or 0

    labels = ['Expenses', 'Income']
    sizes = [total_expenses, total_income]

    fig = px.pie(names=labels, values=sizes, title='Expense vs. Income Ratio', color_discrete_sequence=['lightblue', 'lightgreen'])
    expense_income_ratio_chart = fig.to_html(full_html=False)

    return render(request, 'visualizations.html', {
        'monthly_expenses_chart': monthly_expenses_chart,
        'expense_distribution_chart': expense_distribution_chart,
        'income_vs_expenses_chart': income_vs_expenses_chart,
        'user_spending_chart': user_spending_chart,
        'expense_income_ratio_chart': expense_income_ratio_chart,
    })
