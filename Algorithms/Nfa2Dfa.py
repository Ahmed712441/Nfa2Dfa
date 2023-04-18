from GUI.Node import *

def keyExists(dictt:dict,key:str):
    try:
        dictt[key]
        return True
    except:
        return False


class NFA2DFA:

    def __init__(self,initialNode,DrawingCanvas,on_finish_callback) -> None:
        self.__initialNode = initialNode
        self.__DrawingCanvas = DrawingCanvas
        self.__on_finish_callback = on_finish_callback
        # self.__transitionTable = None
        self.__alphabets = set() # set of alphabets
        self.__fringe = [[initialNode.get_label(),[initialNode]]] # nodes that are not yet processed (new nodes)
        self.__visited = set() # nodes that are already propagated
        self.__graph = dict() # transition table
        self.propagate()
        
        
    @staticmethod
    def update_label(label,nodes):
        new_nodes = ','.join([node.get_label() for node in nodes])
        if '{' in label:
           return label[:-1] + ',' +new_nodes+'}'
        else:
            return '{'+ label + ',' + new_nodes+'}'

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