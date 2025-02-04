from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Decorators
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .decorators import allowerd_users
from .decorators import unauthenticated_user

from datetime import date
import pandas as pd

# Models and Forms
from backend.models import Info, Book, Student, Issue, Reservation, Class
from backend.fields import book_fields, class_fields, student_fields, reservation_fields, issue_fields
from .forms import BookForm, ClassForm, StudentForm, IssueForm, ReservationForm, LoginForm
from .custom import get_fields


# Excel to JSON parser
def parser_view(request):    
    info = Info.objects.all().first()
    data = None
    if request.method == "POST":
        if 'file' in  request.FILES:
            dataFrame = pd.read_excel(request.FILES['file'], engine = "openpyxl")    
            data = dataFrame.to_json(indent = 4, orient = "records", force_ascii = False)
        else:
            return redirect("parser-view")

    context = { "json": data, "school_name": info.school_name }
    return render(request, "apis/index.html", context)


@unauthenticated_user
@csrf_exempt
def login_view(request):
    form = LoginForm()
    info = Info.objects.all().first()

    if request.method == 'POST':
        form = LoginForm(request, data = request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username = username, password = password)
            if user is not None:
                login(request, user)
                return redirect('home-view')

    context = { "form": form, "messages": messages, "school_name": info.school_name }

    return render(request, 'registration/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('login-view')


def home_view(request):
    info = Info.objects.all().first()
    books = Book.objects.all()
    tableFields = book_fields()
    fields = []
    # Model field list
    for field in Book._meta.get_fields():
        if field.name != "reservation":
            fields.append(field.name) 

    context = {
        "querySet": books,
        "fields": fields,
        "tfields": tableFields[0],
        "tlength": len(fields),
        "school_name": info.school_name,
    }

    return render(request, "home.html", context)

def error_view(request):
    return render(request, "components/error.html")

def tutorial_view(request):
    info = Info.objects.all().first()
    context = {
        "school_name": info.school_name,
    }
    return render(request, "tutorial/index.html", context)

class BookGPView(View):
    @method_decorator(allowerd_users(["book-editing"]))
    def get(self, request):
        info = Info.objects.all().first()
        books = Book.objects.all()
        tableFields = book_fields()
        form = BookForm()
        fields = []

        # Model field list
        for field in Book._meta.get_fields():
            if field.name != "reservation":
                fields.append(field.name) 

        context = {
            "fields": fields,
            "querySet": books,
            "form": form,
            "tfields": tableFields[0],
            "tlength": len(fields) + 1,
            "school_name": info.school_name,
        }

        return render(request, "book/index.html", context)

    @method_decorator(allowerd_users(["book-editing"]))
    def post(self, request):
        form = BookForm()

        if request.method == "POST":
            form = BookForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("book-view")
            else:
                return form.errors

class BookPDView(View):
    def get_object(self, pk):
        try:
            return Book.objects.get(id = pk)
        except Book.DoesNotExist:
            raise Http404
    
    @method_decorator(allowerd_users(["book-editing"]))
    def get(self, request, pk):
        return self.get_object(pk)

    @method_decorator(allowerd_users(["book-editing"]))
    def delete(self, request, pk):
        book = self.get_object(pk)
        error = JsonResponse({"error": "Sve knjige nisu vraćene!"})

        if len(Reservation.objects.all()) == 0: # If there is no book's at all 
            book.delete()
            return JsonResponse(dict(code = 204, content = "Knjiga je izbrisana"))
        elif not Reservation.objects.get(book = book): # If the selected book is not reservated
            book.delete()
            return JsonResponse(dict(code = 204, content = "Knjiga je izbrisana"))
        else: # If the all books of this type are returned
            reservation = Reservation.objects.get(book = book)
            if reservation.issued == reservation.returned:
                book.delete()
                return JsonResponse(dict(code = 204, content = "Knjiga je izbrisana"))

        error.status_code = 403
        return error

class ClassGPView(View):
    @method_decorator(allowerd_users(["class-editing"]))
    def get(self, request):
        info = Info.objects.all().first()
        classes = Class.objects.all()
        tableFields = class_fields()
        form = ClassForm()
        fields = []

        # Model field list
        for field in Class._meta.get_fields():
            if field.name != "student":
                fields.append(field.name) 

        context = {
            "fields": fields,
            "querySet": classes,
            "form": form,
            "tfields": tableFields[0],
            "tlength": len(fields) + 1,
            "school_name": info.school_name,
        }

        return render(request, "class/index.html", context)

    @method_decorator(allowerd_users(["class-editing"]))
    def post(self, request):
        form = ClassForm()

        if request.method == "POST":
            form = ClassForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("class-view")
            else:
                return form.errors


class ClassPDView(View):
    def get_object(self, pk):
        try:
            return Class.objects.get(id = pk)
        except Class.DoesNotExist:
            raise Http404

    @method_decorator(allowerd_users(["class-editing"]))
    def get(self, request, pk):
        return self.get_object(pk)
    
    @method_decorator(allowerd_users(["class-editing"]))
    def delete(self, request, pk):
        classes = self.get_object(pk)
        classes.delete()
        return JsonResponse(dict(code = 204, content = "Odjeljenje je izbrisano!"))


class StudentGPView(View):
    @method_decorator(allowerd_users(["student-editing"]))
    def get(self, request):
        info = Info.objects.all().first()
        students = Student.objects.all()
        tableFields = student_fields()
        form = StudentForm()
        fields = []

        # Model fields
        for field in Student._meta.get_fields():
            if field.name != "issue":
                fields.append(field.name)


        context = {
            "fields": fields,
            "querySet": students,
            "form": form,
            "tfields": tableFields[0],
            "tlength": len(fields) + 1,
            "school_name": info.school_name,
        }

        return render(request, "student/index.html", context)

    @method_decorator(allowerd_users(["student-editing"]))
    def post(self, request):
        form = StudentForm()

        if request.method == "POST":
            form = StudentForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("student-view")
            else:
                return form.errors

class StudentPDView(View):
    def get_object(self, pk):
        try:
            return Student.objects.get(id = pk)
        except Student.DoesNotExist:
            raise Http404

    @method_decorator(allowerd_users(["student-editing"]))
    def get(self, request, pk):
        return self.get_object(pk)
    
    @method_decorator(allowerd_users(["student-editing"]))
    def delete(self, request, pk):
        student = self.get_object(pk)
        student.delete()
        return JsonResponse(dict(code = 204, content = "Učenik je izbrisan!"))


class ReservationGPView(View):
    @method_decorator(allowerd_users(["reservation-editing"]))
    def get(self, request):
        info = Info.objects.all().first()
        reservation = Reservation.objects.filter(professor = request.user.get_full_name())
        tableFields = reservation_fields()
        form = ReservationForm()
        fields = get_fields(Reservation, "issue")

        context = {
            "fields": fields,
            "querySet": reservation,
            "form": form,
            "tfields": tableFields[0],
            "tlength": len(fields) + 1,
            "school_name": info.school_name,
        }

        return render(request, "reservation/index.html", context)
    
    @method_decorator(allowerd_users(["reservation-editing"]))
    def post(self, request):
        info = Info.objects.all().first()
        reservation = Reservation.objects.all()
        form = ReservationForm()
        fields = get_fields(Reservation, "issue")

        if request.method == "POST":
            form = ReservationForm(request.POST)
            if form.is_valid():
                # Updating the book DB
                book = Book.objects.get(id = form.cleaned_data["book"].id)
                book.quantity -= form.cleaned_data["quantity"]
                book.save()

                # Saving the user 
                data = form.save(commit = False)
                data.professor = request.user.get_full_name()
                data.save()
                return redirect("reservation-view")
        
        context = {
            "fields": fields,
            "querySet": reservation,
            "form": form,
            "school_name": info.school_name,
        }

        return render(request, "reservation/index.html", context)

class ReservationPDView(View):
    def get_object(self, pk):
        try:
            return Reservation.objects.get(id = pk)
        except Reservation.DoesNotExist:
            raise Http404
    
    @method_decorator(allowerd_users(["reservation-editing"]))
    def get(self, request, pk):
        return self.get_object(pk)
        
    @method_decorator(allowerd_users(["reservation-editing"]))
    def delete(self, request, pk):
        reservation = self.get_object(pk)
        error = JsonResponse({"error": "Sve knjige nisu vraćene!"})

        if request.is_ajax():
            if reservation.issued == reservation.returned:
                book = Book.objects.get(id = reservation.book.id)
                book.quantity += reservation.quantity
                book.save()

                reservation.delete()
                return JsonResponse(dict(code = 204, content = "Rezervacija je izbrisana!"))
        error.status_code = 403
        return error
            

class IssueGPView(View):
    @method_decorator(allowerd_users(["issue-editing"]))
    def get(self, request):
        info = Info.objects.all().first()
        issues = Issue.objects.all()
        tableFields = issue_fields()
        form = IssueForm()
        fields = [field.name for field in Issue._meta.get_fields()]

        context = {
            "fields": fields,
            "querySet": issues,
            "form": form,
            "tfields": tableFields[0],
            "tlength": len(fields) + 1,
            "school_name": info.school_name,
        }

        return render(request, "issue/index.html", context)

    @method_decorator(allowerd_users(["issue-editing"]))
    def post(self, request):
        info = Info.objects.all().first()
        issues = Issue.objects.all()
        form = IssueForm()
        fields = [field.name for field in Issue._meta.get_fields()]

        if request.method == "POST":
            form = IssueForm(request.POST)
            if form.is_valid():
                issue = Reservation.objects.get(id = form.cleaned_data["reservation"].id)
                issue.issued += 1
                issue.save()

                form.save()
                return redirect("issue-view")

        context = {
            "fields": fields,
            "querySet": issues,
            "form": form,
            "school_name": info.school_name,
        }

        return render(request, "issue/index.html", context)

class IssuePDView(View):
    # Getting the Issue object
    def get_object(self, pk):
        try:
            return Issue.objects.get(id = pk)
        except Issue.DoesNotExist:
            raise Http404

    @method_decorator(allowerd_users(["issue-editing"]))
    def get(self, request, pk):
        return self.get_object(pk)
    
    @method_decorator(allowerd_users(["issue-editing"]))
    def put(self, request, pk):
        issue = self.get_object(pk)
        data = {}

        if request.is_ajax():
            reservation = issue.reservation
            
            if issue.returnStatus:
                # Updating the issues DB to the latest info
                issue.returnStatus = False
                issue.returnDate = None
                issue.debt = 0
                reservation.returned -= 1
            else:
                issue.returnStatus = True
                issue.returnDate = date.today()
                if date.today() > reservation.endDate:
                    delta = date.today() - reservation.endDate
                    issue.debt = delta.days * .5
                reservation.returned += 1
            
            # Saving the changes
            issue.save()
            reservation.save()

            # Preparing the data for returning into template
            data['id'] = issue.id
            data['returnStatus'] = issue.returnStatus
            data['returnDate'] = issue.returnDate
            data['debt'] = issue.debt
            data['content'] = "Uspješno ste izmjenili podatke o knjizi!"

            return JsonResponse(data)
    
    @method_decorator(allowerd_users(["issue-editing"]))
    def delete(self, request, pk):
        issue = self.get_object(pk)
        reservation = issue.reservation
        reservation.issued -= 1
        reservation.returned -=1
        reservation.save()
        issue.delete()

        return JsonResponse(dict(code = 204, content = "Učenik je izbrisan!"))

