from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from . import util
from random import choice
import markdown2


class SearchForm(forms.Form):
    q = forms.CharField()

def validate_title(title):
        if title in util.list_entries():
            raise ValidationError("ERROR: This entry already exists.")
        return title

class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title", validators=[validate_title])
    content = forms.CharField(widget=forms.Textarea, label="Content")

class EditButtonForm(forms.Form):
    t = forms.CharField()

class EditEntryForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea, label="Content")

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, TITLE):
    content = util.get_entry(TITLE)
    if content:
        content = markdown2.markdown(content)
        return render(request, "entry.html", {
            "content": content, # Must pass as {{content|safe}} lest markdown2 escape raw html chars
            "TITLE": TITLE
        })
    else:
        return render(request, "not-found.html")

def search(request):
    matches = []
    form = SearchForm(request.GET)
    if form.is_valid():
        q = form.cleaned_data["q"]
        for entry in util.list_entries():
            if entry == q:
                return HttpResponseRedirect(q)
            elif q in entry:
                matches.append(entry)
    return render(request, "search.html", {
        "matches": matches
        })

def create(request):
    form = NewEntryForm()
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = f"#{title}\n{form.cleaned_data['content']}"
            util.save_entry(title, content)
            return HttpResponseRedirect(title)
    return render(request, "create.html", {
        "form": form
        })

def edit(request):
    if request.method == "GET":
        form = EditButtonForm(request.GET)
        if form.is_valid():
            title = form.cleaned_data["t"]
            content = util.get_entry(title)
            edit_form = EditEntryForm(initial={'title': title, 'content': content})
        return render(request, "edit.html", {
            "form": edit_form
            })
    else:
        form = EditEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = bytes(form.cleaned_data["content"], 'utf8') # bytes( ... , 'utf8') avoids extra '\n'
            util.save_entry(title, content)
            return HttpResponseRedirect(title)

def random(request):
    entries = util.list_entries()
    return HttpResponseRedirect(choice(entries))