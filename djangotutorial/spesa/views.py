from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Spesa, Categoria
from .utils import calcola_debito
from .forms import SpesaForm
from datetime import datetime
from django.contrib import messages
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
import math, telegram

def lista_spese(request):
    # Filtro per spese saldate
    filtro_saldate = request.GET.get('saldate')
    spese = Spesa.objects.all()
    if filtro_saldate == 'si':
        spese = spese.filter(saldata=True)
    elif filtro_saldate == 'no':
        spese = spese.filter(saldata=False)

    # Ottieni i nomi degli owner distinti
    owners = Spesa.objects.values_list('owner', flat=True).distinct()

    # Verifica che ci siano esattamente due owner
    if len(owners) != 2:
        messages.error(request, "Devono esserci esattamente due proprietari per calcolare il debito.")
        return render(request, 'spesa/lista_spese.html', {'spese': spese, 'filtro_corrente': filtro_saldate})

    # Assegna i nomi degli owner
    owner1 = owners[0]
    owner2 = owners[1]

    # Calcola le spese per ogni owner NON SALDATE
    spese_owner1 = spese.filter(owner=owner1, saldata=False).aggregate(Sum('spesa'))['spesa__sum'] or 0
    spese_owner2 = spese.filter(owner=owner2, saldata=False).aggregate(Sum('spesa'))['spesa__sum'] or 0

    # Calcola il debito (owner2 - owner1) / 2
    debito = (spese_owner2 - spese_owner1) / 2
    debito_assoluto = math.fabs(debito) 

    if request.method == 'POST':
        spesa_id = request.POST.get('spesa_id')
        spesa = get_object_or_404(Spesa, pk=spesa_id)
        spesa.saldata = True
        spesa.save()
        messages.success(request, 'Spesa saldata con successo.')
        return redirect('spesa:lista_spese')

    return render(request, 'spesa/lista_spese.html', {
        'spese': spese,
        'debito': debito,
        'debito_assoluto': debito_assoluto,
        'filtro_corrente': filtro_saldate,
        'owner1': owner1,
        'owner2': owner2,
    })

def nuova_spesa(request):
    if request.method == 'POST':
        form = SpesaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Spesa creata con successo.') # Messaggio di successo
            return redirect('spesa:lista_spese')
        else:
            messages.error(request, 'Errore nella creazione della spesa. Controlla i dati.')
    else:
        form = SpesaForm()
    return render(request, 'spesa/nuova_spesa.html', {'form': form})

def modifica_spesa(request, pk):
    spesa = get_object_or_404(Spesa, pk=pk)
    if request.method == 'POST':
        form = SpesaForm(request.POST, instance=spesa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Spesa modificata con successo.') # Messaggio di successo
            return redirect('spesa:lista_spese')
        else:
            messages.error(request, 'Errore nella modifica della spesa. Controlla i dati.')
    else:
        form = SpesaForm(instance=spesa)
    return render(request, 'spesa/modifica_spesa.html', {'form': form, 'spesa': spesa})

def elimina_spesa(request, pk):
    spesa = get_object_or_404(Spesa, pk=pk)
    if request.method == 'POST':
        spesa.delete()
        messages.success(request, 'Spesa eliminata con successo.') # Messaggio di successo
        return redirect('spesa:lista_spese')
    return render(request, 'spesa/elimina_spesa.html', {'spesa': spesa})


BOT_TOKEN = "7263693607:AAE5IgZ2Y-0Lz_k7cZ0cjImFhqm3ePtTGwU" #Ottieni il token dalla variabile d'ambiente
bot = telegram.Bot(token=BOT_TOKEN)

@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        try:
            update = telegram.Update.de_json(request.body.decode('utf-8'), bot)
            chat_id = update.effective_chat.id
            message_text = update.message.text

            if message_text.startswith("/salda"):
                try:
                    parts = message_text.split(" ")
                    if len(parts) != 2:
                        raise ValueError("Uso: /salda <ID_SPESA>")
                    id_spesa = int(parts[1])
                    spesa = Spesa.objects.get(pk=id_spesa)
                    spesa.saldata = True
                    spesa.save()
                    bot.sendMessage(chat_id=chat_id, text=f"Spesa con ID {id_spesa} saldata.")
                except (ValueError, IndexError):
                    bot.sendMessage(chat_id=chat_id, text="Uso: /salda <ID_SPESA>")
                except Spesa.DoesNotExist:
                    bot.sendMessage(chat_id=chat_id, text="Spesa non trovata.")
                return HttpResponse("OK")
            elif message_text.startswith("/start"):
                bot.sendMessage(chat_id=chat_id, text="Ciao! Invia un messaggio nel formato: Proprietario,Spesa,Data[,Categoria1,Categoria2,...]. Usa /salda <id> per saldare una spesa")
                return HttpResponse("OK")

            parts = message_text.split(',')
            if len(parts) < 3:
                raise ValueError("Numero di argomenti insufficienti. Usa: Proprietario,Spesa,Data[,Categoria1,Categoria2,...]")

            owner = parts[0].strip()
            spesa_amount = float(parts[1].strip())
            data_str = parts[2].strip()
            data = datetime.strptime(data_str, '%Y-%m-%d').date()
            categorie_nomi = [cat.strip() for cat in parts[3:]]
            categorie = []
            for nome in categorie_nomi:
                try:
                    categoria = Categoria.objects.get(nome=nome)
                    categorie.append(categoria)
                except Categoria.DoesNotExist:
                    bot.sendMessage(chat_id=chat_id, text=f"Categoria '{nome}' non trovata.")
                    return HttpResponse("OK")

            nuova_spesa = Spesa(owner=owner, spesa=spesa_amount, data=data)
            nuova_spesa.save()
            nuova_spesa.categorie.set(categorie)

            messaggio_debito = calcola_debito(owner)
            bot.sendMessage(chat_id=chat_id, text=f"Spesa aggiunta con successo! ID: {nuova_spesa.id}\n{messaggio_debito}")

        except ValueError as e:
            bot.sendMessage(chat_id=chat_id, text=f"Formato del messaggio non valido: {e}. Usa: Proprietario,Spesa,Data[,Categoria1,Categoria2,...] (Data in formato AAAA-MM-GG)")
        except Exception as e:
            logger.error(f"Errore durante l'elaborazione del webhook: {e}")
            bot.sendMessage(chat_id=chat_id, text=f"Errore durante l'elaborazione: {e}")
        return HttpResponse("OK")
    return HttpResponse("GET requests are not allowed.")