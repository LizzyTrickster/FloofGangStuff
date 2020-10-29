#!/usr/bin/env python3
# Copyright of Lizzy Trickster (Lizzy Green)

from django.shortcuts import render, redirect
from django.db.utils import IntegrityError
from django.contrib import messages
from django.contrib.auth import logout
from django.views import View

from django.http import JsonResponse, HttpResponse
from social_django.models import UserSocialAuth

from .ext import UserInputError
from .models import Birthday
import datetime


def landing_page(request):
    return render(request, "landing.html")


def today(request):
    current_date = datetime.datetime.utcnow().strftime("%d%m")
    peoples = Birthday.objects.filter(birthday__exact=current_date)
    if request.META.get('HTTP_ACCEPT', '*/*') == 'application/json':
        birthdays = list()
        for user in peoples:
            entry = dict(displayName=user.display_name, ping=user.notify)
            if user.notify:
                entry['discordID'] = int(UserSocialAuth.get_social_auth_for_user(user.user, provider="discord")[0].extra_data['discord_id'])
            birthdays.append( entry )
        data = dict(date=current_date, count=len(birthdays), birthdays=birthdays)
        return JsonResponse(data)
    else:
        return render(request, "birthday/today.html", context=dict(users=peoples))


def today_neos(request):
    current_date = datetime.datetime.utcnow().strftime("%d%m")
    peoples = Birthday.objects.filter(birthday__exact=current_date)
    return HttpResponse("\n".join([user.display_name for user in peoples]), content_type="text/plain")


class Submissions(View):
    days = [*range(1, 32)]
    months = [*range(1, 13)]

    def get(self, request):
        entry = None
        if request.user.is_authenticated:
            try:
                entry = Birthday.objects.get(user=request.user)
            except:
                entry = None
        class_string = None
        if request.user.is_authenticated and entry:
                class_string = 'form-complete'
        elif not request.user.is_authenticated:
            class_string = 'form-nologin'
        return render(request, "birthday/submission.html",
                      context=dict(logged_in=request.user.is_authenticated,
                                   disabled=(not request.user.is_authenticated or entry),
                                   class_string=class_string,
                                   entry=entry,
                                   days=self.days,
                                   months=self.months
                                   )
                      )

    def post(self, request):
        uname = request.POST.get('uname', "")
        day = int(request.POST.get('bday', -1))
        month = int(request.POST.get('bmon', -1))
        notify = bool(request.POST.get('noti', False))

        entry: Birthday = None
        context = dict(logged_in=request.user.is_authenticated, days=self.days, months=self.months, _STATUS_CODE=None)
        if request.user.is_authenticated:
            try:
                entry = Birthday.objects.get(user=request.user)
                if f"{day:02}{month:02}" in (entry.birthday, "-1-1"):
                    entry.notify = notify
                    entry.save()
                    messages.add_message(request, messages.SUCCESS, "Successfully updated notification preferences")
                else:
                    messages.add_message(request, messages.WARNING, "Day and Month values provided in the form don't match with existing entry. "
                                                                    "Did you manually edit the HTML?")
                context = {**context, **{"disabled": True, "class_string": "form-complete", "entry": entry}}

            except Birthday.DoesNotExist:
                # The birthday object didn't already exist so this is likely not an update
                try:
                    if month in [4, 6, 9, 11] and day > 30:
                        raise UserInputError
                    elif month == 2 and day > 29:
                        raise UserInputError
                    entry = Birthday.objects.create(user=request.user, display_name=uname, birthday=f"{day:02}{month:02}", notify=notify)
                except IntegrityError:  # OPTIMISE This might not be needed anymore?
                    messages.add_message(request, messages.ERROR, "Duplicate entry exists!?")  # TODO Add error notification stuff here?
                except UserInputError:
                    messages.error(request, f"Invalid day ({day}) specified for month {month}. Your response has not been recorded.")
                    context = {**context, **{"disabled": False, "class_string": None, "entry": None, "_STATUS_CODE": 422}}
                except:
                    raise
                else:
                    messages.add_message(request, messages.SUCCESS, "Entry successfully recorded!")
                    context = {**context, **{"disabled": True, "class_string": "form-complete", "entry": entry}}
        else:
            context = {**context, **{"disabled": True, "class_string": "form-nologin", "entry": None}}

        return render(request, "birthday/submission.html", context=context, status=context.get("_STATUS_CODE") or 200)


def logout_view(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS, "Successfully logged out!")
    return redirect("/")
