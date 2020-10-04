#!/usr/bin/env python3
# Copyright of Lizzy Trickster (Lizzy Green)

from django.shortcuts import render, redirect
from django.db.utils import IntegrityError
from django.contrib import messages
from django.contrib.auth import logout
from django.views import View

from .ext import UserInputError
from .models import Birthday
import datetime


def landing_page(request):
    return render(request, "landing.html")


def today(request):
    current_date = datetime.datetime.utcnow().strftime("%d%m")
    peoples = Birthday.objects.filter(birthday__exact=current_date)
    return render(request, "birthday/today.html", context=dict(users=peoples))


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
        uname = request.POST['uname']
        day = int(request.POST['bday'])
        month = int(request.POST['bmon'])
        error_msg = f"Invalid day ({day}) specified for month {month}. Your response has not been recorded."
        entry: Birthday = None
        if request.user.is_authenticated:
            try:
                if month in [4, 6, 9, 11] and day > 30:
                    raise UserInputError
                elif month == 2 and day > 29:
                    raise UserInputError

                entry = Birthday.objects.create(user=request.user, display_name=uname, birthday=f"{day:02}{month:02}")
            except IntegrityError:
                messages.add_message(request, messages.ERROR, "Duplicate entry exists!?")
            except UserInputError:
                messages.error(request, error_msg)
            except:
                raise
            else:
                messages.add_message(request, messages.SUCCESS, "Entry successfully recorded!")

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


def logout_view(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS, "Successfully logged out!")
    return redirect("/")
