from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate,login
from django.http import HttpResponseRedirect,HttpResponse
from models import Category
from models import Page
from forms import CategoryForm
from forms import PageForm,UserForm,UserProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime


def index(request):
    #request.session.set_test_cookie() # cookie testing
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    # Query for categories - add the list to our context dictionary.
    #category_list = Category.objects.order_by('-likes')[:5]
    category_list = Category.objects.all()
    context_dict = {'categories': category_list}

# new code
    #for category in category_list:
    #    category.url = encode_url(category.name)
    for category in category_list:
        category.url = category.name.replace(' ', '_')

    page_list = Page.objects.order_by('-views')[:5]
    context_dict['pages'] = page_list

    #### new code ####
    # we have to obtain the response first so that we can add the cookie information
    response =  render_to_response('rango/index.html', context_dict, context)

    #to fetch the number of visits to the site we use
    # COOKIES.get() . If the cookie exist , the value is casted as an integer.
    #  if the cookie doesnt exist ,we default zero
    visits  = int (request.COOKIES.get('visits','0'))

    #to check whether cookie last_visit exits
    if 'last_visit' in request.COOKIES:
        #if cookie exit , the get the cokie's value
        last_visit = request.COOKIES['last_visit']
        # caste the value to the python date/time object
        last_visit_time = datetime.strptime(last_visit[:-7],"%Y-%m-%d %H:%M:%S")

        # If its more than a day since the last visit
        if(datetime.now() - last_visit_time).days > 0:
            #reassign the value of the cookie to +1 of what it was before
            response.set_cookie('visits',visits+1)
            # update the last visit cookie
            response.set_cookie('last_visit',datetime.now())
    else:
        #cookie last_visit doesn't exist , so create it to the current date/time
        response.set_cookie('last_visit',datetime.now())
    # return response nback to the user, updating any cookies that need changed
    return response
    ### END NEW CODE ####

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
    context = RequestContext(request)
    return render_to_response('rango/about.html',{},context)
    #return HttpResponse("Rango says come to my application")

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

#def add_page(request,category_name_url):
##z   category_name = decode_url(category_name_url)
 #   if request.method =='POST':
 #       form = PageForm(request.POST)
 #       if form.is_valid():
 #           page = form.save(commit = False)
 #           try:
 #               cat = Category.objects.get(name=category_name)
 #               page.category = cat
 #           except Category.DoesNotExist:
 #               return render_to_response('rango/add_category.html',{},context)#
#
#            page.views = 0
#            page.save()
 #           return category(request,category_name_url)
 #       else:
 #           print form.errors
 #   else:
 #       form = PageForm()

  #  return render_to_response('rango/add_page.html',
  #      {'category_name_url':category_name_url,
  #       'category_name' : category_name, 'form':form},
  #      context)
def add_page(request, category_name_url):
    context = RequestContext(request)

    category_name = decode_url(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            # This time we cannot commit straight away.
            # Not all fields are automatically populated!
            page = form.save(commit=False)

            # Retrieve the associated Category object so we can add it.
            # Wrap the code in a try block - check if the category actually exists!
            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                # If we get here, the category does not exist.
                # Go back and render the add category form as a way of saying the category does not exist.
                return render_to_response('rango/add_category.html', {}, context)

            # Also, create a default value for the number of views.
            page.views = 0

            # With this, we can then save our new model instance.
            page.save()

            # Now that the page is saved, display the category instead.
            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()

    return render_to_response( 'rango/add_page.html',
            {'category_name_url': category_name_url,
             'category_name': category_name, 'form': form},
             context)

def decode_url(category_name_url):
    category_name = category_name_url.replace('_',' ')

    return category_name

def register(request):
    # cookie worked well
    if request.session.test_cookie_worked():
        print ">>>> TEST COOKIE WORKED!"
        request.session.delete_test_cookie()
    # Like before, get the request's context.
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render_to_response(
            'rango/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
            context)

def user_login(request):
    context = RequestContext(request)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # django machinery to check if username/password combination is valid
        user = authenticate(username = username,password = password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse("Your Rango account is disabled.")

        else:
             print "Invalid login details: {0},{1}".format(username,password)
            # return HttpResponse("Invalid login details supplied.")
             return render_to_response('rango/invalidLogin.html',{},context)

    else:
        return render_to_response('rango/login.html',{},context)


# remember that user object is always available in the request object

def some_view(request):
    if not request.user.is_authenticated():
        return HttpResponse("you are logged in ")
    else:
        return HttpResponse("you are not logged in ")


@login_required # login_required is a decorator used for restricting access
def restricted(request):
    return HttpResponse("Since you're logged in , you can see this text!")

# for logging out
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')




