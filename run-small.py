import modsinglescalar as rmd
#parameter order for run(*) is run(alpha,cost,lam,k,sample_amount, learning_parameter,gens,runs)

a = 1
lam = [10,30]
cost = [0.01,0.05,0.1,0.2,0.3,0.4,0.5,0.7,0.8,0.9]
seq_length = [1,3,5,9,13,15,17,20]
sample_amount = [1,3,5,7,9,12,15]  #+ [200,300,400,500]
learning_parameter = [1,2,4,6,8,10]
gens = 20
runs = 1000

for c in cost:
    for l in lam:
        for k in seq_length:
            for sampl in sample_amount:
                for learn in learning_parameter:
                    rmd.run(a,c,l,k,sampl,learn,gens,runs)
