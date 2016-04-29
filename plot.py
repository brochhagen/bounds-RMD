#####
#Read in CSV, plot results. Not done yet#
#####
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_context(rc={'lines.markeredgewidth': 0.5})




###Plots##

X = np.arange(len(lexica))
Y_unwgh= np.sqrt(p_by_lexica)
Y_wgh = np.sqrt(p_by_lexica_wgh)

width = 0.35
#ymin,ymax = 0,np.max(np.array([Ya[np.argmax(results3a)],Yb[np.argmax(results3b)],Yc[np.argmax(results3c)]]))+0.01
#ax.set_xticks(np.array([len(compIndices)/2,(len(hypotheses)-len(compIndices))/2]))

fig, ax = plt.subplots()
bar1 = ax.bar(X, Y_wgh, width,color='r')
bar2 = ax.bar(X+width,Y_unwgh,width,color='y')

plt.ylabel('Mean in population')
ax.set_xticks(X+width)
ax.set_xticklabels(('L1', 'L2', 'L3', 'L4','L5','L6'))
ax.legend((bar1[0], bar2[0]), ('Wgh', 'Unwgh'))
ax.margins(0.025, 0.025)
#ax.text(.5,.9,'$\alpha$ = 1, c = %r, $\lambda$ = %r, pairs = %r, k = %r',
#        horizontalalignment='center',
#        transform=ax.transAxes) % (alpha, cost, lam, lexical_pairs, k)
ax.set_title('a = %r, c = %r, lam = %r, pairs = %r, k = %r' % (alpha, cost, lam, lexical_pairs, k))

#ax.set_ylim([ymin,ymax])
plt.show()

