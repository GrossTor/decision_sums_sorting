# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 14:39:56 2017
@author: Torsten Gross @ Humboldt University Berlin / Charite Universitaetsmedizin Berlin

A sum where each of the N summands can be independently chosen from two choices
yields 2^N possible summation outcomes. This is an O(K^2)-algorithm that finds
the K smallest/largest of these sums by evading the enumeration of all sums.

As described in: 
"Sorting sums over binary decision summands"
Torsten Gross, Nils Bluethgen, 2017

See comments at end of file for an example.
"""

import numpy as np

def sort_choice_sum_gen(scores):
    N=np.shape(scores)[0]
    score_sort=np.argsort(scores,1)
    delta=np.abs(scores[:,0]-scores[:,1])
    sorted_delta_inds=np.argsort(delta)
    sorted_delta=delta[sorted_delta_inds]
    sorted_delta_inds=np.argsort(sorted_delta_inds)
    delta_diff=sorted_delta[1:]-sorted_delta[:-1]

    pendings=[N*(False,)]
    pending_sums=[np.sum(scores.min(1))]
    while True:
        
        #extract next choice
        next_choice=pendings.pop()
        next_sum=pending_sums.pop()
        yield next_sum,tuple(score_sort[i,int(next_choice[j])] for i,j in enumerate(sorted_delta_inds))
        if np.all(next_choice):
            break #It would be enough to do half
        
        #generate putative choices
        putatives=[]
        putative_sums=[]
        if not next_choice[0]:
            new_putative=(True,)+next_choice[1:]
            if new_putative not in pendings: #sort out duplicates
                putatives.append((True,)+next_choice[1:])
                putative_sums.append(next_sum+sorted_delta[0])
        for ind in range(N-1):
            if (next_choice[ind],next_choice[ind+1])==(True,False):
                new_putative=next_choice[:ind]+ (False,True) + next_choice[ind+2:]
                if new_putative not in pendings: #sort out duplicates
                    putatives.append(new_putative)
                    putative_sums.append(next_sum+delta_diff[ind])
        if not putatives:
            continue #no new putatives, so just stay with the current pendings
            
        #merge putative choices into pending choices
        putative_sorted_inds=list(np.argsort(putative_sums)) #from small to large
        pending_ind,shift,putatives_is_empty=0,0,False
        putative_sorted_ind=putative_sorted_inds.pop()
        original_len_pendings=len(pending_sums)
        while pending_ind < original_len_pendings:
            while putative_sums[putative_sorted_ind] >= pending_sums[pending_ind+shift]:
                pendings.insert(pending_ind+shift,putatives[putative_sorted_ind])                
                pending_sums.insert(pending_ind+shift,putative_sums[putative_sorted_ind])                
                shift+=1        
                if putative_sorted_inds:
                    putative_sorted_ind=putative_sorted_inds.pop()
                else:
                    putatives_is_empty=True
                    break #stop merging because there are no more putative choices
            if putatives_is_empty:
                break #stop merging because there are no more putative choices
            pending_ind+=1
            
        #append_the_rest
        if not putatives_is_empty:
            for putative_sorted_ind in reversed(putative_sorted_inds+[putative_sorted_ind]): #from large to small
                pendings.append(putatives[putative_sorted_ind])
                pending_sums.append(putative_sums[putative_sorted_ind])
            
            
            
##############
#example run:#
##############
#
#N=100
#K=10000
#scores=np.random.rand(N,2)
#sort_gen=sort_choice_sum_gen(scores)
#for i in range(K):
#    curr_score,curr_choice=sort_gen.next()
#