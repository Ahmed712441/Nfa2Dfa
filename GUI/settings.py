from pathlib import Path
import math
from tkinter.ttk import *

BASE_DIR = Path(__file__).resolve().parent.parent.__str__()

RADUIS = 30
CIRCLE_COLOR_NORMAL = "#0f0"
LINE_COLOR_NORMAL = "#fff"
LINE_LABEL_COLOR = 'black'
CIRCLE_COLOR_SELECTED = "blue"
LINE_COLOR_SELECTED = 'black'
CANVAS_BACKGROUND_COLOR = 'grey'
INITIAL_NODE_COLOR = 'white'
GOAL_NODE_COLOR = 'red'
GOAL_INITIAL_COLOR = 'yellow'
TREE_NODE_RADUIS = 20
TREE_VER_DISTANCE = 90
TREE_NORMAL_HOR_DISTANCE = 30
ACTIVE_NODE_COLOR = 'orange'
VISITED_NODE_COLOR = 'grey'
FRINGE_NODE_COLOR = 'yellow'
ALREADY_VISITED_COLOR = 'red'
GOAL_PATH_COLOR = 'purple'
ACTIVE_LINE_COLOR = 'black'
GOAL_PATH_LINE_COLOR = 'black'
GOAL_PATH_LINE_LABEL_COLOR = 'white'
LABEL_SELECTED_BG_COLOR = 'black'
CROSS_DISTANCE = TREE_NODE_RADUIS* 0.7071 # cos,sin(45)
VALUE_COLOR = 'red'
SLEEP_AMOUNT = 1
ROUNDED_RADUIS = 30 
EPSILON = '\u03B5'
HORIZONTAL_DISTANCE = 120
DRAWING_SHIFT = 300
DRAWING_ANGLE_TAN = (2*RADUIS+15) / HORIZONTAL_DISTANCE
ALPHA = 0.15 # used for smooth curve on same horizontal level in x calculation (DFA drawing)
BETA = 0.9 # used for smooth curve on same horizontal level in y calculation (DFA drawing)
ALPHA_LABEL = 0.22 # used for smooth curve on same horizontal level in x calculation (DFA drawing)
BETA_LABEL = 0.35 # used for smooth curve on same horizontal level in y calculation (DFA drawing)
LABEL_DIST = 55