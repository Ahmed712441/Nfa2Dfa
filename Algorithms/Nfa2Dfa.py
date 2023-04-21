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
        # self.__graph = graph
        self.__graph = [i for i in range(3)]
        self.__alphabet = alphabet
        self.__level1 = DRAWING_SHIFT
        self.calculate_vertical_distance()
        self.draw()

    def calculate_vertical_distance(self):
        self.__num_of_nodes = len(self.__graph) + 1
        self.__nodes_in_line = math.ceil(self.__num_of_nodes/2)
        x1 = DRAWING_SHIFT
        x2 = DRAWING_SHIFT+(self.__nodes_in_line-1)*HORIZONTAL_DISTANCE
        y2 = DRAWING_SHIFT+RADUIS
        self.__level2 = y2 + (x2-x1)*DRAWING_ANGLE_TAN - RADUIS # y1 = 60+x+RADUIS 


    def draw(self):
        
        nodes = []
        for i in range(self.__num_of_nodes):
            level = self.__level1 if i % 2 == 0 else self.__level2
            hor_shift = math.floor(i/2)*HORIZONTAL_DISTANCE
            n = DFANode(self.__canvas,60+hor_shift,level,f'node{i}')
            # n2 = Node(self.__canvas,60+HORIZONTAL_DISTANCE,60,'node2')
            n.create()
            nodes.append(n)
            # n2.create()
        # self.connect_all_levels(nodes)
        self.connect_all_in_same_level(nodes)

    def connect_all_levels(self,nodes):
        '''
        testing function connect all nodes in upper level with nodes in lower level and vice versa
        '''
        for i in range(0,self.__num_of_nodes,2):
            for j in range(1,self.__num_of_nodes,2):
                nodes[i].connect_node(nodes[j],'a')
                nodes[j].connect_node(nodes[i],'a')
            
    def connect_all_in_same_level(self,nodes):
        '''
        testing function connect all nodes in in lower level with each other
        '''
        for i in range(0,self.__num_of_nodes,2):
            for j in range(0,self.__num_of_nodes,2):
                if i == j:
                    continue
                nodes[i].connect_node(nodes[j],'a')
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
        # print(self.__fringe[0])
        # print(epsilon_node)
        # return currLines

    def propagate(self):
        # print(self.__initialNode.lines_out,self.__fringe)
        self.setup_node()
        currNodeLabel , currNodes = self.__fringe.pop(0)
        self.__visited.add(currNodeLabel)
        currLines = [line for node in currNodes for line in node.lines_out ]
        # epsilon_connected = []
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
            # print("labels:" ,labels)
            label = '{' + ','.join(labels) + '}'
            # print(""label)
            label = label if len(label) > 3 else label[1]
            if not label in self.__visited :
                self.__fringe.append([label,nodes])

    def draw(self):

        Drawer(self.__DrawingCanvas,self.__graph,self.__alphabets)

