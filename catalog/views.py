from django.shortcuts import render


from .models import Book, Author, BookInstance, Genre

def index(request):
   
    num_books=Book.objects.all().count()
    num_instances=BookInstance.objects.all().count()
    
    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count() 
	
    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1
    
   
    return render(
        request,
        'index.html',
        context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors,'num_visits':num_visits},
    )
	
from django.views import generic

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10
	
class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10	
	
	
class BookDetailView(generic.DetailView):
    model = Book
	
class AuthorDetailView(generic.DetailView):
    model = Author	

from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
  
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

from django.contrib.auth.mixins import PermissionRequiredMixin		
class AllLoanedBooksByUserListView(PermissionRequiredMixin,generic.ListView):

    model = BookInstance
    template_name = 'catalog/bookinstance_list_all_borrowed_user.html'
    permission_required = 'catalog.can_mark_returned'
    painate_by = 10
    def get_queryset(self):
	    return BookInstance.objects.filter(status__exact='o').order_by('due_back')
		
from django.contrib.auth.decorators import permission_required		
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

from .forms import RenewBookForm

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_inst=get_object_or_404(BookInstance, pk = pk)

   
    if request.method == 'POST':

      
        form = RenewBookForm(request.POST)

       
        if form.is_valid():
            
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

          
            return HttpResponseRedirect(reverse('all-borrowed') )

   
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})