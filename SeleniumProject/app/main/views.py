import threading
import time
import schedule

from django.shortcuts import render
from django.http import JsonResponse
from .models import Tenders, Keywords
from .tender_data import update_data

from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings

def prikazi_tendere(request):
    tenders = Tenders.objects.all()
    # schedule.every(2).minutes.do(update_data)
    # #
    # # # Definirajte funkciju za pokretanje rasporeda u pozadini
    # def run_schedule():
    #     while True:
    #         schedule.run_pending()
    #         time.sleep(1)
    # #
    # # # Pokrenite raspored u pozadini koristeći threading
    # schedule_thread = threading.Thread(target=run_schedule)
    # schedule_thread.start()
    update_data()

    return render(request, 'index.html', {'tenders': tenders})

def update_keywords(request):
    if request.method == 'POST':
        keywords = request.POST.get('keywords')
        Keywords.objects.create(kljucne_rijeci=keywords)
        return JsonResponse({'message': 'Rijeci su uspjesno dodate!'})
    return render(request, 'index.html')

# def pretraga_i_spremanje_tendera(request):
#     update_data()
#     return JsonResponse({'message': 'Tenderi su uspješno pretraženi i dodani u bazu!'})


