from beautifultable import BeautifulTable
from pyvis.network import Network

def charger_tableau_contraintes(nom_fichier):
    '''
    Cette fonction a pour but de contruire le tableau de contraintes en lisant le fichier txt
    entrée nom_fichier : nom du fichier txt (str)
    sortie tableau_contraintes : tableau de contraintes (dict)
    '''
    #Initiliser le tableau de contraintes
    tableau_contraintes = {}

    # Lecture du fichier pour charger les contraintes
    with open(nom_fichier, 'r') as fichier:
        for ligne in fichier:
            valeurs = ligne.split()
            sommet = valeurs[0]
            poids = int(valeurs[1])
            predecesseurs = valeurs[2:]
            tableau_contraintes[sommet] = {"Poids": poids, "predecesseurs": predecesseurs, "successeurs": []}

    # Ajout des successeurs pour chaque sommet
    for sommet, info in tableau_contraintes.items():
        for autre_sommet, autre_info in tableau_contraintes.items():
            if sommet in autre_info["predecesseurs"]:
                info["successeurs"].append(autre_sommet)

    # Ajout de la tâche fictive alpha (0) avec des prédecesseurs vides et des successeurs tous les sommets (du tableau sans predecesseurs [2::]=0) sauf 0
    tableau_contraintes["0"] = {"Poids": 0, "predecesseurs": [], "successeurs": [sommet for sommet in tableau_contraintes if tableau_contraintes[sommet]['predecesseurs'] == []]}

    # Ajout de la tâche fictive omega (dernier_sommet) avec des prédécesseurs tous les sommets sans successeurs
    dernier_sommet = str(len(tableau_contraintes))
    tableau_contraintes[dernier_sommet] = {"Poids": 0,
                                           "predecesseurs": [sommet for sommet, info in tableau_contraintes.items() if
                                                            not(info["successeurs"])], "successeurs": []}

    # Maintenant tout les sommets qui n'ont pas de predecesseurs ont pour predecesseur alpha(premier sommet)
    for element in tableau_contraintes['0']['successeurs']:
        tableau_contraintes[element]['predecesseurs'].append('0')

    # Maintenant tout les sommets qui n'ont pas de successeurs ont pour successeur omega(dernier sommet)
    for element in tableau_contraintes[dernier_sommet]['predecesseurs']:
        tableau_contraintes[element]['successeurs'].append(dernier_sommet)

    return tableau_contraintes


def build_tableau_contraintes(tableau_contraintes):
    '''
    Cette fonction a pour but de construire le tableau de contraintes visuellement et lister tous les arcs
    entrée tableau_contraintes : tableau de contraintes (dict)
    sortie tableau : tableau de contraintes (BeatifulTable)
    sortie step : liste d'arcs (liste)
    '''
    # Initialiser step
    step = []
    # Initialiser tableau
    tableau = BeautifulTable()
    # Initialiser les titre des colonnes
    tableau.columns.header = ["Tache", "Duree", "Contraintes"]
    for sommet in tableau_contraintes:
        # Remplir le tableau
        tableau.rows.append([sommet,tableau_contraintes[sommet]['Poids'],tableau_contraintes[sommet]['predecesseurs']])
        # Stocker les arcs dans step
        if tableau_contraintes[sommet]['successeurs'] != []:
            for successor in tableau_contraintes[sommet]['successeurs']:
                step.append(sommet + " -> " + successor + " = " + str(tableau_contraintes[sommet]['Poids']))
    return tableau, step

def build_matrice_valeurs(tableau_contraintes) :
    '''
    Cette fonction a pour but de construire la matrice des valeurs visuellement
    entrée tableau_contraintes : tableau de contraintes (dict)
    sortie matrice_valeurs : matrice des valeurs (visuel)
    '''
    # Initialiser la matrice des valeurs
    matrice_valeurs = BeautifulTable()
    # Remplir la matrice des valeurs
    for sommet_1 in tableau_contraintes:
        cpt = []
        for sommet_2 in tableau_contraintes:
            if sommet_2 in tableau_contraintes[sommet_1]["successeurs"]:
                cpt.append(tableau_contraintes[sommet_1]["Poids"])
            else :
                cpt.append("*")
        matrice_valeurs.rows.append(cpt)
    # Mettre en titre de colonnes tous les sommets
    matrice_valeurs.columns.header = [sommet for sommet in tableau_contraintes]
    # Mettre en titre de lignes tous les sommets
    matrice_valeurs.rows.header = [sommet for sommet in tableau_contraintes]
    return matrice_valeurs


def build_graph(tableau_contraintes) :
    '''
    Cette fonction a pour but de construire visuellement le graphe en prenant en compte les points critiques (l'automate)
    entrée tableau_contraintes : tableau de contraintes (dict)
    sortie : graph.html (html)
    '''
    # Initialiser le graphe
    net = Network(directed=True)
    # Création des nodes c'est-à-dire les sommets
    for sommet in tableau_contraintes:
        if tableau_contraintes[sommet]['critical'] : #sommet rouge si c'est critique
            net.add_node(sommet, label=sommet, color='red')
        else :
            net.add_node(sommet, label=sommet) #sinon normal
    # Création des liens entres les sommets
    for sommet_1 in tableau_contraintes:
        if tableau_contraintes[sommet_1]['successeurs'] != []:
            for successeur in tableau_contraintes[sommet_1]['successeurs'] :
                net.add_edge(sommet_1,successeur)
    # Afficher le graphe dans graph.html
    net.show("E5_graph.html", notebook=False)
    return

def build_graph_circuit(tableau_contraintes) :
    '''
    Cette fonction a pour but de construire visuellement le graphe sans prenant en compte les points critiques (l'automate)
    entrée tableau_contraintes : tableau de contraintes (dict)
    sortie : graph.html (html)
    '''
    # Initialiser le graphe
    net = Network(directed=True)
    # Création des nodes c'est-à-dire les sommets
    for sommet in tableau_contraintes:
        net.add_node(sommet, label=sommet) #sinon normal
    # Création des liens entres les sommets
    for sommet_1 in tableau_contraintes:
        if tableau_contraintes[sommet_1]['successeurs'] != []:
            for successeur in tableau_contraintes[sommet_1]['successeurs'] :
                net.add_edge(sommet_1,successeur)
    # Afficher le graphe dans graph.html
    net.show("E5_graph.html", notebook=False)
    return


def calculer_rangs(tableau_contraintes, f):
    '''
    Cette fonction a pour but de tous les rangs de chaque sommet
    entrée tableau_contraintes : tableau de contraintes (dict)
    sortie rangs : rangs des sommets (dict)
    '''
    #Initialisation des rangs
    rangs = {}
    for sommet in tableau_contraintes:
        rangs[sommet] = None  # Initialisation des rangs à None

    # Calcule du rang de chaque sommet
    for sommet in tableau_contraintes:
        f.write("Parcourir le sommet : "+ str(sommet) + "\n")
        calculer_rang(tableau_contraintes, rangs, sommet, f)

    return rangs


def calculer_rang(tableau_contraintes, rangs, sommet, f, visited=None, stack=None):
    '''
    Cette fonction a pour but de tous les rangs de chaque sommet
    entrée tableau_contraintes : tableau de contraintes (dict)
    entrée rangs : les rangs des sommets (dict)
    entrée sommet : sommet qu'on veut connaitre le rang (str)
    sortie rangs[sommet] : sommet et son rang (element du dict rangs)
    '''
    f.write("-> "+ str(sommet)+"\n")
    if visited is None:
        visited = set()
    if stack is None:
        stack = set()

    if sommet in stack:
        raise ValueError("Le graphe contient un circuit.")

    if sommet in visited:
        return rangs[sommet]  # Retourner le rang du sommet s'il a déjà été visité

    visited.add(sommet)
    stack.add(sommet) #ajoutation de sommet dans pile


    if rangs[sommet] is not None:
        stack.remove(sommet)  # Retirer le sommet de la pile s'il a déjà été traité
        return rangs[sommet]

    if sommet == "0":
        rangs[sommet] = 0
    elif sommet == str(len(tableau_contraintes) - 1):
        rang_max_predecesseurs = max(
            rangs[predecesseur] for predecesseur in tableau_contraintes[sommet]["predecesseurs"])
        rangs[sommet] = rang_max_predecesseurs + 1
    else:
        rang_max_predecesseurs = 0
        for predecesseur in tableau_contraintes[sommet]["predecesseurs"]:
            calculer_rang(tableau_contraintes, rangs, predecesseur, f, visited, stack)
            rang_max_predecesseurs = max(rang_max_predecesseurs, rangs[predecesseur])
        rangs[sommet] = rang_max_predecesseurs + 1
    stack.remove(sommet)  # Retirer le sommet de la pile après le traitement
    return rangs[sommet]


def calculer_dates_plus_tot(tableau_contraintes, rangs):
    '''
    Cette fonction a pour but de calculer les dates aux plus tot
    entrée tableau_contraintes : tableau de contraintes (dict)
    entrée rangs : ...... ()
    sortie dates_plus_tot : les dates aux plus tot (dict)
    '''
    dates_plus_tot = {}

    # Parcours du graphe dans l'ordre topologique (par rang)
    for sommet in sorted(tableau_contraintes.keys(), key=lambda x: rangs[x]):
        if sommet == "0":
            dates_plus_tot[sommet] = 0
        else:
            predecesseurs = tableau_contraintes[sommet]["predecesseurs"]
            if predecesseurs:
                # Calcul de la date au plus tôt pour le sommet
                date_max_predecesseurs = max(
                    dates_plus_tot[predecesseur] + tableau_contraintes[predecesseur]["Poids"] for predecesseur in
                    predecesseurs
                )
                dates_plus_tot[sommet] = date_max_predecesseurs
            else:
                # Si le sommet n'a pas de prédecesseur, sa date au plus tôt est 0
                dates_plus_tot[sommet] = 0

    return dates_plus_tot



def calculer_dates_plus_tard(tableau_contraintes, rangs, dates_plus_tot):
    '''
    Cette fonction a pour but de calculer les dates aux plus tard
    entrée tableau_contraintes : tableau de contraintes (dict)
    entrée rangs : ...... ()
    entrée dates_plus_tot : les dates aux plus tot (dict)
    sortie dates_plus_tard : les dates aux plus tard (dict)
    '''
    dates_plus_tard = {}

    # Parcours du graphe dans l'ordre inverse (par rang décroissant)
    for sommet in sorted(tableau_contraintes.keys(), key=lambda x: -rangs[x]):
        if sommet == str(len(tableau_contraintes) - 1):
            dates_plus_tard[sommet] = dates_plus_tot[sommet]
        else:
            successeurs = tableau_contraintes[sommet]["successeurs"]
            if successeurs:
                # Calcul de la date au plus tard pour le sommet
                date_min_successeurs = min(
                    dates_plus_tard[successeur] - tableau_contraintes[sommet]["Poids"] for successeur in successeurs
                )
                dates_plus_tard[sommet] = date_min_successeurs
            else:
                # Si le sommet n'a pas de successeur, sa date au plus tard est égale à sa date au plus tôt
                dates_plus_tard[sommet] = dates_plus_tot[sommet]

    return dates_plus_tard



def tableau_contraintes_complet(tableau_contraintes, rangs):
    '''
    Cette fonction a pour but de construire un tableau de contraintes complet c'est en rajoutant es,ls,float,etc...
    entrée tableau_contraintes : tableau de contraintes (dict)
    sortie data : tableau de contraintes complets (dict)
    sortie table : tableau de contraintes complets (visuel)
    '''
    # Calcul des dates plus tot
    dates_plus_tot = calculer_dates_plus_tot(tableau_contraintes,rangs)
    # Calcul des dates plus tard
    dates_plus_tard = calculer_dates_plus_tard(tableau_contraintes, rangs, dates_plus_tot)
    # Inialiser le tableau de contraintes complets en copiant le tableau de contraintes de base
    data = tableau_contraintes
    # Parcourir tous les sommets, et ajouter leur dates aux plus tot, plus tard, float et indiquer si c'est un point critique
    for sommet in data:
        data[sommet]['es'] = dates_plus_tot[sommet]
        data[sommet]['ls'] = dates_plus_tard[sommet]
        data[sommet]['float'] = dates_plus_tard[sommet] - dates_plus_tot[sommet]
        if data[sommet]['float'] == 0:
            data[sommet]['critical'] = True
        else :
            data[sommet]['critical'] = False
    # Initialiser un tableau visuel
    table = BeautifulTable()
    # Initialiser les titres des colonnes
    table.columns.header = ["Rang", "Sommet", "Poids", "ES", "LS", "Float", "Critical"]
    # Remplir les données corespondantes
    for sommet in sorted(tableau_contraintes.keys(), key=lambda x: rangs[x]):
        info = tableau_contraintes[sommet]
        table.rows.append([rangs[sommet],sommet,info['Poids'],data[sommet]['es'],data[sommet]['ls'],data[sommet]['float'],str(data[sommet]['critical'])])
    return data, table

def trouver_chemins_critiques_possibles(tableau_contraintes):
    '''
    Cette fonction a pour but de trouver les chemins partant de alpha jusqu'à omega passant par les points critiques
    entrée tableau_contraintes : tableau de contraintes complet (dict)
    sortie chemins_critiques : liste de tous les chemins partant de alpha jusqu'à omega passant par les points critiques (liste)
    '''
    chemins_critiques = []

    def parcourir_chemin(sommet_actuel, chemin_actuel):
        chemin_actuel.append(sommet_actuel)
        if sommet_actuel == str(len(tableau_contraintes) - 1):  # Vérifie si nous avons atteint le dernier sommet
            if chemin_critique(chemin_actuel):
                chemins_critiques.append(chemin_actuel.copy())
        else:
            for successeur in tableau_contraintes[sommet_actuel]["successeurs"]:
                parcourir_chemin(successeur, chemin_actuel)
        chemin_actuel.pop()

    def chemin_critique(chemin):
        for sommet in chemin:
            if tableau_contraintes[sommet]["float"] != 0:
                return False
        return True

    # Commencer à parcourir à partir du premier sommet (sommet "0")
    parcourir_chemin("0", [])

    return chemins_critiques

def check_arc_negatif(tableau_contraintes):
    '''
    Cette fonction a pour but de détecter si il y a un arc négatif
    entrée tableau_contraintes : tableau de contraintes complet (dict)
    sortie status : True si il y a sinon False (bool)
    '''
    # Initialiser status false par défaut
    status = False
    # Parcourir dans tous les sommets
    for sommet in tableau_contraintes:
        # Vérifie le sommet a un poids négatif
        if tableau_contraintes[sommet]['Poids'] < 0:
            # Si c'est le cas, status est True et on terminer la vérification
            status = True
            return status
    return status

def chemins_critiques(data,f):
    '''
    Cette fonction a pour but de trouver tous les points critques
    entrée tableau_contraintes : tableau de contraintes complet (dict)
    sortie chemins_critiques : liste de tous les chemins partant de alpha jusqu'à omega passant par les points critiques (liste)
    '''
    # Initialiser duree = duree du chemin critique = 'es' du sommet omega
    duree = data[str(len(data)-1)]['es']
    # Initialiser chemins = liste de tous les chemins partant de alpha jusqu'à omega passant par les points critiques
    chemins = trouver_chemins_critiques_possibles(data)
    # Initialiser remove, une liste qui stock l'indice de tous les chemins qui ne sont pas critiques dans chemins
    remove = []
    # Parcourir tous les chemin dans chemins
    for chemin in chemins:
        # Calculer la duree de chaque chemin
        cpt = 0
        for sommet in chemin:
            cpt += data[sommet]['Poids']
        # Si sa duree n'est pas égale à la duree du chemin critique
        if cpt != duree:
            # On rajouter l'indice du chemin dans remove
            remove.append(chemin)
    # Dans chemins, on enlève tous les chemins qui de sont pas critiques
    remove.sort(reverse=True)
    for element in remove:
        chemins.remove(element)
    # Formatter l'affichage
    for chemin in chemins:
        f.write("\n")
        f.write(" -> ".join(chemin))
    return



def trace_execution():
    '''
    Cette fonction a pour but de generer les traces de tous les tables
    entrée : vide
    sortie : les traces d'exécutions de tous les tables dans le dossier E5_trace
    '''
    # Parcourir tous les tables
    for i in range(1,15):
        # Création du fichier
        f = open("E5_trace/E5_trace_table "+str(i)+".txt", "w")
        # Charger les tableaux de contraintes corespondant aux tables
        nom_fichier = 'E5_tables/E5_table '+ str(i) + '.txt'
        tableau_contraintes = charger_tableau_contraintes(nom_fichier)
        tableau, step = build_tableau_contraintes(tableau_contraintes)
        f.write('\nTable '+ str(i) + " :\n")
        f.write(str(tableau)+'\n')
        f.write("* Creation du graphe d'ordonnancement\n")
        f.write("Nombre de sommets : "+str(len(tableau_contraintes))+"\n")
        f.write("Nombre d'arcs' : "+str(len(step))+"\n")
        for arc in step:
            f.write(arc+'\n')
        f.write("* Creation du matrice des valeurs\n")
        f.write(str(build_matrice_valeurs(tableau_contraintes))+'\n')
        f.write("* Detection d'arc negatif\n")
        # Détection d'arc négatif
        if check_arc_negatif(tableau_contraintes) is True:
            f.write("=> Il possede d'arcs negatifs\n")
        else :
            f.write("=> Il ne possede pas d'arcs negatifs\n")
            f.write("* Detection de circuit - Parcours en prodondeur\n")
            # Détection de circuit
            try: # Essaye de construire le tableau de contraintes complets et trouver le chemin critique
                rangs = calculer_rangs(tableau_contraintes,f)
                if rangs:
                    data, table = tableau_contraintes_complet(tableau_contraintes, rangs)
                    f.write("\n=> Il n'y a pas de circuit\n")
                    f.write("* Calendrier complet\n")
                    f.write(str(table)+"\n")
                    f.write("* Les chemins critiques\n")
                    chemins_critiques(data,f)
            except ValueError as e: # Si il y a de circuit on renvoie un message error
                f.write("=> Il se peut que le graphe fourni dans le tableau de contrainte possede un circuit.")


# Main
mode = int(input("Entrez 1 pour tester une table\nEntrez 2 pour tester tous les tables\nVotre choix : "))
while mode != 1 and mode !=2:
    mode = int(input("Entrez 1 pour tester une table\nEntrez 2 pour tester tous les tables\nVotre choix : "))
if (mode == 2):
    trace_execution()
    print("Tous les traces des tables se trouvent dans le dossier E5_trace")
else :
    i = int(input("Quelle table voulez-vous tester : "))
    while i<1 or i>14:
        i = int(input("Quelle table voulez-vous tester : "))
    nom_fichier = 'E5_tables/E5_table '+ str(i) + '.txt'
    f = open("E5_trace unique.txt", "w")
    tableau_contraintes = charger_tableau_contraintes(nom_fichier)
    tableau, step = build_tableau_contraintes(tableau_contraintes)
    f.write('\nTable '+ str(i) + " :\n")
    f.write(str(tableau)+'\n')
    f.write("* Creation du graphe d'ordonnancement\n")
    f.write("Nombre de sommets : "+str(len(tableau_contraintes))+"\n")
    f.write("Nombre d'arcs' : "+str(len(step))+"\n")
    for arc in step:
        f.write(arc+'\n')
    f.write("* Creation du matrice des valeurs\n")
    f.write(str(build_matrice_valeurs(tableau_contraintes))+'\n')
    f.write("* Detection d'arc negatif\n")
    # Détection d'arc négatif
    if check_arc_negatif(tableau_contraintes) is True:
        f.write("=> Il possede d'arcs negatifs\n")
    else :
        f.write("=> Il ne possede pas d'arcs negatifs\n")
        f.write("* Detection de circuit - Parcours en prodondeur\n")
        # Dectection de circuit
        try: # Essaye de construire le tableau de contraintes complets et trouver le chemin critique
            rangs = calculer_rangs(tableau_contraintes,f)
            if rangs:
                data, table = tableau_contraintes_complet(tableau_contraintes, rangs)
                f.write("\n=> Il n'y a pas de circuit\n")
                f.write("* Calendrier complet\n")
                f.write(str(table)+"\n")
                f.write("* Les chemins critiques\n")
                chemins_critiques(data,f)
                build_graph(tableau_contraintes)
        except ValueError as e: # Si il y a de circuit on renvoie un message error
            f.write("=> Il se peut que le graphe fourni dans le tableau de contrainte possede un circuit.")
            build_graph_circuit(tableau_contraintes)
        print("Vous pouvez voir\n - le graphe visuellement depuis le fichier E5_graph.html\n - les traces d'exécution dans le fichier E5_ trace unique.txt")

































