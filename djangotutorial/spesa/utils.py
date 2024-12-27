from .models import Spesa

def calcola_debito(owner_richiedente):
    spese = Spesa.objects.filter(saldata=False) # Filtra solo le spese non saldate
    debiti = {}

    for spesa in spese:
        if spesa.owner not in debiti:
            debiti[spesa.owner] = 0
        debiti[spesa.owner] += spesa.spesa

    debito_totale = 0
    debitore = None
    creditore = None
    
    #Gestione del caso in cui l'utente non abbia debiti con nessuno
    if owner_richiedente not in debiti:
        return "Nessun debito."

    for persona, importo in debiti.items():
        if persona != owner_richiedente:
            if persona not in debiti:
                debiti[persona] = 0
            differenza = debiti[owner_richiedente] - importo
            if differenza > 0:
                debito_totale = differenza
                debitore = persona
                creditore = owner_richiedente
            elif differenza < 0:
                debito_totale = abs(differenza)
                debitore = owner_richiedente
                creditore = persona
            break #considera solo la prima persona diversa dall'owner richiedente. Da rivedere se si vuole gestire il debito con più persone.

    if debito_totale == 0:
        return "Nessun debito."
    else:
        return f"{debitore} deve {debito_totale} a {creditore}."