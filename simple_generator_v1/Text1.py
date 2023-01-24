import bpy
from math import *
import bmesh
import random
import time
import numpy as np


# klasa reprezentująca genotyp zamku
class Castle:
    def __init__(self, towers_p, tower_w, tower_h, m_point, mp_h, mp_w, bottom_points, tower_objects, cordinate_system_point, points):
        self.towers_points = towers_p
        self.tower_w = tower_w
        self.tower_h = tower_h
        self.main_point = m_point
        self.mp_h = mp_h
        self.mp_w = mp_w
        self.bottom_points = bottom_points
        self.tower_objects = tower_objects
        self.points = points
        self.cordinate_system_point = cordinate_system_point



class Stack:
    def __init__ (self):    # Kostruktor
        self.Stack = []
 
    def Push(self, s):      # Dodawanie elementów
        self.Stack.append(s)
 
    def Pop(self):          # Usuwanie elementu
        self.Stack.pop(len(self.Stack)-1)
 
    def Size(self):         # Ilość elementów na convex_shell_pointsie
        return len(self.Stack)
 
    def Top(self):          # Zwraca ostatni element
        return self.Stack[ len(self.Stack) - 1 ]
 
    def Empty(self):        # Sprawdza czy convex_shell_points jest pusty
        if len(self.Stack) == 0 : 
            return True
        else : 
            return False
    
    def get_elem(self, i):
        return self.Stack[len(self.Stack) - 1 - i]



# tworzy obiekt z podanych punktów
def add_mesh(name, verts, faces, edges=None, col_name="Collection"):    
    if edges is None:
        edges = []
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(mesh.name, mesh)
    col = bpy.data.collections[col_name]
    col.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    mesh.from_pydata(verts, edges, faces)



#tworzy punkty kola
def create_circle_points(nr_points, z, a_x, a_y):
    new_verts = []
    step = 2 * pi /nr_points 

    for i in range(nr_points):
        t = i * step 
        
        x = cos(t) + a_x
        y = sin(t) + a_y 
        new_verts.append((x,y,z))

    return new_verts



# tworzy cylinder w podanych współrzędnych
def create_cylinder(nr_points, x, y, z1, z2):
#    pi = pi    
    
    circle_faces = []
    face = []
        
    all_verts = create_circle_points(nr_points, z1, x, y)
    top_verts = create_circle_points(nr_points, z2, x, y)

    # tworze punkty z dolnego kola i z gornego
    for i in range(len(top_verts)):
        all_verts.append(top_verts[i])
              
    all_faces = []

    # tworze polaczenie punktow dolnego okregu
    face = []    

    for i in range(nr_points):
        face.append(i)
            
    all_faces.append(face)

    # tworzy polaczenie punktow gornego okregu
    face = []

    for i in range(nr_points, 2*nr_points ):
        face.append(i)

    all_faces.append(face)

    # tworze sciany
    face = []
    for i in range(nr_points-1):
        face.append(i)
        face.append(i+nr_points)
        face.append(i+1+nr_points)
        face.append(i+1)
        all_faces.append(face)
        face = []
            
    face.append(nr_points - 1)    
    face.append(2*nr_points - 1)    
    face.append(nr_points)    
    face.append(0)
    all_faces.append(face)    

    add_mesh("cylinder", all_verts, all_faces )



# tworzy dach
def create_pyramid(nr_points, x, y, z1, z2):
    all_verts = create_circle_points(nr_points, z1, x, y)
    all_verts.append((x, y, z2))
    
    all_faces = []
    
     # tworze polaczenie punktow dolnego okregu
    face = []    
    for i in range(nr_points):
        face.append(i)
            
    all_faces.append(face)
    
    # tworze sciany z wierzchołkiem
    face = []
    for i in range(nr_points-1):
        face.append(i)
        face.append(i+1)
        face.append(nr_points)
        all_faces.append(face)
        face = []
    
    face.append(0)
    face.append(nr_points-1)
    face.append(nr_points)
    all_faces.append(face)
            
    add_mesh("pyramid", all_verts, all_faces )



# oblicza długość prostej między odcinkami
def calculate_segment_length(x1, y1, x2, y2):
    return sqrt(pow(x2-x1, 2) + pow(y2-y1, 2))



# oblicza kąt między prostą a osią x
def calculate_angle(x1, y1, x2, y2):
  delta_y = y2 - y1
  delta_x = x2 - x1

  if delta_x != 0:
      return atan2(delta_y , delta_x) * 180 / pi
  else:
      return 90.0

    

# tworzy mur zamku
def create_wall(x1, y1, x2, y2, z1, z2):
    a_y = 0.3
    
    all_verts = []    
    #dolne punkty
    all_verts.append((x1, y1+a_y, z1))
    all_verts.append((x1, y1-a_y, z1))
    all_verts.append((x2, y2-a_y, z1))
    all_verts.append((x2, y2+a_y, z1))
    # górne punkty
    all_verts.append((x1, y1+a_y, z2))
    all_verts.append((x1, y1-a_y, z2))
    all_verts.append((x2, y2-a_y, z2))
    all_verts.append((x2, y2+a_y, z2))

    all_faces = []
    
    # dodaje ściany boczne
    face = []
    for i in range(3):
        face.append(i)
        face.append(i+1)
        face.append(i+5)
        face.append(i+4)
        all_faces.append(face)
        face = []
        
    all_faces.append([0, 3, 7, 4])    
    
    #dodaje podstawy
    all_faces.append([0, 1, 2, 3])    
    all_faces.append([4, 5, 6, 7])    
        
    add_mesh("wall", all_verts, all_faces )
    ob = bpy.context.active_object
    


# generuje liste punktów w układzie współrzędnych
def generate_points(max_nr):
    points = []
    s_point = []
    
    for i in range(max_nr): 
        x = round(random.uniform(-15.0, 15.0), 2)
        y = round(random.uniform(0.0, 30.0), 2)
        s_point.append(x)
        s_point.append(y)
        points.append(s_point)
        s_point = []
        
    return points



# znajduje punkt o najmniejszym y
def find_starting_point(towers_points):
    min_point = towers_points[0]
    
    for i in range(1, len(towers_points)):
        if towers_points[i][1] < min_point[1]:
            min_point = towers_points[i]
        elif towers_points[i][1] == min_point[1]:
            if towers_points[i][0] < min_point[0]:
                min_point = towers_points[i]

    return min_point     



# do sortowania listy punktów
def get_alpha(point):
    return point[2]



# sortuje wierzchołki względem rosnących kątów nachylenia wektorów wodzących do osi OX 
def calculate_alpha(towers_points):
    points = []
    
    for i in range(len(towers_points)):
        x = towers_points[i][0]
        y = towers_points[i][1] 
        d = abs(x) + abs(y)
         
        if x>=0:
            if y>=0:
                alfa = y/d
            elif y<0:
                alfa = 4 - (abs(y)/d)
        elif x<0:
            if y>=0:
                alfa = 2 - (y/d)
            elif y<0:
                alfa = 2 + (abs(y)/d)
                
        points.append([x, y, alfa])
        
    points.sort(key=get_alpha)    
    return points



# oblicza wyznacznik macierzy dla 3 kolejnych punktów
def is_right(convex_shell_points, point):
    top = convex_shell_points.Top()
    convex_shell_points.Pop()
    next_top = convex_shell_points.Top()
    convex_shell_points.Push(top)
    
    redrix = np.array([[next_top[0], next_top[1], 1.0], 
                       [top[0], top[1], 1.0],
                       [point[0], point[1], 1.0]])

    return round(np.linalg.det(redrix), 2)



# tworzy otoczke wypukłą na podstawie podanych punktów
def create_convex_shell(towers_points):
    # pobiera element z najmniejszym y
    starting_point = find_starting_point(towers_points)
    towers_points.remove(starting_point)
    
    # dla reszty punktów obliczam ich alfa (współrzędą polarną)
    alpha_points = calculate_alpha(towers_points)
        
    convex_shell_points = Stack()
    convex_shell_points.Push(starting_point)
    convex_shell_points.Push([alpha_points[0][0], alpha_points[0][1]])
    convex_shell_points.Push([alpha_points[1][0], alpha_points[1][1]])
    
    for i in range(2, len(alpha_points)):
        while is_right(convex_shell_points, alpha_points[i]) < 0.0: 
            convex_shell_points.Pop()
        convex_shell_points.Push([alpha_points[i][0], alpha_points[i][1]])

    result_points = []                
    for i in range(convex_shell_points.Size()):
        result_points.append(convex_shell_points.get_elem(i))
    
    return result_points
    


# usuwa z otoczki punkty leżące zbyt blisko siebie
def delete_too_narrow_convex_points(convex_points, tower_width):
    last_points = []
    last_points.append(convex_points[0])
    
    # usuwam punkty otoczki, które leżą za blisko siebie
    for i in range(1, len(convex_points)):
        if abs(calculate_segment_length(convex_points[i][0], convex_points[i][1], convex_points[i-1][0], convex_points[i-1][1])) >= float(tower_width) + 2.0:
            last_points.append(convex_points[i])
    
    return last_points



# generuje na ekranie wieże z podanej listy punktów
def generate_towers(last_points, tower_width, tower_height):
    for i in range(len(last_points)):
        create_cylinder(50, 0.0, 0.0, 0.0, 1.0)
        ob = bpy.context.active_object
        ob.scale = (tower_width, tower_width, tower_height)
        ob.location = (last_points[i][0], last_points[i][1], 0)
        ob.data.materials.append(red)
        
        create_pyramid(40, 0.0, 0.0, 0.0, 1.0)
        ob = bpy.context.active_object
        ob.scale = (tower_width*1.1, tower_width*1.1, tower_height/2)
        ob.location = (last_points[i][0], last_points[i][1], tower_height)
        ob.data.materials.append(brown)
        


# generuje pojedynczą ściane
def generate_single_wall(point1, point2, tower_width, tower_height):
    create_wall(0.0, 0.0, 1.0, 0.0, 0.0, 1.0)
    ob = bpy.context.active_object
        
    length = calculate_segment_length(point1[0], point1[1], point2[0], point2[1])
    ob.scale = (length, tower_width/2, tower_height/2)
        
    radian = calculate_angle(point1[0], point1[1], point2[0], point2[1])
    ob.rotation_euler = (0,0,radians(radian))
        
    ob.location = (point1[0], point1[1], 0.0)
    ob.data.materials.append(red)
    


# generuje ściany na ekranie
def generate_walls(points, tower_width, tower_height):
    for i in range(1, len(points)):
        generate_single_wall(points[i-1], points[i], tower_width, tower_height)
    
    generate_single_wall(points[len(points)-1], points[0], tower_width, tower_height)
    
        
    
# ustala współrzędne punktu będącego w środku murów         
def get_centre_point(points):
    min_y = find_starting_point(points)
    max_y = points[0]
    min_x = points[0]
    max_x = points[0]
        
    for i in range(1, len(points)):
        if points[i][1] > max_y[1]:
            max_y = points[i]
        
        if points[i][0] < min_x[0]:
            min_x = points[i]
        
        if points[i][0] > max_x[0]:
            max_x = points[i]
            
    x = (max_x[0] + min_x[0]) / 2
    y = (max_y[1] + min_y[1]) / 2

    if (abs(max_x[0]) - abs(min_x[0])) > abs(max_y[1]) - abs(min_y[1]):
        size = abs(max_x[0]) - abs(min_x[0])
    else:
        size = abs(max_y[1]) - abs(min_y[1])
        
    x = round(x)
    y = round(y)
    
    if not x%3==0:
        if (x+1)%3==0:
            x = x+1
        elif (x-1)%3==0:
            x = x-1
        elif (x+2)%3==0:
            x = x+2
        elif (x-2)%3==0:
            x = x-2   
    
    if not y%3==0:
        if (y+1)%3==0:
            y = y+1
        elif (y-1)%3==0:
            y = y-1
        elif (y+2)%3==0:
            y = y+2
        elif (y-2)%3==0:
            y = y-2      
    
    return [x, y], 1.5 #round(size)
    
    

# tworzy wierze w zamku
def create_castle_tower(point, scale, tower_height):
    width = scale/2.5
    
    create_cylinder(50, 0.0, 0.0, 0.0, 1.0)
    ob = bpy.context.active_object
    ob.scale = (width, width, tower_height*0.5)
    ob.location = (point[0], point[1], point[2])
    ob.data.materials.append(blue)
        
    create_pyramid(40, 0.0, 0.0, 0.0, 1.0)
    ob = bpy.context.active_object
    ob.scale = (width*1.1, width*1.1, scale)
    ob.location = (point[0], point[1], point[2]+tower_height*0.5)
    ob.data.materials.append(black)
    
    create_pyramid(40, 0.0, 0.0, 0.0, 1.0)
    ob = bpy.context.active_object
    ob.scale = (width, width, scale/2)
    ob.rotation_euler = (0,radians(180), 0)
    ob.location = (point[0], point[1], point[2])
    ob.data.materials.append(blue)  
    


# generuje główny budynek w zamku
def generate_main_building(point, size, tower_width, tower_height):
    obj_nr = random.randint(1, 3) 
    height = 1.5
    scale = 1.5
    objects = []
    
    #generuje obiekt w podstawie
    create_obj_with_doors(point, scale, height)
    
    #generuje obiekty wszerz podstawy
    bottom_points = add_bottom_objects(point, scale, height)
    
    for i in range(obj_nr):    
        new_p = [point[0], point[1], 3*height + 2*height*i]
        objects.append(create_middle_obj(new_p, scale, height))

    new_p = [point[0], point[1], 3*height + 2*height*obj_nr]
    objects.append(create_top_obj(new_p, scale, height, tower_height))
    
    return bottom_points, scale, height, objects



# tworzy dolną część budynku
def create_obj_with_doors(point, scale, height):
    # gł część
    bpy.ops.mesh.primitive_cube_add()
    cube1 = bpy.context.active_object
    cube1.scale = (scale, scale, height)
    cube1.location = (point[0], point[1], height)
    cube1.data.materials.append(blue)
    
    # drzwi
    bpy.ops.mesh.primitive_cube_add()
    cube1 = bpy.context.active_object
    cube1.scale = (height/3, scale/3, height/2.5)
    
    x = random.uniform(point[0]-height/3, point[0]+height/3) 
    cube1.location = (x, point[1]-scale+scale/4, height/2.5)
    cube1.data.materials.append(brown) 
    
    
    
# tworzy część budynku z oknami    
def create_middle_obj(point, scale, height):
    rand_obj = random.randint(1, 3)
  
    match rand_obj:
        # tworze obiekt z kwadratowymi oknami
        case 1:
            create_obj_with_cubic_window(point, scale, height)
        
        # tworze obiekt z okrągłymi oknami
        case 2:
            create_obj_with_circle_window(point, scale, height)
        
        # tworze obiekt z wcięciami
        case 3:
            create_indentend_obj(point, scale, height)
    
    return rand_obj



# twory obiekt z kwadratowymi oknami
def create_obj_with_cubic_window(point, scale, height):
    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    obj.scale = (scale, scale, height)
    obj.location = (point[0], point[1], point[2])
    obj.data.materials.append(blue)

    # tworze okno
    cube = create_cubic_window()
    
    # umiejscowienie okien
    cube = bpy.context.active_object
    cube.location = (point[0], point[1]-scale, point[2])
    cube.scale = (0.4*scale, 0.1, 0.4*scale)
    
    # okno na lewej ścianie
    l_cube = bpy.context.active_object.copy()
    l_cube.rotation_euler = (0,0,radians(90))
    l_cube.location = (point[0]-scale, point[1], point[2])
    bpy.context.collection.objects.link(l_cube)
    
    # okno na prawej ścianie
    r_cube = bpy.context.active_object.copy()
    r_cube.rotation_euler = (0,0,radians(90))
    r_cube.location = (point[0]+scale, point[1], point[2])
    bpy.context.collection.objects.link(r_cube)
    
    # okno na tylnej ścianie
    b_cube = bpy.context.active_object.copy()
    b_cube.location = (point[0], point[1]+scale, point[2])
    b_cube.scale = (0.4*scale, 0.1, 0.4*scale)
    bpy.context.collection.objects.link(b_cube)

    

# def tworzy obiekt z okrągłymi oknami
def create_obj_with_circle_window(point, scale, height):
    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    obj.scale = (scale, scale, height)
    obj.location = (point[0], point[1], point[2])
    obj.data.materials.append(blue)

    # tworze okno
    cube = create_circle_window()
    
    # umiejscowienie okien
    cube = bpy.context.active_object
    cube.scale = (0.4*scale, 0.4*scale, 0.1)
    cube.rotation_euler = (radians(90), radians(90),0)
    cube.location = (point[0], point[1]-scale, point[2])
    
    # okno na lewej ścianie
    l_cube = bpy.context.active_object.copy()
    l_cube.rotation_euler = (0, radians(90), 0)
    l_cube.location = (point[0]-scale-0.1, point[1], point[2])
    bpy.context.collection.objects.link(l_cube)
    
    # okno na prawej ścianie
    r_cube = bpy.context.active_object.copy()
    r_cube.rotation_euler = (0, radians(90), 0)
    r_cube.location = (point[0]+scale, point[1], point[2])
    bpy.context.collection.objects.link(r_cube)
    
    # okno na tylnej ścianie
    b_cube = bpy.context.active_object.copy()
    b_cube.location = (point[0], point[1]+scale+0.1, point[2])
    cube.scale = (0.4*scale, 0.4*scale, 0.1)
    bpy.context.collection.objects.link(b_cube)    
    
    

# tworzy kwadratowe okno
def create_cubic_window():
    bpy.ops.mesh.primitive_cube_add()
    cube1 = bpy.context.active_object
    cube1.scale = (1.2, 0.5, 1.2)
    cube1.location = (-2, 0.0, 2.0)
    cube1.data.materials.append(brown)
    bpy.context.active_object.name = 'cube'

    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object
    cube.location = (0.0, 0.0, 0.0)
    cube.scale = (4, 0.5, 4)
    cube.data.materials.append(brown)
    
    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers["Boolean"].object = cube1
    bpy.ops.object.modifier_apply(modifier="Boolean")
    
    cube1.location = (-2, 0.0, -2.0)
    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers["Boolean"].object = cube1
    bpy.ops.object.modifier_apply(modifier="Boolean")
        
    cube1.location = (2, 0.0, -2.0)
    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers["Boolean"].object = cube1
    bpy.ops.object.modifier_apply(modifier="Boolean")

    cube1.location = (2, 0.0, 2.0)
    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers["Boolean"].object = cube1
    bpy.ops.object.modifier_apply(modifier="Boolean")    
        
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['cube'].select_set(True)
    bpy.ops.object.delete()
    
    return cube



# tworzy okrągłe okno
def create_circle_window():
    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object
    cube.scale = (0.5, 0.5, 1)
    cube.location = (0.7, 0.7, 0)
    bpy.context.active_object.name = 'cube'

    create_cylinder(50, 0.0, 0.0, 0.0, 1.0)
    cylinder = bpy.context.active_object
    cylinder.scale = (2, 2, 0.5)
    cylinder.data.materials.append(brown)

    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers["Boolean"].object = cube
    bpy.ops.object.modifier_apply(modifier="Boolean")
    
    cube.location = (-0.7, 0.7, 0)
    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers["Boolean"].object = cube
    bpy.ops.object.modifier_apply(modifier="Boolean")
    
    cube.location = (-0.7, -0.7, 0)
    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers["Boolean"].object = cube
    bpy.ops.object.modifier_apply(modifier="Boolean")
    
    cube.location = (0.7, -0.7, 0)
    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers["Boolean"].object = cube
    bpy.ops.object.modifier_apply(modifier="Boolean")
    
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['cube'].select_set(True)
    bpy.ops.object.delete()
    
    return cylinder    



# tworzy obiekt z wcięciem
def create_indentend_obj(point, scale, height):
    bpy.ops.mesh.primitive_cube_add()
    cube1 = bpy.context.active_object
    cube1.scale = (1.2, 1.2, 1.2)
    cube1.location = (2, 2, 0)
    bpy.context.active_object.name = 'cube'
    cube1.data.materials.append(brown)

    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object
    cube.location = (0.0, 0.0, 0.0)
    cube.scale = (2, 2, 2)
    cube.data.materials.append(blue)
    
    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers["Boolean"].object = cube1
    bpy.ops.object.modifier_apply(modifier="Boolean")
    
    cube1.location = (-2, 2, 0)
    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers["Boolean"].object = cube1
    bpy.ops.object.modifier_apply(modifier="Boolean")
        
    cube1.location = (-2, -2, 0)
    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers["Boolean"].object = cube1
    bpy.ops.object.modifier_apply(modifier="Boolean")

    cube1.location = (2, -2, 0)
    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers["Boolean"].object = cube1
    bpy.ops.object.modifier_apply(modifier="Boolean")    
              
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['cube'].select_set(True)
    bpy.ops.object.delete()
    
    cube.location = (point[0], point[1], point[2])
    cube.scale = (scale, scale, height)
    
    

# generuje obiekt na szczycie 
def create_top_obj(point, scale, height, tower_height):
    rand_obj = random.randint(1, 2)

    match rand_obj:
        # tworze obiekt z wieżami na krawędziach
        case 1:
           create_obj_with_towers(point, scale, height, tower_height)      

        # tworze wieże z zegarem 
        case 2:
           create_clock([point[0], point[1], point[2]-height], scale, height)
    
    return rand_obj
           

# tworzy obiekt z wieżami na krawędziach
def create_obj_with_towers(point, scale, height, tower_height):
    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object
    cube.scale = (scale, scale, height)
    cube.location = (point[0], point[1], point[2])
    cube.data.materials.append(blue)
    
    value = 0.1
    # prawy góra
    corner_point = [point[0] + scale, point[1] + scale, point[2] - (height)*value]
    create_castle_tower(corner_point, height, tower_height)
    
    #prawy dół
    corner_point = [point[0] + scale, point[1] - scale, point[2] - (height)*value]
    create_castle_tower(corner_point, height, tower_height)
    
    #lewy dół
    corner_point = [point[0] - scale, point[1] - scale, point[2] - (height)*value]
    create_castle_tower(corner_point, height, tower_height)
    
    #lewy góra
    corner_point = [point[0] - scale, point[1] + scale, point[2] - (height)*value]
    create_castle_tower(corner_point, height, tower_height)



# tworzy zegary
def create_clock(point, scale, height):
    # dopełnienie podstawy
    create_pyramid(4, 0.0, 0.0, 0.0, 1.0)
    ob = bpy.context.active_object
    ob.rotation_euler = (0, 0, radians(45))
    ob.scale = (scale*1.4, scale*1.4, height)
    ob.location = (point[0], point[1], point[2])
    ob.data.materials.append(blue)
        
    # główna wieża    
    create_cylinder(20, 0.0, 0.0, 0.0, 1.0)
    ob = bpy.context.active_object
    ob.scale = (scale, scale, height*2)
    ob.location = (point[0], point[1], point[2])
    ob.data.materials.append(blue)
        
    # dach wieży    
    create_pyramid(40, 0.0, 0.0, 0.0, 1.0)
    ob = bpy.context.active_object
    ob.scale = (scale*1.1, scale*1.1, scale)
    ob.location = (point[0], point[1], point[2]+2*height)
    ob.data.materials.append(black)
    
    # zegary
    create_cylinder(20, 0.0, 0.0, 0.0, 1.0)
    ob = bpy.context.active_object
    ob.scale = (scale/3, scale/3, scale*2.1)
    ob.rotation_euler = (radians(90), 0, 0)
    ob.location = (point[0], point[1]+scale+0.05, point[2]+height)
    ob.data.materials.append(yellow)
    
    clock = bpy.context.active_object.copy()
    clock.rotation_euler = (radians(90), 0, radians(90))
    clock.location = (point[0]-scale-0.05, point[1], point[2]+height)
    bpy.context.collection.objects.link(clock)
    
    # wskazówki 1
    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object
    cube.scale = (scale/90, scale+0.15, scale/7)
    cube.location = (point[0], point[1]-0.03, point[2]+height+scale/8)
    cube.data.materials.append(black)
    
    clock_h = bpy.context.active_object.copy()
    clock_h2 = bpy.context.active_object.copy()
    cube2 = bpy.context.active_object.copy()
    
    clock_h.rotation_euler = (0, radians(60), 0)
    clock_h.scale = (scale/90, 0.15+scale/2, scale/7)
    clock_h.location = (point[0]-scale/14, point[1]-0.03-scale/2, point[2]+height)
    bpy.context.collection.objects.link(clock_h)

    clock_h2 = bpy.context.active_object.copy()
    clock_h2.rotation_euler = (0, radians(300), 0)
    clock_h2.scale = (scale/90, 0.15+scale/2, scale/7)
    clock_h2.location = (point[0]+scale/14, point[1]-0.03+scale/2, point[2]+height)
    bpy.context.collection.objects.link(clock_h2)
    
    # wskazówki 2
    cube2.rotation_euler = (0, 0, radians(90))
    cube2.location = (point[0]+0.03, point[1], point[2]+height+scale/8)
    bpy.context.collection.objects.link(cube2)
        
    clock2_h = bpy.context.active_object.copy()
    clock2_h2 = bpy.context.active_object.copy()
    
    clock2_h.rotation_euler = (0, radians(300), radians(90))
    clock2_h.scale = (scale/90, 0.15+scale/2, scale/7)
    clock2_h.location = (point[0]-0.03-scale/2, point[1]+scale/14, point[2]+height)
    bpy.context.collection.objects.link(clock2_h)
    
    clock2_h2.rotation_euler = (0, radians(60), radians(90))
    clock2_h2.scale = (scale/90, 0.15+scale/2, scale/7)
    clock2_h2.location = (point[0]+0.03+scale/2, point[1]-scale/14, point[2]+height)
    bpy.context.collection.objects.link(clock2_h2)    
    
    

#dodaje elementy wszerz elementu głównego
def add_bottom_objects(point, scale, height):
    obj_nr = random.randint(1, 20)
    bottom_obj = [point]
    
    for i in range(obj_nr):
        found_p = False
        while not found_p:
            checks = 1
            #wybieram punkt od którego wyjde
            point_nr = random.randint(0, len(bottom_obj)-1)
            temp_p = [bottom_obj[point_nr][0], bottom_obj[point_nr][1]]
                    
            while not found_p and checks <= 4:
                # wybieram kierunek w którym dodam sąsiada
                direction_nr = random.randint(0, 3)
                match direction_nr:
                # u góry
                    case 0:
                        new_p = [temp_p[0], temp_p[1] + 2*scale]
                    # w prawo    
                    case 1:
                        new_p = [temp_p[0] + 2*scale, temp_p[1]]
                    # u dołu    
                    case 2:
                        new_p = [temp_p[0], temp_p[1] - 2*scale]
                    # w lewo
                    case 3:
                        new_p = [temp_p[0] - 2*scale, temp_p[1]]
                    
                if not check_if_point_in_list(bottom_obj, [round(new_p[0],2), round(new_p[1], 2)] ):
                    bottom_obj.append([round(new_p[0], 2), round(new_p[1], 2)])
            
                    bpy.ops.mesh.primitive_cube_add()
                    cube = bpy.context.active_object
                    cube.scale = (scale, scale, height)
                    cube.location = (new_p[0], new_p[1], height)
                    cube.data.materials.append(blue)
                    found_p = True
                    checks = 1
                else:
                    checks += 1
        
    bottom_obj.sort(key = lambda x: x[0])
    return bottom_obj

            
           
# sprawdza czy punkt jest w liście            
def check_if_point_in_list(list, point):
    for i in range(len(list)):
        if list[i][0] == point[0] and list[i][1] == point[1]:
            return True    
    return False    



# oblicza najmniejsze odległości między klockami a ścianami
def get_match_value(towers_points, points, size):
    min_dist = []
    
    for i in range(len(points)):
        min = size
        for j in range(1, len(towers_points)):
            distance = calculate_distance(points[i], towers_points[j-1], towers_points[j] )
            if distance <= min:
                min = distance  
        min_dist.append(min)
             
    min_dist.sort()

    return min_dist


           
# oblicza odległość punktu od prostej            
def calculate_distance(p, s1, s2):
    p = np.array([p[0], p[1]])
    s1 = np.array([s1[0], s1[1]])
    s2 = np.array([s2[0], s2[1]])
    return np.linalg.norm(np.cross(s2 - s1, s1 - p))/np.linalg.norm(s2 - s1)



# funkcja dopasowania
def matching_function(castle): #(towers_points, bottom_points, scale):
    points = 0
    new_points = []
    
    # sprawdzam ile punktów jest poza murami
    e = []
    for i in range(1, len(castle.towers_points)):
        e_temp = [round(castle.towers_points[i][0]-castle.towers_points[i-1][0], 2), round(castle.towers_points[i][1]-castle.towers_points[i-1][1], 2)] 
        e.append(e_temp)
    
    e_temp = [round(castle.towers_points[0][0]-castle.towers_points[len(castle.towers_points)-1][0], 2), round(castle.towers_points[0][1]-castle.towers_points[len(castle.towers_points)-1][1], 2)] 
    e.append(e_temp)
    
    outside = 0
    for i in range(len(castle.bottom_points)):
        f = []
        plus = 0
        minus = 0
        
        for j in range(len(castle.towers_points)):
            f_temp = [round(castle.bottom_points[i][0]-castle.towers_points[j][0],2), round(castle.bottom_points[i][1]-castle.towers_points[j][1],2)]
            f.append(f_temp)
    
        for n in range(len(e)):
            d = round(e[n][0] * f[n][1] - f[n][0] * e[n][1], 2)
            
            if d >= 0:
                plus += 1 
            if d < 0:
                minus += 1
            
        if plus != 0 and minus != 0:
            outside += 1
        else:
            new_points.append(castle.bottom_points[i])

    if outside < len(castle.bottom_points)-3 and outside != 0:
        points -= outside*100
    else:
        new_points = castle.bottom_points
        
    # liczy punkty z ilości wież 
    points += len(castle.towers_points)*5
    
    # oblicza minimalne odległości od ścian dla każdego bloku
    min_distances = get_match_value(castle.towers_points, new_points, castle.mp_h)
        
    for n in range(len(min_distances)):
        if min_distances[n] < castle.mp_h:
            points += 1
        elif min_distances[n] < 2*castle.mp_h:    
            points += 2
        else:
            points += 20

    # oblicza ilość symetrii między klockami
    symetry = 0
    x_symetries = []
    y_symetries = []
    
    for i in range(len(new_points)):
        if round(new_points[i][0], 2) not in x_symetries:
            x_symetries.append(round(new_points[i][0], 2))
        if round(new_points[i][1], 2) not in y_symetries:
            y_symetries.append(round(new_points[i][1], 2))

    for i in range(len(x_symetries)):
        x_symetry = 0
        for j in range(len(new_points)):
            x = x_symetries[i] - new_points[j][0]
            
            if new_points[j][0] < x_symetries[i]:
                if check_if_x_symetry_point_exist(new_points, [x_symetries[i], new_points[j][1]], new_points[j] ):
                    x_symetry += 1
                    continue
        symetry += pow(x_symetry, 2)
    
    for i in range(len(y_symetries)):
        y_symetry = 0
        for j in range(len(new_points)):
            y = y_symetries[i] - new_points[j][1]
            
            if new_points[j][1] < y_symetries[i]:
                if check_if_y_symetry_point_exist(new_points, [new_points[j][0], y_symetries[i]], new_points[j] ):
                    y_symetry += 1
                    continue
        symetry += pow(y_symetry, 2)

    points += symetry    
    return points
    


# sprawdza czy punkt ma punkt symetryczny według symetrii x
def check_if_x_symetry_point_exist(points, middle_point, point):
    x = round(middle_point[0]-point[0], 2)
    
    for i in range(len(points)):    
        if (points[i][0] == round(x + middle_point[0],2) and points[i][1] == point[1]):
            return True
    return False
          


# sprawdza czy punkt ma punkt symetryczny według symetrii y
def check_if_y_symetry_point_exist(points, middle_point, point):
    y = round(middle_point[1]-point[1], 2)
    
    for i in range(len(points)):   
        if (points[i][1] == round(y + middle_point[1],2) and points[i][0] == point[0]):
            return True
    return False



# funkcja tworząca rodzica oraz jego genotyp
def create_parent(x, y, red, brown, blue, black, yellow):
    # losuje ilość punktów
    towers_nr = random.randint(3, 50)
    
    # generuje liste punktów
    towers_points = generate_points(towers_nr)
    
    # tworzy otoczke wypukłą z podanych punktów i zwraca punkty tej ortoczki
    convex_points = create_convex_shell(towers_points)

    # ustawiam skalę szerokości i wysokości wież
    tower_width =  2 
    tower_height = 7 

    # usuwam z otoczki punkty leżące zbyt blisko siebie
    last_points = delete_too_narrow_convex_points(convex_points, tower_width)

    # punkty przed zmianą
    org_points = []
        
    for i in range(len(last_points)):
        org_points.append([last_points[i][0], last_points[i][1]])
        last_points[i] = [last_points[i][0] + x, last_points[i][1] + y]

    # generuje wieże
    generate_towers(last_points, tower_width, tower_height)
    
    # generuje ściany między wieżami
    generate_walls(last_points, tower_width, tower_height)
    
    # generuje budynek w środku - zamek
    point, size = get_centre_point(org_points)  
    point = [point[0]+x, point[1]+y]
    bottom_points, scale, height, objects = generate_main_building(point, size, tower_width, tower_height) 

    # ustawienie wczesnieszych wartosci
    for i in range(len(bottom_points)):
        bottom_points[i] = [bottom_points[i][0] - x, bottom_points[i][1] - y]
    
    point = [point[0]-x, point[1]-y]
    return Castle(org_points, tower_width, tower_height, point, height, scale, bottom_points, objects, [-15, 0], 0)



#funkcja krzyżująca dwa genotypy na dwójke dzieci
def crossing(parent1, parent2):
    towers1 = []
    towers2 = []
    
    x1 = -30
    x2 = 30
    y = 40
    
    # mieszam liste wież dla obu dzieci: 1-12, 2-21 
    for i in range(len(parent1.towers_points)//2):
        towers1.append([parent1.towers_points[i][0]+x1, parent1.towers_points[i][1]+y])
        
    for i in range(len(parent2.towers_points)//2, len(parent2.towers_points)):
        towers1.append([parent2.towers_points[i][0]+x1, parent2.towers_points[i][1]+y])
    
    for i in range(len(parent2.towers_points)//2):
        towers2.append([parent2.towers_points[i][0]+x2, parent2.towers_points[i][1]+y])
        
    for i in range(len(parent1.towers_points)//2, len(parent1.towers_points)):
        towers2.append([parent1.towers_points[i][0]+x2, parent1.towers_points[i][1]+y])

    # punkt środkowy i wymiary kostek
    point1 = [parent1.main_point[0]+x1, p1.main_point[1]+y]
    p1_w = p2.mp_w
    p1_h = p1.mp_h
    
    point2 = [parent2.main_point[0]+x2, p2.main_point[1]+y]
    p2_w = p1.mp_w
    p2_h = p2.mp_h

    # mieszanie kostek: 1-12, 2-21  
    bottom_p1 = []
    bottom_p2 = []
    for i in range(len(parent1.bottom_points)//2):
        bottom_p1.append([parent1.bottom_points[i][0]+x1, parent1.bottom_points[i][1]+y])
    
    for i in range(len(parent2.bottom_points)//2, len(parent2.bottom_points)):
        bottom_p1.append([parent2.bottom_points[i][0]+x1, parent2.bottom_points[i][1]+y])

    for i in range(len(parent2.bottom_points)//2):
        bottom_p2.append([parent2.bottom_points[i][0]+x2, parent2.bottom_points[i][1]+y])
    
    for i in range(len(parent1.bottom_points)//2, len(parent1.bottom_points)):
        bottom_p2.append([parent1.bottom_points[i][0]+x2, parent1.bottom_points[i][1]+y])

    # mieszanie główego budynku: 1-12, 2-21
    main_b1 = []
    main_b2 = []
    for i in range(len(parent1.tower_objects)//2):
        main_b1.append(parent1.tower_objects[i])
    
    for i in range(len(parent2.tower_objects)//2, len(parent2.tower_objects)):
        main_b1.append(parent2.tower_objects[i])
        
    for i in range(len(parent2.tower_objects)//2):
        main_b2.append(parent2.tower_objects[i])
    
    for i in range(len(parent1.tower_objects)//2, len(parent1.tower_objects)):
        main_b2.append(parent1.tower_objects[i])

    ch1 =  Castle(towers1, parent1.tower_w, parent1.tower_h, point1, p1_h, p1_w, bottom_p1, main_b1, [x1, y], 0)
    ch2 =  Castle(towers2, parent2.tower_w, parent2.tower_h, point2, p2_h, p2_w, bottom_p2, main_b2, [x2, y], 0)

    return ch1, ch2



# generuje zamek o podanym genotypie
def generate_castle(child):
    # generacja wież w murach
    generate_towers(child.towers_points, child.tower_w, child.tower_h)
    
    #generacja ścian między wieżami
    generate_walls(child.towers_points, child.tower_w, child.tower_h)
    
    # generacja podstawy środkowego obiektu
    create_obj_with_doors(child.main_point, child.mp_w, child.mp_h)
    
    # generacja reszty kostek
    for i in range(len(child.bottom_points)):
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.active_object
        cube.scale = (child.mp_w, child.mp_w, child.mp_h)
        cube.location = (child.bottom_points[i][0], child.bottom_points[i][1], child.mp_h)
        cube.data.materials.append(blue)

    # generacja reszty śrokowego obiektu
    for i in range(len(child.tower_objects)):
        tmp_point = [child.main_point[0], child.main_point[1], 3*child.mp_h + 2*child.mp_h*i]
        match child.tower_objects[i]:
            # tworze obiekt z kwadratowymi oknami
            case 1:
                create_obj_with_cubic_window(tmp_point, child.mp_w, child.mp_h)
            
            # tworze obiekt z okrągłymi oknami
            case 2:
                create_obj_with_circle_window(tmp_point, child.mp_w, child.mp_h)
            
            # tworze obiekt z wcięciami
            case 3:
                create_indentend_obj(tmp_point, child.mp_w, child.mp_h)
        
    tmp_point = [child.main_point[0], child.main_point[1], 2*len(child.tower_objects)*child.mp_h + 3*child.mp_h]
    match child.tower_objects[len(child.tower_objects)-1]:
        # tworze obiekt z wieżami na krawędziach
        case 1:
           create_obj_with_towers(tmp_point, child.mp_w, child.mp_h, child.tower_h)      
        # tworze wieże z zegarem 
        case 2:
           create_clock([tmp_point[0], tmp_point[1], tmp_point[2]-child.mp_h], child.mp_w, child.mp_h)



# dodaje punkt do listy wież
def relocate_towers_and_add_new_tower(towers, new_tower, cordinate_point):
    new_towers = []
    new_towers.append([round(new_tower[0]-cordinate_point[0],2), round(new_tower[1]-cordinate_point[1],2)])
    
    # przesunięcie do początku ukł współrzędnych
    for i in range(len(towers)):
        new_towers.append([round(towers[i][0]-cordinate_point[0],2), round(towers[i][1]-cordinate_point[1],2)])
    
    alpha_points = calculate_alpha(new_towers)
    new_towers = []
    
    for i in range(len(alpha_points)):
        new_towers.append([alpha_points[i][0]+cordinate_point[0], alpha_points[i][1]+cordinate_point[1]])
    
    return new_towers
    
    
    
# dokonuje mutacji na wieżach i obiektach podstawy
def mutate(child):
    rand_op = random.randint(1, 4)
    
    # mutacja wież
    match rand_op:
        # dodaj wieżę
        case 1:
            temp_x = random.uniform(child.cordinate_system_point[0]-15, child.cordinate_system_point[0]+15)
            temp_y = random.uniform(child.cordinate_system_point[1], child.cordinate_system_point[1]+30)
            rand_point = [temp_x, temp_y]
            child.towers_points = relocate_towers_and_add_new_tower(child.towers_points, rand_point, child.cordinate_system_point)         
        # przesuń jedną wieżę
        case 2:
            rand_tower_nr = random.randint(0, len(child.towers_points)-1)
            temp_x = random.uniform(-5, 5)
            temp_y = random.uniform(-5, 5)
            child.towers_points[rand_tower_nr] = [round(child.towers_points[rand_tower_nr][0],2)+temp_x, round(child.towers_points[rand_tower_nr][1],2)+temp_y]
            
        # usuń jedną wieżę
        case 3:
            rand_tower_nr = random.randint(0, len(child.towers_points)-1)
            child.towers_points.pop(rand_tower_nr)
            
        case 4:
            pass

    
    # mutacja klocków
    rand_op = random.randint(1, 3)
    match rand_op:
        # dodaj klocek
        case 1:
            while(1):
                temp_x = round(random.choice(range(child.main_point[0]-15, child.main_point[0]+15, 3)), 2)
                temp_y = round(random.choice(range(child.main_point[1]-15, child.main_point[1]+15, 3)), 2)
                
                if not check_if_point_in_list(child.bottom_points, [temp_x, temp_y]):
                    child.bottom_points.append([temp_x, temp_y])
                    break;
        
        # przesuń
        case 2:
            while(1):
                rand_nr = random.randint(0, len(child.bottom_points)-1)
                temp_x = round(random.choice(range(-15, 15, 3)), 2)
                temp_y = round(random.choice(range(-15, 15, 3)), 2)
                
                if check_if_point_in_list(child.bottom_points, [child.bottom_points[rand_nr][0]+temp_x, child.bottom_points[rand_nr][1]+temp_y]):
                    child.bottom_points[rand_nr] = [child.bottom_points[rand_nr][0]+temp_x, child.bottom_points[rand_nr][1]+temp_y]
                    break;
        
        # usuń klocek
        case 3:
            rand_nr = random.randint(0, len(child.bottom_points)-1)
            child.bottom_points.pop(rand_nr)
       
        case 4:
            pass



if __name__ == "__main__":
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.outliner.orphans_purge()
    bpy.ops.outliner.orphans_purge()
    bpy.ops.outliner.orphans_purge()
    
    red = bpy.data.materials.get("Red")
    if not red:
        red = bpy.data.materials.new(name="Red")
    red.diffuse_color = [0.4, 0.0, 0.0 , 1.0]
    
    brown = bpy.data.materials.get("Brown")
    if not brown:
        brown = bpy.data.materials.new(name="Brown")
    brown.diffuse_color = [0.1, 0.03, 0.0 , 1.0] 
    
    blue = bpy.data.materials.get("Blue")
    if not blue:
        blue = bpy.data.materials.new(name="Blue")
    blue.diffuse_color = [0.0, 0.0, 0.6 , 1.0]

    black = bpy.data.materials.get("Black")
    if not black:
        black = bpy.data.materials.new(name="Black")
    black.diffuse_color = [0.0, 0.0, 0.0 , 1.0]
    
    yellow = bpy.data.materials.get("Yellow")
    if not yellow:
        yellow = bpy.data.materials.new(name="Yellow")
    yellow.diffuse_color = [1.0, 1.0, 0.0 , 1.0]

    p1 = create_parent(-30,0,red, brown, blue, black, yellow)
    p2 = create_parent(30, 0, red, brown, blue, black, yellow)

    child1, child2 = crossing(p1, p2)
    
    mutate(child1)
    generate_castle(child1)
    
    mutate(child2)
    generate_castle(child2)
    
    print("parent 1 (left):", matching_function(p1))
    print("parent 2 (right):", matching_function(p2))
    print("child 1 (left):", matching_function(child1))
    print("child 2 (right):", matching_function(child2))
    
    bpy.ops.object.select_all(action='DESELECT')