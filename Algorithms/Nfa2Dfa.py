from GUI.Node import *
from GUI.settings import *
import math

def keyExists(dictt:dict,key:str):
    try:
        dictt[key]
        return True
    except:
        return False


class Drawer:

    def __init__(self,canvas,graph,alphabet) -> None:
        self.__canvas = canvas
        self.__graph = graph
        self.__alphabets = alphabet
        self.check_error_state()
        self.reformat_transition_table()
        self.create_graph_table()
        self.__level1 =  self.calculate_level1_shift() # DRAWING_SHIFT
        self.calculate_vertical_distance()
        self.draw()

    def check_error_state(self):

        # check for error state and add it if need for any node
        has_error_state = False
        for key in self.__graph.keys():
            adj = self.__graph[key] # new dict with all reached node from this node and alpahbets need for transition
            for alphabet in self.__alphabets:
                if not keyExists(adj,alphabet):
                    has_error_state = True
                    self.__graph[key][alphabet] = ['err_state']

        if has_error_state:
            self.create_error_state()

    def create_error_state(self):
        
        err_state = dict()
        for alphabet in self.__alphabets:
            err_state[alphabet] = ['err_state']
        self.__graph['err_state'] = err_state

    def reformat_transition_table(self):

        '''
        reformat the structure of self.__graph (transition table) from maping to list of Node to map to string with node name
        '''
        for key in self.__graph.keys():
            adj = self.__graph[key]
            for alphabet in adj.keys():
                propagation_nodes = self.__graph[key][alphabet]
                propagation_nodes.sort()
                if len(propagation_nodes) == 1:
                    self.__graph[key][alphabet] = ''.join(propagation_nodes[0].__str__()) 
                else:
                    self.__graph[key][alphabet] = '{'+','.join([n.__str__() for n in propagation_nodes])+'}'
    

    def create_graph_table(self):
        '''
        similar to transition table but instead of maping each alphabet to each node map nodes to alphabets reached by
        '''
        self.__graph_map = dict()
        nodes = list(self.__graph.keys())
        
        # intialize with empty list
        for n in nodes:
            self.__graph_map[n] = dict()
            for recursive_node in nodes:
                self.__graph_map[n][recursive_node] = []

        # reformat        
        for n in nodes:
            adj = self.__graph[n]
            for alphabet in adj.keys():
                self.__graph_map[n][adj[alphabet]].append(alphabet)

        #clean non reachable nodes
        for ni in nodes:
            for nj in nodes:
                alphabets = self.__graph_map[ni][nj]
                alphabets.sort()
                if len(alphabets) == 0:
                    del self.__graph_map[ni][nj]
                else:
                    self.__graph_map[ni][nj] = ','.join(alphabets)
        
    def calculate_level1_shift(self):
        self.__num_of_nodes = len(self.__graph) + 1
        self.__nodes_in_line = math.ceil(self.__num_of_nodes/2)
        dx = (self.__nodes_in_line)*HORIZONTAL_DISTANCE
        shift = (BETA-BETA_LABEL) * dx
        return shift

    def calculate_vertical_distance(self):

        x1 = self.__level1
        x2 = self.__level1+(self.__nodes_in_line-1)*HORIZONTAL_DISTANCE
        y2 = self.__level1+RADUIS
        self.__level2 = y2 + (x2-x1)*DRAWING_ANGLE_TAN - RADUIS # y1 = 60+x+RADUIS 


    def draw(self):
        
        print(self.__graph)
        print(self.__graph_map)
        # for node in self.__graph_map:
            
        nodes_labels = list(self.__graph_map.keys())
        nodes = {node:"" for node in nodes_labels}
        for i in range(len(nodes_labels)):
            curr_level = 1 if i % 2 == 0 else 2
            level = self.__level1 if i % 2 == 0 else self.__level2
            hor_shift = math.floor(i/2)*HORIZONTAL_DISTANCE
            n = DFANode(self.__canvas,60+hor_shift,level,f'{nodes_labels[i]}',level=curr_level)
            n.create()
            nodes[nodes_labels[i]] = n
        
        # connecting nodes
        for out_node in nodes_labels:
            next_nodes = self.__graph_map[out_node]
            for in_node in next_nodes:
                label = self.__graph_map[out_node][in_node]
                # if out_node == in_node:
                # else:
                nodes[out_node].connect_node(nodes[in_node],label)
                
                
class NFA2DFA:

    def __init__(self,initialNode,DrawingCanvas,on_finish_callback) -> None:
        self.__initialNode = initialNode
        self.__DrawingCanvas = DrawingCanvas
        self.__on_finish_callback = on_finish_callback
        self.__alphabets = set() # set of alphabets
        self.__fringe = [[initialNode.get_label(),[initialNode]]] # nodes that are not yet processed (new nodes)
        self.__visited = set() # nodes that are already propagated
        self.__graph = dict() # transition table
        self.propagate()
        self.draw()
        
    @staticmethod
    def update_label(label,nodes):
        new_nodes = ','.join([node.get_label() for node in nodes])
        if '{' in label and new_nodes:
           return label[:-1] + ',' +new_nodes+'}'
        elif new_nodes:
            return '{'+ label + ',' + new_nodes+'}'
        else:
            return label

    def setup_node(self):
        '''
        setup node for epsilon connected node before propagating
        '''
        currNodeLabel , currNodes = self.__fringe[0]
        currLines = [line for node in currNodes for line in node.lines_out ]
        epsilon_nodes = [line.Node_in for line in currLines if line.has_epsilon()]
        epsilon_nodes.sort()
        new_label = NFA2DFA.update_label(currNodeLabel,epsilon_nodes)
        currNodes += epsilon_nodes
        self.__fringe[0] = [new_label,currNodes]
        

    def propagate(self):
        
        self.setup_node()
        currNodeLabel , currNodes = self.__fringe.pop(0)
        self.__visited.add(currNodeLabel)
        currLines = [line for node in currNodes for line in node.lines_out ]
        
        self.__graph[currNodeLabel] = self.propagate_lines(currLines)
        self.updateFringe(self.__graph[currNodeLabel])
        # print(currLines,self.__graph[currNodeLabel] )
        # self.updateFringe(self.__graph[currNodeLabel])
        
        if len(self.__fringe) > 0 :
            self.propagate()
        else:    
            print("graph : ",self.__graph)
            print("fringe : ",self.__fringe)
            print("visited nodes : ",self.__visited)
            print("alphabets : ",self.__alphabets)

    def propagate_lines(self,Lines) -> dict:
        out = dict()
        for line in Lines:
            
            alphabets = line.get_weight().split(',')
            for alphabet in alphabets:
                if alphabet == EPSILON:
                    continue
                self.__alphabets.add(alphabet)
                if keyExists(out,alphabet):
                    if not line.Node_in in out[alphabet]:
                        out[alphabet].append(line.Node_in)
                else:
                    out[alphabet] = [line.Node_in]

        return out
    
    
    def updateFringe(self,currMap:dict) -> None:
        for key in currMap.keys():
            nodes = currMap[key]
            labels = set([node.get_label() for node in nodes])
            labels = [label for label in labels]
            labels.sort()
            label = '{' + ','.join(labels) + '}'
            label = label if len(label) > 3 else label[1]
            if not label in self.__visited :
                self.__fringe.append([label,nodes])

    def draw(self):

        Drawer(self.__DrawingCanvas,self.__graph,self.__alphabets)

