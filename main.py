import sys
from GUI.settings import * 

sys.path.append(BASE_DIR)

from tkinter import *
from GUI.settings import * 
from tkinter.ttk import *
from GUI.treecanvas import TreeCanvas
from GUI.canvas import DrawingCanvas
from GUI.Buttons import *
from Algorithms.Nfa2Dfa import NFA2DFA
from GUI.Node import Line,Node
from GUI.utils import mouse
from tkinter.filedialog import *
from tkinter import messagebox
from GUI.table import TransitionTableWindow

class MainCanvas(Frame):

    def __init__(self,root,width=200,height=200):
        self.width = width
        Frame.__init__(self, root,width=width,height=height) 
        mouse.set_root(self)
        self.__drawing_canvas = DrawingCanvas(self,event_root = root,onselect=self.__on_element_selection,onrelease=self.__on_element_release)
        self.__tree_canvas = TreeCanvas(self)
        self.__control_bar = Button_Bar(self)
        self.__H_label = Label(self,text = "Change Line Label : ")
        self.__H_text = Entry(self)
        self.__H_text.insert(END, "change line label")
        self.__H_text.config(state=DISABLED)
        self.__Name_label = Label(self,text = "Change Node Name :")
        self.__Name_text = Entry(self)
        self.__Name_text.insert(END, "Change node name")
        self.__Name_text.config(state=DISABLED)
        self.__Name_text.bind('<Return>',lambda x: self.__change_node())
        self.__H_text.bind('<Return>',lambda x: self.__change_node())
        self.__submit_changes = Button(self ,text="Submit Changes" , command=self.__change_node)
        self.__submit_changes.config(state=DISABLED)
        self.__current_thread = None
        self.__convert_button = Button(self ,text="Convert Nfa to Dfa" , command=self.__submit_callback)
        self.__show_transition_table_b = Button(self ,text="Show Transition Table" , command=self.__show_transition_table)
        self.__show_transition_table_b.config(state=DISABLED)
        self.__drawing_canvas_buttons = DrawingCanvasButtons(self,self.delete_all,self.__on_save,self.__on_upload)
        self.__drawer = None
        root.bind('<Control-s>',lambda x: self.__on_save())
        root.bind('<Control-o>',lambda x: self.__on_upload())
        self.__pack_on_screen()
    
    def __on_save(self):
        file_path = asksaveasfilename(initialfile='Untitled.gtxt',
                                        defaultextension=".gtxt",
                                        filetypes=[
                                            ("Graph Documents","*.gtxt")])
        if file_path:
            try:
                self.__drawing_canvas.save(file_path)
            except:
                self.__drawing_canvas.delete_all()
                
    def __on_upload(self):
        file_path = askopenfilename(defaultextension=".gtxt",
                                      filetypes=[
                                        ("Graph Documents","*.gtxt")])
        if file_path:
            try:
                self.__drawing_canvas.load(file_path)
            except :
                messagebox.showerror(title="File open error",message="Unable to open corrupted file")
                self.__drawing_canvas.delete_all()

    def get_drawing_canvas(self):
        return self.__drawing_canvas

    def __on_element_selection(self):
        self.focus()
        if isinstance(self.__drawing_canvas.selected , Line):
            self.__H_text.config(state=NORMAL)
            self.__submit_changes.config(state=NORMAL)
            self.__H_text.delete(0, 'end')
            self.__H_text.insert(END, str(self.__drawing_canvas.selected.get_weight()))
        if isinstance(self.__drawing_canvas.selected , Node):
            self.__Name_text.config(state=NORMAL)
            # self.__H_text.config(state=NORMAL)
            self.__submit_changes.config(state=NORMAL)
            # self.__H_text.delete(0, 'end')
            self.__Name_text.delete(0, 'end')
            # self.__H_text.insert(END, str(self.__drawing_canvas.selected.get_heurastic()))
            self.__Name_text.insert(END, str(self.__drawing_canvas.selected.get_label()))
            
    
    def __on_element_release(self):
        
        self.__H_text.delete(0, 'end')
        self.__Name_text.delete(0, 'end')
        self.__Name_text.insert(END, "Change node name")
        self.__H_text.insert(END, "weight (Line) , Heurastic(Node)")
        self.__H_text.config(state=DISABLED)
        self.__submit_changes.config(state=DISABLED)
        self.__Name_text.config(state=DISABLED)
        

    def __change_node(self):
        if isinstance(self.__drawing_canvas.selected , Line):
            try:
                # self.__drawing_canvas.selected.set_weight(int(self.__H_text.get()))
                self.__drawing_canvas.selected.set_weight(self.__H_text.get())
            except :
                messagebox.showerror(title="ValueError",message="weight must be integer")
        elif isinstance(self.__drawing_canvas.selected , Node):
            try:
                # self.__drawing_canvas.selected.set_heurastic(int(self.__H_text.get()))
                self.__drawing_canvas.set_selected_label(self.__Name_text.get())
                # self.__drawing_canvas.selected.set_label(self.__Name_text.get())
            except:
                messagebox.showerror(title="ValueError",message="Node Name already exists")

    def __submit_callback(self,**kwargs):

        if self.__drawing_canvas.initial_node and self.__drawing_canvas.final_nodes > 0:
            
            self.__drawer = NFA2DFA(self.__drawing_canvas.initial_node,self.__tree_canvas.canvas,None)
            self.__control_bar.disable()
            self.__show_transition_table_b.config(state=NORMAL)
            self.__drawing_canvas_buttons.disable()
            self.__convert_button.config(state=DISABLED)
        else:
            message = ''
            if not self.__drawing_canvas.initial_node:
                message+= "Any NFA must contain initial node\n"
            
            if self.__drawing_canvas.final_nodes <= 0:
                message+= "Any NFA must contain at least one final node" 
            
            messagebox.showerror(title="Node Error",message=message)

    def __pack_on_screen(self):
        
        
        
        self.__convert_button.grid(row=0,column=0,sticky = "NSEW",padx=(0, 5))
        self.__show_transition_table_b.grid(row=1,column=0,sticky = "NSEW",padx=(0, 5))
        self.__Name_label.grid(row=0,column=1,sticky = "NSEW",padx=(0, 5))
        self.__Name_text.grid(row=1,column=1,sticky = "NSEW",padx=(0, 5))
        self.__H_label.grid(row=0,column=2,sticky = "NSEW")
        self.__H_text.grid(row=1,column=2,sticky = "NSEW")
        self.__submit_changes.grid(row=1,column=3,sticky = "NSEW",padx=(5, 0))
        self.__tree_canvas.grid(row=2,column=0,sticky = "NSEW")
        self.__drawing_canvas.grid(row=2,column=1,columnspan=2,sticky = "NSEW")
        self.__control_bar.grid(row=2,column=3,sticky = "NSEW")
        
        self.__drawing_canvas_buttons.grid(row=3,column=1,columnspan=2)
        
        
        self.columnconfigure(0,weight=4)
        self.columnconfigure(1,weight=2)
        self.columnconfigure(2,weight=2)
        self.columnconfigure(3,weight=1)
        self.rowconfigure(2,weight=1)
    
    def __show_transition_table(self):
        if self.__drawer:
            table = self.__drawer.get_graph()
            alphabets = self.__drawer.get_alphabets()
            TransitionTableWindow(self,table,alphabets)

    

    def delete_all(self):
        if self.__drawer:
            self.__drawer = None
            self.__on_element_release()
            self.__tree_canvas.canvas.delete("all")
            self.__drawing_canvas.reset()
            self.__control_bar.enable()
            self.__drawing_canvas_buttons.enable()
            self.__show_transition_table_b.config(state=DISABLED)
            self.__convert_button.config(state=NORMAL)
        else:
            self.__drawing_canvas.delete_all()


 

if __name__ == "__main__":
    
    
    root =  Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    w = 1200 if w > 1200 else w
    h = 720 if h > 720 else h
    root.geometry("%dx%d+0+0" % (w, h))
    
    root.title('NFA to DFA')
    root.iconbitmap(os.path.join(BASE_DIR,'GUI','images','logo.ico'))
    can = MainCanvas(root,920,720)
    
    can.grid(row=0,column=0,sticky = "NSEW")
    
    root.columnconfigure(0,weight=1)
    root.rowconfigure(0,weight=1)
    for arg in sys.argv:
        if arg[-5:] == '.gtxt':
          can.get_drawing_canvas().load(arg)

    root.mainloop()
