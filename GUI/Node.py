from abc import abstractmethod
from .settings import *
from .Interfaces import Element,InteractionInterface
from .utils import OverlapException,DuplicateConnectionException,create_label

class Line(Element):

    def __init__(self,canvas,Node_out,Node_in,weight=1):
        
        self.__id = None
        self.__canvas = canvas
        self.Node_in = Node_in
        self.Node_out = Node_out
        self.__weight = str(weight)
        self.__has_epsilon = EPSILON in self.__weight

    def get_canvas(self):
        return self.__canvas

    def get_line_id(self):
        return self.__id 

    def get_label_id(self):
        return self.__label_id 

    def get_save_data(self):

        return  str(self.__weight) + '\t' + str(self.Node_out.get_id()) + '\t' + str(self.Node_in.get_id())  +  '\n'

    def __repr__(self):
        
        return str(self.__weight) + '\t' + str(self.Node_out.get_id()) + '\t' + str(self.Node_in.get_id())

    def has_epsilon(self):
        return self.__has_epsilon

    def get_weight(self):
        return self.__weight
    
    def set_weight(self,new_weight:str):
        
        if new_weight != self.__weight:
            self.__weight = new_weight
            self.__canvas.itemconfig(self.__label_id, text=str(new_weight))
            self.__has_epsilon = EPSILON in self.__weight
            print(self.__has_epsilon)


    def add_label(self):

        x1,y1,x2,y2 = self.__canvas.coords(self.__id)
        x = (x1 + x2)//2
        y = (y1 + y2)//2
        self.__label_id = self.__canvas.create_text((x, y), text=self.__weight)

    def add_label_rounded(self,x,y):
        # Node_in_x+RADUIS+ROUNDED_RADUIS,Node_in_y-RADUIS-ROUNDED_RADUIS
        self.__label_id = self.__canvas.create_text((x, y), text=self.__weight)

    def get_id(self):
        return self.__id


    def create_rounded(self):
        #created when connecting node to itself
        Node_in_x , Node_in_y = self.Node_in.get_coor()
        curv_coor = (Node_in_x+RADUIS+ROUNDED_RADUIS,Node_in_y-RADUIS-ROUNDED_RADUIS) 
        self.__id = self.__canvas.create_line(Node_in_x+RADUIS,Node_in_y,curv_coor[0],curv_coor[1],Node_in_x,Node_in_y-RADUIS,smooth=1,arrow="last",fill=LINE_COLOR_NORMAL)
        self.add_label_rounded(curv_coor[0]-10,curv_coor[1]+10)
        
        return self

    def create(self,smooth=0):
        Node_in_x , Node_in_y = self.Node_in.get_coor()
        Node_out_x , Node_out_y = self.Node_out.get_coor()

        dx = abs(Node_in_x - Node_out_x)
        dy =  None        

        if dx != 0:
            dy = abs(Node_in_y - Node_out_y)
        else:
            dy = Node_in_y - Node_out_y

        if dx == 0 :
            if(Node_in_y < Node_out_y):
                self.__id = self.__canvas.create_line(Node_out_x+RADUIS,Node_out_y,Node_in_x+RADUIS,Node_in_y,arrow="last",fill=LINE_COLOR_NORMAL)
            else:
                self.__id = self.__canvas.create_line(Node_out_x-RADUIS,Node_out_y,Node_in_x-RADUIS,Node_in_y,arrow="last",fill=LINE_COLOR_NORMAL)
        elif(dx > dy):
            if(Node_in_y < Node_out_y):
                self.__id = self.__canvas.create_line(Node_out_x,Node_out_y+RADUIS,Node_in_x,Node_in_y+RADUIS,arrow="last",fill=LINE_COLOR_NORMAL)
            else:
                self.__id = self.__canvas.create_line(Node_out_x,Node_out_y-RADUIS,Node_in_x,Node_in_y-RADUIS,arrow="last",fill=LINE_COLOR_NORMAL)
        else:
            if(Node_in_x < Node_out_x):
                self.__id = self.__canvas.create_line(Node_out_x+RADUIS,Node_out_y,Node_in_x+RADUIS,Node_in_y,arrow="last",fill=LINE_COLOR_NORMAL)
            else:
                self.__id = self.__canvas.create_line(Node_out_x-RADUIS,Node_out_y,Node_in_x-RADUIS,Node_in_y,arrow="last",fill=LINE_COLOR_NORMAL)
            
        self.add_label()
        self.__canvas.lower(self.__id)

        return self

    def set_brother(self,line_id,treecanvas):
        self.__tree_line = line_id
        self.__tree_canvas = treecanvas

    def reset(self):
        self.__tree_line = None
        self.__tree_canvas = None
        self.deselect()
        

    def set_active(self):
        
        self.select()
        self.__tree_canvas.itemconfig(self.__tree_line, fill=ACTIVE_LINE_COLOR)
    
    def set_goal_path(self):

        self.select()
        self.__tree_canvas.itemconfig(self.__tree_line, fill=GOAL_PATH_LINE_COLOR)
    
    def reset_line(self):
        
        self.deselect()
        self.__tree_canvas.itemconfig(self.__tree_line, fill=LINE_COLOR_NORMAL)
    

    def delete(self):
        
        self.Node_in.lines_in.remove(self)
        self.Node_out.lines_out.remove(self)
        self.Node_out.adj.remove(self.Node_in)
        self.__canvas.delete(self.__id)
        self.__canvas.delete(self.__label_id)
        del self


    def select(self):

        self.__canvas.itemconfig(self.__id, fill=LINE_COLOR_SELECTED)
        self.__canvas.itemconfig(self.__label_id,fill=GOAL_PATH_LINE_LABEL_COLOR)

    def deselect(self):

        self.__canvas.itemconfig(self.__id, fill=LINE_COLOR_NORMAL)
        self.__canvas.itemconfig(self.__label_id,fill=LINE_LABEL_COLOR)
    
    def bind_event(self,callback,binded_event='<Button-1>'):
        
        self.__canvas.tag_bind(self.__label_id,binded_event,lambda event, arg=self.__id: callback(event, arg))
        self.__canvas.tag_bind(self.__id, binded_event, lambda event, arg=self.__id: callback(event, arg))

    def __str__(self):

        return "line id: "+str(self.__id) + " connecting:  "+str(self.Node_out) +" with "+str(self.Node_in) 


class Node(Element,InteractionInterface):

    def __init__(self,canvas,x,y,label,heurastic=0,goal=False,initial=False,expanded_level=1000000):
        super(Node,self).__init__(canvas)
        self.adj = [] # carries adjancent nodes
        self.lines_out = [] # has all out lines 
        self.lines_in = [] # has all in lines
        self.__goal = goal # is this node a goal or not 
        self.__canvas = canvas # canvas object helps in drawing on screen
        self.__x = x # x coordinate of its center
        self.__y = y # y coordinate of its center
        self.__label = label # unique label used to identify each node used mainly in GUI 
        self.__initial = initial # boolean value to define if this node is initial or not
        self.__heurastic = heurastic
        self.visited = False
        self.__expanded_level = expanded_level
    
    def get_save_data(self):
        initial = '1' if self.__initial else '0'
        goal = '1' if self.__goal else '0'
        # + str(self.__heurastic) + '\t'
        return str(self.__id) + '\t' + str(self.__label) + '\t' + str(self.__x) + '\t' + str(self.__y) + '\t' + initial + '\t' + goal +'\n'

    def set_heurastic(self,new_heurastic:int):
        if not self.__goal and  new_heurastic != self.__heurastic:
            self.__heurastic = new_heurastic
            self.__canvas.itemconfig(self.__heurastic_id, text=str(self.__heurastic))
    
    def get_heurastic(self):
        return self.__heurastic

    def get_label_id(self):
        return self.__label_id
    
    def label(self):
        return self.__label

    def get_epsilon_nodes(self,avoid):
        epsilon_nodes = [line.Node_in for line in self.lines_out if line.has_epsilon()]
        newavoid = avoid + epsilon_nodes
        for node in epsilon_nodes:
            if node not in avoid:
                epsilons = node.get_epsilon_nodes(newavoid)
                for epsilon in epsilons:
                    epsilon_nodes.append(epsilon)
        return epsilon_nodes
    
    def get_label(self):
        print('called')
        nodes = self.get_epsilon_nodes([self])
        print('returned')
        nodes.append(self)
        nodes.sort()
        # print(nodes)
        return create_label(nodes)

    def set_label(self,new_label):
        if new_label != self.__label:
            self.__label = new_label
            self.__canvas.itemconfig(self.__label_id, text=str(new_label))


    def set_initial(self):

        self.__initial = True
        self.__reset_color()

    def reset_initial(self):
        
        self.__initial = False
        self.__reset_color()

    def set_goal(self):

        # self.set_heurastic(0)        
        self.__goal = True
        self.__reset_color()

    def reset_goal(self):
        
        self.__goal = False
        self.__reset_color()

    def is_goal(self):
        
        return self.__goal

    def connect_node(self,node,weight=1):

        if node in self.adj :
            raise DuplicateConnectionException()
            
        self.adj.append(node)
        l = Line(self.__canvas,self,node,weight)
        l.create()       
        self.lines_out.append(l)
        node.lines_in.append(l)
        return l
    
    def connect_to_itself(self,weight='1'):
        
        if self in self.adj :
            raise DuplicateConnectionException()

        l = Line(self.__canvas,self,self,weight)
        l.create_rounded()
        self.lines_out.append(l)
        self.lines_in.append(l)
        self.adj.append(self)
        
        return l

    def __repr__(self):
        return str(self.__label)

    def get_coor(self):
        return self.__x , self.__y

    def __create_circle(self): 
        
        x0 = self.__x - RADUIS
        y0 = self.__y - RADUIS
        x1 = self.__x + RADUIS
        y1 = self.__y + RADUIS
        overlap = self.__canvas.find_overlapping(x0, y0, x1, y1)
        if len(overlap):
            raise OverlapException()
            
        return self.__canvas.create_oval(x0, y0, x1, y1,fill=CIRCLE_COLOR_NORMAL)


    def create(self):
        self.__id = self.__create_circle()
        self.__label_id = self.__canvas.create_text((self.__x, self.__y), text=self.__label)
        # self.__heurastic_id = self.__canvas.create_text((self.__x-RADUIS, self.__y-RADUIS), text=self.__heurastic,fill=VALUE_COLOR)
        super(Node,self).set_id(self.__id)
        return self.__id

    def get_id(self):
        return self.__id
    
    def delete(self):
        
        for line in self.lines_in + self.lines_out:
            line.delete()
        
        self.__canvas.delete(self.__id)
        self.__canvas.delete(self.__label_id)
        # self.__canvas.delete(self.__heurastic_id)
        del self

    def __lt__(self,other):
        return self.label() < other.label() 

    def select(self):

        self.__canvas.itemconfig(self.__id, fill=CIRCLE_COLOR_SELECTED)

    def __reset_color(self):
        
        if self.__goal and self.__initial:
            self.__canvas.itemconfig(self.__id, fill=GOAL_INITIAL_COLOR)
        elif self.__initial:
            self.__canvas.itemconfig(self.__id, fill=INITIAL_NODE_COLOR)
        elif self.__goal:
            self.__canvas.itemconfig(self.__id, fill=GOAL_NODE_COLOR)
        else:
            self.__canvas.itemconfig(self.__id, fill=CIRCLE_COLOR_NORMAL)

    def get_canvas(self):
        return self.__canvas

    def deselect(self):
        
        self.__reset_color()
        

    def bind_event(self,callback,binded_event='<Button-1>'):
        self.__canvas.tag_bind(self.__id, binded_event, lambda event, arg=self.__id: callback(event, arg))
        self.__canvas.tag_bind(self.__label_id, binded_event, lambda event, arg=self.__id: callback(event, arg))

    # def __str__(self):
    
        # return "Node("+ str(self.__label)+")"
    
    def __str__(self):
        return  str(self.__label)

    def mark_visited(self):
        super().mark_visited()
        self.visited = True
    
    def reset(self):
        super().reset_cross()
        self.__reset_color()
        self.visited = False

    def set_expanded_level(self,level):
        self.__expanded_level = level if level < self.__expanded_level else self.__expanded_level

    def get_expanded_level(self):
        return self.__expanded_level
        
    def is_initial(self):
        return self.__initial



    def load(self,string:str):

        attr = string.split('\t')
        self.__label = attr[1]
        self.__x = float(attr[2])
        self.__y = float(attr[3])
        # self.__heurastic = int(attr[4])
        self.__initial = (attr[4] == '1') 
        goal = (attr[5] =='1')
        self.create()
        if goal:
            self.set_goal()
        self.__reset_color()

    def epsilon_connect(self,next_node):
        
        if next_node in self.adj:
            for line in self.lines_out:
                if line.Node_in == next_node:
                    if line.has_epsilon() :
                        raise DuplicateConnectionException()
                    label = line.get_weight()
                    new_label = EPSILON+','+ label
                    line.set_weight(new_label)
                    # line.has_epsilon = True
                
        else:
            l =  self.connect_node(next_node,EPSILON)
            # l.has_epsilon = True

            return l
        
        return None
    
class DFACurvedLine(Line):

    def __init__(self, canvas, Node_out, Node_in, weight=1):
        super().__init__(canvas, Node_out, Node_in, weight)
        self.__selected = False

    def create_rounded(self):
        l = super().create_rounded()
        self.bind_event(self.toggle)
        return l
    
    def create_rounded_line(self,sign):
        Node_in_x , Node_in_y = self.Node_in.get_coor()
        Node_out_x , Node_out_y = self.Node_out.get_coor()
        dx = Node_out_x - Node_in_x
        
        curv_coor = (Node_out_x-ALPHA*dx, Node_out_y-sign*BETA*abs(dx))
               
        self.__line_id_ = self.get_canvas().create_line(Node_out_x,Node_out_y-sign*RADUIS,curv_coor[0],curv_coor[1],Node_in_x,Node_in_y-sign*RADUIS,smooth=1,arrow="last",fill=LINE_COLOR_NORMAL)
        
        self.add_label_rounded(curv_coor[0]-ALPHA_LABEL*dx,curv_coor[1]+sign*BETA_LABEL*abs(dx))
        
        return self
    
    def get_label_id(self):
        try:
            id = super().get_label_id()
            if id:
                return id 
            else:
                raise Exception("None value for id")
        except:
            return self.__label_id_
        
    
    def get_line_id(self):
        try:
            id = super().get_line_id()
            if id:
                return id 
            else:
                raise Exception("None value for id")
        except:
            return self.__line_id_ 

    def select(self):
        self.__selected = True
        label_id = self.get_label_id()
        line_id = self.get_line_id()
        canvas = self.get_canvas()
        
        canvas.lift(line_id)
        canvas.lift(label_id)
        self.Node_out.lift()
        
        
        canvas.itemconfig(label_id,font=('Arial', 20),fill=LINE_COLOR_NORMAL)
        canvas.itemconfig(line_id, width=5 , fill=LINE_COLOR_SELECTED)
        

    def deselect(self):
        self.__selected = False
        label_id = self.get_label_id()
        line_id = self.get_line_id()
        canvas = self.get_canvas()

        canvas.itemconfig(label_id, font=('Arial', 10),fill=LINE_LABEL_COLOR)
        canvas.itemconfig(line_id, width=1 , fill=LINE_COLOR_NORMAL)

    def toggle(self):
        if self.__selected:
            self.deselect()
        else:
            self.select()

    def bind_event(self, callback, binded_event='<Button-1>'):
        canvas = self.get_canvas()
        label_id = self.get_label_id()
        line_id = self.get_line_id()
        canvas.tag_bind(label_id,binded_event,lambda event, arg=line_id: callback())
        canvas.tag_bind(line_id, binded_event, lambda event, arg=line_id: callback())
        
    def add_label(self):
        
        weight = self.get_weight()
        line_id = self.get_line_id()
        canvas = self.get_canvas()

        x1,y1,x2,y2 = canvas.coords(line_id)
        dy = y1-y2
        dx = x1-x2
        angle= math.atan2(dy,dx)
        x = x1 - LABEL_DIST*math.cos(angle)
        y = y1 - LABEL_DIST*math.sin(angle)
        self.__label_id_ = canvas.create_text((x, y), text=weight)

    

class DFANode(Node):

    def __init__(self, canvas, x, y, label, level, heurastic=0, goal=False, initial=False, expanded_level=1000000,):
        super().__init__(canvas, x, y, label, heurastic, goal, initial, expanded_level)
        self.__level = level 

    def lift(self):
        id = super().get_id()
        label_id = super().get_label_id()
        canvas = super().get_canvas()

        canvas.lift(id)
        canvas.lift(label_id)

    def connect_to_itself(self,weight):
        
        if self in self.adj :
            raise DuplicateConnectionException()

        l = DFACurvedLine(self.get_canvas(),self,self,weight)
        l.create_rounded()
        self.lines_out.append(l)
        self.lines_in.append(l)
        self.adj.append(self)
        
        return l

    def connect_node(self,node,weight=1):
        x1 , y1 = node.get_coor()
        x2 , y2 = self.get_coor()
        
        if node in self.adj :
            raise DuplicateConnectionException()
        
        if node == self:
            return self.connect_to_itself(weight)

        sign = 1 if self.__level == 1 else -1 # used for drawing downward or upward

        l =  None
        if y1 == y2:
            l = DFACurvedLine(self.get_canvas(),self,node,weight)
            l.create_rounded_line(sign)
        else:
            l = DFACurvedLine(self.get_canvas(),self,node,weight)
            l.create()
        l.bind_event(l.toggle)

        return l