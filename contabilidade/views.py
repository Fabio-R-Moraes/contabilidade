from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def contas(request):
    return render(request, 'contas.html')

def notas(request):
    return render(request, 'notas.html')
