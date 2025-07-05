import pygame
import math
import numpy as np
import time
import random as rd

### Pygame init
pygame.init()

### FPS & time init
clock = pygame.time.Clock()
FPS = 200

### Game Window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 450

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("TIPE")

### Image
background = pygame.image.load("background3.png").convert()
BACKGROUND_WIDTH = background.get_width()

### Typeface
font = pygame.font.Font(None, 40)
text_color = (0,0,0)

### TYPE : JOINT
JOINT_RADIUS = 10
SPEED_LIMIT = 10

class Joint:
	def __init__(self, position_x, position_y, adhesion):
		self.position_x = position_x
		self.position_y = position_y
		self.position_x_init = position_x
		self.position_y_init = position_y
		self.adhesion = adhesion ### Représenté par la couleur noir à blanc donc entre 0 et 255 : 0 = adhérant, 255 = glissant
		self.contact = False
		self.speed_x = 0
		self.speed_y = 0
		self.bone_speed_x = 0
		self.bone_speed_y = 0


	def get_position_x(self):
		return self.position_x

	def get_position_y(self):
		return self.position_y

	def get_adhesion(self):
		return self.adhesion

	def get_contact(self):
		return self.contact

	def get_speed_x(self):
		return self.speed_x

	def get_speed_y(self):
		return self.speed_y

	def get_bone_speed_x(self):
		return self.bone_speed_x

	def get_bone_speed_y(self):
		return self.bone_speed_y


	def modify_position_x(self, position_x):
		self.position_x = position_x

	def modify_position_y(self, position_y):
		self.position_y = position_y

	def modify_adhesion(self, adhesion_value):
		self.adhesion = adhesion_value

	def modify_contact(self, contact):
		self.contact = contact

	def modify_speed_x(self, speed_x):
		self.speed_x = speed_x

	def modify_speed_y(self, speed_y):
		self.speed_y = speed_y

	def modify_bone_speed_x(self, speed_x):
		self.bone_speed_x = speed_x

	def modify_bone_speed_y(self, speed_y):
		self.bone_speed_y = speed_y


	def joint_display(self):
		pygame.draw.circle(screen, (0, self.get_adhesion(), 20), ( self.get_position_x() , self.get_position_y() ), JOINT_RADIUS) ###location, colorRGB, center, radius


	def joint_movement(self): #Applique le mouvement en fonction de la vitesse
		if self.get_contact():
			contact = self.get_adhesion()/255
		else:
			contact = 1
		self.modify_position_x(self.get_position_x() + contact * (self.get_speed_x() + self.get_bone_speed_x()))
		self.modify_position_y(self.get_position_y() + self.get_speed_y() + self.get_bone_speed_y())

	def speed_limit(self):
		if self.get_speed_x() < - SPEED_LIMIT:
			self.modify_speed_x( - SPEED_LIMIT)
		if self.get_speed_x() > SPEED_LIMIT:
			self.modify_speed_x( SPEED_LIMIT)		
		if self.get_speed_y() < - SPEED_LIMIT:
			self.modify_speed_y( - SPEED_LIMIT)
		if self.get_speed_y() > SPEED_LIMIT:
			self.modify_speed_y( SPEED_LIMIT)

		if self.get_bone_speed_x() < - SPEED_LIMIT:
			self.modify_bone_speed_x( - SPEED_LIMIT)
		if self.get_bone_speed_x() > SPEED_LIMIT:
			self.modify_bone_speed_x( SPEED_LIMIT)
		if self.get_bone_speed_y() < - SPEED_LIMIT:
			self.modify_bone_speed_y( - SPEED_LIMIT)
		if self.get_bone_speed_y() > SPEED_LIMIT:
			self.modify_bone_speed_y( SPEED_LIMIT)

### TYPE : BONE
BONE_MAX_LENGTH = 300
BONE_MIN_LENGTH = 30
ONE_METER_REF = 250 # Permet de lier norme de moment et de force : un mammifère à des os de 10cm à 1.2m : utile seulement avec le bras de levier
BONE_MASS = 5 # Cuisse d'un homme de 80 kg
SURFACE = 0.1 # Surface os/muscle : unité

class Bone:
	def __init__(self, joint1: Joint, joint2: Joint, bone_length: int, bone_mass: int):
		self.joint1 = joint1
		self.joint2 = joint2
		self.bone_length = bone_length
		self.bone_mass = bone_mass # Valeur entre 1 et 10 à comparer avec BONE_MASS
		self.rotation_joint1 = 0 # Vitesse de rotation avec joint 1 fixé : w
		self.rotation_joint2 = 0 # Vitesse de rotation avec joint 2 fixé : w
		self.rotation_joint1_muscle = 0 # Même chose mais pour l'elasticité du muscle
		self.rotation_joint2_muscle = 0
		self.bone_stress = 0



	def bone_display(self):
		bone_color = 170 - (self.bone_mass -5)*10
		pygame.draw.line(screen, (bone_color,bone_color,bone_color), ( self.joint1.get_position_x() , self.joint1.get_position_y() ), ( self.joint2.get_position_x() , self.joint2.get_position_y() ), width = 5 )

	def bone_middle_x(self):
		return (self.joint1.get_position_x() + self.joint2.get_position_x())/2

	def bone_middle_y(self):
		return (self.joint1.get_position_y() + self.joint2.get_position_y())/2

	def bone_get_rotation1(self):
		return (self.rotation_joint1)

	def bone_get_rotation2(self):
		return (self.rotation_joint2)

	def bone_true_length(self):
		return np.sqrt( ( self.joint1.get_position_x() - self.joint2.get_position_x() )**2 + ( self.joint1.get_position_y() - self.joint2.get_position_y() )**2 )

	def reajust_bone(self):
		bone_true_length = self.bone_true_length()
		bone_young_modulus = 20*(10^9) # Source internet
		bone_stress = bone_young_modulus*(bone_true_length - self.bone_length)/bone_true_length
		bone_reajustment = bone_stress*SURFACE/self.bone_mass
		bone_epsilon = 1
		bone_dampling = 0.8

		self.bone_stress = self.bone_stress + bone_stress

		if np.abs(bone_reajustment) < bone_epsilon:
			self.joint1.modify_bone_speed_x(bone_dampling * self.joint1.get_bone_speed_x())
			self.joint1.modify_bone_speed_y(bone_dampling * self.joint1.get_bone_speed_y())
			self.joint2.modify_bone_speed_x(bone_dampling * self.joint2.get_bone_speed_x())
			self.joint2.modify_bone_speed_y(bone_dampling * self.joint2.get_bone_speed_y())
			return

		bone_true_length_x = self.joint1.get_position_x() - self.joint2.get_position_x()
		bone_true_length_y = self.joint1.get_position_y() - self.joint2.get_position_y()
		bone_ratio = np.abs( bone_true_length_x/( np.abs( bone_true_length_x ) + np.abs( bone_true_length_y ) ) )

		if self.joint1.get_contact():
			contact1 = 1*(self.joint1.get_adhesion()/255)
		else:
			contact1 = 1

		if self.joint2.get_contact():
			contact2 = 1*(self.joint2.get_adhesion()/255)
		else:
			contact2 = 1

		if self.joint1.get_position_x() == self.joint2.get_position_x():
			if self.joint1.get_position_y() < self.joint2.get_position_y():
				self.joint1.modify_bone_speed_y( self.joint1.get_bone_speed_y() + bone_reajustment )
				self.joint2.modify_bone_speed_y( self.joint2.get_bone_speed_y() - bone_reajustment )
			else:
				self.joint1.modify_bone_speed_y( self.joint1.get_bone_speed_y() - bone_reajustment )
				self.joint2.modify_bone_speed_y( self.joint2.get_bone_speed_y() + bone_reajustment )

		if self.joint1.get_position_y() == self.joint2.get_position_y():
			if self.joint1.get_position_x() < self.joint2.get_position_x():
				self.joint1.modify_bone_speed_x( self.joint1.get_bone_speed_x() + contact1 * bone_reajustment )
				self.joint2.modify_bone_speed_x( self.joint2.get_bone_speed_x() - contact2 * bone_reajustment )
			else:
				self.joint1.modify_bone_speed_x( self.joint1.get_bone_speed_x() - contact1 * bone_reajustment )
				self.joint2.modify_bone_speed_x( self.joint2.get_bone_speed_x() + contact2 * bone_reajustment )
		
		if ( self.joint1.get_position_x() < self.joint2.get_position_x() ) and ( self.joint1.get_position_y() < self.joint2.get_position_y() ):
			self.joint1.modify_bone_speed_x( self.joint1.get_bone_speed_x() + contact1 * bone_ratio * bone_reajustment )
			self.joint1.modify_bone_speed_y( self.joint1.get_bone_speed_y() + (1-bone_ratio) * bone_reajustment )
			self.joint2.modify_bone_speed_x( self.joint2.get_bone_speed_x() - contact2 * bone_ratio * bone_reajustment )
			self.joint2.modify_bone_speed_y( self.joint2.get_bone_speed_y() - (1-bone_ratio) * bone_reajustment )

		if ( self.joint1.get_position_x() < self.joint2.get_position_x() ) and ( self.joint1.get_position_y() > self.joint2.get_position_y() ):
			self.joint1.modify_bone_speed_x( self.joint1.get_bone_speed_x() + contact1 * bone_ratio * bone_reajustment )
			self.joint1.modify_bone_speed_y( self.joint1.get_bone_speed_y() - (1-bone_ratio) * bone_reajustment )
			self.joint2.modify_bone_speed_x( self.joint2.get_bone_speed_x() - contact2 * bone_ratio * bone_reajustment )
			self.joint2.modify_bone_speed_y( self.joint2.get_bone_speed_y() + (1-bone_ratio) * bone_reajustment )

		if ( self.joint1.get_position_x() > self.joint2.get_position_x() ) and ( self.joint1.get_position_y() < self.joint2.get_position_y() ):
			self.joint1.modify_bone_speed_x( self.joint1.get_bone_speed_x() - contact1 * bone_ratio * bone_reajustment )
			self.joint1.modify_bone_speed_y( self.joint1.get_bone_speed_y() + (1-bone_ratio) * bone_reajustment )
			self.joint2.modify_bone_speed_x( self.joint2.get_bone_speed_x() + contact2 * bone_ratio * bone_reajustment )
			self.joint2.modify_bone_speed_y( self.joint2.get_bone_speed_y() - (1-bone_ratio) * bone_reajustment )

		if ( self.joint1.get_position_x() > self.joint2.get_position_x() ) and ( self.joint1.get_position_y() > self.joint2.get_position_y() ):
			self.joint1.modify_bone_speed_x( self.joint1.get_bone_speed_x() - contact1 * bone_ratio * bone_reajustment )
			self.joint1.modify_bone_speed_y( self.joint1.get_bone_speed_y() - (1-bone_ratio) * bone_reajustment )
			self.joint2.modify_bone_speed_x( self.joint2.get_bone_speed_x() + contact2 *bone_ratio * bone_reajustment )
			self.joint2.modify_bone_speed_y( self.joint2.get_bone_speed_y() + (1-bone_ratio) * bone_reajustment )

### TYPE : MUSCLE
MUSCLE_MAX_LENGTH = 0.9*BONE_MAX_LENGTH
MUSCLE_REF = 255/2 # Permet d'avoir des valeurs de force entre 0 et 2
MUSCLE_MAX_LENGTH = 90/100 # Pourcentage du max par rapport aux os

class Muscle:
	def __init__(self, bone1: Bone, bone2: Bone, strength, min_length, max_length):
		self.bone1 = bone1
		self.bone2 = bone2
		self.strength = strength # valeur entre 0 et 255
		self.min_length = min_length
		self.max_length = max_length
		self.is_contracting = True
		self.limit = MUSCLE_MAX_LENGTH * (bone1.bone_length + bone2.bone_length)/2
		self.muscle_stress = 0
		self.muscle_length_save = self.muscle_length() 


	def muscle_display(self):
		if self.is_contracting:
			color = (255-self.strength,20,20)
		else:
			color = (50,50,255-self.strength)
		pygame.draw.line(screen, color, ( self.bone1.bone_middle_x() , self.bone1.bone_middle_y() ), ( self.bone2.bone_middle_x() , self.bone2.bone_middle_y() ), width = 15 )
		pygame.draw.circle(screen, color, ( self.bone1.bone_middle_x() , self.bone1.bone_middle_y() ), JOINT_RADIUS)
		pygame.draw.circle(screen, color, ( self.bone2.bone_middle_x() , self.bone2.bone_middle_y() ), JOINT_RADIUS)
	

	def muscle_length(self):
		return np.sqrt( ( self.bone1.bone_middle_x() - self.bone2.bone_middle_x() )**2 + ( self.bone1.bone_middle_y() - self.bone2.bone_middle_y() )**2 )


	def muscle_elasticity(self): # Calcule la force (loi de hook) 
		E = 100*(1e6)
		epsilon_muscle = (self.muscle_length() - self.limit)/self.limit
		#print(epsilon_muscle)
		if epsilon_muscle <= 0:
			self.bone1.rotation_joint1_muscle = 0 #self.bone1.rotation_joint1_muscle/2                   # A JUSTIFIER
			self.bone1.rotation_joint2_muscle = 0 #self.bone1.rotation_joint2_muscle/2
			self.bone2.rotation_joint1_muscle = 0 #self.bone2.rotation_joint1_muscle/2
			self.bone2.rotation_joint2_muscle = 0 #self.bone2.rotation_joint2_muscle/2
			return 0
		else:
			self.muscle_stress = self.muscle_stress + E*epsilon_muscle
			return E*epsilon_muscle*SURFACE


	def muscle_moment(self):
		# Quel est le point fixe et Coordonnées des articulations du bâton 1 et 2
		if self.bone1.joint1 == self.bone2.joint1 :
			jointfixe = self.bone1.joint1

			#X1_bone1 = self.bone1.joint2.get_position_x()
			#Y1_bone1 = self.bone1.joint2.get_position_y()

			#X1_bone2 = self.bone2.joint2.get_position_x()
			#Y1_bone2 = self.bone2.joint2.get_position_y()

		elif self.bone1.joint1 == self.bone2.joint2 :
			jointfixe = self.bone1.joint1

			#X1_bone1 = self.bone1.joint2.get_position_x()
			#Y1_bone1 = self.bone1.joint2.get_position_y()

			#X1_bone2 = self.bone2.joint1.get_position_x()
			#Y1_bone2 = self.bone2.joint1.get_position_y()

		elif self.bone1.joint2 == self.bone2.joint1 :
			jointfixe = self.bone1.joint2

			#X1_bone1 = self.bone1.joint1.get_position_x()
			#Y1_bone1 = self.bone1.joint1.get_position_y()

			#X1_bone2 = self.bone2.joint2.get_position_x()
			#Y1_bone2 = self.bone2.joint2.get_position_y()

		elif self.bone1.joint2 == self.bone2.joint2 :
			jointfixe = self.bone1.joint2

			#X1_bone1 = self.bone1.joint1.get_position_x()
			#Y1_bone1 = self.bone1.joint1.get_position_y()

			#X1_bone2 = self.bone2.joint1.get_position_x()
			#Y1_bone2 = self.bone2.joint1.get_position_y()

		else:
			print("Error in muscle_moment")

		if self.is_contracting:
			F = self.strength/MUSCLE_REF
		else:
			F = -self.strength/MUSCLE_REF

		# Coordonnées du centre des bâtons
		x1 = self.bone1.bone_middle_x()
		y1 = self.bone1.bone_middle_y()
		x2 = self.bone2.bone_middle_x()
		y2 = self.bone2.bone_middle_y()
		d = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)

		# Calcul des composantes de la force selon x et y : attention y est décroissant
		dx = (x2 - x1)/ONE_METER_REF
		dy = (y2 - y1)/ONE_METER_REF
		Fx = dx*F/d
		Fy = dy*F/d  # attention y décroissant

		# Calcul du moment M1 pour le bâton 1
		M1 = ( (x1 - jointfixe.get_position_x()) * Fy + (y1 - jointfixe.get_position_y()) * Fx )/ONE_METER_REF

		# Calcul du moment M2 pour le bâton 2
		M2 = ( (x2 - jointfixe.get_position_x()) * Fy + (y2 - jointfixe.get_position_y()) * Fx )/ONE_METER_REF

		#if abs((abs(self.bone1.bone_length - self.bone2.bone_length)/2)-self.muscle_length())<2: # Traite le cas où tous est plat
			#return (0, 0, jointfixe)
		#else:
		return (M1, M2, jointfixe)

	
	def muscle_moment_elasticity(self):
		if self.bone1.joint1 == self.bone2.joint1 :
			jointfixe = self.bone1.joint1

		elif self.bone1.joint1 == self.bone2.joint2 :
			jointfixe = self.bone1.joint1

		elif self.bone1.joint2 == self.bone2.joint1 :
			jointfixe = self.bone1.joint2

		elif self.bone1.joint2 == self.bone2.joint2 :
			jointfixe = self.bone1.joint2

		else:
			print("Error in muscle_moment")

		f = self.muscle_elasticity()
		F = f/MUSCLE_REF
		#print(F)
		#print(self.strength)

		# Coordonnées du centre des bâtons
		x1 = self.bone1.bone_middle_x()
		y1 = self.bone1.bone_middle_y()
		x2 = self.bone2.bone_middle_x()
		y2 = self.bone2.bone_middle_y()
		d = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)

		# Calcul des composantes de la force selon x et y : attention y est décroissant
		dx = (x2 - x1)/ONE_METER_REF
		dy = (y2 - y1)/ONE_METER_REF
		Fx = dx*F/d
		Fy = dy*F/d  # attention y décroissant

		# Calcul du moment M1 pour le bâton 1
		M1 = ( (x1 - jointfixe.get_position_x()) * Fy + (y1 - jointfixe.get_position_y()) * Fx )/ONE_METER_REF

		# Calcul du moment M2 pour le bâton 2
		M2 = ( (x2 - jointfixe.get_position_x()) * Fy + (y2 - jointfixe.get_position_y()) * Fx )/ONE_METER_REF

		return (M1, M2, jointfixe)

	"""
	def muscle_movement_translation(self): # is_relaxing = True : vers taille max
		muscle_true_length = self.muscle_length()
		muscle_strength = (1/2)*(self.strength)/255 #valeur entre 0 et 1
		muscle_young_modulus = 0.01
		muscle_ajustment = 5
		if muscle_true_length > self.max_length :
			muscle_reajustment = (-muscle_ajustment) + muscle_young_modulus*muscle_strength*(muscle_true_length - self.max_length)/muscle_true_length
		elif muscle_true_length < self.min_length + 10 :
			muscle_reajustment = (muscle_ajustment) - muscle_young_modulus*muscle_strength*(muscle_true_length - self.min_length)/muscle_true_length
		elif self.is_contracting :
			muscle_reajustment = muscle_young_modulus*muscle_strength*(muscle_true_length - self.min_length)/muscle_true_length
		else :
			muscle_reajustment = 0

		muscle_true_length_x = self.bone1.bone_middle_x() - self.bone2.bone_middle_x()
		muscle_true_length_y = self.bone1.bone_middle_y() - self.bone2.bone_middle_y()
		muscle_ratio = np.abs( muscle_true_length_x/( np.abs( muscle_true_length_x ) + np.abs( muscle_true_length_y ) ) )


		if self.bone1.bone_middle_x() == self.bone2.bone_middle_x():
			if self.bone1.bone_middle_y() < self.bone2.bone_middle_y():
				self.bone1.joint1.modify_speed_y( self.bone1.joint1.get_speed_y() + muscle_reajustment )
				self.bone1.joint2.modify_speed_y( self.bone1.joint1.get_speed_y() + muscle_reajustment )

				self.bone2.joint1.modify_speed_y( self.bone2.joint2.get_speed_y() - muscle_reajustment )
				self.bone2.joint2.modify_speed_y( self.bone2.joint2.get_speed_y() - muscle_reajustment )
			else:
				self.bone1.joint1.modify_speed_y( self.bone1.joint1.get_speed_y() - muscle_reajustment )
				self.bone1.joint2.modify_speed_y( self.bone1.joint1.get_speed_y() - muscle_reajustment )

				self.bone2.joint1.modify_speed_y( self.bone2.joint2.get_speed_y() + muscle_reajustment )
				self.bone2.joint2.modify_speed_y( self.bone2.joint2.get_speed_y() + muscle_reajustment )

		if self.bone1.bone_middle_y() == self.bone2.bone_middle_y():
			if self.bone1.bone_middle_x() < self.bone2.bone_middle_x():
				self.bone1.joint1.modify_speed_x( self.bone1.joint1.get_speed_x() + muscle_reajustment )
				self.bone1.joint2.modify_speed_x( self.bone1.joint1.get_speed_x() + muscle_reajustment )

				self.bone2.joint1.modify_speed_x( self.bone2.joint2.get_speed_x() - muscle_reajustment )
				self.bone2.joint2.modify_speed_x( self.bone2.joint2.get_speed_x() - muscle_reajustment )
			else:
				self.bone1.joint1.modify_speed_x( self.bone1.joint1.get_speed_x() - muscle_reajustment )
				self.bone1.joint2.modify_speed_x( self.bone1.joint1.get_speed_x() - muscle_reajustment )

				self.bone2.joint1.modify_speed_x( self.bone2.joint2.get_speed_x() + muscle_reajustment )
				self.bone2.joint2.modify_speed_x( self.bone2.joint2.get_speed_x() + muscle_reajustment )
		
		if ( self.bone1.bone_middle_x() < self.bone2.bone_middle_x() ) and ( self.bone1.bone_middle_y() < self.bone2.bone_middle_y() ):
			self.bone1.joint1.modify_speed_x( self.bone1.joint1.get_speed_x() + muscle_ratio * muscle_reajustment )
			self.bone1.joint2.modify_speed_x( self.bone1.joint1.get_speed_x() + muscle_ratio * muscle_reajustment )
			self.bone1.joint1.modify_speed_y( self.bone1.joint1.get_speed_y() + (1-muscle_ratio) * muscle_reajustment )
			self.bone1.joint2.modify_speed_y( self.bone1.joint1.get_speed_y() + (1-muscle_ratio) * muscle_reajustment )

			self.bone2.joint1.modify_speed_x( self.bone2.joint2.get_speed_x() - muscle_ratio * muscle_reajustment )
			self.bone2.joint2.modify_speed_x( self.bone2.joint2.get_speed_x() - muscle_ratio * muscle_reajustment )
			self.bone2.joint1.modify_speed_y( self.bone2.joint2.get_speed_y() - (1-muscle_ratio) * muscle_reajustment )
			self.bone2.joint2.modify_speed_y( self.bone2.joint2.get_speed_y() - (1-muscle_ratio) * muscle_reajustment )

		if ( self.bone1.bone_middle_x() < self.bone2.bone_middle_x() ) and ( self.bone1.bone_middle_y() > self.bone2.bone_middle_y() ):
			self.bone1.joint1.modify_speed_x( self.bone1.joint1.get_speed_x() + muscle_ratio * muscle_reajustment )
			self.bone1.joint2.modify_speed_x( self.bone1.joint1.get_speed_x() + muscle_ratio * muscle_reajustment )
			self.bone1.joint1.modify_speed_y( self.bone1.joint1.get_speed_y() - (1-muscle_ratio) * muscle_reajustment )
			self.bone1.joint2.modify_speed_y( self.bone1.joint1.get_speed_y() - (1-muscle_ratio) * muscle_reajustment )

			self.bone2.joint1.modify_speed_x( self.bone2.joint2.get_speed_x() - muscle_ratio * muscle_reajustment )
			self.bone2.joint2.modify_speed_x( self.bone2.joint2.get_speed_x() - muscle_ratio * muscle_reajustment )
			self.bone2.joint1.modify_speed_y( self.bone2.joint2.get_speed_y() + (1-muscle_ratio) * muscle_reajustment )
			self.bone2.joint2.modify_speed_y( self.bone2.joint2.get_speed_y() + (1-muscle_ratio) * muscle_reajustment )

		if ( self.bone1.bone_middle_x() > self.bone2.bone_middle_x() ) and ( self.bone1.bone_middle_y() < self.bone2.bone_middle_y() ):
			self.bone1.joint1.modify_speed_x( self.bone1.joint1.get_speed_x() - muscle_ratio * muscle_reajustment )
			self.bone1.joint2.modify_speed_x( self.bone1.joint1.get_speed_x() - muscle_ratio * muscle_reajustment )
			self.bone1.joint1.modify_speed_y( self.bone1.joint1.get_speed_y() + (1-muscle_ratio) * muscle_reajustment )
			self.bone1.joint2.modify_speed_y( self.bone1.joint1.get_speed_y() + (1-muscle_ratio) * muscle_reajustment )

			self.bone2.joint1.modify_speed_x( self.bone2.joint2.get_speed_x() + muscle_ratio * muscle_reajustment )
			self.bone2.joint2.modify_speed_x( self.bone2.joint2.get_speed_x() + muscle_ratio * muscle_reajustment )
			self.bone2.joint1.modify_speed_y( self.bone2.joint2.get_speed_y() - (1-muscle_ratio) * muscle_reajustment )
			self.bone2.joint2.modify_speed_y( self.bone2.joint2.get_speed_y() - (1-muscle_ratio) * muscle_reajustment )

		if ( self.bone1.bone_middle_y() > self.bone2.bone_middle_x() ) and ( self.bone1.bone_middle_y() > self.bone2.bone_middle_y() ):
			self.bone1.joint1.modify_speed_x( self.bone1.joint1.get_speed_x() - muscle_ratio * muscle_reajustment )
			self.bone1.joint2.modify_speed_x( self.bone1.joint1.get_speed_x() - muscle_ratio * muscle_reajustment )
			self.bone1.joint1.modify_speed_y( self.bone1.joint1.get_speed_y() - (1-muscle_ratio) * muscle_reajustment )
			self.bone1.joint2.modify_speed_y( self.bone1.joint1.get_speed_y() - (1-muscle_ratio) * muscle_reajustment )

			self.bone2.joint1.modify_speed_x( self.bone2.joint2.get_speed_x() + muscle_ratio * muscle_reajustment )
			self.bone2.joint2.modify_speed_x( self.bone2.joint2.get_speed_x() + muscle_ratio * muscle_reajustment )
			self.bone2.joint1.modify_speed_y( self.bone2.joint2.get_speed_y() + (1-muscle_ratio) * muscle_reajustment )
			self.bone2.joint2.modify_speed_y( self.bone2.joint2.get_speed_y() + (1-muscle_ratio) * muscle_reajustment )
	"""

	def muscle_cycle(self):
		muscle_epsilon = 5
		if self.muscle_length() > self.max_length - muscle_epsilon:
			self.is_contracting = True
		elif self.muscle_length() < self.min_length + muscle_epsilon:
			self.is_contracting = False

### TYPE : CREATURE
class Creature:
	def __init__(self, list_joint: list[Joint], list_bone: list[Bone], list_muscle: list[Muscle]):
		self.list_joint = list_joint
		self.list_bone = list_bone
		self.list_muscle = list_muscle
		self.score_save = - np.around(self.creature_position_x())
		self.score_energy = 0
		self.stress = 0


	def creature_get_muscles(self):
		return self.list_muscle
	
	def creature_get_bones(self):
		return self.list_bone

	def creature_get_joints(self):
		return self.list_joint


	def creature_add_muscle(self, muscle):
		self.list_muscle = list_muscle.append(muscle)

	def creature_add_bone(self, bone):
		self.list_bone = list_bone.append(bone)

	def creature_add_joint(self, joint):
		self.list_joint = list_joint.append(joint)


	def creature_position_x(creature):
		creature_average_x = 0
		creature_number_of_joint = len(creature.creature_get_joints())

		for joint in creature.creature_get_joints():
			creature_average_x = creature_average_x + joint.get_position_x()

		return (creature_average_x/creature_number_of_joint)

	def creature_position_y(creature):
		creature_average_y = 0
		creature_number_of_joint = len(creature.creature_get_joints())

		for joint in creature.creature_get_joints():
			creature_average_y = creature_average_y + joint.get_position_y()

		return (creature_average_y/creature_number_of_joint)

	def creature_min_position_x(creature):
		creature_min_x = 2*SCREEN_WIDTH

		for joint in creature.creature_get_joints():
			if joint.get_position_x() < creature_min_x:
				creature_min_x = joint.get_position_x()

		return creature_min_x

	def creature_max_position_x(creature):
		creature_max_x = SCREEN_WIDTH

		for joint in creature.creature_get_joints():
			if joint.get_position_x() > creature_max_x:
				creature_max_x = joint.get_position_x()

		return creature_max_x

	def creature_rotation_calculus(creature): # Transformation des moments en rotation : Théoreme du moment cinétique
		for muscle in creature.creature_get_muscles():
			(M1,M2,jointfixe) = muscle.muscle_moment() # M1 = Moment de l'os 1 par rapport à joint1 fixé ; M2 = Moment os2 p/r joint1 fixé
			#print("M1 :", M1, "M2 : ", M2)

			bone_mass1 = muscle.bone1.bone_mass
			bone_mass2 = muscle.bone2.bone_mass
			r1 = (muscle.bone1.bone_true_length()/2)/ONE_METER_REF
			r2 = (muscle.bone2.bone_true_length()/2)/ONE_METER_REF

			# Calcul de w' :

			# Pour bone 1 :
			if muscle.bone1.joint1 == jointfixe:
				w_prime1 = M1/( bone_mass1 * r1**2 )
				muscle.bone1.rotation_joint1 = muscle.bone1.rotation_joint1 + w_prime1 # vitesse de rotation avec le joint1 fixé
				#print(w_prime1)
			else:
				w_prime2 = M1/( bone_mass1 * r1**2 )
				muscle.bone1.rotation_joint2 = muscle.bone1.rotation_joint2 + w_prime2 # vitesse de rotation avec le joint2 fixé
				#print(w_prime2)
			
			# Pour bone 2 :
			if muscle.bone2.joint1 == jointfixe:
				w_prime3 = M2/( bone_mass2 * r2**2 )
				muscle.bone2.rotation_joint1 = muscle.bone2.rotation_joint1 + w_prime3 # vitesse de rotation avec le joint1 fixé
				#print(w_prime3)
			else:
				w_prime4 = M2/( bone_mass2 * r2**2 )
				muscle.bone2.rotation_joint2 = muscle.bone2.rotation_joint2 + w_prime4 # vitesse de rotation avec le joint2 fixé
				#print(w_prime4)

	def creature_rotation_calculus_elasticity(creature): # Transformation des moments en rotation : Théoreme du moment cinétique
		for muscle in creature.creature_get_muscles():
			(M1,M2,jointfixe) = muscle.muscle_moment_elasticity() # M1 = Moment de l'os 1 par rapport à joint1 fixé ; M2 = Moment os2 p/r joint1 fixé
			#print("M1 :", M1, "M2 : ", M2)

			bone_mass1 = muscle.bone1.bone_mass
			bone_mass2 = muscle.bone2.bone_mass
			r1 = (muscle.bone1.bone_true_length()/2)/ONE_METER_REF
			r2 = (muscle.bone2.bone_true_length()/2)/ONE_METER_REF

			# Calcul de w' :

			# Pour bone 1 :
			if muscle.bone1.joint1 == jointfixe:
				w_prime1 = M1/( bone_mass1 * r1**2 )
				muscle.bone1.rotation_joint1_muscle = muscle.bone1.rotation_joint1_muscle + w_prime1 # vitesse de rotation avec le joint1 fixé
				#print(w_prime1)
			else:
				w_prime2 = M1/( bone_mass1 * r1**2 )
				muscle.bone1.rotation_joint2_muscle = muscle.bone1.rotation_joint2_muscle + w_prime2 # vitesse de rotation avec le joint2 fixé
				#print(w_prime2)
			
			# Pour bone 2 :
			if muscle.bone2.joint1 == jointfixe:
				w_prime3 = M2/( bone_mass2 * r2**2 )
				muscle.bone2.rotation_joint1_muscle = muscle.bone2.rotation_joint1_muscle + w_prime3 # vitesse de rotation avec le joint1 fixé
				#print(w_prime3)
			else:
				w_prime4 = M2/( bone_mass2 * r2**2 )
				muscle.bone2.rotation_joint2_muscle = muscle.bone2.rotation_joint2_muscle + w_prime4 # vitesse de rotation avec le joint2 fixé
				#print(w_prime4)

	def creature_movement_rotation(creature):
		creature.creature_rotation_calculus()
		creature.creature_rotation_calculus_elasticity()

		for bone in creature.creature_get_bones():
			x1 = bone.joint1.get_position_x()
			y1 = bone.joint1.get_position_y()
			x2 = bone.joint2.get_position_x()
			y2 = bone.joint2.get_position_y()

			l = bone.bone_length

			s = FPS # Permet de régler les w trop grand                                                                      A CHANGER ? 
			w1 = (bone.bone_get_rotation1()+bone.rotation_joint1_muscle)/s # rotation à joint1 fixé
			w2 = (bone.bone_get_rotation2()+bone.rotation_joint2_muscle)/s
			#print("w1 :", w1, "w2 :", w2)

			tolerance = 1e-6

			if abs(w1) > tolerance or abs(w2) > tolerance:

				#print(".")
				#print(f"Initial positions - Joint1: ({x1}, {y1}), Joint2: ({x2}, {y2})")
				#print(f"Rotations - w1: {w1}, w2: {w2}")
				#print(f"Bone length: {l}")

				dx = x2 - x1
				dy = y2 - y1 # y décroissant mais ici on change rien

				theta = np.arctan2(dy, dx)
				#print(f"Theta: {theta}")

				if abs(w1) > tolerance:
					# Mise à jour de la position de joint2 avec joint1 fixé
					new_x2 = x1 + l * np.cos(theta + w1)
					new_y2 = y1 + l * np.sin(theta + w1)
					#print(f"New Joint2 position: ({new_x2}, {new_y2})")

					bone.joint2.modify_position_x(new_x2)
					bone.joint2.modify_position_y(new_y2)

				if abs(w2) > tolerance:
					# Mise à jour de la position de joint1 avec joint2 fixé
					new_x1 = x2 - l * np.cos(theta + w2)
					new_y1 = y2 - l * np.sin(theta + w2)
					#print(f"New Joint1 position: ({new_x1}, {new_y1})")
					#print(".")

					bone.joint1.modify_position_x(new_x1)
					bone.joint1.modify_position_y(new_y1)

	def stress_update(creature):
		for muscle in creature.creature_get_muscles():
			creature.stress = max (creature.stress, muscle.muscle_stress)
		for bone in creature.creature_get_bones():
			creature.stress = max (creature.stress, bone.bone_stress)

	def energy_update(creature):
		for muscle in creature.creature_get_muscles():
			creature.score_energy = creature.score_energy + (muscle.strength * abs(muscle.muscle_length()-muscle.muscle_length_save))

	### Score
	def score_update(creature):
		return np.around(creature.creature_position_x()) + creature.score_save

	def score_display(creature):
		score_value = font.render( str( creature.score_update() ) , True , text_color ) # Convertir le nombre en texte pour l'afficher
		screen.blit( score_value, ( creature.creature_position_x() - 30 , creature.creature_position_y() - 10 ) )
		"""
		score_value = font.render( str( creature.score_energy ) , True , (230,50,50) ) # Ici pour l'energie
		screen.blit( score_value, ( creature.creature_position_x() - 30 , creature.creature_position_y() - 40 ) )
	 	"""

### Ground and Gravity 
GROUND_POSITION = 420
GRAVITY_POWER = 0.98

def ground_physic(joint):
	ground_dampling = -1 #-0.3 #Voir Google Doc pour source
	if joint.get_position_y() > GROUND_POSITION:
		joint.modify_contact(True)
		joint.modify_position_y(GROUND_POSITION)
		if joint.get_speed_y() > 0 :
			joint.modify_speed_y(ground_dampling * joint.get_speed_y())

	else:
		joint.modify_contact(False)

def gravity(joint):
	# PFD : m*a = m*g => a = g
	joint.modify_speed_y(joint.get_speed_y() + GRAVITY_POWER)

def wall(joint):
	if joint.get_position_x()>SCREEN_WIDTH:
		joint.modify_position_x(SCREEN_WIDTH)
	if joint.get_position_x()<0:
		joint.modify_position_x(0)
	if joint.get_position_y()<0:
		joint.modify_position_y(0)

### Random
RANDOM_CREATE_BOX = 400
RANDOM_MIN_JOINT = 3
RANDOM_MAX_JOINT = 5
RANDOM_MIN_BONE = 2
RANDOM_MAX_MUSCLE = 2


def random_create_joint():
	return Joint(rd.randint(5,RANDOM_CREATE_BOX), rd.randint(5,RANDOM_CREATE_BOX), rd.randint(0,255))

def random_create_bone(random_joint_list, random_rank_tab):
	if (len(random_joint_list) <= 2):
		return #Creation d'os impossible avec une seule articulation

	random_j1, random_j2 = rd.sample(range(0, len(random_joint_list) ), 2)

	random_joint1 = random_joint_list[random_j1]
	random_joint2 = random_joint_list[random_j2]

	random_rank_1 = random_rank_tab[random_j1]
	random_rank_2 = random_rank_tab[random_j2]
	random_min_rank = min (random_rank_1, random_rank_2)

	for i in range(0, len(random_joint_list)):
		if (random_rank_tab[i] == random_rank_1 or random_rank_tab[i] == random_rank_2):
			random_rank_tab[i] = random_min_rank

	random_bone_length = (np.round(np.sqrt((random_joint2.get_position_x() - random_joint1.get_position_x())**2 + (random_joint2.get_position_y() - random_joint1.get_position_y())**2))) # distance euclidienne
	
	random_bone_mass = rd.randint(1,10)                                               # A REVOIR POUR LES BORNES

	return Bone( random_joint1, random_joint2, random_bone_length , random_bone_mass)

def random_create_bone_connexity(random_joint_list, random_rank_tab, random_bone_list):
	if (len(random_joint_list) <= 2):
		return #Creation d'os impossible avec une seule articulation

	for i in range(1, len(random_joint_list)):
		if (random_rank_tab[i] != 0):
			if (i == 1):
				random_j = 0
			else:
				random_j = rd.randint(0, i-1)
			random_joint = random_joint_list[random_j]
			random_rank = random_rank_tab[i]

			for k in range(0, len(random_joint_list)):
				if (random_rank_tab[k] == random_rank):
					random_rank_tab[k] = 0

			random_bone_length = (np.round(np.sqrt((random_joint.get_position_x() - random_joint_list[i].get_position_x())**2 + (random_joint.get_position_y() - random_joint_list[i].get_position_y())**2))) # distance euclidienne
			
			random_bone_mass = rd.randint(1,10)                                               # A REVOIR POUR LES BORNES

			random_bone = Bone( random_joint_list[i], random_joint, random_bone_length, random_bone_mass )

			if not (random_bone in random_bone_list) and (random_bone != None):
				random_bone_list.append( random_bone )

def random_create_muscle(random_bone_list):
	if (len(random_bone_list) < 2):
		return #Creation de muscle impossible avec un seul os
	"""
	random_muscle1 = random_bone_list.pop(rd.randint( 0, len(random_bone_list)-1 )) # c'est des os
	random_muscle2 = random_bone_list[rd.randint( 0, len(random_bone_list)-1 )]
	
	random_bone_list.append(random_muscle1)
    """
	random_bones = rd.sample(random_bone_list, k=2)
	random_muscle1 = random_bones[0]
	random_muscle2 = random_bones[1]

	if (random_muscle1.joint1 == random_muscle2.joint1) or (random_muscle1.joint2 == random_muscle2.joint1) or (random_muscle1.joint1 == random_muscle2.joint2) or (random_muscle1.joint2 == random_muscle2.joint2) :

		muscle_length_max = MUSCLE_MAX_LENGTH * (random_muscle1.bone_length + random_muscle2.bone_length)/2
		random_muscle_min_length = rd.randint( 0, math.floor(muscle_length_max/2) )
		random_muscle_max_length = rd.randint( random_muscle_min_length, math.floor(muscle_length_max - 5) )

		return Muscle( random_muscle1, random_muscle2, rd.randint(1,255), random_muscle_min_length, random_muscle_max_length )

	else:
		return 0

def random_create_creature():
	rd.seed()
	# Joint
	random_number_of_joint = rd.randint(RANDOM_MIN_JOINT, RANDOM_MAX_JOINT)
	random_joint_list = []

	for i in range(0, random_number_of_joint):
		random_joint_list.append( random_create_joint() )

	# Bone
	random_bone_list = []

	random_joint_rank_tab = list(range(len(random_joint_list)))

	for i in range(0, RANDOM_MIN_BONE):
		random_bone = random_create_bone(random_joint_list, random_joint_rank_tab)

		if not (random_bone in random_bone_list) and (random_bone != None):
			random_bone_list.append( random_bone )

	random_create_bone_connexity(random_joint_list, random_joint_rank_tab, random_bone_list)

	# Muscle
	random_muscle_list = []
	for i in range(0, RANDOM_MAX_MUSCLE):
		muscle = random_create_muscle(random_bone_list)
		if muscle != 0:
			random_muscle_list.append(muscle)


	return Creature(random_joint_list, random_bone_list, random_muscle_list)

### Background Scrolling
def background_scrolling_display(creature):
    max_x = creature.creature_max_position_x()
    min_x = creature.creature_min_position_x()

    if min_x > SCREEN_WIDTH:
    	creature.score_save = np.around(creature.creature_position_x()) + creature.score_save + np.around(creature.creature_position_x() - SCREEN_WIDTH)
    	for joint in creature.creature_get_joints():
    		joint.modify_position_x(joint.get_position_x()-max_x)
    	

### Main
def main():

	### Test : Square & Pole & Triangle
	joint1 = Joint(200,200,50)
	joint2 = Joint(200,400,50)
	joint3 = Joint(400,400,50)
	joint4 = Joint(400,200,50)

	bone1 = Bone(joint1,joint2,200,1)
	bone2 = Bone(joint2,joint3,200,1)
	bone3 = Bone(joint3,joint4,200,1)
	bone4 = Bone(joint4,joint1,200,1)

	muscle1 = Muscle(bone1,bone2,200,200,100)
	muscle2 = Muscle(bone4,bone3,2,200,100)

	list_muscle1 = [muscle1]
	list_bone1 = [bone1,bone2,bone3,bone4]
	list_joint1 = [joint1,joint2,joint3,joint4]

	square = Creature(list_joint1,list_bone1,list_muscle1)

	joint5 = Joint(500,200,150)
	joint6 = Joint(500,400,150)

	bone5 = Bone(joint5,joint6,200,1)

	list_muscle2 = []
	list_bone2 = [bone5]
	list_joint2 = [joint5,joint6]

	pole = Creature(list_joint2,list_bone2,list_muscle2)

	joint7 = Joint(600,300,0)
	joint8 = Joint(700,170,0)
	joint9 = Joint(800,300,0)

	bone6 = Bone(joint7,joint8,200,1)
	bone7 = Bone(joint8,joint9,200,1)
	bone8 = Bone(joint9,joint7,200,1)

	list_muscle3 = []
	list_bone3 = [bone6,bone7,bone8]
	list_joint3 = [joint7,joint8,joint9]

	triangle = Creature(list_joint3,list_bone3,list_muscle3)

	joint10 = Joint(600,300,200)
	joint11 = Joint(700,170,200)
	joint12 = Joint(800,300,200)

	bone9 = Bone(joint10,joint11,200,1)
	bone10 = Bone(joint10,joint12,200,5)

	muscle3 = Muscle(bone9,bone10,125,20,100)

	list_muscle4 = [muscle3]
	list_bone4 = [bone9,bone10]
	list_joint4 = [joint10,joint11,joint12]
	pyramid = Creature(list_joint4,list_bone4,list_muscle4)


	### TEST : SELECTION
	list_creature = [pyramid]#random_create_creature()]

	### Game Loop
	run = True
	while run:

		clock.tick(FPS)

		### Background Initialisation
		screen.blit(background, (0,0)) ### image, 0,0 = top left
		screen.blit(background, (- BACKGROUND_WIDTH,0))

		for creature in list_creature:
			
			list_muscle = creature.creature_get_muscles()
			list_bone = creature.creature_get_bones()
			list_joint = creature.creature_get_joints()

		### Physic Refreshment

			for muscle in list_muscle:
				muscle.muscle_display() # Display Refreshment 
				muscle.muscle_cycle()
				#muscle.muscle_movement_translation()

			for bone in list_bone:
				bone.bone_display() # Display Refreshment 
				bone.reajust_bone()

			for joint in list_joint:
				joint.joint_display() # Display Refreshment 
				ground_physic(joint)
				#wall(joint)
				gravity(joint)
				joint.joint_movement()
				joint.speed_limit()

			creature.creature_movement_rotation()

			creature.score_display() # Display Refreshment 

		### Display : Background

			background_scrolling_display(creature)

		### Game Exit
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

		### Game Screen Update
		pygame.display.update()

	pygame.quit()

def main_ml(creatures, t):

	### TEST : SELECTION
	list_creature = creatures

	### Temps limite
	start_time = time.time()
	time_limit = t # En secondes

	### Game Loop
	run = True
	while run:

		clock.tick(FPS)

		### Background Initialisation
		screen.blit(background, (0,0)) ### image, 0,0 = top left
		screen.blit(background, (- BACKGROUND_WIDTH,0))

		for creature in list_creature:
			
			list_muscle = creature.creature_get_muscles()
			list_bone = creature.creature_get_bones()
			list_joint = creature.creature_get_joints()

		### Physic Refreshment

			for muscle in list_muscle:
				muscle.muscle_cycle()
				#muscle.muscle_movement_translation()

			for bone in list_bone:
				bone.reajust_bone()

			for joint in list_joint:
				ground_physic(joint)
				#wall(joint)
				gravity(joint)
				joint.joint_movement()
				joint.speed_limit()

			creature.creature_movement_rotation()
			creature.stress_update()
			creature.energy_update()

		### Display : Background

			background_scrolling_display(creature)

		### Game Exit
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

		if time.time() - start_time > time_limit:
			run = False

		### Game Screen Update
		pygame.display.update()

	### Background Reinitialisation
	screen.blit(background, (0,0)) ### image, 0,0 = top left
	screen.blit(background, (- BACKGROUND_WIDTH,0))
	#pygame.quit()

def main_ml_show(creatures, t):

	### TEST : SELECTION
	list_creature = creatures

	### Temps limite
	start_time = time.time()
	time_limit = t # En secondes

	### Game Loop
	run = True
	while run:

		clock.tick(FPS)

		### Background Initialisation
		screen.blit(background, (0,0)) ### image, 0,0 = top left
		screen.blit(background, (- BACKGROUND_WIDTH,0))

		for creature in list_creature:
			
			list_muscle = creature.creature_get_muscles()
			list_bone = creature.creature_get_bones()
			list_joint = creature.creature_get_joints()

		### Physic Refreshment

			for muscle in list_muscle:
				muscle.muscle_display() # Display Refreshment 
				muscle.muscle_cycle()
				#muscle.muscle_movement_translation()

			for bone in list_bone:
				bone.bone_display() # Display Refreshment 
				bone.reajust_bone()

			for joint in list_joint:
				joint.joint_display() # Display Refreshment 
				ground_physic(joint)
				#wall(joint)
				gravity(joint)
				joint.joint_movement()
				joint.speed_limit()

			creature.creature_movement_rotation()
			creature.stress_update()
			creature.energy_update()

			creature.score_display() # Display Refreshment 

		### Display : Background

			background_scrolling_display(creature)

		### Game Exit
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

		if time.time() - start_time > time_limit:
			run = False

		### Game Screen Update
		pygame.display.update()

	### Background Reinitialisation
	screen.blit(background, (0,0)) ### image, 0,0 = top left
	screen.blit(background, (- BACKGROUND_WIDTH,0))
	#pygame.quit()


#main()