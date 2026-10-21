import random
import numpy as np
from multiprocessing import Pool
import evaluateMPI
import time
import csv
import math
import os
import copy
#import time


#particle class, initializes the particles
#dimension: number of ion channels to be optimized
class Particle:
    def __init__(self, dimension):
        
        #each channel is initialized with a random number in the boundaries set for the specific channel
        self.position = list(np.array([random.uniform(lower(i), upper(i)) for i in range(dimension)]))
       
        #the velocity of each channel is set depending on the boundaries of the channel
        #self.velocity=np.array([random.uniform(-(upper(ions[i])-lower(ions[i])), upper(ions[i])-lower(ions[i])) for i in range(dimension)])
        self.velocity=np.array([0 for i in range(dimension)])
        
        self.best_position = self.position.copy()
        self.best_score = float('inf')
        self.score = 0

#get lower bound for parameter
def lower(parameterNr):
    #nonlinear stage (d, e1, e2, f2, g, h, q):
    #  d >= 200: steep refractory exponential, needed for the 2 Hz rise at 5 ms (new bounds, used since opt-Nonlinear-Convo-CM15-fb-2hz-newbounds)
    #  g, h >= 0.01: at 0 the -log(q*PA)*h term vanishes -> no PA coupling and no supernormal dip
    #NOTE: lower() is shared with the LINEAR stage (a, b, c) - remove the d>=200 line before a linear
    #run, otherwise parameter 0 (a) is forced >= 200
    if parameterNr==0:#d
        return 200
    if parameterNr==4:
        return 0.01
    elif parameterNr==5:
        return 0.01
    return 0
    


'''
#get upper bound for parameter
#params for linear memory function: a, b, c
def upper(parameterNr):

    if parameterNr==0:
        return 1
    elif parameterNr==1:
        return 0.01
    #elif parameterNr==2:
    #    return 0.01#old bound for the subtractive -c*y form; c now multiplies +log1p(y)
    #    in memory_feedback and needs real room to have an effect (real y tops out ~30-40,
    #    log1p(40)~3.7, so c up to 1 gives a max contribution ~3.7, comparable in scale to a)
    elif parameterNr==2:
        return 1
    elif parameterNr==3:
        return 1

    #return 10
'''

#get upper bound for parameter
#params for nonlinear memory function (2D, a/b/c frozen from the linear stage): d, e1, e2, f2, g, h, q
#New bounds (used since opt-Nonlinear-Convo-CM15-fb-2hz-newbounds). e1, e2 and f2 are capped because exp(-d*(x-e1)) and exp(-f2*(x-e2)) overflow for large
#d*e1 / f2*e2 (with wider caps most evaluations returned scores > 1e3); good solutions lie well inside.
def upper(parameterNr):

    if parameterNr==0:#d: steepness of refractory-phase recovery (originally 50; 500 allows a ms time scale)
        return 500
    elif parameterNr==1:#e1: horizontal shift 1 (originally 1)
        return 0.02
    elif parameterNr==2:#e2: horizontal shift 2 (originally 1)
        return 0.2
    elif parameterNr==3:#f2: decay rate of supernormal-phase exponential
        return 30
    elif parameterNr==4:#g: vertical offset
        return 10
    elif parameterNr==5:#h: depth/PA-coupling of supernormal phase (log-coefficient)
        return 10
    elif parameterNr==6:#q: PA multiplier inside the log term
        return 20



#check if lower or upper bound is reached
def checkBound(pos, dimension):
    #print("###")
    #print("Particle position:"+str(pos))
    for i in range(dimension):
        if pos[i] < lower(i):
            #print("particle reached lower bound: "+str(pos[i]))
            pos[i]=lower(i)
        elif pos[i] > upper(i):
            #print("particle reached upper bound: "+str(pos[i]))
            pos[i]=upper(i)
        #pos[i]=round(pos[i],7)
    #print(pos)
    return list(pos)

'''
def checkVelocity(velocity, dimension):
    for i in range(dimension):
        if abs(velocity[i]) > (upper(ions[i])-lower(ions[i]))*0.1:
            s=np.sign(velocity[i])
            velocity[i]=s*(upper(ions[i])-lower(ions[i]))*0.1
    return velocity
'''           

#update particle position
#particle: particle to be updated
#global_best_position: best position of all particles
#inertia_weight: weight for velocity
#cognitive_weight: weight for best position of particle
#social_weight: weight for best global position of all particles
#dimension: number of ion channels to be optimized
def update_particle(particle, global_best_position, randomParticle, inertia_weight, cognitive_weight, social_weight, c2, randPart_weight, c3, rand_velocity_weight, dimension, num_iterations, i, bestScore1, bestScore2):
    r1, r2, r3 = random.random(), random.random(), random.random()
    #print("update_particle: global_best_position",global_best_position)
    #print("update_particle: particle.position",particle.position)
    cognitive_component = np.array([(particle.best_position[i] - particle.position[i]) for i in range(dimension)])
    social_component = np.array([(global_best_position[i] - particle.position[i]) for i in range(dimension)])
    
    randPart_component = np.array([(randomParticle.best_position[i] - particle.position[i]) for i in range(dimension)])
    rand_velocity = np.array([random.uniform(-upper(i)/2, upper(i)/2) for i in range(dimension)])
    
    #inertia_weight is updated
    w_min=0.2
    w_max=1
    if i==0:
        inertia_weight=w_min
    else:
        inertia_weight = max(w_min, inertia_weight - ((w_max-w_min)/num_iterations)*i*(bestScore1-bestScore2))
        if inertia_weight==float('inf'):
            inertia_weight=w_max*i
        
        #print(bestScore1)
        #print(bestScore2)
        #print(inertia_weight - ((w_max-w_min)/num_iterations)*i*(bestScore1-bestScore2))
    
    #constriction factor
    psi = 2/abs(2-(c2+c3)**2-5*(c2+c3))
    
    particle.velocity = psi * (inertia_weight * particle.velocity 
                               + cognitive_weight * r1 * cognitive_component 
                               + social_weight * r2 * c2 * social_component 
                               + randPart_weight * r3 * c3 * randPart_component 
                               + rand_velocity_weight * rand_velocity)
    #print("Inertia",inertia_weight * particle.velocity)
    #print("Cognitve",cognitive_weight * r1 *cognitive_component)
    #print("Social", social_weight * r2 * social_component)
    #print("RandParticle", randPart_weight * r3 * c3 * randPart_component)
    #print("RandVelocity", rand_velocity_weight * rand_velocity)
    #print("Velocity:"+str(particle.velocity))
    particle.position += particle.velocity
    particle.position = checkBound(particle.position, dimension)
    
    particle.score = 0#?????

