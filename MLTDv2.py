import pickle
import argparse
import os
import networkx
import numpy as np
import copy
import json


from typing import List
from collections import Counter
from collections import deque

import random
import graphviz
class Node():
    def  __init__(self,
                  key : str,
                  parent = None,
                  child = None,
                  label = None):
        self.key = key
        if child is None:
            child = []
        if label is None:
            label = []
        self.label = label
        self.child = child
        self.parent = parent
        self.expanded = 0
        
    def __str__(self, level=0):
        #ret = " "*level+repr(self.key)+"\n"
        ret = " "*level+repr(self.key)+repr(self.label)+"\n"
        for c in self.child:
            ret += c.__str__(level+1)
        return ret

    def __copy__(self):
        return Node(self.key, self.parent, self.child.copy(), self.label.copy())

def create_graph_from_root(r):
    graph = graphviz.Digraph('G', format='png')
    output_file= path + "output.png"
    graph.attr('node', 
               shape='oval',
               fixedsize='true', 
               width='1', 
               height='.75',
               fontsize='12'
               )
    
    graph.attr('edge', 
               arrowsize='0.4',
               splines='false'
               )
    
    graph.node(r.key, str(r.label))
    nodes = deque([r])
    curr = nodes.pop()
    nodes.extend(curr.child)
    while nodes:
        curr = nodes.pop()
        graph.edge(curr.parent.key, curr.key)
        graph.node(curr.key, str(curr.label))
        nodes.extend(curr.child)
    graph.render('output', view=True)    

def delete_node(r, key):
    nodes = deque([r])
    curr = nodes.pop()
    nodes.extend(curr.child)
    while curr.key != key and nodes:
        curr = nodes.pop()
        nodes.extend(curr.child)
    if curr.key == key:
        curr.parent.child.remove(curr)
        for c in curr.child:
            c.parent = curr.parent
            curr.parent.child.append(c)
   
def delete_label(r, l, key):
    #print(l, key)
    nodes = deque([r])
    curr = nodes.pop()
    nodes.extend(curr.child)
    while curr.key != key and nodes:
        curr = nodes.pop()
        nodes.extend(curr.child)
    #print("Curr key ", curr.key, " with curr label ", curr.label)
    if curr.key == key and l in curr.label:
        curr.label.remove(l)

def expand_node(r, key, l):
    nodes = deque([r])
    curr = nodes.pop()
    nodes.extend(curr.child)
    while curr.key != key and nodes:
        curr = nodes.pop()
        nodes.extend(curr.child)
    if curr.key == key:
        curr.expanded = curr.expanded + 1
        new_node = Node(curr.key + '-' + str(curr.expanded))
        if curr.parent != None:
            curr.parent.child.remove(curr)
            curr.parent.child.append(new_node)
        new_node.child.append(curr)
        new_node.parent = curr.parent
        curr.parent = new_node
        curr.label = remove_sorted(curr.label, l)
        new_node.label = concat_sorted(new_node.label, l)

    

def create_tree_from_json(root_string, p, lvl, n, L, tag):
    root = Node(str(n + lvl*10) + tag)
    root.parent = p
    root.label = root_string['label']
    for l in root.label:
        L[l] = root
    for c in root_string['children']:
        n = n + 1
        child, L, n = create_tree_from_json(c, root, lvl + 1, n, L, tag)
        root.child.append(child)
    return root, L, n

def print_tree(root: Node):
    q = deque()
    print(root)
    

def compute_sizes(root: Node):
    if len(root.child) == 0:
        return 1
    root.size = 1
    for c in root.child:
        root.size += compute_sizes(c)
    return root.size
    
def sorted_intersection(l1, l2):
    if not l1 or not l2:
        return []
    i = 0
    j = 0
    intersection = []
    while i != len(l1) and j != len(l2):
        if l1[i] == l2[j]:
            intersection.append(l1[i])
            i += 1
            j += 1
        elif l1[i] < l2[j]:
            i += 1
        else:
            j += 1
    return intersection  

def remove_sorted(l, r):
    i = 0
    j = 0
    new_l = []
    while i != len(l) and j != len(r):
        if l[i] == r[j]:
            i += 1
            j += 1
        elif l[i] < r[j]:
            new_l.append(l[i])
            i += 1
        else:
            j += 1
    while i < len(l):
        new_l.append(l[i])
        i += 1
    return new_l      

def concat_sorted(l, a):
    i = 0
    j = 0
    new_l = []
    for k in range(0, len(l) + len(a)):
        if j >= len(a) or (i < len(l) and l[i] < a[j]):
            new_l.append(l[i])
            i += 1
        else:
            new_l.append(a[j])
            j += 1
    return new_l

def post_order(r):
    post = []
    q = deque([r])
    while q:
        curr = q.pop()
        q.extend(curr.child)
        post.append(curr)
    post.reverse()
    return post

def compute_labels(r):
    nodes = deque([r])
    labels = []
    while nodes:
        curr = nodes.popleft()
        nodes.extend(curr.child)
        for l in curr.label:
            labels.append(l)
    return labels

def compute_differences(r_F, r_G):
    nodes = deque([r_F])
    #Find the difference in the label sets of F and G
    labels_F = []
    while nodes:
        curr = nodes.popleft()
        nodes.extend(curr.child)
        labels_F.extend(curr.label)
    nodes = deque([r_G])
    labels_G = []
    while nodes:
        curr = nodes.popleft()
        nodes.extend(curr.child)
        labels_G.extend(curr.label)
    difference = list(set(labels_F) - set(labels_G))
    difference.extend(list(set(labels_G) - set(labels_F)))
    return difference
    

def remove_differences(r_F, r_G, diff_list):
    removed_count = 0
    nodes = deque([r_F])
    while nodes:
        curr = nodes.popleft()
        nodes.extend(curr.child)
        i = 0
        for l in range(len(curr.label)):
            if curr.label[i] in diff_list and len(curr.label) > 1:
                curr.label.remove(curr.label[i])
                removed_count = removed_count + 1
            elif curr.label[i] in diff_list and len(curr.label) == 1:
                removed_count = removed_count + 1
                delete_node(r_F, curr.key)
            else:
                i = i + 1
    nodes = deque([r_G])
    while nodes:
        curr = nodes.popleft()
        nodes.extend(curr.child)
        i = 0
        for l in range(len(curr.label)):
            if curr.label[i] in diff_list and len(curr.label) > 1:
                curr.label.remove(curr.label[i])
                removed_count = removed_count + 1
            elif curr.label[i] in diff_list and len(curr.label) == 1:
                removed_count = removed_count + 1
                delete_node(r_G, curr.key)
            else:
                i = i + 1
    return removed_count
    
#Given a node, finds the nearest branching descendant and returns path to it (inclusive)
def nearest_branching(v):
    path = [v]
    curr = v
    while len(curr.child) == 1:
        curr = curr.child[0]
        path.append(copy.copy(curr))
    return path, curr
    
#Can be improved by searching children more explicitly
#Note that node expansion requires considering non-branching nodes separately  
def check_if_eq(r_F, r_G):
    #print("Check if eq", file=f_wr)
    post_F = post_order(r_F)
    post_G = post_order(r_G)
    con_dist = {}
    for u in post_F:
        con_dist[u.key] = {}
        for v in post_G:   
            #If u or v are non-branching nodes, check if expansions lead to label matches
            if len(u.child) == 1 or len(v.child) == 1:
                nb_F, b_F = nearest_branching(u)
                nb_G, b_G = nearest_branching(v)
                i_F = 0
                i_G = 0
                count_F = 0
                count_G = 0
                while i_F != len(nb_F) and i_G != len(nb_G):
                    while i_F != len(nb_F) and len(nb_F[i_F].label) == 0:
                        i_F = i_F + 1
                    while i_G != len(nb_G) and len(nb_G[i_G].label) == 0:
                        i_G = i_G + 1
                    if i_F == len(nb_F) or i_G == len(nb_G):
                        break
                    shared = sorted_intersection(nb_F[i_F].label, nb_G[i_G].label)
                    count_F = count_F + len(shared)
                    count_G = count_G + len(shared)
                    if len(nb_F[i_F].label) != count_F and len(nb_G[i_G].label) != count_G:
                        break
                    if len(nb_F[i_F].label) == count_F:
                        i_F = i_F + 1
                        count_F = 0
                    if len(nb_G[i_G].label) == count_G:
                        i_G = i_G + 1
                        count_G = 0
                        
                while i_F != len(nb_F) and len(nb_F[i_F].label) == 0:
                        i_F = i_F + 1
                while i_G != len(nb_G) and len(nb_G[i_G].label) == 0:
                        i_G = i_G + 1
                if i_F == len(nb_F) and i_G == len(nb_G):
                    #If branching node labels equal, we check their constraint distance
                    if b_F.label == b_G.label:
                        con_dist[u.key][v.key] = con_dist[b_F.key][b_G.key]
                    else:
                        #If branching node labels don't equal, subtract 1 from distance to account for labels in below case
                        con_dist[u.key][v.key] = con_dist[b_F.key][b_G.key] - 1
                else:
                    con_dist[u.key][v.key] = 2
                #print("if end", file=f_wr)
            #If u and v are both branching nodes, try to find a matching between their children
            else:
                #print("else start for", u.key, v.key)
                c_u = u.child.copy()
                c_v = v.child.copy()
                if len(c_u) != len(c_v):
                    #print("Unequal child length")
                    con_dist[u.key][v.key] = 2
                else:
                    match_fl = True
                    for c in c_u:
                        i = 0
                        while i < len(c_v) and con_dist[c.key][c_v[i].key] != 0:
                            i = i + 1
                    
                        if i != len(c_v):
                            c_v.remove(c_v[i])
                        else:
                            #print("breaking out for", c.key)
                            match_fl = False
                            break
                    if match_fl:
                        if u.label == v.label:
                            con_dist[u.key][v.key] = 0
                        else:
                            con_dist[u.key][v.key] = 1
                    else:
                        #print("No match for one")
                        con_dist[u.key][v.key] = 2
                #print("else end", file=f_wr)
            # print("Con dist of ", u.key, v.key, " is ", con_dist[u.key][v.key])
    #print("Returning", file=f_wr)
    return con_dist[r_F.key][r_G.key]

#L_F and L_G are just dictionaries where keys are labels and an entry is the node with that label
#just used for a non-asymptotic speedup (could do a search through the tree instead for it)
#Returns 0, 1, or 2 if the passed forests are equal, off by 1 label, or different beyond a single label
#When 1 is returned, also returns the node with the label not shared between F and G as well as the label that is not shared 
def check_dist_two(roots_F, roots_G, L1, L2):
    # Create a virtual root if either F or G is a forest to make them trees (virtual roots have empty labels so trivially they will match)
    if not isinstance(roots_F, list):
        roots_F = [roots_F]
    if not isinstance(roots_G, list):
        roots_G = [roots_G]
    
    if len(roots_F) == 0 or len(roots_G) == 0:
        if len(roots_F) == 0 and len(roots_G) == 0:
            return 0, None
        else:
            return 2, None
    
    if len(roots_F) > 1 and len(roots_G) > 1:
        r_F = Node('-1')
        r_F.child = roots_F
        r_G = Node(-1)
        r_G.child = roots_G
    elif len(roots_F) > 1 or len(roots_G) > 1:
        return 2, None
    else:
        r_F = roots_F[0]
        r_G = roots_G[0]
        
    nodes = deque([r_F])
    #Find the difference in the label sets of F and G
    labels_F = []
    while nodes:
        curr = nodes.popleft()
        nodes.extend(curr.child)
        labels_F.extend(curr.label)
    nodes = deque([r_G])
    labels_G = []
    while nodes:
        curr = nodes.popleft()
        nodes.extend(curr.child)
        labels_G.extend(curr.label)
    difference = list(set(labels_F) - set(labels_G))
    difference.extend(list(set(labels_G) - set(labels_F)))
    #If differences are at most 1, check for equality after removing the difference if it exists, otherwise return immediately
    if len(difference) == 1:
        if len(labels_F) > len(labels_G):
            diff_node = L1[difference[0]]
            diff_node.label = remove_sorted(diff_node.label, difference)
        else:
            diff_node = L2[difference[0]]
            diff_node.label = remove_sorted(diff_node.label, difference)
            
        if check_if_eq(r_F, r_G) == 0:
            diff_node.label = concat_sorted(diff_node.label, difference)
            return 1, (diff_node, difference[0])
        else:
            diff_node.label = concat_sorted(diff_node.label, difference)
            return 2, None
    elif len(difference) == 0:
        if check_if_eq(r_F, r_G) == 0:
            return 0, None
        else:
            return 2, None
    else:
        return len(difference), None


def forest_helper(F_1, F_2, target, d, L_1, L_2, S):
    l = target.label[0]
    if l in L_2:
        match = L_2[l]
        shared = sorted_intersection(target.label, match.label)
    if args.v:
        print("------------------------Forest Helper--------------------------------", file=f_wr)
        pr_list_2 = [(r.key, r.label) for r in F_2]
        pr_list_1 = [(r.key, r.label) for r in F_1]
        print("first forest", pr_list_1, " and second forest", pr_list_2, file=f_wr)
        print("Edit sequence is ", S, " and d is ", d, file=f_wr)
    #First if label already deleted or not present in F_2, delete label and potentially node if no labels left
    if l not in L_2 or len(shared) == 0: 
        if args.v:
            print("label not present in F_2 for", target, " and F_2[0] is", F_2[0], file=f_wr)
        target.label = remove_sorted(target.label, [l])
        S.append(('ld', l, target.key))
        if len(target.label) == 0:
            if target in F_1:
                #global counter
                #counter = counter + 1
                #If target is a root, remove target and add its children as new roots
                if args.v:
                    print("Furthermore, target is a root", file=f_wr)
                F_1.remove(target)
                for c in target.child:
                    F_1.append(c)
                    c.parent = None
                S.append(('nd', target.key, target.label))
                if args.v:
                    rn = random.randrange(1,10000)
                    try:
                        print("min_dist type before MLTDv2", type(min_dist), rn, file=f_wr)
                    except:
                        print("No min dist before MLTDv2", rn, file=f_wr)
                min_dist, min_S = MLTDv2(F_1, F_2, d + 1, L_1, L_2, S.copy())
                if args.v:
                    print("min_dist datatype:", type(min_dist), rn, file=f_wr)  
                    print(min_dist, file=f_wr)
                    print("min_S datatype:", type(min_S), file=f_wr)
                    print(min_S, file=f_wr)
                S.pop()
                F_1.append(target)
                for c in target.child:
                    F_1.remove(c)
                    c.parent = target
                #OR leave target as an empty labelled node that will never be deleted
                #temp_dist, temp_S = MLTDv2(F_1, F_2, d + 1, L_1, L_2, S.copy())
                #if args.v:
                #    print("temp_dist datatype:", type(temp_dist), file=f_wr)
                #if temp_dist < min_dist:
                #    min_dist = temp_dist
                #    min_S = temp_S
            else:
                #Same as above case, but no need to remove from root list and need to instead set parent links accordingly
                target.parent.child.remove(target)
                target.parent.child.extend(target.child)
                for c in target.child:
                    c.parent = target.parent
                S.append(('nd', target.key, target.label))
                min_dist, min_S = MLTDv2(F_1, F_2, d + 1, L_1, L_2, S.copy())
                S.pop()
                for c in target.child:
                    target.parent.child.remove(c)
                    c.parent = target
                target.parent.child.append(target)
                #temp_dist, temp_S = MLTDv2(F_1, F_2, d + 1, L_1, L_2, S.copy())
                #if temp_dist < min_dist:
                #    min_dist = temp_dist
                #    min_S = temp_S
        else:
            min_dist, min_S = MLTDv2(F_1, F_2, d + 1, L_1, L_2, S.copy())
        target.label = concat_sorted(target.label, [l])
        S.pop()
        return min_dist, min_S
    if args.v:
        print("Forest Helper on target:", target, " and match:", match, file=f_wr)
    r_2 = match
    while r_2 != None and r_2 not in F_2:
        r_2 = r_2.parent
    if args.v:
        print("r_2 is ", r_2, file=f_wr)
    r_1 = target
    while r_1 != None and r_1 not in F_1:
        r_1 = r_1.parent
    # If matching node is not in subtree of remaining roots, delete labels and potentially node if no labels left
    if r_2 is None:
        if args.v:
            print("Match not in subtree", file=f_wr)
        shared = sorted_intersection(target.label, match.label)
        target.label = remove_sorted(target.label, shared)
        for l in shared:
            S.append(('ld', l, target.key))
        if len(target.label) == 0:
            if target in F_1:
                #If target is a root, remove target and add its children as new roots
                F_1.remove(target)
                for c in target.child:
                    c.parent = None
                    F_1.append(c)
                S.append(('nd', target.key, target.label))
                min_dist, min_S = MLTDv2(F_1, F_2, d + len(shared), L_1, L_2, S.copy())
                S.pop()
                F_1.append(target)
                for c in target.child:
                    F_1.remove(c)
                    c.parent = target
                #OR leave target as an empty labelled node that will never be deleted
                #temp_dist, temp_S = MLTDv2(F_1, F_2, d + len(shared), L_1, L_2, S.copy())
                #if temp_dist < min_dist:
                #    min_dist = temp_dist
                #    min_S = temp_S
            else:
                #Same as above case, but no need to remove from root list and need to instead set parent links accordingly
                target.parent.child.remove(target)
                for c in target.child:
                    target.parent.child.append(c)
                    c.parent = target.parent
                S.append(('nd', target.key, target.label))
                min_dist, min_S = MLTDv2(F_1, F_2, d + len(shared), L_1, L_2, S.copy())
                S.pop()
                for c in target.child:
                    target.parent.child.remove(c)
                    c.parent = target
                target.parent.child.append(target)
        else:
            min_dist, min_S = MLTDv2(F_1, F_2, d + len(shared), L_1, L_2, S.copy())
        target.label = concat_sorted(target.label, shared)
        for l in shared:
            S.pop()
        return min_dist, min_S
    else:    
        #If a matching node is in F_2, find the highest one
        par = match.parent
        while par != r_2.parent:
            if len(sorted_intersection(target.label, par.label)) != 0:
                match = par
            par = par.parent
        if target == r_1:
            if match == r_2:
                #both roots of trees, we check for if they are equal    or 1 label deletion off (empty nodes cannot be deleted)
                F_1.remove(target)
                F_2.remove(match)
                if args.v:
                    print("Target and Match before check_dist_two:", target, match, file=f_wr)    
                dist, diff = check_dist_two(target, match, L_1, L_2)
                if args.v:
                    print("After check_dist_two:", target, match, file=f_wr)
                if dist < 2:
                    if args.v:
                        print("Distance less than 2 for target and match", file=f_wr)
                    if dist == 1:
                        S.append(('ld', diff[1], diff[0].key))
                    min_dist, min_S = MLTDv2(F_1, F_2, d + dist, L_1, L_2, S.copy())
                    if args.v:
                        print("Min_dist in dist < 2 is type", type(min_dist), file=f_wr)
                    if dist == 1:
                        S.pop()
                    F_1.append(target)
                    F_2.append(match)
                else:
                    dist2, diff = check_dist_two(F_1, F_2, L_1, L_2)
                    if dist2 < 2:
                        if args.v:
                            print("Distance less than 2 for rest of F_1 and F_2 here", file=f_wr)
                        if dist2 == 1:
                            S.append(('ld', diff[1], diff[0].key))
                        min_dist, min_S = MLTDv2(target, match, d + dist2, L_1, L_2, S.copy())
                        if dist2 == 1:
                            S.pop()
                        F_1.append(target)
                        F_2.append(match)
                    else:
                        if args.v:
                            rn = random.randrange(0, 10000)
                            print("Dist and dist2 are ", dist, dist2, "for target:\n ", target, "and match: \n", match, rn, file=f_wr)
                        temp_dist, temp_S = MLTDv2(target, match, d + dist2, L_1, L_2, S.copy())
                        if args.v:
                            print("temp_dist type and dist is", type(temp_dist), temp_dist, rn, file=f_wr)
                        min_dist, min_S = MLTDv2(F_1, F_2, temp_dist - dist2, L_1, L_2, temp_S)
                        if args.v:
                            print("min_dist type and dist is", type(min_dist), min_dist, rn, file=f_wr)
                        F_1.append(target)
                        F_2.append(match)
                        shared = sorted_intersection(target.label, match.label)
                        target.label = remove_sorted(target.label, shared)
                        match.label = remove_sorted(match.label, shared)
                        #pr_list_2 = [(r.key, r.label) for r in F_2]
                        #pr_list_1 = [(r.key, r.label) for r in F_1]
                        #print("After labels are removed and not added yet first forest", pr_list_1, " and second forest", pr_list_2, counter, file=f_wr)
                        #print("Target and match:", target, match, file=f_wr)
                        for l in shared:
                            S.append(('ld', l, target.key))
                            S.append(('ld', l, match.key))
                        if len(target.label) == 0:
                            F_1.remove(target)
                            for c in target.child:
                                F_1.append(c)
                                c.parent = None
                            S.append(('nd', target.key, target.label))
                        if len(match.label) == 0:
                            F_2.remove(match)
                            for c in match.child:
                                F_2.append(c)
                                c.parent = None
                            S.append(('nd', match.key, match.label))       
                        temp_dist, temp_S = MLTDv2(F_1, F_2, d + 2*len(shared), L_1, L_2, S.copy())
                        if len(match.label) == 0:
                            for c in match.child:
                                F_2.remove(c)
                                c.parent = match
                            F_2.append(match)
                            S.pop()
                        if len(target.label) == 0:
                            for c in target.child:
                                F_1.remove(c)
                                c.parent = target
                            F_1.append(target)
                            S.pop()             
                        if args.v:
                            print("temp_dist type and dist is", type(temp_dist), temp_dist, rn, file=f_wr)
                        for l in shared:
                            S.pop()
                            S.pop()
                        if temp_dist < min_dist:
                            min_dist = temp_dist
                            min_S = temp_S
                        #pr_list_2 = [(r.key, r.label) for r in F_2]
                        #pr_list_1 = [(r.key, r.label) for r in F_1]
                        #print("After call to MLTD", pr_list_1, " and second forest", pr_list_2, counter, file=f_wr)
                        #print("Target and match:", target, match, file=f_wr)
                        target.label = concat_sorted(target.label, shared)
                        match.label = concat_sorted(match.label, shared)
                return min_dist, min_S        
            else:
                if args.v:
                    print("Target root, match in a subtree", file=f_wr)
                #Only target is a root, match is in a root's subtree of F_2
                #In this case, find highest unlabeled node and try top delete all nodes in path to root above it to match the "target" and "match" nodes together
                highest_empty_node = match
                curr = match.parent
                while curr != r_2.parent:
                    if len(curr.label) == 0:
                        highest_empty_node = curr
                    curr = curr.parent
                if highest_empty_node == r_2:
                    #If the root of the tree containing match is empty-labeled, can't be deleted so match entire trees together
                    F_1.remove(target)
                    F_2.remove(r_2)
                    dist, diff = check_dist_two(target, r_2, L_1, L_2)
                    if dist < 2:
                        if args.v:
                            print("Dist of target match less than 2", file=f_wr)
                        if dist == 1:
                            S.append(('ld', diff[1], diff[0].key))
                        min_dist, min_S = MLTDv2(F_1, F_2, d + dist, L_1, L_2, S.copy())
                        if dist == 1:
                            S.pop()
                        F_1.append(target)
                        F_2.append(r_2)
                    else:
                        dist2, diff = check_dist_two(F_1, F_2, L_1, L_2)
                        if dist2 < 2:
                            if args.v:
                                print("Dist of F_1, F_2 less than 2", file=f_wr)
                                pr_list_2 = [(r.key, r.label) for r in F_2]
                                pr_list_1 = [(r.key, r.label) for r in F_1]
                                print("first forest", pr_list_1, " and second forest", pr_list_2, file=f_wr)
                            if dist2 == 1:
                                S.append(('ld', diff[1], diff[0].key))
                            min_dist, min_S = MLTDv2(target, r_2, d + dist2, L_1, L_2, S.copy())
                            if dist == 1:
                                S.pop()
                            F_1.append(target)
                            F_2.append(r_2)
                        else:
                            temp_dist, temp_S = MLTDv2(target, r_2, d + dist2, L_1, L_2, S.copy())
                            min_dist, min_S = MLTDv2(F_1, F_2, temp_dist - dist2, L_1, L_2, temp_S)
                            F_1.append(target)
                            F_2.append(r_2)
                            shared = sorted_intersection(target.label, match.label)
                            target.label = remove_sorted(target.label, shared)
                            match.label = remove_sorted(match.label, shared)
                            for l in shared:
                                S.append(('ld', l, target.key))
                                S.append(('ld', l, match.key))
                            if len(target.label) == 0:
                                F_1.remove(target)
                                for c in target.child:
                                    F_1.append(c)
                                    c.parent = None
                                S.append(('nd', target.key, target.label))
                            if len(match.label) == 0:
                                match.parent.child.remove(match)
                                for c in match.child:
                                    match.parent.child.append(c)
                                    c.parent = match.parent
                                S.append(('nd', match.key, match.label))
                            temp_dist, temp_S = MLTDv2(F_1, F_2, d + 2 * len(shared), L_1, L_2, S.copy())
                            if len(target.label) == 0:
                                for c in target.child:
                                    F_1.remove(c)
                                    c.parent = target
                                F_1.append(target)
                                S.pop()
                            if len(match.label) == 0:
                                for c in match.child:
                                    match.parent.child.remove(c)
                                    c.parent = match
                                match.parent.child.append(match)
                                S.pop()
                            for l in shared:
                                S.pop()
                                S.pop()
                            if temp_dist < min_dist:
                                min_dist = temp_dist
                                min_S = temp_S
                            target.label = concat_sorted(target.label, shared)
                            match.label = concat_sorted(match.label, shared)
                else:
                    if args.v:
                        print("Some empty nodes above highest_empty", file=f_wr)
                        pr_list_2 = [(r.key, r.label) for r in F_2]
                        pr_list_1 = [(r.key, r.label) for r in F_1]
                        print("Before any modifications to first forest ", pr_list_1, " and second forest", pr_list_2, file=f_wr)
                    deleted = highest_empty_node.parent
                    prev = highest_empty_node
                    F_2_added = []
                    F_2_deleted = []
                    num_deleted = 0
                    label_count = 0
                    while deleted != r_2.parent:
                        F_2.extend(deleted.child)
                        F_2.remove(prev)
                        F_2_added.extend(deleted.child)
                        F_2_added.remove(prev)
                        F_2_deleted.append(deleted)
                        S.append(('nd', deleted.key, deleted.label))
                        label_count = label_count + len(deleted.label)
                        prev = deleted
                        deleted = deleted.parent
                    F_2.remove(r_2)
                    #If highest empty labelled node is not a root, then we've deleted nodes on the path to the root and we should match "target" and "match" nodes together, delete the shared labels from "target", or delete "target"
                    F_1.remove(target)
                    temp_dist, temp_S = MLTDv2(target, highest_empty_node, d + label_count, L_1, L_2, S.copy())
                    min_dist, min_S = MLTDv2(F_1, F_2, temp_dist, L_1, L_2, temp_S)
                    F_1.append(target)
                    #print("After target added back to first forest ", pr_list_1, " and second forest", pr_list_2, counter, file=f_wr)
                    #print("Target and match:", target, match, file=f_wr)
                    for v in F_2_added:
                            F_2.remove(v)
                    F_2.append(r_2)
                    for v in F_2_deleted:
                        S.pop()
                    shared = sorted_intersection(target.label, match.label)
                    target.label = remove_sorted(target.label, shared)
                    match.label = remove_sorted(match.label, shared)
                    for l in shared:
                        S.append(('ld', l, target.key))
                        S.append(('ld', l, match.key))
                    if len(target.label) == 0:
                        F_1.remove(target)
                        for c in target.child:
                            F_1.append(c)
                            c.parent = None
                        S.append(('nd', target.key, target.label))
                    if len(match.label) == 0:
                        match.parent.child.remove(match)
                        for c in match.child:
                            match.parent.child.append(c)
                            c.parent = match.parent
                        S.append(('nd', match.key, match.label))
                    temp_dist, temp_S = MLTDv2(F_1, F_2, d + 2 * len(shared), L_1, L_2, S.copy())
                    if len(target.label) == 0:
                        for c in target.child:
                            F_1.remove(c)
                            c.parent = target
                        F_1.append(target)
                        S.pop()
                    if len(match.label) == 0:
                        for c in match.child:
                            match.parent.child.remove(c)
                            c.parent = match
                        match.parent.child.append(match)
                        S.pop()
                    for l in shared:
                        S.pop()
                        S.pop()
                    match.label = concat_sorted(match.label, shared)
                    target.label = concat_sorted(target.label, shared)
                    if temp_dist < min_dist:
                        min_dist = temp_dist
                        min_S = temp_S
                    #pr_list_2 = [(r.key, r.label) for r in F_2]
                    #pr_list_1 = [(r.key, r.label) for r in F_1]
                    #print("After modifications are set back to original first forest ", pr_list_1, " and second forest", pr_list_2, counter, file=f_wr)
                return min_dist, min_S
        else:
            #Neither "target" nor "match" are root nodes of their respective trees, have to match their entire trees together.
            F_1.remove(r_1)
            F_2.remove(r_2)
            dist, diff = check_dist_two(r_1, r_2, L_1, L_2)
            if args.v:
                print("Both target and match in subtree", file=f_wr)
            if dist < 2:
                if dist == 1:
                    S.append(('ld', diff[1], diff[0].key))
                min_dist, min_S = MLTDv2(F_1, F_2, d + dist, L_1, L_2, S.copy())
                if dist == 1:
                    S.pop()
                F_1.append(r_1)
                F_2.append(r_2)
            else:
                dist2, diff = check_dist_two(F_1, F_2, L_1, L_2)
                if dist < 2:
                    if dist2 == 1:
                        S.append(('ld', diff[1], diff[0].key))
                    min_dist, min_S = MLTDv2(r_1, r_2, d + dist2, L_1, L_2, S.copy())
                    F_1.append(r_1)
                    F_2.append(r_2)
                else:
                    #Match their trees together, delete shared labels in "target", or delete "target"
                    temp_dist, temp_S = MLTDv2(r_1, r_2, d + dist2, L_1, L_2, S.copy())
                    min_dist, min_S = MLTDv2(F_1, F_2, temp_dist - dist2, L_1, L_2, temp_S)
                    F_1.append(r_1)
                    F_2.append(r_2)
                    shared = sorted_intersection(target.label, match.label)
                    target.label = remove_sorted(target.label, shared)
                    match.label = remove_sorted(match.label, shared)
                    for l in shared:
                        S.append(('ld', l, target.key))
                        S.append(('ld', l, match.key))
                    if len(target.label) == 0:
                        target.parent.child.remove(target)
                        for c in target.child:
                            target.parent.child.append(c)
                            c.parent = target.parent
                        S.append(('nd', target.key, target.label))
                    if len(match.label) == 0:
                        match.parent.child.remove(match)
                        for c in match.child:
                            match.parent.child.append(c)
                            c.parent = match.parent
                        S.append(('nd', match.key, match.label))
                    temp_dist, temp_S = MLTDv2(F_1, F_2, d + 2*len(shared), L_1, L_2, S.copy())
                    if len(target.label) == 0:
                        for c in target.child:
                            target.parent.child.remove(c)
                            c.parent = target
                        target.parent.child.append(target)
                        S.pop()
                    if len(match.label) == 0:
                        for c in match.child:
                            match.parent.child.remove(c)
                            c.parent = match
                        match.parent.child.append(match)
                        S.pop()
                    for l in shared:
                        S.pop()
                        S.pop()
                    match.label = concat_sorted(match.label, shared)
                    target.label = concat_sorted(target.label, shared)
                    if temp_dist < min_dist:
                        min_dist = temp_dist
                        min_S = temp_S    
            return min_dist, min_S
                
def MLTDv2(T_F, T_G, d, L_F, L_G, S):
    if args.v:
        print("--------------- MLTDv2----------", file=f_wr)
        print("Edit sequence is ", S, " and d is ", d, file=f_wr)
    if not isinstance(T_F, list):
        T_F = [T_F]
    if not isinstance(T_G, list):
        T_G = [T_G]
    if d > k:
        if args.v:
            print("Distance too large", file=f_wr)
        return k + 1000, S

    #print(len(T_F), len(T_G))

    if len(T_F) == 0:
        if args.v:
            print("F is empty, deleting G", file=f_wr)
        dist = d
        for r in T_G:
            post = post_order(r)
            for node in post:
                dist = dist + len(node.label)
                S.append(('nd', node.key, node.label))
        if dist > k:
            return k + 1000, S
        else:
            return dist, S
    elif len(T_G) == 0:
        if args.v:
            print("G is empty, deleting F", file=f_wr)
        dist = d
        for r in T_F:
            post = post_order(r)
            for node in post:
                dist = dist + len(node.label)
                S.append(('nd', node.key, node.label))
        if dist > k:
            return k + 1000, S
        else:
            if args.v:
                print("Deleted F", file=f_wr)
                print(dist, file=f_wr)
            return dist, S

    # HERE compare trees only
    elif len(T_F) == 1 and len(T_G) == 1:
        if args.v:
            print("HERE !!! F and G are trees, first tree:\n", T_F[0], "Second tree:\n", T_G[0], file=f_wr)
        r_F = T_F[0]
        r_G = T_G[0]
        shared = sorted_intersection(r_F.label, r_G.label)
        if args.v:
            print("shared: ", shared, file=f_wr)
        
        if len(shared) == len(r_F.label) and len(shared) == len(r_G.label):
            #perfect match
            #Issue with extension if one node is a single child and one is a branching node, may be optimal to extend multi-branch node into empty node and delete child label or instead it may be optimal to not extend and just delete non-branching node or let it be matched to one of the branching children (and delete remaining children) - note thi shappens in not just the case this comment is contained in
            min_dist, min_S = MLTDv2(r_F.child, r_G.child, d, L_F, L_G, S.copy())
            return min_dist, min_S
        elif len(shared) == len(r_F.label):
            if args.v:
                print("r_F fully shared, r_G not", file=f_wr)
            r_G.label = remove_sorted(r_G.label, shared)
            S.append(('ne', r_G.key, shared))
            min_dist, min_S = MLTDv2(r_F.child, [r_G], d, L_F, L_G, S.copy())
            S.pop()
            r_G.label = concat_sorted(r_G.label, shared)
            return min_dist, min_S
        elif len(shared) == len(r_G.label):
            if args.v:
                print("r_G fully shared, r_F not", file=f_wr)
            r_F.label = remove_sorted(r_F.label, shared)
            S.append(('ne', r_F.key, shared))
            min_dist, min_S = MLTDv2([r_F], r_G.child, d, L_F, L_G, S.copy())
            S.pop()
            r_F.label = concat_sorted(r_F.label, shared)
            return min_dist, min_S
        else:
            #delete either root
            if args.v:
                print("Delete root of F", file=f_wr)                   
                print("first forest ", r_F, " and second forest", r_G, file=f_wr)

            if len(shared) > 0:
                r_F.label = remove_sorted(r_F.label, shared)
                S.append(('ne', r_F.key, shared))

                r_G.label = remove_sorted(r_G.label, shared)
                S.append(('ne', r_G.key, shared))                

            S.append(('nd', r_F.key, r_F.label))
            min_dist, min_S = MLTDv2(r_F.child, [r_G], d + len(r_F.label), L_F, L_G, S.copy())
            S.pop()
            r_G.label = concat_sorted(r_G.label, shared)
            #r_F.label = remove_sorted(r_F.label, shared)

            if args.v:
                print("Delete root of G", file=f_wr)
                print("first forest ", r_F, " and second forest", r_G, file=f_wr)
            S.append(('nd', r_G.key, r_G.label))
            temp_dist, temp_S = MLTDv2([r_F], r_G.child, d + len(r_G.label), L_F, L_G, S.copy())

            if temp_dist < min_dist:
                min_dist = temp_dist
                min_S = temp_S
            S.pop()
            r_F.label = concat_sorted(r_F.label, shared)
            #match roots together, delete any unshared labels

            if len(shared) > 0:
                S.pop()
                S.pop()
            return min_dist, min_S
        
    else:
        # Find the labelled node at the highest level in remaining trees
        nodes = deque(T_F + T_G)
        labeled = nodes.popleft()
        nodes.extend(labeled.child)
        while len(labeled.label) == 0 and nodes:
            labeled = nodes.popleft()
            nodes.extend(labeled.child)
        #If no labeled nodes left, check if remaining forests are equal
        if len(labeled.label) == 0:
            dist, _ = check_dist_two(T_F, T_G, L_F, L_G)
            if dist == 0:
                return d, S
            else:
                return k + 1000, S
        #Call forest helper with parameters in correct order according to if labeled is in F or G
        r = labeled
        while r not in T_F and r not in T_G:
            r = r.parent
        if r in T_F:
            if args.v:
                print("Node", r, "found in T_F with first tree", T_F[0], file=f_wr)
            min_dist, min_S = forest_helper(T_F, T_G, labeled, d, L_F, L_G, S.copy())
            if args.v:
                print("Min dist type", type(min_dist), min_dist, file=f_wr)
            return min_dist, min_S
        else:
            if args.v:
                print("Found in T_G", r, file=f_wr)
            min_dist, min_S = forest_helper(T_G, T_F, labeled, d, L_G, L_F, S.copy())
            if args.v:
                print("Min dist type", type(min_dist), min_dist, file=f_wr)
            return min_dist, min_S

def random_tree2(tag, M, lM):
    n = 0
    root = Node(str(n) + tag)
    root.label = [0]
    nodes = deque([root])
    c_length = random.randrange(1, M)
    for i in range(c_length):
        n = n + 1
        next_c = Node(str(n) + tag)
        next_c.parent = root
        root.child.append(next_c)
        nodes.append(next_c)
        
    while nodes:
        curr = nodes.pop()
        r = random.random()
        if r < .8:
            c_length = random.randrange(1, M)
            for i in range(c_length):
                n = n + 1
                next_c = Node(str(n) + tag)
                next_c.parent = curr
                curr.child.append(next_c)
                nodes.append(next_c)
    nodes = deque([root])
    labelset = list(range(1, lM*(n+1)))
    L = {}
    L[0] = root
    nodes.pop()
    nodes.extend(root.child)
    while nodes:
        curr = nodes.pop()
        nodes.extend(curr.child)
        for _ in range(lM):
            l = random.randrange(1, len(labelset))
            curr.label.append(labelset[l])
            L[labelset[l]] = curr
            labelset.remove(labelset[l])
        curr.label.sort()
    return root, L
    
def random_tree(tag, M, lM):
    labelset = list(range(1, lM*M*M))
    print(labelset)
    root = Node('0' + tag)
    root.label = [0]
    r = random.randrange(1, M)
    L = {}
    for i in range(1, r+1):
        c = Node(str(i) + tag)
        for j in range(lM):
            l = random.randrange(1,len(labelset))
            L[labelset[l]] = c
            c.label.append(labelset[l])
            labelset.remove(labelset[l])
        labelset.remove(labelset[l])
        c.parent = root
        c.label.sort()
        root.child.append(c)
    for v in root.child:
        r = random.randrange(1, M)
        for i in range(1, r+1):
            c = Node(v.key + str(i) + tag)
            for j in range(lM):
                l =random.randrange(1,len(labelset))
                L[labelset[l]] = c
                c.label.append(labelset[l])
                labelset.remove(labelset[l])
            c.label.sort()
            c.parent = v
            v.child.append(c)
    return root, L

def shell(root_F, root_G, L_F, L_G):  
    k_values = [16, 32, 48, 64, 128, 256, 512, 1024, 2048, 4096]
    i = 0
    #print("First tree \n", root_F)
    #print("Second tree \n", root_G)

    diff_list = compute_differences(root_F, root_G)
    pre_edits = remove_differences(root_F, root_G, diff_list)
    print("Deleted ", pre_edits, "of ",  len(diff_list), "non-common labels")
    print("First tree with common labels only \n", root_F)
    print("Second tree with common labels only \n", root_G)

    while i < len(k_values):
        global k
        k = k_values[i]
        print("Beginning ", k)
        d, S = MLTDv2(root_F, root_G, 0, L_F, L_G, [])
        #print(root_F)
        #print(root_G)
        print("Finished ", k)
        if d <= k:
            print("There are ", pre_edits, " non-common labels with ", int(d / 2), " additional edits when checking ", k)
            print(S)

            with open('/Users/wuchh/project/dev/results/tests/real-data/edit_string.pkl', 'wb') as edits_file:
                pickle.dump((S, ntl), edits_file)

            break
        i = i + 1
    #return (d/2) / len(compute_labels(root_F))    

    #with open('/Users/wuchh/project/dev/results/tests/edits.pkl', 'wb') as handle:
    #    pickle.dump((S, ntl), handle)

    l_deleted = []
    for edit in S:
        if edit[0] == 'nd':
            if args.pi:
                for l in edit[2]:
                    if not ntl[int(l)] in l_deleted:
                        l_deleted.append(ntl[int(l)])
            if edit[1][len(edit[1]) - 1] == 'F':
                delete_node(root_F, edit[1])
            elif edit[1][len(edit[1]) - 1] == 'G':
                delete_node(root_G, edit[1])
        elif edit[0] == 'ld':
            if args.pi:
                if not ntl[int(edit[1])] in l_deleted:
                    l_deleted.append(ntl[int(edit[1])])
            if edit[2][len(edit[2]) - 1] == 'F':
                delete_label(root_F, edit[1], edit[2])
            elif edit[2][len(edit[2]) - 1] == 'G':
                delete_label(root_G, edit[1], edit[2])
            '''   
            elif edit[0] == 'ne':
            if edit[1][len(edit[1]) - 1] == 'F':
                expand_node(root_F, edit[1], edit[2])
            elif edit[1][len(edit[1]) - 1] == 'G':
                expand_node(root_G, edit[1], edit[2])
            '''

    print("Set of labels deleted: ", l_deleted)

    #print("After edit sequence:")
    #print("First tree \n", root_F)
    #print("Second tree \n", root_G)
    #print(check_if_eq(root_F, root_G))

    '''nodes = deque([root_F]) 
    labels_F = []
    while nodes:
        curr = nodes.popleft()
        nodes.extend(curr.child)
        labels_F.extend(curr.label)
    nodes = deque([root_G])
    labels_G = []
    while nodes:
        curr = nodes.popleft()
        nodes.extend(curr.child)
        labels_G.extend(curr.label)

    print("Remaining labels in first tree", labels_F, " and remaining labels in second tree", labels_G)'''
    #print(len(compute_differences(root_F, root_G)))
    return d
parser = argparse.ArgumentParser("Description: compute MLTD between two trees stored in files")    
parser.add_argument("-v", help="Print to output file", action='store_true')
#args= parser.parse_args()

if __name__ == '__main__':
    #k = 8
    #counter = 0


    path = os.path.dirname(os.path.abspath(__file__))
    path += "/"
    #path += "\\"
    parser = argparse.ArgumentParser("Description: compute MLTD between two trees stored in files")
    parser.add_argument('-r', help="randomly generate trees", action='store_true')
    parser.add_argument('-r2', help="randomly generate trees with second method", action='store_true')
    parser.add_argument('-pi', help="read trees in from pickle file", action='store_true')
    parser.add_argument('-tr', help="read trees in from tree file", action='store_true')
    parser.add_argument("tree_file_1", help="the file name of the first file to read", type=str)
    parser.add_argument("tree_file_2", help="the file name of the second file to read", type=str)
    parser.add_argument("-v", help="Print to output file", action='store_true')
    args = parser.parse_args()

    if args.v:
        f_wr = open(path + "output.txt", "w")
        f_wr.write("----------------Starting MLTD--------------------- \n")

    print(args)

    if args.r:
        root_F = None
        while not root_F:
            try:
                root_F, L_F = random_tree('F', 5, 4)
            except:
                print("Failed to generate tree, retrying")
        root_G = None
        while not root_G:
            try:
                root_G, L_G = random_tree('G', 5, 4)
            except:
                print("Failed to generate tree, retrying")
    elif args.r2:
        root_F, L_F = random_tree2('F', 2, 3)
        root_G, L_G = random_tree2('G', 2, 3)
    elif args.pi:
        n = 1
        ltn = {}
        ntl = {}
        with open(path + args.tree_file_1, 'rb') as f:
            F = pickle.load(f)
            V_F = list(F.nodes)
            E_F = list(F.edges)
            A_F = {}
            for v in V_F:
                A_F[v]= Node(str(v) + 'F')
            r_F = []
            for e in E_F:
                A_F[e[1]].label = F.edges[e]['label'].split('\n')
                for l in A_F[e[1]].label:
                    ltn[l] = n
                    ntl[n] = l
                    n = n + 1
                A_F[e[1]].label.sort()
                A_F[e[0]].child.append(A_F[e[1]])
                A_F[e[1]].parent = A_F[e[0]]
            r_F = []
            for v in V_F:
                if A_F[v].parent is None:
                    r_F.append(A_F[v])
            root_F = r_F[0]

        with open(path + args.tree_file_2, 'rb') as f:
            G = pickle.load(f)
            V_G = list(G.nodes)
            E_G = list(G.edges)
            A_G = {}
            for v in V_G:
                A_G[v]= Node(str(v) + 'G')
            r_G = []
            for e in E_G:
                A_G[e[1]].label = G.edges[e]['label'].split('\n')
                for l in A_G[e[1]].label:
                    ltn[l] = n
                    ntl[n] = l
                    n = n + 1
                A_G[e[1]].label.sort()
                A_G[e[0]].child.append(A_G[e[1]])
                A_G[e[1]].parent = A_G[e[0]]
            r_G = []
            for v in V_G:
                if A_G[v].parent is None:
                    r_G.append(A_G[v])
            root_G = r_G[0]

        nodes = deque([root_F])  
        L_F = {}
        while nodes:
            curr = nodes.popleft()
            nodes.extend(curr.child)
            l_copy = curr.label.copy()
            for l in l_copy:
                L_F[str(ltn[l])] = curr
                curr.label.remove(l)
                curr.label = concat_sorted(curr.label, [str(ltn[l])])
        nodes = deque([root_G])
        L_G = {}
        while nodes:
            curr = nodes.popleft()
            nodes.extend(curr.child)
            l_copy = curr.label.copy()
            for l in l_copy:
                L_G[str(ltn[l])] = curr
                curr.label.remove(l)
                curr.label = concat_sorted(curr.label, [str(ltn[l])])
    elif args.tr:
        curr_f = open("C:\\Users\\123ja\\Documents\\Research\\NIH\\1-mut\\simNo_1-s_30-m_120-sample_1.tree", "r")
        Lines = curr_f.readlines()
        nodeset = {}
        for line in Lines:
            node_info = line.split()
            print(node_info)
            if node_info[0] != 'node_id':
                new_node = Node(node_info[0])
                if node_info[0] != 'ROOT':
                    nodeset[int(new_node.key)] = new_node
                    new_node.label = node_info[2].split(',')
                    new_node.label.sort()
                    if node_info[1] == 'ROOT':
                        print('root parent')
                        new_node.parent = root_F
                        root_F.child.append(new_node)
                    else:
                        print('nonroot parent')
                        new_node.parent = nodeset[int(node_info[1])]
                        new_node.parent.child.append(new_node)
                else:
                    root_F = new_node
                    new_node.label.append('-1')
        nodes = deque([root_F])  
        L_F = {}
        while nodes:
            curr = nodes.popleft()
            nodes.extend(curr.child)
            l_copy = curr.label.copy()
            for l in l_copy:
                L_F[l] = curr
        curr_f = open("C:\\Users\\123ja\\Documents\\Research\\NIH\\1-mut\\simNo_1-s_30-m_120.ground_truth.tree", "r")
        nodeset = {}
        Lines = curr_f.readlines()
        for line in Lines:
            node_info = line.split()
            print(node_info)
            if node_info[0] != 'node_id':
                new_node = Node(node_info[0])
                if node_info[0] != 'ROOT':
                    nodeset[int(new_node.key)] = new_node
                    new_node.label = node_info[2].split(',')
                    new_node.label.sort()
                    if node_info[1] == 'ROOT':
                        new_node.parent = root_G
                        root_G.child.append(new_node)
                    else:
                        new_node.parent = nodeset[int(node_info[1])]
                        new_node.parent.child.append(new_node)
                else:
                    root_G = new_node
                    new_node.label.append('-1')
        nodes = deque([root_G])  
        L_G = {}
        while nodes:
            curr = nodes.popleft()
            nodes.extend(curr.child)
            l_copy = curr.label.copy()
            for l in l_copy:
                L_G[l] = curr
    else:
        f_F = open(path + args.tree_file_1, "r")
        file_str_F = f_F.read()
        root_json_F = json.loads(file_str_F)
        L_F = {}
        root_F, L_F, _ = create_tree_from_json(root_json_F, None, 0, 0, L_F, 'F')
        f_G = open(path + args.tree_file_2, "r")
        file_str_G = f_G.read()
        root_json_G = json.loads(file_str_G)
        L_G = {}
        root_G, L_G, _ = create_tree_from_json(root_json_G, None, 0, 0, L_G, 'G')
        #print(root_F)
        #print(root_G)
    
    shell(root_F, root_G, L_F, L_G)
    
    #create_graph_from_root(root_F)
    #exit(1)
 