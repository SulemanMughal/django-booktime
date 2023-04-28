import  sys
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, authenticate,login
# from django.views.generic.edit import FormView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import (
    FormView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib import messages
from main import forms
from django.http import HttpResponseRedirect
from django.views.generic.list import ListView
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin
)
from django import forms as django_forms
from django.db import models as django_models
import django_filters
from django_filters.views import FilterView


# from django.shortcuts import 
from main import models
from .forms import loginForm
import logging
logger = logging.getLogger(__name__)
# from django.urls import reverse
# Create your views here.

def index(request):
    template_name = 'main/home.html'
    context = {
        "section" : "home"
    }
    return render(request, template_name, context)


def about_us(request):
    template_name = 'main/about_us.html'
    context = {
        "section" : "about"
    }
    return render(request, template_name, context)

def contact_us(request):
    if request.method == 'POST':
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            form.send_mail()
            return HttpResponseRedirect('/')
    else:
        context = {
            "section" : "contact",
            "form" : forms.ContactForm(),
        }
        return render(request, 'contact_form.html', context)

class ProductListView(ListView):
    template_name = "main/product_list.html"
    paginate_by = 4
    
    def get_queryset(self):
        tag = self.kwargs['tag']
        self.tag = None
        if tag != "all":
            self.tag = get_object_or_404(
            models.ProductTag, slug=tag
            )
        if self.tag:
            products = models.Product.active_products.active().filter(
            tags=self.tag
            )
        else:
            products = models.Product.active_products.active()
        return products.order_by("name")

# TODO  :   User Login View
def UserLoginView(request):
    template_name= "main/login.html"
    if request.user.is_authenticated:
        return redirect("index")
    else:
        if request.method == "POST" :
            form = loginForm(request.POST)
            valuenext = request.POST.get('next')
            if form.is_valid():
                try:
                    u = authenticate(
                        request, 
                        username = form.cleaned_data["username"], 
                        password = form.cleaned_data["password"]
                    )
                    if u is not None:
                        if u.is_active:
                            login(request, u)
                            if len(valuenext) != 0 and valuenext is not None:
                                return redirect(valuenext)
                            else:
                                return redirect("index")
                        else:
                            messages.error(request, "User does not verify himself or he has been blocked from using our services due to violation of our terms and conditions.")
                    else:
                        messages.error(request, "Username or password has been entered incorrectly.")
                except Exception as e:
                    logger.error(e, exc_info=sys.exc_info())
                    messages.error(request, "Please login after sometimes. Requests are not processed at this time.")
            else:
                messages.error(request, "Please entered correct information for respective required fields.")

    form = loginForm()
    context = {
        "form" : form,
        "section" : True
    }
    return render(request, template_name, context)



# TODO  :   User Logout View
def UserLogoutView(request):
    logout(request)
    return redirect('index')



class AddressListView(LoginRequiredMixin, ListView):
    model = models.Address
    
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class AddressCreateView(LoginRequiredMixin, CreateView):
    model = models.Address
    fields = [
    "name",
    "address1",
    "address2",
    "zip_code",
    "city",
    "country",
    ]
    success_url = reverse_lazy("address_list")
    
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Address
    fields = [
    "name",
    "address1",
    "address2",
    "zip_code",
    "city",
    "country",
    ]
    success_url = reverse_lazy("address_list")
    
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Address
    success_url = reverse_lazy("address_list")

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

# TODO  :   Add products to the basket
def add_to_basket(request):
    product = get_object_or_404(
    models.Product, pk=request.GET.get("product_id")
    )
    basket = request.basket
    if not request.basket:
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None
        basket = models.Basket.objects.create(user=user)
        request.session["basket_id"] = basket.id
    basketline, created = models.BasketLine.objects.get_or_create(
        basket=basket, product=product
    )
    if not created:
        basketline.quantity += 1
        basketline.save()
    return HttpResponseRedirect(
        reverse("product", args=(product.slug,))
    )


def manage_basket(request):
    template_name="main/basket.html"
    if not request.basket:
        context={"formset": None}
        return render(request, template_name,context )
    if request.method == "POST":
        formset = forms.BasketLineFormSet(
            request.POST, instance=request.basket
        )
        if formset.is_valid():
            formset.save()
    else:
        formset = forms.BasketLineFormSet(
            instance=request.basket
        )
    if request.basket.is_empty():
        context = {"formset": None}
        return render(request, template_name, context)
    context = {"formset": formset}
    return render(request, template_name, context)


class AddressSelectionView(LoginRequiredMixin, FormView):
    template_name = "address_select.html"
    form_class = forms.AddressSelectionForm
    success_url = reverse_lazy('checkout_done')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        del self.request.session['basket_id']
        basket = self.request.basket
        basket.create_order(
        form.cleaned_data['billing_address'],
        form.cleaned_data['shipping_address']
        )
        return super().form_valid(form)


class DateInput(django_forms.DateInput):
    input_type = 'date'

class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = models.Order
        fields = {
            'user__email': ['icontains'],
            'status': ['exact'],
            'date_updated': ['gt', 'lt'],
            'date_added': ['gt', 'lt'],
        }
        filter_overrides = {
            django_models.DateTimeField: {
            'filter_class': django_filters.DateFilter,
            'extra': lambda f:{
            'widget': DateInput}}}


class OrderView(UserPassesTestMixin, FilterView):
    filterset_class = OrderFilter
    login_url = reverse_lazy("user-login")
    
    def test_func(self):
        return self.request.user.is_staff is True