import bpy
from math import *
import bmesh
import random
import time
import numpy as np


class Stack:
    def __init__ (self):        # Kostruktor
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
#    ob.data.rederials.append(red)
#    create_cubes(x1, y1, x2, y2, z2)
    


# tworzy małe kwadraty na górze ściny
def create_cubes(x1, y1, x2, y2, z):
    a_x = 0.0
    a_y = 0.0
    x = x1
    y = y1
    
    if y1 == y2:
        a_y = 0.4
        
        z1 = z+0.8
        dist = (abs(x1)+abs(x2))/4
        
        if x2 < x1:
            x = x2
        
        for i in range(1, 4):
            a = dist * i
            bpy.ops.mesh.primitive_cube_add()
            cube = bpy.context.active_object
            cube.location = (x+a, y1, z+0.3)
            cube.scale = (0.3, 0.3, 0.3)
            ob = bpy.context.active_object
            ob.data.materials.append(red)
        
    elif x1 == x2:
        a_x = 0.4
        
        z1 = z+0.8
        dist = (abs(y1)+abs(y2))/4
        
        if y2 < y1:
            y = y2
        
        for i in range(1, 4):
            a = dist * i
            bpy.ops.mesh.primitive_cube_add()
            cube = bpy.context.active_object
            cube.location = (x1, y+a, z+0.3)
            cube.scale = (0.3, 0.3, 0.3)
            ob = bpy.context.active_object
            ob.data.materials.append(brown)



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
        while is_right(convex_shell_points, alpha_points[i]) < 0.0: # is_right(convex_shell_points.Top(), convex_shell_points.Next_To_Top(), alpha_points[i]) < 0.0:
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
def generate_towers(last_points):
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
def generate_single_wall(point1, point2):
    create_wall(0.0, 0.0, 1.0, 0.0, 0.0, 1.0)
    ob = bpy.context.active_object
        
    length = calculate_segment_length(point1[0], point1[1], point2[0], point2[1])
    ob.scale = (length, tower_width/2, tower_height/2)
        
    radian = calculate_angle(point1[0], point1[1], point2[0], point2[1])
    ob.rotation_euler = (0,0,radians(radian))
        
    ob.location = (point1[0], point1[1], 0.0)
    ob.data.materials.append(red)
    


# generuje ściany na ekranie
def generate_walls(points):
    for i in range(1, len(points)):
        generate_single_wall(points[i-1], points[i])
    
    generate_single_wall(points[len(points)-1], points[0])
    
        
    
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
    
    return [x,y], size

    

# tworzy wierze w zamku
def create_castle_tower(point, scale):
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
def generate_main_building(point, size):
    obj_nr = random.randint(1, 3)
    height = random.uniform(tower_height/(obj_nr+4), tower_height/(obj_nr+2))
    scale = random.uniform(size/15, size/10)
    
    if scale > 1.5*height:
        scale = 1.5*height 
    
    #generuje obiekt w podstawie
    create_obj_with_doors(point, scale, height)
    
    for i in range(obj_nr):    
        new_p = [point[0], point[1], 3*height + 2*height*i]
        create_middle_obj(new_p, scale, height)

    new_p = [point[0], point[1], 3*height + 2*height*obj_nr]
    create_top_obj(new_p, scale, height)



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
    x = random.uniform(point[0]-0.6*scale, point[0]+0.6*scale)
    z = random.uniform(point[2]+height-0.4*scale, point[2]-height+0.4*scale)
    cube.location = (x, point[1]-scale, z)
    cube.scale = (0.4*scale, 0.1, 0.4*scale)
    
    # okno na lewej ścianie
    l_cube = bpy.context.active_object.copy()
    l_cube.rotation_euler = (0,0,radians(90))
    y = random.uniform(point[1]-0.6*scale, point[1]+0.6*scale)
    z = random.uniform(point[2]+height-0.4*scale, point[2]-height+0.4*scale)
    l_cube.location = (point[0]-scale, y, z)
    bpy.context.collection.objects.link(l_cube)
    
    # okno na prawej ścianie
    r_cube = bpy.context.active_object.copy()
    r_cube.rotation_euler = (0,0,radians(90))
    y = random.uniform(point[1]-0.6*scale, point[1]+0.6*scale)
    z = random.uniform(point[2]+height-0.4*scale, point[2]-height+0.4*scale)
    r_cube.location = (point[0]+scale, y, z)
    bpy.context.collection.objects.link(r_cube)
    
    # okno na tylnej ścianie
    b_cube = bpy.context.active_object.copy()
    x = random.uniform(point[0]-0.6*scale, point[0]+0.6*scale)
    z = random.uniform(point[2]+height-0.4*scale, point[2]-height+0.4*scale)
    b_cube.location = (x, point[1]+scale, z)
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
    x = random.uniform(point[0]-0.6*scale, point[0]+0.6*scale)
    z = random.uniform(point[2]+height-0.4*scale, point[2]-height+0.4*scale)
    cube.location = (x, point[1]-scale, z)
    
    # okno na lewej ścianie
    l_cube = bpy.context.active_object.copy()
    l_cube.rotation_euler = (0, radians(90), 0)
    y = random.uniform(point[1]-0.6*scale, point[1]+0.6*scale)
    z = random.uniform(point[2]+height-0.4*scale, point[2]-height+0.4*scale)
    l_cube.location = (point[0]-scale-0.1, y, z)
    bpy.context.collection.objects.link(l_cube)
    
    # okno na prawej ścianie
    r_cube = bpy.context.active_object.copy()
    r_cube.rotation_euler = (0, radians(90), 0)
    y = random.uniform(point[1]-0.6*scale, point[1]+0.6*scale)
    z = random.uniform(point[2]+height-0.4*scale, point[2]-height+0.4*scale)
    r_cube.location = (point[0]+scale, y, z)
    bpy.context.collection.objects.link(r_cube)
    
    # okno na tylnej ścianie
    b_cube = bpy.context.active_object.copy()
    x = random.uniform(point[0]-0.6*scale, point[0]+0.6*scale)
    z = random.uniform(point[2]+height-0.4*scale, point[2]-height+0.4*scale)
    b_cube.location = (x, point[1]+scale+0.1, z)
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
def create_top_obj(point, scale, height):
    rand_obj = random.randint(1, 2)

    match rand_obj:
        # tworze obiekt z wieżami na krawędziach
        case 1:
           create_obj_with_towers(point, scale, height)      

        # tworze wieże z zegarem 
        case 2:
           create_clock([point[0], point[1], point[2]-height], scale, height)
        
           

# tworzy obiekt z wieżami na krawędziach
def create_obj_with_towers(point, scale, height):
    bpy.ops.mesh.primitive_cube_add()
    cube = bpy.context.active_object
    cube.scale = (scale, scale, height)
    cube.location = (point[0], point[1], point[2])
    cube.data.materials.append(blue)
    
    value = 0.1
    # prawy góra
    corner_point = [point[0] + scale, point[1] + scale, point[2] - (height)*value]
    create_castle_tower(corner_point, height)
    
    #prawy dół
    corner_point = [point[0] + scale, point[1] - scale, point[2] - (height)*value]
    create_castle_tower(corner_point, height)
    
    #lewy dół
    corner_point = [point[0] - scale, point[1] - scale, point[2] - (height)*value]
    create_castle_tower(corner_point, height)
    
    #lewy góra
    corner_point = [point[0] - scale, point[1] + scale, point[2] - (height)*value]
    create_castle_tower(corner_point, height)



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
    
    
    # losuje ilość punktów
    towers_nr = random.randint(3, 50)
    
    # generuje liste punktów
    towers_points = generate_points(towers_nr)
    
    # tworzy otoczke wypukłą z podanych punktów i zwraca punkty tej ortoczki
    convex_points = create_convex_shell(towers_points)

    # ustawiam skalę szerokości i wysokości wież
    tower_width = random.randint(1, 3)
    tower_height = random.randint(4, 8)

    # usuwam z otoczki punkty leżące zbut blisko siebie
    last_points = delete_too_narrow_convex_points(convex_points, tower_width)

    # generuje wieże
    generate_towers(last_points)
    
    # generuje ściany między wieżami
    generate_walls(last_points)
    
    # generuje budynek w środku - zamek
    point, size = get_centre_point(last_points)    
    generate_main_building(point, size) #point, size)

    bpy.ops.object.select_all(action='DESELECT')