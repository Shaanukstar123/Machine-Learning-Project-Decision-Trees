import numpy as np


def cross_val(data,k=10): #k-fold cross validation
    test_set = {}
    training_set = {}
    validation_set = {}

    split = len(data)//(k//2)
    validation_split  = len(data)//(k)#splits data into training:testing:validation (2 sweeps  = 10)
    for i in range(k//2): 
        test_set[i] = data[i*split:(i*split)+validation_split]
        validation_set[i] = data[(i*split)+validation_split:(i*split)+split]
        training_set[i] = np.delete(data,slice(i*split,(i*split)+split),axis = 0)
    
    for i in range(k//2):
        index = i+k//2 
        validation_set[index] = data[i*split:(i*split)+validation_split]
        test_set[index] = data[(i*split)+validation_split:(i*split)+split]
        training_set[index] = np.delete(data,slice(i*split,(i*split)+split),axis = 0)

    return test_set,training_set,validation_set

def evaluate(root,test_set,is_pruning=1,confusion_matrix=[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]):

    rooms_actual = {1:0,2:0,3:0,4:0}
    true_positives = {1:0,2:0,3:0,4:0}
    false_positives = {1:0,2:0,3:0,4:0}

    correct = 0
    total = 0

    for row in test_set:#[test_set_index]: #loops through each test case
        total+=1
        rooms_actual[row[-1]]+=1 # for confusion matrix
        prediction = eval_tree(root,row)
        confusion_matrix[(int(row[-1]))-1][(int(prediction))-1] +=1
        if prediction == row[-1]:
            correct+=1
            true_positives[prediction]+=1
        else:
            false_positives[prediction]+=1
       
    accuracy = correct/total
    if is_pruning ==1:
        return accuracy #just returns accuracy if this function is used by pruning
    else:
        return confusion_matrix,accuracy,rooms_actual,true_positives,false_positives          
    

def eval_tree(root, input):
    """ DFS traversal through decision tree and prins leaf nodes

    Input: root node (type: tree)
    return an integer
    """
    
    if not root.node['left'] and not root.node['right']: 
        return root.node['attribute']
    
    attr = root.node['attribute']
    if input[attr] <= root.node['val']:
        return eval_tree(root.node['left'], input)
    else:    
        return eval_tree(root.node['right'], input)   

def get_metrics(rooms_actual,true_positives,false_positives):
    precision = {1:0,2:0,3:0,4:0}
    recall = {1:0,2:0,3:0,4:0}
    f1 ={1:0,2:0,3:0,4:0}
    for room in range(1,5):
        precision[room] = true_positives[room]/(true_positives[room]+false_positives[room])
        recall[room] = true_positives[room]/rooms_actual[room]
        f1[room] = (2*precision[room]*recall[room])/(precision[room]+recall[room])

    return ((precision,recall,f1))  


def calc_avg_metrics(root, test_set, accuracy, precision, recall, f1,confusion_matrix):
    temp_accuracy  = accuracy
    confusion_matrix,accuracy,rooms_actual,true_positives,false_positives = evaluate(root,test_set,0,confusion_matrix)
    accuracy += temp_accuracy

    metrics = get_metrics(rooms_actual,true_positives,false_positives)
    for i in range(1,5):
        precision[i] += metrics[0][i]
        recall[i]+= metrics[1][i]
        f1[i]+= metrics[2][i]
        if i == 9: #Divides by k=10 to get averaged metrics
            precision[i]/=10
            recall[i]/=10
            f1[i]/=10
            accuracy/=10

    return confusion_matrix,accuracy,precision,recall,f1

def normalise(precision,recall,f1,conf_matrix):
    for i in precision:
        if precision[i]!=0:
            precision[i]/=10
    for i in recall:
        if recall[i]!=0:
            recall[i]/=10
    for i in f1:
        if f1[i]!=0:
            f1[i]/=10
    for i in range(len(conf_matrix)-1):
        for j in range(len(conf_matrix[i])-1):
            if conf_matrix[i][j]!=0:
                conf_matrix[i][j]/= 10
    return precision,recall,f1,conf_matrix