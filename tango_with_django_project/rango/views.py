from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from models import Category
from models import Page
from forms import CategoryForm
from forms import PageForm
def index(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    # Query for categories - add the list to our context dictionary.
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories': category_list}

    # The following two lines are new.
    # We loop through each category returned, and create a URL attribute.
    # This attribute stores an encoded URL (e.g. spaces replaced with underscores).
    for category in category_list:
        category.url = category.name.replace(' ', '_')

    # Render the response and return to the client.
    return render_to_response('rango/index.html', context_dict, context)

def category(request,category_name_url):
    context = RequestContext(request)
    category_name = category_name_url.replace('_',' ')
    context_dict = {'category_name': category_name}
    try:

        category = Category.objects.get(name=category_name)
        pages = Page.objects.filter(category = category)
        context_dict['pages'] = pages
        context_dict ['category'] = category
        context_dict ['category_name_url'] = category_name_url
    except Category.DoesNotExist:
        pass
    return render_to_response('rango/category.html',context_dict,context)
def about(request):
    return HttpResponse("Rango says come to my application")

def add_category(request):
    # get the context from the request
    context = RequestContext(request)
    # a HTTP POST?
    if request.method == 'POST':
       form  = CategoryForm(request.POST)
       #have we been provided with the valid form
       if form.is_valid():
           #save the new category to the database.
           form.save(commit=True)
           #now call the index() view
           # the user will be shown the homepage
           return index(request)
       else:
           #the supplied form contained errors - just print them to the terminal.
           print form.errors
    else:
        # if the request was not a POST, display the form to enter details
        form = CategoryForm()
    # bad form(or form details), no form supplied ..
    # Render the form with error messages (if any)
    return render_to_response('rango/add_category.html',{'form':form},context)

def add_page(request,category_name_url):
    context = RequestContext(request)
    category_name = decode_url(category_name_url)
    if request.method =='POST':
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit = False)
            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                return render_to_response('rango/add_category.html',{},context)

            page.views = 0
            page.save()
            return category(request,category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()

    return render_to_response('rango/add_page.html',
        {'category_name_url':category_name_url,
         'category_name' : category_name, 'form':form},
        context)



