###Plots##
#Reordering the array so that compositional languages are at indices 0-3:
c3a = [results3a[compIndices[0]],results3a[compIndices[1]], results3a[compIndices[2]],results3a[compIndices[3]]]
c3b = [results3b[compIndices[0]],results3b[compIndices[1]], results3b[compIndices[2]],results3b[compIndices[3]]]
c3c = [results3c[compIndices[0]],results3c[compIndices[1]], results3c[compIndices[2]],results3c[compIndices[3]]]

for i in range(len(compIndices)): 
    results3a = np.delete(results3a,compIndices[i])
    results3a = np.insert(results3a,i,c3a[i])

    results3b = np.delete(results3b,compIndices[i])
    results3b = np.insert(results3b,i,c3b[i])

    results3c = np.delete(results3c,compIndices[i])
    results3c = np.insert(results3c,i,c3c[i])
    
###Adding some white space to separate C from H:
for i in range(len(compIndices),len(compIndices)+10):
    results3a = np.insert(results3a,i,0)
    results3b = np.insert(results3b,i,0)
    results3c = np.insert(results3c,i,0)


X = np.arange(len(hypotheses)+10)
Ya = np.sqrt(results3a)
Yb = np.sqrt(results3b)
Yc = np.sqrt(results3c)

ymin,ymax = 0,np.max(np.array([Ya[np.argmax(results3a)],Yb[np.argmax(results3b)],Yc[np.argmax(results3c)]]))+0.01

fig, ax = plt.subplots()
ax.set_xticks(np.array([len(compIndices)/2,(len(hypotheses)-len(compIndices))/2]))
ax.set_xticklabels(('compositional', 'holistic'))
plt.ylabel('Mean in population')
ax.bar(X,Ya,width=1)
ax.margins(0.025, 0.025)
ax.text(.5,.9,'Functional pressure and iterated learning',
        horizontalalignment='center',
        transform=ax.transAxes)
ax.set_ylim([ymin,ymax])
plt.show()

fig, ax = plt.subplots()
ax.set_xticks(np.array([len(compIndices)/2,(len(hypotheses)-len(compIndices))/2]))
ax.set_xticklabels(('compositional', 'holistic'))
ax.bar(X,Yb)
ax.margins(0.025, 0.025)
ax.text(.5,.9,'Only iterated learning',
        horizontalalignment='center',
        transform=ax.transAxes)
ax.set_ylim([ymin,ymax])
plt.show()

fig, ax = plt.subplots()
ax.set_xticks(np.array([len(compIndices)/2,(len(hypotheses)-len(compIndices))/2]))
ax.set_xticklabels(('compositional', 'holistic'))
ax.bar(X,Yc)
ax.text(.5,.9,'Learning prior',
        horizontalalignment='center',
        transform=ax.transAxes)
ax.margins(0.025,0.025)
ax.set_ylim([ymin,ymax])
plt.show()


sys.exit()

tick_dist = 5.0
full_res = []
l5_dom = []
table_begs, table_ends = [], []
table_val = .8

for x in range(muRange):
    x = x * .01

    lexica_prior = np.array([mutual_prior(t.lexicon,x) for t in typeList])
    lexica_prior = lexica_prior / sum(lexica_prior)
    q = get_mutation_matrix(k,contexts)

    scores = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    sd = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    beg0,beg1,beg2,beg3,beg4,beg5 = [], [], [], [], [], []
    end0,end1,end2,end3,end4,end5 = [], [], [], [], [], []
    begs = [beg0,beg1,beg2,beg3,beg4,beg5]
    ends = [end0,end1,end2,end3,end4,end5]
    p_sum = np.zeros(len(p))

    for i in range(games):
        p = np.random.dirichlet(np.ones(len(typeList))) # unbiased random starting state
        for r in range(rounds):
            if r == 0:
                first = p
            pPrime = p * [np.sum(u[t,] * p)  for t in range(len(typeList))]
            pPrime = pPrime / np.sum(pPrime)
            p = np.dot(pPrime, q)
        record(first,p,begs,ends)
        p_sum += p

    
    for i in range(len(begs)):
        if len(begs[i]) > 0:
            scores[i] += len(ends[i])
            sd[i] = np.std([j[i] for j in begs[i]])
            begs[i] = np.around(np.sum(begs[i],axis=0) / len(begs[i]), decimals=3)
            ends[i] = np.around(np.sum(ends[i],axis=0) / len(ends[i]), decimals =3)
    if x == table_val:
        for i in range(len(begs)):
            table_begs.append(begs[i])
            table_ends.append(ends[i])
            table_scores = scores
    l5dom_sum = ends[5]
    p_sum = np.around((p_sum / games),decimals=3)
    print '### mu:', x
    print '#p_sum:', p_sum
    print '#p_l5dom:', l5dom_sum

    full_res.append(p_sum)
    l5_dom.append(l5dom_sum)

print >> w, '###### Results for table c = %r #####' % table_val
print >> w, '### Settings:'
print >> w, '#cost vector:', c
print >> w, '#Distribution over contexts:', kw1,kw2,kw3 
print >> w, 'with distribution over states:', kDict
print >> w, 'k (length of obs):', k
print >> w, 'Total independent sims %r of %r generations each' % (games,rounds)
print >> w, 'Total scores for max:', table_scores
print >> w, '#Begs:'
for i in range(len(table_begs)):
    print >> w, table_begs[i]
print >> w, '#Ends:'
for i in range(len(table_begs)):
    print >> w, table_ends[i]



res_l0 = []
res_l1 = []
res_l2 = []
res_l3 = []
res_l4 = []
res_l5 = []



X = np.arange(muRange) #positions in X

print >> o, '###### Results over mu#####'
print >> o, '### Settings:'
print >> o, '#cost vector:', c
print >> o, '#Distribution over contexts:', kw1,kw2,kw3 
print >> o, 'with distribution over states:', kDict
print >> o, 'k (length of obs):', k
print >> o, 'Total independent sims %r of %r generations each' % (games,rounds)

for i in range(len(full_res)):
    print >> o, full_res[i]
    res_l0.append(full_res[i][0])
    res_l1.append(full_res[i][1])
    res_l2.append(full_res[i][2])
    res_l3.append(full_res[i][3])
    res_l4.append(full_res[i][4])
    res_l5.append(full_res[i][5])

plt.plot(X,res_l0, label='$L_1$', marker='s', markevery=10, markersize=7)
plt.plot(X,res_l1, label='$L_2$', marker='D', markevery=10, markersize=7)
plt.plot(X,res_l2, label='$L_3$', marker='o', markevery=7, markersize=7)
plt.plot(X,res_l3, label='$L_4$', marker='<', markevery=9, markersize=8)
plt.plot(X,res_l4, label='$L_5$', marker='>', markevery=10, markersize=8)
plt.plot(X,res_l5, label='$L_6$', marker='*', markevery=10, markersize=10)


plt.ylabel('Proportion in population')
plt.xlabel('$\mu \cdot 100$')
plt.legend(loc = 'best')

plt.xticks(np.arange(min(X), max(X)+1, tick_dist))

plt.show()

#L5 centric plot:
res_dom5l0 = []
res_dom5l1 = []
res_dom5l2 = []
res_dom5l3 = []
res_dom5l4 = []
res_dom5l5 = []

print >> f, '###### (Sub)set of results over mu in which L_5 was the most represented language #####'
print >> f, '### Settings:'
print >> f, '#cost vector:', c
print >> f, '#Distribution over contexts:', kw1,kw2,kw3 
print >> f, 'with distribution over states:', kDict
print >> f, 'k (length of obs):', k
print >> f, 'Total independent sims %r of %r generations each' % (games,rounds)

for i in range(len(l5_dom)):
    print >> f, l5_dom[i]
    res_dom5l0.append(l5_dom[i][0])
    res_dom5l1.append(l5_dom[i][1])
    res_dom5l2.append(l5_dom[i][2])
    res_dom5l3.append(l5_dom[i][3])
    res_dom5l4.append(l5_dom[i][4])
    res_dom5l5.append(l5_dom[i][5])

plt.plot(X,res_dom5l0, label='$L_1$', marker='s', markevery=10, markersize=7)
plt.plot(X,res_dom5l1, label='$L_2$', marker='D', markevery=10, markersize=7)
plt.plot(X,res_dom5l2, label='$L_3$', marker='o', markevery=7, markersize=7)
plt.plot(X,res_dom5l3, label='$L_4$', marker='<', markevery=9, markersize=8)
plt.plot(X,res_dom5l4, label='$L_5$', marker='>', markevery=10, markersize=8)
plt.plot(X,res_dom5l5, label='$L_6$', marker='*', markevery=10, markersize=10)
#plt.plot(X,res_l5, label ='L5 mean', linestyle='--')

plt.ylabel('Proportion in population')
plt.xlabel('$\mu \cdot 100$')
plt.legend(loc = 'best')



plt.xticks(np.arange(min(X), max(X)+1, tick_dist))

plt.show()

