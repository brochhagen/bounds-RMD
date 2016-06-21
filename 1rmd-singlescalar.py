#####
#RMD with parametrized iterated parental learning 
#1 pairs of scalar items, six lexica per scalar pair. 
#2 possible signaling behaviors: literal or gricean
#12 types (6 lexica * 2 signaling behaviors) per signaling pair
#6 literal types, 6 gricean types, 12 types in total
#####

import numpy as np
np.set_printoptions(threshold=np.nan)
from random import sample
from itertools import product
from player import LiteralPlayer,GriceanPlayer
import sys 
import datetime
import csv

#####
l1,l2,l3,l4,l5,l6 = np.array( [[0.,0.],[1.,1.]] ), np.array( [[1.,1.],[0.,0.]] ), np.array( [[1.,1.],[1.,1.]] ), np.array( [[0.,1.],[1.,0.]] ), np.array( [[0.,1.],[1.,1.]] ), np.array( [[1.,1.],[1.,0.]] )

alpha = 1# rate to control difference between semantic and pragmatic violations
cost = 0.1 # cost for LOT-concept with upper bound
lam = 10 # soft-max parameter
k = 3  # length of observation sequences
sample_amount = 10 #amount of k-length samples for each production type

gens = 20 #number of generations per simulation run
runs = 50 #number of independent simulation runs

states = 2 #number of states
messages = 2 #number of messages

learning_parameter = 1 #prob-matching = 1, increments approach MAP
state_freq = np.ones(states) / float(states) #frequency of states s_1,...,s_n 


f_mean = csv.writer(open('./results/singlescalar-mean-a%d-c%.2f-l%d-k%d-samples%d-learn%.2f-g%d-r%d.csv' %(alpha,cost,lam,k,sample_amount, learning_parameter, gens,runs),'wb')) #file to store mean results
######



print '#Starting, ', datetime.datetime.now()

t1,t2,t3,t4,t5,t6 = LiteralPlayer(alpha,l1), LiteralPlayer(alpha,l2), LiteralPlayer(alpha,l3), LiteralPlayer(alpha,l4), LiteralPlayer(alpha,l5), LiteralPlayer(alpha,l6)
t7,t8,t9,t10,t11,t12 =  GriceanPlayer(alpha,lam,l1), GriceanPlayer(alpha,lam,l2), GriceanPlayer(alpha,lam,l3), GriceanPlayer(alpha,lam,l4), GriceanPlayer(alpha,lam,l5), GriceanPlayer(alpha,lam,l6)

typeList = [t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12]

print '#Computing likelihood, ', datetime.datetime.now()
likelihoods = np.array([t.sender_matrix for t in typeList])

lexica_prior = np.array([2, 2- 2* cost, 2, 2 - cost , 2 , 2-cost, 2, 2- 2* cost, 2, 2 - cost , 2 , 2-cost])
lexica_prior = lexica_prior / sum(lexica_prior)

def normalize(m):
    return m / m.sum(axis=1)[:, np.newaxis]

def summarize_counts(lst):
    """summarize counts for tuples of k-states and k-messages""" 
    counter = [0 for _ in xrange(states**messages)]
    for i in xrange(len(lst)):
        s,m = lst[i][0] *2, lst[i][1]
        counter[s+m] += 1
    return counter

def get_obs(k):
    """Returns summarized counts of k-length <s_i,m_j> production observations as [#(<s_0,m_0>), #(<s_0,m_1), #(<s_1,m_0>, #(s_1,m_1)], ...]] = k"""
    s = list(xrange(states))
    m = list(xrange(messages))
    atomic_observations = list(product(s,m))
   
    obs = [] #store all produced k-length (s,m) sequences 
    for t in xrange(len(typeList)):
        produced_obs = [] #store k-length (s,m) sequences of a type
        production_vector = likelihoods[t].flatten()
        doubled_state_freq = np.column_stack((state_freq,state_freq)).flatten() # P(s)
        sample_vector = production_vector * doubled_state_freq #P(s) * P(m|s,t_i)
        for i in xrange(sample_amount):
            sample_t = [np.random.choice(len(atomic_observations),p=sample_vector) for _ in xrange(k)]
            sampled_obs = [atomic_observations[i] for i in sample_t]
            produced_obs.append(summarize_counts(sampled_obs))
        obs.append(produced_obs)
    return obs


def get_likelihood(obs):
    out = np.zeros([len(likelihoods), len(obs)]) # matrix to store results in
    for lhi in range(len(likelihoods)):
        for o in range(len(obs)):
            out[lhi,o] = likelihoods[lhi,0,0]**obs[o][0] * (likelihoods[lhi,0,1])**(obs[o][1]) *\
                         likelihoods[lhi,1,0]**obs[o][2] * (likelihoods[lhi,1,1])**(obs[o][3]) # first line is some, second is all
    return out


def get_mutation_matrix(k):
    obs = get_obs(k) #get production data from all types
    out = np.zeros([len(likelihoods),len(likelihoods)]) #matrix to store Q

    for parent_type in xrange(len(likelihoods)):
        type_obs = obs[parent_type] #Parent production data
        lhs = get_likelihood(type_obs) #P(parent data|t_i) for all types
        post = normalize(lexica_prior * np.transpose(lhs)) #P(t_j|parent data) for all types; P(d|t_j)P(t_j)
        parent_production_q = np.dot(lhs,post)**learning_parameter 
        
        out[parent_type] = parent_production_q[parent_type] #store the parents row Q_{parent_type}

    return normalize(out)

def get_utils():
    out = np.zeros([len(typeList), len(typeList)])
    for i in range(len(typeList)):
        for j in range(len(typeList)):
            out[i,j] = (np.sum(typeList[i].sender_matrix * np.transpose(typeList[j].receiver_matrix)) + \
                     np.sum(typeList[j].sender_matrix * np.transpose(typeList[i].receiver_matrix))) / 4
    return out


print '#Computing utilities, ', datetime.datetime.now()
u = get_utils()


###Multiple runs
print '#Beginning multiple runs, ', datetime.datetime.now()

f_mean.writerow(["sig_behavior","lexicon","proportion"])
p_sum = np.zeros(len(typeList)) #vector to store results from a run

for i in xrange(runs):
    q = get_mutation_matrix(k) #compute new Q for each new run, as it now depends on sampled observations
    p = np.random.dirichlet(np.ones(len(typeList))) # unbiased random starting state

    for r in range(gens):
        pPrime = p * [np.sum(u[t,] * p)  for t in range(len(typeList))]
        pPrime = pPrime / np.sum(pPrime)
        p = np.dot(pPrime, q)
    p_sum += p

p_mean = p_sum / runs


def record_by_type(p_vec,csv_file):
    for i in range(len(p_vec)):
        if i < len(p_vec)/2:
            stype = 'literal'
        else: stype = 'gricean'
        if i < len(p_vec)/2:
            lexicon = i
        else:
            lexicon = i - len(p_vec)/2
        csv_file.writerow([stype,str(lexicon),str(p_vec[i])])

record_by_type(p_mean,f_mean)


print '###Overview of results###', datetime.datetime.now()
print 'Parameters: alpha = %d, c = %.2f, lambda = %d, k = %d, samples per type = %d, learning parameter = %.2f, generations = %d, runs = %d' % (alpha, cost, lam, k, sample_amount, learning_parameter, gens, runs)
print 'Mean by type:'
print p_mean


sys.exit()

def lexica_vec(p_vec): 
    p_by_lexica = np.zeros(6)
    for i in xrange(len(p_vec)):
        if i < len(p_vec)/2:
            p_by_lexica[i] += p_vec[i]
        else:
            r = i - len(p_vec)/2
            p_by_lexica[r] += p_vec[i]
    return p_by_lexica

