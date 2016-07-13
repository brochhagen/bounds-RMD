#####
#Read in CSV, plot results.
#####
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_context(rc={'lines.markeredgewidth': 0.5})
import csv
import sys

d = open('./results/singlescalar-a1-c0.10-l10-k3-samples10-learn1.00-g20-r50.csv','rt')
f = csv.reader(d)

def initial_population(f):
    out = []
    firstline = True
    d.seek(0)
    for i in f:
        p = np.zeros(12)
        if firstline:
            firstline = False
            continue
        p[0] = float(i[1])
        p[1] = float(i[2])
        p[2] = float(i[3])
        p[3] = float(i[4])
        p[4] = float(i[5])
        p[5] = float(i[6])
        p[6] = float(i[7])
        p[7] = float(i[8])
        p[8] = float(i[9])
        p[9] = float(i[10])
        p[10] = float(i[11])
        p[11] = float(i[12])
        out.append(p)
    return out

def final_population(f):
    out = []
    firstline = True
    d.seek(0)
    for i in f:
        p = np.zeros(12)
        if firstline:
            firstline = False
            continue
        p[0] = float(i[-12])
        p[1] = float(i[-11])
        p[2] = float(i[-10])
        p[3] = float(i[-9])
        p[4] = float(i[-8])
        p[5] = float(i[-7])
        p[6] = float(i[-6])
        p[7] = float(i[-5])
        p[8] = float(i[-4])
        p[9] = float(i[-3])
        p[10] = float(i[-2])
        p[11] = float(i[-1])
        out.append(p)
    return out


p_initial_list = initial_population(f)
p_final_list = final_population(f)

initial_mean = sum(p_initial_list) / len(p_initial_list)
final_mean = sum(p_final_list) / len(p_final_list)


sys.exit()
def results_by_lexica_single(f):
    p = np.zeros(6)
    firstline = True
    for i in f:
        if firstline:
            firstline = False
            continue
        p[int(i[1])] += float(i[-1])
    return p

Y_single = results_by_lexica_single(f1)
Y_multi = results_by_lexica_multi(f2)

print Y_single
print Y_multi
###Plots##

X = np.arange(6) #number of lexica




width = 0.35
#ymin,ymax = 0,np.max(np.array([Ya[np.argmax(results3a)],Yb[np.argmax(results3b)],Yc[np.argmax(results3c)]]))+0.01
#ax.set_xticks(np.array([len(compIndices)/2,(len(hypotheses)-len(compIndices))/2]))

fig, ax = plt.subplots()
bar1 = ax.bar(X, Y_single, width,color='r')
bar2 = ax.bar(X+width,Y_multi,width,color='y')

plt.ylabel('Mean in population')
ax.set_xticks(X+width)
ax.set_xticklabels(('L1', 'L2', 'L3', 'L4','L5','L6'))
ax.legend((bar1[0], bar2[0]), ('single scalar', '3 scalars'))
ax.margins(0.025, 0.025)
#ax.text(.5,.9,'$\alpha$ = 1, c = %r, $\lambda$ = %r, pairs = %r, k = %r',
#        horizontalalignment='center',
#        transform=ax.transAxes) % (alpha, cost, lam, lexical_pairs, k)
ax.set_title('Weighted mutation. a = %r, c = %r, lam = %r, k = %r' % (1, .1, 30, 9))

#ax.set_ylim([ymin,ymax])
plt.show()

