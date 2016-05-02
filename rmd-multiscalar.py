#####
#RMD for unweighted and weighted (community) learning with Bayesian (iterated) learning as M. 
#3 pairs of scalar items, six lexica per scalar pair. 
#2 possible signaling behaviors: literal or gricean
#12 types (6 lexica * 2 signaling behaviors) per signaling pair
#6*6*6 = 216  literal types, 216 gricean types, 432 types in total
#####


import numpy as np
#np.set_printoptions(threshold=np.nan)
from random import sample
from itertools import product, permutations, combinations_with_replacement
from player import LiteralPlayer,GriceanPlayer
import sys 
import datetime
import csv


alpha = 1 # rate to control difference between semantic and pragmatic violations
cost = 0.9 # cost for LOT-concept with upper bound
lam = 30 # soft-max parameter
k = 3  # number of learning observations
mc = 1000 #amount of samples from OBS when k > 4

gens = 30 #number of generations per simulation run
runs = 100 #number of independent simulation runs


lexical_pairs = 3 #number of 2x2 matrices
states = 2 #number of states
messages = 2 #number of messages


f_unwgh_mean = csv.writer(open('./results/multiscalar-unwgh-mean-a%d-c%f-l%d-k%d-g%d-r%d.csv' %(alpha,cost,lam,k,gens,runs),'wb')) #file to store each unweighted simulation run after n generations
f_wgh_mean = csv.writer(open('./results/multiscalar-wgh-mean-a%d-c%f-l%d-k%d-g%d-r%d.csv' %(alpha,cost,lam,k,gens,runs),'wb')) #file to store each weighted simulation run after n generations

f_q = csv.writer(open('./results/multiscalar-q-matrix-a%d-c%f-l%d-k%d-g%d-r%d.csv' %(alpha,cost,lam,k,gens,runs),'wb')) #file to store Q-matrix


print '#Starting, ', datetime.datetime.now()
lexica = [np.array( [[0.,0.],[1.,1.]] ), np.array( [[1.,1.],[0.,0.]] ), np.array( [[1.,1.],[1.,1.]] ), np.array( [[0.,1.],[1.,0.]] ), np.array( [[0.,1.],[1.,1.]] ), np.array( [[1.,1.],[1.,0.]] )]

def types(l):
    """outputs list of types from list of lexica input.""" 
    typeList = []
    for i in l:
        typeList.append(LiteralPlayer(alpha,i))
    for i in l:
        typeList.append(GriceanPlayer(alpha,lam,i))
    return typeList 

typeList = types(lexica)


def lex_prior(l):
    """outputs learning prior vector from list of lexica input. Assumes twice as many types than lexica. First half of the vector is literal, second half is gricean."""
    cost_v = np.zeros(len(lexica))
    for j in range(len(l)):
        lexicon_score = 0.
        for i in range(l[j].shape[1]):
            if (i == 0 or i == 1) and l[j][0,i] > 0 and l[j][1,i] == 0:
                lexicon_score += cost
        cost_v[j] = states - lexicon_score
    cost_v =  np.array([sum(p) for p in product(cost_v,repeat=lexical_pairs)]) #for all len(lexica)**(#states) "big" lexica 
    return np.append(cost_v,cost_v) #doubling for first half literal, second half gricean

lex_prior = lex_prior(lexica)
lexica_prior = lex_prior / sum(lex_prior)

#def labels_by_bound(prior_list):
#    """Outputs list of labels by lexicalized bounds from learning prior vector."""
#    unique_vals = sorted(list(set(prior_list))) #sorted just in case
#    labels = []
#    for i in unique_vals:
#        labels.append([j for j,x in enumerate(prior_list) if x == i])
#    return labels
#bound_labels = labels_by_bound(lexica_prior)

print '#Computing likelihood, ', datetime.datetime.now()
likelihoods = np.array([t.sender_matrix for t in typeList])

def m_permutation(m,n):
    """Returns matrix n-permutation. Used to reuse likelihood matrix computed for a single scalar pair"""
    r,c = m.shape

    arr_i = np.array(list(product(range(r), repeat=n)))
    arr_j = np.array(list(product(range(c), repeat=n)))

    out = m.ravel()[(arr_i*c)[:,None,:] + arr_j].prod(2)
    return out

#def m_combination(m,n):
## Get input array's shape
#    r,c = m.shape
#
#    # Setup arrays corresponding to labels i and j
#    arr_i = np.array(list(combinations_with_replacement(range(r), n)))
#    arr_j = np.array(list(combinations_with_replacement(range(c), n)))
#
## Use linear indexing with ".ravel()" to extract elements.
## Perform elementwise product along the rows for the final output
#    out = m.ravel()[(arr_i*c)[:,None,:] + arr_j].prod(2)
#    return out


def labels(s,m,lex):
    """Returns list of labels that specifies which lexica are assigned to what type."""
    a = [i for i in range(len(lexica))]
    b = [i for i in range(len(lexica), 2* len(lexica))]
    lab1 = [list(p) for p in product(a, repeat=lex)]
    lab2 = [list(p) for p in product(b, repeat=lex)]
    return lab1 + lab2

labels = labels(states,messages,lexical_pairs)


def normalize(m):
    """Matrix row-wise normalization"""
    return m / m.sum(axis=1)[:, np.newaxis]

def get_obs(k):
    """Returns summarized counts of k-length <s_i,m_j> observations as [#(<s_0,m_0>), #(<s_0,m_1), #(<s_1,m_0>, #(s_1,m_1)], sum[...] = k"""
    inputx = [x for x in list(product(range(states), repeat=k))] #k-tuple where the i-th observed state was state k_i 
    outputy = [y for y in list(product(range(messages),repeat=k))] #k-tuple where the i-th observed message was k_i 
    D = list(product(inputx,outputy)) #list of all possible state-message combinations
    if k > 4: D = sample(D,mc) #sample from D if sequence > 4 to manage computational load
    
    out = []
    for i in range(len(D)): #this can probably be made more succint but it's a straightforward way to summarize counts
        s0m0 = 0
        s0m1 = 0
        s1m0 = 0
        s1m1 = 0
        for j in range(k):
            if D[i][0][j] == 0:
                if D[i][1][j] == 0:
                    s0m0 += 1
                else: 
                    s0m1 += 1
            else:
                if D[i][1][j] == 0:
                    s1m0 += 1
                else:
                    s1m1 += 1
        out.append([s0m0,s0m1,s1m0,s1m1])
    return out


def get_obs_likelihood(k):
    obs = get_obs(k)
    out1 = np.ones([len(likelihoods)/2, len(obs)]) # matrix to store results in for literal
    out2 = np.ones([len(likelihoods)/2, len(obs)]) # matrix to store results in for gricean
    #Literal and gricean are not computed in a single matrix because combination of lexica should be within a signaling behavior.

    for lhi in range(len(likelihoods)/2):
        for o in range(len(obs)):
            out1[lhi,o] = (likelihoods[lhi,0,0]**obs[o][0] * (likelihoods[lhi,0,1])**(obs[o][1]) *\
                         likelihoods[lhi,1,0]**obs[o][2] * (likelihoods[lhi,1,1])**(obs[o][3]))
            out2[lhi,o] = (likelihoods[lhi+len(likelihoods)/2,0,0]**obs[o][0] * (likelihoods[lhi+len(likelihoods)/2,0,1])**(obs[o][1]) *\
                         likelihoods[lhi+len(likelihoods)/2,1,0]**obs[o][2] * (likelihoods[lhi+len(likelihoods)/2,1,1])**(obs[o][3]))
    
    pOut1 = m_permutation(out1,lexical_pairs) #combine literal lexica
    pOut2 = m_permutation(out2,lexical_pairs) #combine gricean lexica
    lh = np.concatenate((normalize(pOut1),normalize(pOut2)),axis=0) #Glue literal and gricean matrices after combinations
    return lh


def get_mutation_matrix(k):
    # we want: Q_ij = \sum_d p(d|t_i) p(t_j|d); this is the dot-product of the likelihood matrix and the posterior
    lhs = get_obs_likelihood(k)
    post = normalize(lexica_prior * np.transpose(lhs))
    return np.dot(lhs, post)

def weighted_mutation(p,q):
    """Mutation by community learning instead of standard mutation"""
    m = np.zeros([len(p),len(p)])
    for i in range(len(p)):
        for j in range(len(p)):
            m[i,j] = p[j] * q[i,j]
    return normalize(m)

def get_utils():
    #Compute utilities for a single lexical pair first
    out = np.zeros([len(typeList), len(typeList)])
    for i in range(len(typeList)):
        for j in range(len(typeList)):
            out[i,j] = (np.sum(typeList[i].sender_matrix * np.transpose(typeList[j].receiver_matrix)) + \
                     np.sum(typeList[j].sender_matrix * np.transpose(typeList[i].receiver_matrix))) / 4

    #Combine utilities for 3 x lexical pairs
    macro_out = np.zeros([len(labels), len(labels)])
    for i in range(len(labels)):
        for j in range(len(labels)):
                macro_out[i,j] = (out[labels[i][0],labels[j][0]] + out[labels[i][1],labels[j][1]] + out[labels[i][2],labels[j][2]]) / 3.
    return macro_out


print '#Computing Q, ', datetime.datetime.now()

q = get_mutation_matrix(k)

for i in q:
    f_q.writerow(i)

print '#Computing utilities, ', datetime.datetime.now()

u = get_utils()

###Multiple runs
print '#Beginning multiple runs, ', datetime.datetime.now()



f_unwgh_mean.writerow(["stype","l1","l2","l3","proportion"])
f_wgh_mean.writerow(["stype","l1","l2","l3","proportion"])


p_sum = np.zeros(len(labels))
p_sum_wgh = np.zeros(len(labels))

for i in xrange(runs):

    p = np.random.dirichlet(np.ones(len(labels))) # unbiased random starting state

    for r in range(gens): #unweighted mutation
        pPrime = p * [np.sum(u[t,] * p)  for t in range(len(labels))]
        pPrime = pPrime / np.sum(pPrime)
        p = np.dot(pPrime, q)

    p_sum += p

    p = np.random.dirichlet(np.ones(len(labels))) # unbiased random starting state

    for r in range(gens):  #weighted (community) mutation
        pPrime = p * [np.sum(u[t,] * p)  for t in range(len(labels))]
        pPrime = pPrime / np.sum(pPrime)
        p = np.dot(pPrime, weighted_mutation(p,q))

    p_sum_wgh += p

    print i, datetime.datetime.now()
    
    
p_mean = p_sum / runs
p_wgh_mean = p_sum_wgh / runs

def record_by_type(p_vec,csv_file):
    for i in range(len(p_vec)):
        if i < len(p_vec)/2:
            stype = 'literal'
        else: stype = 'gricean'
        l1,l2,l3 = labels[i][0],labels[i][1],labels[i][2]
        if l1 > len(lexica)-1: l1 = l1 - len(lexica)
        if l2 > len(lexica)-1: l2 = l2 - len(lexica)
        if l3 > len(lexica)-1: l3 = l3 - len(lexica)

        csv_file.writerow([stype,l1,l2,l3,str(p_vec[i])])

record_by_type(p_mean,f_unwgh_mean)
record_by_type(p_wgh_mean,f_wgh_mean)


def lexica_vec(p_vec): 
    p_by_lexica = np.zeros(len(lexica))
    for i in xrange(len(p_vec)):
        prop = 1/3. * p_vec[i]
        l1,l2,l3 = labels[i][0], labels[i][1],labels[i][2]
        if l1 > 5: l1 = l1 - 6
        if l2 > 5: l2 = l2 - 6
        if l3 > 5: l3 = l3 - 6
        p_by_lexica[l1] += prop
        p_by_lexica[l2] += prop
        p_by_lexica[l3] += prop
    return p_by_lexica

print '### Quick overview of results###'
print 'Unweighted mean by lexica:', lexica_vec(p_mean)
print '###'
print 'Weighted mean by lexica:', lexica_vec(p_wgh_mean)
sys.exit()


