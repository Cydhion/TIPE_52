from TIPE52 import *
import csv
import fileinput
import re # Utile pour recuper les créatures
import ctypes # Utile pour recuper les créatures
import gc # Utile pour recuper les créatures
import copy

#INITIALISATION
nb_lignes = 10
'''
def initialisation():
	donnees = []
	for _ in range(nb_lignes):
		creature = random_create_creature()
		donnees.append({
			#'joints': creature.creature_get_joints(),
			#'bones': creature.creature_get_bones(),
			#'muscle': creature.creature_get_muscles(),
			'score': 0.,
			'creature': creature
		}) 

	# Nom du fichier de sortie
	nom_fichier = "donnees.tsv"

	# Écriture du fichier TSV (séparé par des tabulations)
	with open(nom_fichier, mode='w', newline='', encoding='utf-8') as fichier:
		# On extrait les noms de colonnes du premier dictionnaire
		champs = donnees[0].keys()
		
		writer = csv.DictWriter(
			fichier,
			fieldnames=champs,
			delimiter='\t',  # Séparateur = tabulation
			quoting=csv.QUOTE_MINIMAL  # Évite les guillemets inutiles
		)
		
		writer.writeheader()
		writer.writerows(donnees)

	print(f"Fichier '{nom_fichier}' généré avec {len(donnees)} lignes aléatoires.")
'''
donnees = [] # Comme Union Find
scores = []
def initialisation():
	for _ in range(nb_lignes):
		creature = random_create_creature()
		donnees.append(creature) 
		scores.append(0.)

#SELECTION
T = 3*FPS # FPS de test 
T0 = FPS
D0 = ONE_METER_REF
E0 = 1                                           # A revoir car mauvaise unité
C0 = 1e5 # 1Bar

"""
def get_creature_from_address(address_str):
	# Tente de récupérer un objet à partir de son adresse mémoire
	try:
		# Extraction de l'adresse hexadécimale de la chaîne
		addr_str = address_str.split()[-1].strip('>')
		# Convertit l'adresse hexadécimale en entier
		address = int(addr_str, 16)
		# Utilise ctypes pour accéder à la mémoire
		return ctypes.cast(address, ctypes.py_object).value
	except (ValueError, TypeError, ctypes.ArgumentError) as e:
		print(f"Error in get_creature_from_address: {e}")
		return None
"""
"""
def load_creatures_from_tsv(filepath):
	creatures = []
	with open(filepath, 'r', newline='') as f:
		reader = csv.reader(f, delimiter='\t')
		next(reader)  # Skip header (si présent)
		for row in reader:
			score, creature_repr = row
            # Extraction de l'adresse mémoire (juste pour info)
			mem_address = creature_repr.split("at ")[1].strip(">")
			print(f"Chargement Creature @ {mem_address} avec score {score}")
            
            # Si les objets sont toujours en mémoire, vous pourriez les récupérer
            # Mais ce n'est généralement pas recommandé ni fiable
            # creatures.append(eval(creature_repr))  # DANGEREUX !
	return creatures
"""
"""
def get_creatures():
	nom_fichier = "donnees.tsv"
	creatures = []
	with open(nom_fichier, "r") as f:
		next(f)  # Saute la première ligne (en-tête)
		for ligne in f:
			cols = ligne.strip().split("\t")
			if len(cols) < 2:
				continue
			creature = get_creature_from_address(cols[1])
			if creature:
				creatures.append(creature)
	return creatures
"""
def score_val(creature,i): # Voir diapo : 1 Acc, 2 Eff, 3 End, 4 Ca
	D = creature.score_update()
	E = creature.score_energy
	C = creature.stress
	if i == 1:
		return D*T0/(D0*T)

	elif i == 2:		
		return D*E0/(D0*E)

	elif i == 3:
		return D*T0*E0/(D0*T*E)

	elif i == 4:
		return D*C0/(D0*C)

	else:
		print("Erreur dans score_val")
"""
def score_cal(i):
	nom_fichier = "donnees.tsv"
	creatures = get_creatures()
	main_ml(creatures,T*T0) # On fait jouer les creatures sur 15s

	# Nouveaux scores
	new_scores = []
	for creature in creatures:
		new_scores.append(score_val(creature, i))

	# Modification directe du fichier
	with fileinput.input(nom_fichier, inplace=True) as f:
		for i, line in enumerate(f):
			cols = line.strip().split('\t')
			cols[0] = str(new_scores[i])  # Remplace la 1ère colonne
			print('\t'.join(cols))
"""
def score_cal(i):
	creatures = donnees
	main_ml_show(creatures,T/T0) # On fait jouer les creatures sur T secondes

	# Nouveaux scores
	length = len(donnees)
	for j in range(len(donnees)):
		scores[j] = score_val(donnees[j], i)
"""
def trier_tsv_par_score(nom_fichier):
	# Lire le fichier
	with open(nom_fichier, 'r') as f:
		lignes = f.readlines()
	
	# Extraire l'en-tête et les données
	en_tete = lignes[0].strip()
	donnees = [ligne.strip().split('\t') for ligne in lignes[1:]]
	
	# Trier les données par score décroissant (convertir en float pour le tri numérique)
	donnees_triees = sorted(donnees, key=lambda x: float(x[0]), reverse=True)
	
	# Réécrire le fichier
	with open(nom_fichier, 'w') as f:
		f.write(en_tete + '\n')
		for ligne in donnees_triees:
			f.write('\t'.join(ligne) + '\n')
"""

def trier_par_score():
	global donnees, scores
    
    # Fusionne les deux listes en tuples (donnees, scores)
	combined = list(zip(donnees, scores))
    
    # Trie selon les scores (élément [1] du tuple), décroissant
	combined.sort(key=lambda x: x[1], reverse=True)
    
    # Sépare les listes triées
	donnees_triees = [item for item, _ in combined]
	scores_tries = [score for _, score in combined]

	donnees = donnees_triees
	scores = scores_tries


def selection(i):
	score_cal(i)
	trier_par_score()

#REPRODUCTION
"""
def duplicate(nom_fichier): # Créer un nouveau fichier ave
	global donnees
	global scores
	moitie = len(donnees) // 2
	premiere_partie = donnees[:moitie]
    
    # Deep copy de la première moitié
	copie_premiere_partie = copy.deepcopy(premiere_partie)
    
    # Remplacement de la seconde moitié
	donnees[moitie:] = copie_premiere_partie
"""
def duplicate():
	global donnees
	moitie = len(donnees)//2
	premiere_partie = donnees[:moitie]
	
	copie_profonde = copy.deepcopy(premiere_partie)
	
	donnees[moitie:] = copie_profonde

#MUTATION
PROBA_VALEUR = 0.8
PROBA_ADD = 0.5
PROBA_RM = 0.3
def mutate_val(creature):	# Changement des valeurs
	
	for joint in creature.creature_get_joints():
		valeur_modif = rd.randint(1,5)
		if rd.random() < PROBA_VALEUR:
			if joint.adhesion - valeur_modif < 0:
				joint.adhesion = joint.adhesion + valeur_modif
			if joint.adhesion + valeur_modif > 255:
				joint.adhesion = joint.adhesion - valeur_modif
			else:
				if rd.random() < 0.5:
					joint.adhesion = joint.adhesion + valeur_modif
				else:
					joint.adhesion = joint.adhesion - valeur_modif

	for joint in creature.creature_get_joints():
		valeur_modif = rd.randint(1,10)
		if rd.random() < PROBA_VALEUR:
			if (joint.position_x_init - valeur_modif >= 0) :
				if rd.random() < 0.5:
					joint.position_x_init = joint.position_x_init + valeur_modif
				else:
					joint.position_x_init = joint.position_x_init - valeur_modif
			else:
				joint.position_x_init = joint.position_x_init + valeur_modif

	for joint in creature.creature_get_joints():
		valeur_modif = rd.randint(1,10)
		if rd.random() < PROBA_VALEUR:
			if (joint.position_y_init + valeur_modif < GROUND_POSITION) :
				if rd.random() < 0.5:
					joint.position_y_init = joint.position_y_init + valeur_modif
				else:
					joint.position_y_init = joint.position_y_init - valeur_modif
			else:
				joint.position_y_init = joint.position_y_init - valeur_modif

	for bone in creature.creature_get_bones():
		valeur_modif = rd.randint(1,2)
		if rd.random() < PROBA_VALEUR:
			if bone.bone_mass - valeur_modif < 1:
				bone.bone_mass = bone.bone_mass + valeur_modif
			if bone.bone_mass + valeur_modif > 10:
				bone.bone_mass = bone.bone_mass - valeur_modif
			else:
				if rd.random() < 0.5:
					bone.bone_mass = bone.bone_mass + valeur_modif
				else:
					bone.bone_mass = bone.bone_mass - valeur_modif

	for bone in creature.creature_get_bones():
		valeur_modif = rd.randint(1,20)
		if rd.random() < PROBA_VALEUR:
			if bone.bone_length - valeur_modif < BONE_MIN_LENGTH:
				bone.bone_length = bone.bone_length + valeur_modif
			if bone.bone_length + valeur_modif > BONE_MAX_LENGTH:
				bone.bone_length = bone.bone_length - valeur_modif
			else:
				if rd.random() < 0.5:
					bone.bone_length = bone.bone_length + valeur_modif
				else:
					bone.bone_length = bone.bone_length - valeur_modif

	for muscle in creature.creature_get_muscles():
		valeur_modif = rd.randint(1,5)
		if rd.random() < PROBA_VALEUR:
			if muscle.strength - valeur_modif < 0:
				muscle.strength = muscle.strength + valeur_modif
			if muscle.strength + valeur_modif > 255:
				muscle.strength = muscle.strength - valeur_modif
			else:
				if rd.random() < 0.5:
					muscle.strength = muscle.strength + valeur_modif
				else:
					muscle.strength = muscle.strength - valeur_modif

	for muscle in creature.creature_get_muscles():
		valeur_modif = rd.randint(1,5)
		if rd.random() < PROBA_VALEUR:
			if (muscle.min_length + valeur_modif <= muscle.max_length - 10) and (muscle.min_length - valeur_modif >= 10):
				if rd.random() < 0.5:
					muscle.min_length = muscle.min_length + valeur_modif
				else:
					muscle.min_length = muscle.min_length - valeur_modif
			if muscle.min_length - valeur_modif < 10:
				muscle.min_length = muscle.min_length + valeur_modif
			if muscle.min_length + valeur_modif > muscle.max_length - 10:
				muscle.min_length = muscle.min_length - valeur_modif

	for muscle in creature.creature_get_muscles():
		valeur_modif = rd.randint(1,5)
		if rd.random() < PROBA_VALEUR:
			if (muscle.max_length - valeur_modif >= muscle.min_length + 10) and (muscle.max_length + valeur_modif <= muscle.limit - 10):
				if rd.random() < 0.5:
					muscle.max_length = muscle.max_length + valeur_modif
				else:
					muscle.max_length = muscle.max_length - valeur_modif
			if muscle.max_length + valeur_modif > muscle.limit - 10:
				muscle.max_length = muscle.max_length - valeur_modif
			if muscle.max_length - valeur_modif < muscle.min_length + 10:
				muscle.max_length = muscle.max_length + valeur_modif

	for muscle in creature.creature_get_muscles(): # Mise a jour de la variable limit
		muscle.limit = MUSCLE_MAX_LENGTH * (muscle.bone1.bone_length + muscle.bone2.bone_length)/2

def mutate_add(creature):
	muscles = creature.creature_get_muscles()
	bones = creature.creature_get_bones()
	joints = creature.creature_get_joints()
	# Muscle
	if (rd.random() < PROBA_VALEUR):
		muscle = random_create_muscle(bones)
		if muscle != 0:
			muscles.append(muscle)

	# Os & Joint
	if (rd.random() < PROBA_VALEUR):
		joint1 = random_create_joint()
		joint2 = rd.choice(joints)
		length = np.sqrt( ( joint1.get_position_x() - joint2.get_position_x() )**2 + ( joint1.get_position_y() - joint2.get_position_y() )**2 )
		if length > 10:
			bone = Bone( joint1, joint2, length , rd.randint(1,10))

			joints.append(joint1)
			bones.append(bone)

def is_removable(creature, bone0):
	for muscle in creature.creature_get_muscles():
		if ((muscle.bone1 == bone0) or (muscle.bone2 == bone0)):
			return False

	joint_b = bone0.joint1 # Ici on devrait faire le test sur les deux joints mais c'est plus simple avec un seul
	for bone in creature.creature_get_bones():
		if ((bone0 != bone) and ((bone.joint1 == joint_b) or (bone.joint2 == joint_b))):
			return False
	return True

def mutate_remove(creature):
	# Muscle
	muscles = creature.creature_get_muscles()
	if ((rd.random() < PROBA_VALEUR) and (len(muscles) > 2)):
		muscles.pop(rd.randrange(len(muscles)))
	
	# Os & Joint
	bones = creature.creature_get_bones()
	joints = creature.creature_get_joints()
	for _ in range(len(bones)//2):
		if (rd.random() < PROBA_VALEUR) and (len(bones) > 2):
			bone = rd.choice(bones)
			if is_removable(creature, bone):
				joints.remove(bone.joint1) # On sait grâce a is_removable
				bones.remove(bone)

def mutate():
	global donnees
	for i in range(len(donnees)):
		mutate_val(donnees[i])
		mutate_add(donnees[i])
		mutate_remove(donnees[i])

#CYCLE
def reset():
	global donnees
	for i in range(len(donnees)):
		donnees[i].score_save = - np.around(donnees[i].creature_position_x())
		donnees[i].score_energy = 0
		donnees[i].stress = 0
		for joint in donnees[i].creature_get_joints():
			joint.position_x = joint.position_x_init
			joint.position_y = joint.position_y_init
			joint.speed_x = 0
			joint.speed_y = 0
			joint.bone_speed_x = 0
			joint.bone_speed_y = 0
		for bone in donnees[i].creature_get_bones():
			bone.rotation_joint1 = 0 # Vitesse de rotation avec joint 1 fixé : w
			bone.rotation_joint2 = 0 # Vitesse de rotation avec joint 2 fixé : w
			bone.rotation_joint1_muscle = 0 # Même chose mais pour l'elasticité du muscle
			bone.rotation_joint2_muscle = 0
			bone.bone_stress = 0
		for muscle in donnees[i].creature_get_muscles():
			muscle.limit = MUSCLE_MAX_LENGTH * (muscle.bone1.bone_length + muscle.bone2.bone_length)/2
			muscle.muscle_stress = 0

def next_gen(i):
	global donnees
	initialisation()
	run_ml = True
	while run_ml:
		print(donnees)
		print(scores)
		print("\n")
		selection(i)
		print(donnees)
		print(scores)
		print("\n")
		reset()
		show([donnees[0]])
		reset()
		duplicate()
		mutate()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run_ml = False

	pygame.quit()
	
#AFFICHAGE
def show(creature): # Attention creature doit être une liste
	main_ml_show(creature,T/T0)

#TEST DES FONCTIONS
#main()
#initialisation()
#show(donnees)
#print(donnees)
#print(scores)
#selection(1)
#print("\n")
#print(donnees)
#print(scores)
next_gen(4)