# gym_app/admin.py
from django.contrib import admin
from .models import MembershipPlan, Member, Payment, FreeTrial

admin.site.register(MembershipPlan)
admin.site.register(Member)
admin.site.register(Payment)
admin.site.register(FreeTrial)
