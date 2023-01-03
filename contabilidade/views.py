from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Nota, Equipe
from datetime import date

diaHoje = date.today()

class indexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(indexView, self).get_context_data(**kwargs)
        context['NotasHoje'] = Nota.objects.filter(dataNota=diaHoje)
        context['Equipe'] = Equipe.objects.all()
        return context

def contas(request):
    return render(request, 'contas.html')

def notas(request):
    return render(request, 'notas.html')
