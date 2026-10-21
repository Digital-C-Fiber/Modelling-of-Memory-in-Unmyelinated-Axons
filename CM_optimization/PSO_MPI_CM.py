import random
from mpi4py import MPI
from collections import deque
import time
import math
import particleSwarm2GEPSO as gepso
import evaluateMPI
import os
import csv
import sys
import numpy as np
import pandas as pd
import ast

import shutil
import glob


#print in file
#text: text to be printed
#name: folder name, where to save the file
def myPrint(text, name):
    #print(text)
    with open('Results/'+str(name)+'/Messages/messagesMain.txt', 'a', newline='') as f:
        csv.writer(f).writerow([text])

#main function for particle swarm optimization
#num_dimensions: number of dimensions, i.e. ion channels and other parameters to be optimized, 
#num_particles: number of particles, 
#num_iterations: number of iterations, 
#num_protocols: number of stimulation protocols used for optimization, 
#inertia_weight, cognitive_weight, social_weight, c2, randPart_weight, c3, rand_velocity_weight: weights for the optimization, see Sedighizadeh, 2020 on how to set them, 
#name: name of optimization, can be chosen arbitrarily, used for folder and filenames, 
#positionFromFile: if true: choose starting postition of particles from file "particles.csv", which contains position of particles
def particle_swarm_optimization(num_dimensions, num_particles, num_iterations, num_protocols, inertia_weight, cognitive_weight, social_weight, c2, randPart_weight, c3, rand_velocity_weight, name, positionFromFile=False, positionFromParticle=False):
    
    global_best_score_prev=float('inf')
    global_best_score=float('inf')
    global_best_position=list(np.array([random.uniform(gepso.lower(i), gepso.upper(i)) for i in range(num_dimensions)]))#random position in case there are no valid particles

    #create folders
    if not os.path.exists('Results'):
        os.mkdir('Results')
    
    if not os.path.exists('Results/'+str(name)):
        os.mkdir('Results/'+str(name))
        
    if not os.path.exists('Results/'+str(name)+'/Messages'):
        os.mkdir('Results/'+str(name)+'/Messages')

    #create file to save particle position and score
    for i in range(num_particles):
        filename = 'Results/'+str(name)+'/'+str(name)+'particle'+str(i)+'.csv'
        #creates file, deletes content, if file already exists
        with open(filename,'w', newline='') as f:
            csv.writer(f).writerow(["Position", "Score"])

    #create file to save best scores
    filenameBest = 'Results/'+str(name)+'/'+str(name)+'_bestParticles.csv'
    with open(filenameBest,'w', newline='') as f:
            csv.writer(f).writerow(["Position", "Score", "ParticleNr", "IterationNr"])
            
    #create file to save invalid particles
    filenameInvalid = 'Results/'+str(name)+'/'+str(name)+'_invalidParticles.csv'
    with open(filenameInvalid,'w', newline='') as f:
            csv.writer(f).writerow(["Position"])
    
    #create files to store all messages
    with open('Results/'+str(name)+'/Messages/messagesMain.txt', 'w', newline='') as f:
        csv.writer(f).writerow(["Messages"])
        
    with open('Results/'+str(name)+'/Messages/messagesParticlevalid.txt', 'w', newline='') as f:
        csv.writer(f).writerow(["Messages"])
        
    with open('Results/'+str(name)+'/Messages/messagesParticleErrors.txt', 'w', newline='') as f:
        csv.writer(f).writerow(["Messages"])
        
    for i in range(0, num_particles):
        with open('Results/'+str(name)+'/Messages/messagesParticle'+str(i)+'.txt', 'w', newline='') as f:
            csv.writer(f).writerow(["Messages"])
    
    swarm=[]
    
    if positionFromFile:#start with postions from file from previous optimization process, including scores
        myPrint("Load starting particles from file", name)
        #load file
        partilces = pd.read_csv("particles.csv")

        #initialize swarm
        for i in range(num_particles):
            swarm.append(gepso.Particle(num_dimensions))
            pos=ast.literal_eval(partilces["Position"][i])#to list
            swarm[i].position = pos
           
            swarm[i].best_position = pos
            swarm[i].score = partilces["Score"][i]
            swarm[i].best_score = partilces["Score"][i]

            if partilces["Score"][i] < float("inf"):
                swarm[i].valid = True
            else:
                swarm[i].valid = False
            #find global best
            if partilces["Score"][i]<global_best_score:
                global_best_score=partilces["Score"][i]
                global_best_position=pos

        
        #update particles    
        for i in range(num_particles):   
            r1 = int(random.random()*len(swarm))
            gepso.update_particle(swarm[i], global_best_position, swarm[r1], inertia_weight, cognitive_weight, social_weight, c2, randPart_weight, c3, rand_velocity_weight, num_dimensions, num_iterations, i, global_best_score, global_best_score_prev)

    else:#find valid particles
        myPrint("Find/Load particles", name)
        start_time = time.time()

        if positionFromParticle:
            myPrint("Load starting particles from file", name)
            #load file
            partilceFile = pd.read_csv("particle.csv")       
            partilceFilePos=ast.literal_eval(partilceFile["Position"][0])#to list

        for j in range(size-1):
            swarm.append(gepso.Particle(num_dimensions))#create particles randomly  

            if positionFromParticle:
                #initialize swarm
                if j==0:#particle from file
                    pos=partilceFilePos
                else:
                    #other particles are randomly distributed around particle from file
                    pos=list(np.array([random.uniform(partilceFilePos[i]*0.9, partilceFilePos[i]*1.1) for i in range(len(partilceFilePos))]))

                swarm[j].position = pos                                        
    
    #main pso iteration
    for i in range(num_iterations):
        start_time = time.time()
        myPrint("############################## iteration: "+str(i), name)
        
        for particle_id in range(num_particles):
            myPrint("Particle "+str(particle_id)+" position: "+str(swarm[particle_id].position), name)
         
        #run protocols for each particle
        rankCounter=1
        myPrint("Start evaluation of protocols", name)
        for particle_id in range(num_particles):
            # run all protocls
            for protocol in range(0, num_protocols):#protocol 0 is to test is particle is valid
                #myPrint("particle "+str(particle_id)+" protocol "+str(protocol)+" is sent to rank "+str(rankCounter))
                particle_send = (particle_id, swarm[particle_id].position, protocol)
                comm.send(particle_send, dest=rankCounter)# send particle positions to other processes/nodes
                rankCounter+=1
        myPrint("All particles are send to processes", name)
        
        idle=0
        # loop until all particles are ready/ all scores recieved
        while(1):
            particle = comm.recv(source = MPI.ANY_SOURCE, status=status)
            particle_id = particle[0]#particle id
            particle_score = particle[1]#particle score
            particle_protocol = particle[2]

            swarm[particle_id].score += particle_score

            idle+=1
            myPrint("Main recieved "+str(idle)+"/"+str(rankCounter-1)+" particle: "+str(particle_id)+" score= "+str(particle_score)+" protocol= "+ str(particle_protocol)+ ", time: "+str((time.time() - start_time)/60)+" min", name)
            #myPrint("Main: recieved "+str(idle)+"/"+str(rankCounter-1)+", time: "+str((time.time() - start_time)/60)+" min", name)

            #if all messages are recieved, break loop
            if idle==rankCounter-1:
                myPrint("Main: all messages recieved", name)
                break
                    
        myPrint("Time to run all protocols for all particles: "+str((time.time() - start_time)/60)+" min", name)
        start_time = time.time()

        for particle_id in range(num_particles):
            swarm[particle_id].score = swarm[particle_id].score/(num_protocols+1)#protocols and score for balancing pump
            particle_score = swarm[particle_id].score
            myPrint("Main: Particle "+str(particle_id)+" full score "+str(particle_score), name)

            #save position and score
            filename = 'Results/'+str(name)+'/'+str(name)+'particle'+str(particle_id)+'.csv'
            with open(filename,'a', newline='') as f:
                csv.writer(f).writerow([swarm[particle_id].position, particle_score])

            #score better than previous score
            if particle_score < swarm[particle_id].best_score:
                myPrint("Main: Set best score for particle "+str(particle_id), name)
                swarm[particle_id].best_position = list(swarm[particle_id].position)
                swarm[particle_id].best_score = float(particle_score)

            #set global best score and position
            if particle_score < global_best_score :
                myPrint("Main: Set global best score for particle "+str(particle_id), name)
                global_best_score_prev = global_best_score
                global_best_score = float(particle_score)
                global_best_position = list(swarm[particle_id].position)
                global_best_particleNr=particle_id
                copyBestFiles(particle_id)
                
                #save best scores 
                with open(filenameBest,'a', newline='') as f:
                    csv.writer(f).writerow([global_best_position, global_best_score, global_best_particleNr, i])

            #stop optimization if score is good enough
            #if global_best_score < 0.001:
             #   print("best score < 0.001: break")
              #  break

            #update all particles
            r1 = int(random.random()*len(swarm))
            myPrint("Main: update particle "+str(particle_id), name)
            gepso.update_particle(swarm[particle_id], global_best_position, swarm[r1], inertia_weight, cognitive_weight, social_weight, c2, randPart_weight, c3, rand_velocity_weight, num_dimensions, num_iterations, i, global_best_score, global_best_score_prev)
            
        
        myPrint("Time to update particles: "+str((time.time() - start_time)/60)+" min", name)
        
      
    #except Exception as error:
        # handle the exception
     #   print("An exception occurred in PSO_MPI:", type(error).__name__, "–", error) 
    #finally:#gets executed regardless of if there is an exception or not
        #send tag to to end programm
    
    for k in range(1,size):
        comm.send(0, dest=k, tag=200)   

    myPrint("########################### Optimization ready", name)
    myPrint('Best position: '+str(global_best_position), name)
    myPrint('Best score: '+str(global_best_score), name)

def copyBestFiles(particle_id):
    filenamesList = glob.glob('Results/'+str(name)+'/*particle'+str(particle_id)+'.csv')
    for file in filenamesList:
        shutil.copyfile(file, file.replace('particle'+str(particle_id),'particlebest'))
    
########################################################################################################################
############################# run optimization #########################################################################

#global variables
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
status = MPI.Status()


#Current settings = those of the latest nonlinear run (its results: Results/opt-Nonlinear-Convo-CM15-fb-2hz-025-newbounds):
#score = MAE to the 2 Hz reference + 0.3 * MAE to the CM 0.25 Hz data (evaluateMPI.evalRecoveryCycleCM),
#bounds in particleSwarm2GEPSO.py (d [200,500], e1<=0.02, e2<=0.2, f2<=30). CSV score = raw score / 2.
#Give every new run its own name - the safety guard below refuses to overwrite an existing results folder.
name="opt-Nonlinear-Convo-new-run" #to compare different optimizations

#SAFETY GUARD: starting a run opens every result file of Results/<name> in write mode, i.e. it ERASES the
#results of an earlier run with the same name. Stop instead if that folder already holds results.
#Rank 0 checks and broadcasts the decision, so all MPI processes stop together (no hanging workers).
#To deliberately rerun under the same name, rename or delete the old folder first.
if rank==0:
    existing_results=False
    for f in glob.glob('Results/'+str(name)+'/'+str(name)+'*.csv'):
        with open(f) as fh:
            if len(fh.readlines())>1:#more than the header line -> real results
                existing_results=True
                break
else:
    existing_results=None
existing_results=comm.bcast(existing_results, root=0)
if existing_results:
    if rank==0:
        print("STOPPED: Results/"+str(name)+" already contains results. Change 'name' in PSO_MPI_CM.py to start a new run.")
    sys.exit(1)

if rank==0:
    start_time = time.time()

    dimensions=7
    num_particles=14
    num_iterations= 20000
    num_protocols=1
    inertia_weight = 0.2 #w1
    cognitive_weight = 0.4*4 #w2*c1
    social_weight = 0.4*0.5 #w3*alpha1
    c2 = 4
    randPart_weight = 0.4*3 #w4*alpha2
    c3 = 4
    rand_velocity_weight = 0.9*3*4 #w5*alpha3*c4
    
    #only one of these can be true, if both are false, the particles are calculated rondomly
    positionFromFile=False
    positionFromParticle=False#seeding off; if True, particle.csv must lie inside the bounds (it is scored before clipping)

    #start particle swarm optimization
    particle_swarm_optimization(dimensions, num_particles, num_iterations, num_protocols, inertia_weight, cognitive_weight, social_weight, c2, randPart_weight, c3, rand_velocity_weight, name, positionFromFile, positionFromParticle)
    
    myPrint("time taken: "+str((time.time()-start_time)/60)+" min", name)
    
else:
    while(1):
        particle = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
        
        #check tag if all iterations are done
        tag = status.Get_tag()
        if tag == 200:
            #all iterations are done, end program
            break
        
        particle_id = particle[0]
        particle_position= particle[1]
        particle_protocol = particle[2]
        
        args=particle_position
        args.append(name)
        args.append(particle_id)
        args.append(particle_protocol)

        score = evaluateMPI.runEvalParticleCM_2(args)#needs to be changed for different parts of the optimization
        
        #send score to main process
        obj_sent = (particle_id, score, particle_protocol)
        comm.send(obj_sent, dest=0)
        
        
 
        