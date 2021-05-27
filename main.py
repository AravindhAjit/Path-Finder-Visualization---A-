import pygame
from queue import PriorityQueue
from colors import Colors

SCREEN_SIZE = 800
WINDOW = pygame.display.set_mode((SCREEN_SIZE,SCREEN_SIZE))
pygame.display.set_caption("screen")


class Node:
    def __init__(self,row,col,width,total_rows):
        self.row = row
        self.col = col
        self.x = row*width
        self.y = col*width
        self.color = Colors.WHITE_DEFAULT
        self.width = width
        self.total_rows = total_rows
        self.neighbors =[]

    def get_position(self):
        return self.row,self.col 
    
    def is_closed(self):
        return self.color == Colors.RED_VISITED
    
    def is_open(self):
        return self.color == Colors.GREEN_OPEN
    
    def is_obstacle(self):
        return self.color == Colors.BLACK_BARRIER
    
    def is_start(self):
        return self.color == Colors.ORANGE_START

    def is_end(self):
        return self.color == Colors.TURQUOISE_END
    
    def reset(self):
        self.color=Colors.WHITE_DEFAULT
    
    def make_close(self):
        self.color = Colors.RED_VISITED
    
    def make_start(self):
        self.color = Colors.ORANGE_START
    
    def make_open(self):
        self.color = Colors.GREEN_OPEN
    
    def make_obstacle(self):
        self.color = Colors.BLACK_BARRIER
    
    def make_end(self):
        self.color = Colors.TURQUOISE_END
    
    def make_path(self):
        self.color = Colors.PURPLE_PATH

    def draw(self,window):
        pygame.draw.rect(window,self.color,(self.x,self.y,self.width,self.width))
    
    def update_neighbours(self,grid):
        
        self.neighbors = []
        #down
        if self.row <self.total_rows-1 and not grid[self.row+1][self.col].is_obstacle():
           self.neighbors.append(grid[self.row+1][self.col]) 
        #up
        if self.row >0 and not grid[self.row-1][self.col].is_obstacle():
            self.neighbors.append(grid[self.row-1][self.col]) 
        #right
        if self.col <self.total_rows-1 and not grid[self.row][self.col+1].is_obstacle():
            self.neighbors.append(grid[self.row][self.col+1])
        #left
        if self.col >0 and not grid[self.row][self.col-1].is_obstacle():
            self.neighbors.append(grid[self.row][self.col-1]) 
             
           
        
    def __lt__(self,other):
        return False


#heuristic function , find distace between the 2 points(arguements) (L DISTANCE IS CALCULATED)
def heuristic(p1,p2):
    #p1 -> (row,column) ->tuple
    x1,y1=p1
    x2,y2=p2
    return abs(x1-x2)+abs(y1-y2)

def reconstruct(came_from,current,draw):
    while current in came_from:
        current=came_from[current]
        current.make_path()
        draw()

def algorithm(draw,grid,start,end):
    count=0 
    open_set = PriorityQueue()
    open_set.put((0,count,start))
    came_from = {}
    
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start]=0
    
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start]=heuristic(start.get_position(),end.get_position())

    open_set_hash = {start}
    
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2] #fscore,count, "NODE" is selected
        open_set_hash.remove(current)
        
        if current==end:
            reconstruct(came_from,end,draw)
            start.make_start()
            end.make_end()
            return True
        
        for neighbor in current.neighbors:
            temp_g_score = g_score[current]+1
            
            if temp_g_score<g_score[neighbor]: #if we found a better path
                came_from[neighbor] = current
                
                g_score[neighbor]=temp_g_score
                f_score[neighbor]=temp_g_score+heuristic(neighbor.get_position(),end.get_position())
                
                if neighbor not in open_set_hash:
                    count+=1
                    open_set.put((f_score[neighbor],count,neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        draw()

        if current!=start:
            current.make_close()
    return False


def make_grid(rows,width):
    grid =[]
    gap=width//rows
    
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            n=Node(i,j,gap,rows)
            grid[i].append(n)
    return grid

def draw_border_grid(window,row,width):
    gap = width//row
    for i in range(row):
        pygame.draw.line(window,Colors.BLACK_BARRIER,(0,i*gap),(width,i*gap))
        for j in range(row):
            pygame.draw.line(window,Colors.BLACK_BARRIER,(j*gap,0),(j*gap,width))
    
def draw(window,grid,rows,width):
    window.fill(Colors.WHITE_DEFAULT)
    for row in grid:
        for node in row:
            node.draw(window)

    draw_border_grid(window, rows, width)
    
    pygame.display.update()

def get_click_pos(position,rows,width):
    gap = width//rows
    y,x = position

    row = y//gap
    col = x//gap
    return row,col

def main(window,width):
    ROWS = 25
    grid = make_grid(ROWS, width)
    
    start = None
    end=None

    run=True
    started = False

    while run:
        draw(window, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                run = False
            
     
            if pygame.mouse.get_pressed()[0]:
                #left click
                position = pygame.mouse.get_pos()
                row,col = get_click_pos(position, ROWS, width)
                node = grid[row][col]
                if not start and node!=end:
                    start = node
                    start.make_start()
                elif not end and node!=start:
                    end = node
                    end.make_end()
                elif node!=end and node != start:
                    node.make_obstacle()


            elif pygame.mouse.get_pressed()[2]:
                position = pygame.mouse.get_pos()
                row,col = get_click_pos(position, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node==start:
                    start == None
                elif node == end:
                    end=None
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbours(grid)
                    algorithm(lambda: draw(window,grid,ROWS,width),grid,start,end)
                if event.key == pygame.K_ESCAPE:
                    start = None
                    end = None
                    grid=make_grid(ROWS, width)

    pygame.quit()

main(WINDOW,SCREEN_SIZE)