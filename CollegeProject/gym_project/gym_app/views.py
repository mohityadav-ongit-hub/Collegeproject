# gym_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import Member, MembershipPlan, Payment, FreeTrial
from .forms import CustomUserCreationForm, MembershipPlanForm, MemberPlanForm, PaymentForm, AgeForm, AdminLoginForm, FreeTrialForm
from datetime import timedelta, date

def home_view(request):
    return render(request, 'gym_app/base.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.get_messages(request).used = True
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'gym_app/login.html')

@login_required
def dashboard(request):
    members = Member.objects.filter(user=request.user)
    today = date.today()
    for member in members:
        if member.membership_expiry and member.membership_expiry < today + timedelta(days=30):
            member.is_expiring = True
        else:
            member.is_expiring = False
    return render(request, 'gym_app/dashboard.html', {'members': members, 'today': today})

@login_required
def member_detail(request, id):
    member = get_object_or_404(Member, id=id)
    payments = Payment.objects.filter(member=member)
    plan_form = MemberPlanForm(instance=member)
    payment_form = PaymentForm()
    is_admin = request.session.get('admin_access', False)
    if member.user != request.user and not is_admin:
        messages.error(request, "You are not permitted to view this member's details.")
        return render(request, 'gym_app/member_detail.html', {
            'member': None,
            'payments': [],
            'plan_form': None,
            'payment_form': None,
            'is_admin': False
        })
    if request.method == 'POST' and is_admin:
        if 'plan_submit' in request.POST:
            plan_form = MemberPlanForm(request.POST, instance=member)
            if plan_form.is_valid():
                member = plan_form.save(commit=False)
                if member.membership_plan:
                    member.membership_expiry = date.today() + timedelta(
                        days=member.membership_plan.duration_months * 30)
                else:
                    member.membership_expiry = None
                member.save()
                messages.success(request, f'Membership plan updated for {member.user.username}.')
                return redirect('member_detail', id=id)
            else:
                messages.error(request, f'Failed to update plan: {plan_form.errors}')
        elif 'payment_submit' in request.POST:
            payment_form = PaymentForm(request.POST)
            if payment_form.is_valid():
                payment = payment_form.save(commit=False)
                payment.member = member
                payment.save()
                if member.membership_expiry and member.membership_expiry > date.today():
                    member.membership_expiry += timedelta(days=30)
                else:
                    member.membership_expiry = date.today() + timedelta(days=30)
                member.save()
                messages.success(request, f'Payment recorded for {member.user.username}.')
                return redirect('member_detail', id=id)
            else:
                messages.error(request, f'Failed to record payment: {payment_form.errors}')
    return render(request, 'gym_app/member_detail.html', {
        'member': member,
        'payments': payments,
        'plan_form': plan_form,
        'payment_form': payment_form,
        'is_admin': is_admin
    })

def membership_plans(request):
    plans = MembershipPlan.objects.all()
    plan_form = MembershipPlanForm()
    password_form = AdminLoginForm()
    if 'plan_access' not in request.session:
        request.session['plan_access'] = False
    has_access = request.session.get('plan_access', False) or request.session.get('admin_access', False)

    if request.method == 'POST':
        if 'password_submit' in request.POST:
            password_form = AdminLoginForm(request.POST)
            if password_form.is_valid():
                password = password_form.cleaned_data['password']
                if password == 'member121':
                    request.session['plan_access'] = True
                    messages.success(request, 'Access granted to manage plans!')
                    return redirect('plans')
                else:
                    messages.error(request, 'Incorrect password.')
            else:
                for error_message in password_form.errors['password']:
                    messages.error(request, error_message)
        elif 'plan_submit' in request.POST:
            if not has_access:
                messages.error(request, 'You must enter the correct password to add a plan.')
                return redirect('plans')
            plan_form = MembershipPlanForm(request.POST)
            if plan_form.is_valid():
                plan_form.save()
                messages.success(request, 'Plan added successfully!')
                return redirect('plans')
            else:
                for field, errors in plan_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{plan_form.fields[field].label}: {error}")
    return render(request, 'gym_app/plans.html', {
        'plans': plans,
        'plan_form': plan_form,
        'password_form': password_form,
        'has_access': has_access
    })

def logout_view(request):
    logout(request)
    request.session['plan_access'] = False
    request.session['admin_access'] = False
    messages.get_messages(request).used = True
    return redirect('home')

def diet_15_30(request):
    return render(request, 'gym_app/diet/diet_15_30.html')

def diet_30_50(request):
    return render(request, 'gym_app/diet/diet_30_50.html')

def diet_50_70(request):
    return render(request, 'gym_app/diet/diet_50_70.html')

def diet_selection(request):
    if request.method == 'POST':
        form = AgeForm(request.POST)
        if form.is_valid():
            age = form.cleaned_data['age']
            if 15 <= age <= 30:
                return redirect('diet_15_30')
            elif 31 <= age <= 50:
                return redirect('diet_30_50')
            elif 51 <= age <= 70:
                return redirect('diet_50_70')
        else:
            for error_message in form.errors['age']:
                messages.error(request, error_message)
    else:
        form = AgeForm()
    return render(request, 'gym_app/diet/diet_selection.html', {'form': form})

def admin_dashboard(request):
    if 'admin_access' not in request.session:
        request.session['admin_access'] = False
    if request.session['admin_access']:
        members = Member.objects.all()
        return render(request, 'gym_app/admin_dashboard.html', {'members': members})
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            if password == 'admin121':
                request.session['admin_access'] = True
                messages.success(request, 'Admin access granted.')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Incorrect password.')
        else:
            for error_message in form.errors['password']:
                messages.error(request, error_message)
    else:
        form = AdminLoginForm()
    return render(request, 'gym_app/admin_dashboard.html', {'form': form})

def register(request):
    is_free_trial = request.path == '/free-trial-register/'
    if request.method == 'POST':
        if is_free_trial:
            form = FreeTrialForm(request.POST)
            if form.is_valid():
                free_trial = form.save(commit=False)
                free_trial.password = make_password(free_trial.password)
                free_trial.save()
                messages.success(request, 'Free trial registration successful!')
                return redirect('home')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
        else:
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                try:
                    special_plan = MembershipPlan.objects.get(name='Special plan')
                    membership_expiry = date.today() + timedelta(days=special_plan.duration_months * 30)
                except MembershipPlan.DoesNotExist:
                    special_plan = None
                    membership_expiry = None
                    messages.error(request, 'Special Plan not found. No plan assigned.')
                Member.objects.create(
                    user=user,
                    phone=form.cleaned_data['phone'],
                    date_of_birth=form.cleaned_data['date_of_birth'],
                    address=form.cleaned_data['address'],
                    membership_plan=special_plan,
                    membership_expiry=membership_expiry
                )
                messages.success(request, 'Registration successful!')
                return redirect('login')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")
    else:
        form = FreeTrialForm() if is_free_trial else CustomUserCreationForm()
    template = 'gym_app/free_trial_register.html' if is_free_trial else 'gym_app/register.html'
    return render(request, template, {'form': form})

def about(request):
    return render(request, 'gym_app/about.html', {})

def events(request):
   return render(request, 'gym_app/events.html', {})

def event_register(request):
    event = request.GET.get('event', 'unknown')
    # Add logic to handle registration (e.g., save to database, show form)
    context = {'event': event}
    return render(request, 'gym_app/event_register.html', context)