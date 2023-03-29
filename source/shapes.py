import common.location as loc
import tkinter
import random
import math
import os

object_names_array=["circle", "half circle", "square", "heart", "star", "triangle"]
class Annotation:
    """An annotation is what machine learning uses to determine what something is.
    the syntax of our annotation goes as follows `class_id x y width height`  
    the class_id points to what shape it is.
    the rest is a float between 0 - 1"""
    def __init__(self, class_id:int, center_pos:loc.Pos, image_size:loc.Pos, coordinates:list) -> None:
        """## Constructor
        `class_id` a int between  0 - n, wherein n is the amount of machine learning objects there are. See `object_names_array` in the machine learning training model for more info.
        
        `center_pos` the x and y coordinates of the center of the object
        
        `image_size` the x=width and y=hight of the image in pixels
        
        `coordinates` a list of positions with x and y values"""
        assert class_id >= 0
        
        self.class_id=str(class_id)
        self.x=float(center_pos.x)/float(image_size.x)
        self.y=float(center_pos.y)/float(image_size.y)

        min_x = coordinates[0].x
        max_x = coordinates[0].x
        for pos in coordinates:
            min_x = min(min_x, pos.x)
            max_x = max(max_x, pos.x)
        dx = max_x - min_x
        self.width = float(dx)/float(img_size.x)

        min_y = coordinates[0].y
        max_y = coordinates[0].y
        for pos in coordinates:
            min_y = min(min_y, pos.y)
            max_y = max(max_y, pos.y)
        dy = max_y - min_y
        self.height = float(dy)/float(img_size.y)
    def __str__(self) -> str:
        """`class_id x y width height`"""
        return f'{self.class_id} {self.x} {self.y} {self.width} {self.height}'
    def collides(self, other) -> bool:
        """returns bool, true whenever the other collides."""

        self_lower_pos = loc.Pos(x=self.x-self.width/2, y=self.y-self.height/2)
        self_upper_pos = loc.Pos(x=self.x+self.width/2, y=self.y+self.height/2)
        other_lower_pos = loc.Pos(x=other.x-other.width/2, y=other.y-other.height/2)
        other_upper_pos = loc.Pos(x=other.x+other.width/2, y=other.y+other.height/2)
        
        if self_upper_pos.x < other_lower_pos.x: return False # Left of other
        if self_upper_pos.y < other_lower_pos.y: return False # Above other
        if self_lower_pos.x > other_upper_pos.x: return False # Right of other
        if self_lower_pos.y > other_upper_pos.y: return False # Under other
        return True

# Functions to help draw shapes
def calculate_arm_point_(start_pos:loc.Pos, length_trace=1, rotation_rad=0.0) -> loc.Pos:
    """uses the idea of the unit circle to calculate the position from a start position, rotation and length of the arm"""
    return loc.Pos(
        x= start_pos.x + length_trace * math.cos(rotation_rad),
        y= start_pos.y + length_trace * (-math.sin(rotation_rad)),
        force_int=True)
def calculate_shape_arms_(center_pos:loc.Pos, traces= 4, length_traces=10, rotation_rad=0) -> list:
    """Calculates multiple arms out of one point that give a outline"""
    output = []

    trace_rad_spacing = math.pi * 2 / float(traces)

    for i in range(traces):
        output.append(calculate_arm_point_(
            start_pos=      center_pos,
            length_trace=   length_traces,
            rotation_rad=   rotation_rad + i * trace_rad_spacing
        ))

    return output

# Shapes
class Star:
    def __init__(self, center_pos:loc.Pos, size_in_pixels=10, rotation_rad=0.0, depth_percentage=50):
        rotation_rad %= math.pi * 2 / 5 # Shape repeats every 72 degrees

        self.center_pos = center_pos
        self.size_in_pixels = size_in_pixels
        self.rotation_rad=rotation_rad
        self.depth_percentage=depth_percentage

        # store the outline in a list
        self.outline_coordinates = []

        outer_points = calculate_shape_arms_(center_pos=center_pos, traces=5, length_traces=size_in_pixels / 2, rotation_rad=rotation_rad)
        inner_points = calculate_shape_arms_(center_pos=center_pos, traces=5, length_traces=size_in_pixels / 200 * depth_percentage,
                                         rotation_rad=rotation_rad + (math.pi / float(5)))

        self.outline_coordinates.append(outer_points[0])
        self.outline_coordinates.append(inner_points[0])
        self.outline_coordinates.append(outer_points[1])
        self.outline_coordinates.append(inner_points[1])
        self.outline_coordinates.append(outer_points[2])
        self.outline_coordinates.append(inner_points[2])
        self.outline_coordinates.append(outer_points[3])
        self.outline_coordinates.append(inner_points[3])
        self.outline_coordinates.append(outer_points[4])
        self.outline_coordinates.append(inner_points[4])

        self.annotation=Annotation(4, center_pos=center_pos, image_size=img_size, coordinates=self.outline_coordinates)
    def get_polygon_coordinates(self):
        """Returns a list of coordinates that can be used by `tkinter` to draw a `polygon` on a `canvas`"""
        polygon_coordinates = []
        for node in self.outline_coordinates:
            polygon_coordinates.append(  int(round(  node.x,  0  ))  )
            polygon_coordinates.append(  int(round(  node.y,  0  ))  )
        return polygon_coordinates
class Square:
    def __init__(self, center_pos:loc.Pos, size_in_pixels=10, rotation_rad=0.0):
        rotation_rad %= math.pi * 2 / 4 # Shape repeats every 90 degrees

        self.center_pos = center_pos
        self.size_in_pixels = size_in_pixels
        self.rotation_rad=rotation_rad

        # store the outline in a list
        self.outline_coordinates = calculate_shape_arms_(center_pos=center_pos, traces=4, length_traces=size_in_pixels / 2, rotation_rad=rotation_rad)

        self.annotation=Annotation(2, center_pos=center_pos, image_size=img_size, coordinates=self.outline_coordinates)
    def get_polygon_coordinates(self):
        """Returns a list of coordinates that can be used by `tkinter` to draw a `polygon` on a `canvas`"""
        polygon_coordinates = []
        for node in self.outline_coordinates:
            polygon_coordinates.append(  int(round(  node.x,  0  ))  )
            polygon_coordinates.append(  int(round(  node.y,  0  ))  )
        return polygon_coordinates
class SymmetricTriangle:
    def __init__(self, center_pos:loc.Pos, size_in_pixels=10, rotation_rad=0.0):
        rotation_rad %= math.pi * 2 / 3 # Shape repeats every 60 degrees

        self.center_pos = center_pos
        self.size_in_pixels = size_in_pixels
        self.rotation_rad=rotation_rad

        # store the outline in a list
        self.outline_coordinates = calculate_shape_arms_(center_pos=center_pos, traces=3, length_traces=size_in_pixels / 2, rotation_rad=rotation_rad)

        self.annotation=Annotation(5, center_pos=center_pos, image_size=img_size, coordinates=self.outline_coordinates)
    def get_polygon_coordinates(self):
        """Returns a list of coordinates that can be used by `tkinter` to draw a `polygon` on a `canvas`"""
        polygon_coordinates = []
        for node in self.outline_coordinates:
            polygon_coordinates.append(  int(round(  node.x,  0  ))  )
            polygon_coordinates.append(  int(round(  node.y,  0  ))  )
        return polygon_coordinates
class Heart:
    def __init__(self, center_pos:loc.Pos, size_in_pixels=10, rotation_rad=0.0, depth_percentage=50):
        rotation_rad %= math.pi * 2 # Shape repeats every 360 degrees
        depth_percentage=min(80,max(20,depth_percentage)) # Limit depth percentage to 20-80

        self.center_pos = center_pos
        self.size_in_pixels = size_in_pixels
        self.rotation_rad=rotation_rad
        self.depth_percentage=depth_percentage

        radius = size_in_pixels / 2
        pi = math.pi
        pi_2 = pi * 2

        # store the outline in a list
        self.outline_coordinates = []
        
        point_pos = calculate_arm_point_(center_pos,
                                         length_trace=radius,
                                         rotation_rad=3/2*pi + rotation_rad)
        self.outline_coordinates.append(point_pos) # point of the hart
        

        # self.outline_coordinates.append(calculate_arm_point_(center_pos,
        #                                                      length_trace=radius*0.87,
        #                                                      rotation_rad= 65/36*pi + rotation_rad)) # right arc 1
        self.outline_coordinates.append(calculate_arm_point_(center_pos,
                                                             length_trace=radius*1.08,
                                                             rotation_rad= 11/90*pi + rotation_rad)) # right arc 2
        # self.outline_coordinates.append(calculate_arm_point_(center_pos,
        #                                                      length_trace=radius*1.41,
        #                                                      rotation_rad= 1/4*pi + rotation_rad)) # right arc 3
        self.outline_coordinates.append(calculate_arm_point_(center_pos,
                                                             length_trace=radius*1.15,
                                                             rotation_rad= 31/90*pi + rotation_rad)) # right arc 4
        

        upper_help_guide = calculate_arm_point_(point_pos,
                                                length_trace=size_in_pixels,
                                                rotation_rad= 1/2*pi + rotation_rad)
        self.outline_coordinates.append(upper_help_guide)


        hole_pos = calculate_arm_point_(point_pos,
                                        length_trace=size_in_pixels*depth_percentage/100,
                                        rotation_rad= 1/2*pi + rotation_rad)
        self.outline_coordinates.append(hole_pos) # Hole
        self.outline_coordinates.append(hole_pos) # Hole
        

        self.outline_coordinates.append(upper_help_guide)


        self.outline_coordinates.append(calculate_arm_point_(center_pos,
                                                             length_trace=radius*1.15,
                                                             rotation_rad= 38/45*pi + rotation_rad)) # left arc 4
        # self.outline_coordinates.append(calculate_arm_point_(center_pos,
        #                                                      length_trace=radius*1.41,
        #                                                      rotation_rad= 3/4*pi + rotation_rad)) # left arc 3
        self.outline_coordinates.append(calculate_arm_point_(center_pos,
                                                             length_trace=radius*1.08,
                                                             rotation_rad= 79/90*pi + rotation_rad)) # left arc 2
        # self.outline_coordinates.append(calculate_arm_point_(center_pos,
        #                                                      length_trace=radius*0.87,
        #                                                      rotation_rad= 43/36*pi + rotation_rad)) # left arc 1
        

        self.outline_coordinates.append(point_pos) # point of the hart

        self.annotation=Annotation(3, center_pos, image_size=img_size, coordinates=self.outline_coordinates)
    def get_polygon_coordinates(self):
        """Returns a list of coordinates that can be used by `tkinter` to draw a `polygon` on a `canvas`"""
        polygon_coordinates = []
        for node in self.outline_coordinates:
            polygon_coordinates.append(  int(round(  node.x,  0  ))  )
            polygon_coordinates.append(  int(round(  node.y,  0  ))  )
        return polygon_coordinates
    
# Saving data to 
def save_img(tkinter_canvas:tkinter.Canvas, path_filename:str, as_png=False, as_jpg=False, as_gif=False, as_bmp=False, as_eps=False) -> None:
    """Saves the `tkinter.Canvas` object as a image, on the location of `path_filename` as the chosen formats.
    
    ### WARNING this requires Ghostscript, please install https://ghostscript.com/releases/gsdnld.html, and restart your PC 
    - `tkinter_canvas` The canvas that has to be saved as an image.
    - `path_filename` The (absolute) path that point to the image file without the extension. Example:`r'C:\Program Files\my_project\my_folder_with_images\image_1'`
    - `as_###` The bool that can be true to export that file format. This allows multiple at once. At least one is required."""
    if not ( as_png or as_jpg or as_gif or as_bmp or as_eps ):
        print('WARNING: Could not save, as no file format was given.')
        return
    

    tkinter_canvas.pack()
    tkinter_canvas.update()


    # Create that directory if it does not exists yet
    parent_path = os.path.split(path_filename)[0] # 1 directory up
    if not os.path.exists(parent_path): os.makedirs(parent_path)


    from PIL import Image, ImageTk, EpsImagePlugin
    if as_eps:
        tkinter_canvas.postscript(file = path_filename + '.eps')
        img = Image.open(path_filename + '.eps')
    else:
        import io
        postscript = tkinter_canvas.postscript(colormode='color')
        img = Image.open(io.BytesIO(postscript.encode('utf-8')))


    # Warning this requires Ghostscript that has to be installed manually on your operating system
    #
    # Error: `OSError: Unable to locate Ghostscript on paths`
    #
    # Official guide: https://ghostscript.com/docs/9.54.0/Install.htm
    #
    # My guide:
    # 1. CRY
    # 2. https://ghostscript.com/releases/gsdnld.html Just brrrr install this as x64
    # 3. This took me 5.5 hours :'(
    EpsImagePlugin.gs_windows_binary =  r'C:\Program Files\gs\gs10.01.1\bin\gswin64c' # This is the default location, Telling PIL that it should be here


    if as_png: img.save(path_filename + '.png', 'png')
    if as_gif: img.save(path_filename + '.gif', 'gif')
    if as_bmp: img.save(path_filename + '.bmp', 'bmp')
    if as_jpg: img.save(path_filename + '.jpg', 'JPEG')
def save_annotation(list_of_annotations:list, path_filename:str) -> None:

    # Create that directory if it does not exists yet
    parent_path = os.path.split(path_filename)[0] # 1 directory up
    if not os.path.exists(parent_path): os.makedirs(parent_path)

    # Write to the file
    with open(path_filename + '.txt', "w") as file:
        for line in list_of_annotations:
            file.write(f'{line}\n')
        file.flush()
        file.close()

def get_random_tkinter_color_(avoid_color) -> str:
    colors = ["black", "red", "green", "blue", "cyan", "yellow", "magenta"]
    # if type(avoid_color) == type(str):
    #     try:    colors.remove(str.lower(avoid_color))
    #     except: print(f'Told me to avoid color={avoid_color} in `get_random_tkinter_color_`, but that color does not exists')
    # elif type(avoid_color) == type(int): colors.remove(colors[avoid_color])
    return colors[ random.randint(0,  len(colors) - 1  ) ]

def create_random_image(image_code:int, objects:int, img_size:loc.Pos, path:str) -> None:
    # Setup environment
    root = tkinter.Tk()
    canvas_background_color = 'white' # BUG thinker and PIL background not the same
    canvas = tkinter.Canvas(root, bg=canvas_background_color, height=img_size.y, width=img_size.x)
    annotation_info = []

    # Generate shapes
    for i in range(0, objects):
        collision_with_previous_shape = True
        collision_attempts = 0
        while (collision_with_previous_shape and not (collision_attempts > 100 and i > 0)):

            # Get parameters
            shape_size = int(random.randint(50, int(img_size.min() / 2)))
            shape_pos = loc.Pos(x=random.randint(int(shape_size/2), img_size.x - int(shape_size/2)),
                                y=random.randint(int(shape_size/2), img_size.y - int(shape_size/2)),
                                force_int=True)
            shape_color = get_random_tkinter_color_(avoid_color=canvas_background_color)

            # Choose shape
            match random.randint(3,3):
                case 0: 
                    shape = Star(center_pos=shape_pos, size_in_pixels=shape_size,
                                 rotation_rad=random.random() * math.pi * 2,
                                 depth_percentage=random.randint(20,70))
                case 1:
                    shape = Square(center_pos=shape_pos, size_in_pixels=shape_size,
                                   rotation_rad=random.random() * math.pi * 2,)
                case 2:
                    shape = SymmetricTriangle(center_pos=shape_pos, size_in_pixels=shape_size,
                                   rotation_rad=random.random() * math.pi * 2,)
                case 3:
                    shape = Heart(center_pos=shape_pos, size_in_pixels=shape_size,
                                  rotation_rad=random.random() * math.pi * 2,
                                  depth_percentage=50)
                                #   depth_percentage=random.randint(20,70))
                case _:
                    raise Warning('Out of range; in the count of shapes.')


            # In case this collides with another existing shape then skip it
            collision_with_previous_shape = False
            collision_attempts += 1
            for existing_annotation in annotation_info:
                if shape.annotation.collides(existing_annotation):
                    collision_with_previous_shape = True
                    print(f'Debug: Collision: Position.\timage_code={image_code}\tshape=({i}/{objects})')
                    break
        if collision_attempts > 100: continue
        
        # In case it does not collide then add the annotation to the list and draw it on the canvas
        annotation_info.append(shape.annotation)
        canvas.create_polygon(shape.get_polygon_coordinates(),
                              outline=shape_color, width=1,
                              smooth=1,
                              fill=shape_color)
    
    # Summit the data
    save_img(tkinter_canvas=canvas,
            path_filename=os.path.join(path, 'images', f'img ({image_code})'),
            as_jpg=True)
    save_annotation(annotation_info,
                    path_filename=os.path.join(path, 'annotations', f'img ({image_code})'))
    root.destroy()

if __name__ == '__main__':

    img_size = loc.Pos(x=200, y=200)
    path = os.path.join(os.getcwd(), 'files', 'shape_generator')

    image_code_start = 1
    size_batch = 200
    max_objects = 7

    
    for image_code in range(image_code_start, image_code_start + size_batch):
        create_random_image(image_code=image_code,
                            objects=random.randint(1, max_objects),
                            img_size=img_size,
                            path=path)
