from settings import *
import sys
# BASE_DIR = Path(__file__).resolve().parent.parent.__str__()
# print(BASE_DIR)
sys.path.append(BASE_DIR)

from tkinter import *
from GUI.Node import *
from GUI.treecanvas import *
import math



class Drawer:

    def __init__(self,canvas,graph,alphabet) -> None:
        self.__canvas = canvas
        self.__graph = [i for i in range(10)]
        self.__alphabet = alphabet
        self.__level1 =  self.calculate_level1_shift() # DRAWING_SHIFT
        self.calculate_vertical_distance()
        self.draw()

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
        
        nodes = []
        for i in range(self.__num_of_nodes):
            curr_level = 1 if i % 2 == 0 else 2
            level = self.__level1 if i % 2 == 0 else self.__level2
            hor_shift = math.floor(i/2)*HORIZONTAL_DISTANCE
            n = DFANode(self.__canvas,60+hor_shift,level,f'node{i}',level=curr_level)
            n.create()
            nodes.append(n)
            
        self.connect_all_levels(nodes)
        self.connect_all_in_same_level_up(nodes)
        self.connect_all_in_same_level_down(nodes)

    def connect_all_levels(self,nodes):
        '''
        testing function connect all nodes in upper level with nodes in lower level and vice versa
        '''
        for i in range(0,self.__num_of_nodes,2):
            for j in range(1,self.__num_of_nodes,2):
                nodes[i].connect_node(nodes[j],'a')
                nodes[j].connect_node(nodes[i],'a')
            
    def connect_all_in_same_level_up(self,nodes):
        '''
        testing function connect all nodes in in lower level with each other
        '''
        for i in range(0,self.__num_of_nodes,2):
            for j in range(0,self.__num_of_nodes,2):
                if i == j:
                    continue
                nodes[i].connect_node(nodes[j],f'{i}->{j}')
    
    def connect_all_in_same_level_down(self,nodes):
        '''
        testing function connect all nodes in in lower level with each other
        '''
        for i in range(1,self.__num_of_nodes,2):
            for j in range(1,self.__num_of_nodes,2):
                if i == j:
                    continue
                nodes[i].connect_node(nodes[j],f'{i}->{j}')


if __name__ == "__main__":

    
    root =  Tk()
    root.geometry("700x700")

    can = TreeCanvas(root)
    
    can.grid(row=0,column=0,sticky=(N, S, E, W))
    root.rowconfigure(0,weight=1)
    root.columnconfigure(0,weight=1)
    Drawer(can.canvas,[],[])

    root.mainloop()