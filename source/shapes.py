import common.location as loc
from enum import Enum # Keep enums UPPER_CASE according to https://docs.python.org/3/howto/enum.html  
from progress.bar import ShadyBar
import threading
import tkinter
import random
import shutil
import math
import os

object_names_array=["circle", "half circle", "square", "heart", "star", "triangle"]
class Annotation:
    """An annotation is what machine learning uses to determine what something is.
    the syntax of our annotation goes as follows `class_id x y width height`  
    the class_id points to what shape it is.
    the rest is a float between 0 - 1"""
    def __init__(self, class_id:int, image_size:loc.Pos, coordinates:list) -> None:
        """## Constructor
        `class_id` a int between  0 - n, wherein n is the amount of machine learning objects there are. See `object_names_array` in the machine learning training model for more info.
        
        `image_size` the x=width and y=hight of the image in pixels
        
        `coordinates` a list of positions with x and y values"""
        assert class_id >= 0

        self.class_id=str(class_id)

        # Find most up, left, right, down. Coordinates
        pos_top_left = loc.Pos(coordinates[0].x, coordinates[0].y)
        pos_bottom_right = loc.Pos(coordinates[0].x, coordinates[0].y)
        for coordinate in coordinates:
            if coordinate.x < pos_top_left.x:      pos_top_left.x = coordinate.x
            if coordinate.y < pos_top_left.y:      pos_top_left.y = coordinate.y
            if coordinate.x > pos_bottom_right.x:  pos_bottom_right.x = coordinate.x
            if coordinate.y > pos_bottom_right.y:  pos_bottom_right.y = coordinate.y
        self.box = loc.Box(x=     pos_top_left.x,
                           y=     pos_top_left.y,
                           width= pos_bottom_right.x - pos_top_left.x,
                           height=pos_bottom_right.y - pos_top_left.y)

        pos_center = loc.Pos(x= pos_top_left.x + (pos_bottom_right.x - pos_top_left.x) / 2.0,
                             y= pos_top_left.y + (pos_bottom_right.y - pos_top_left.y) / 2.0)
        shape_size = loc.Pos(x= pos_bottom_right.x - pos_top_left.x,
                             y= pos_bottom_right.y - pos_top_left.y)
        
        self.x=float(pos_center.x)/float(image_size.x)
        self.y=float(pos_center.y)/float(image_size.y)

        self.width =  shape_size.x / float(img_size.x)
        self.height = shape_size.y / float(img_size.y)
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
def calculate_shape_arms_(center_pos:loc.Pos, traces= 4, length_traces=10, rotation=0) -> list:
    """Calculates multiple arms out of one point that give a outline"""
    output = []

    trace_rad_spacing = math.pi * 2 / float(traces)

    for i in range(traces):
        output.append(calculate_arm_point_(
            start_pos=      center_pos,
            length_trace=   length_traces,
            rotation_rad=   rotation + i * trace_rad_spacing
        ))

    return output
def angle_mirror_(rad_angle:float, mirror_vertical=False)->float:
    # vertical mirror
    if mirror_vertical:
        rad_angle = math.pi - rad_angle
        rad_angle %= math.pi * 2
    return rad_angle

# Shapes
class Shape:
    def get_polygon_coordinates(self) -> list:
        """Returns a list of coordinates that can be used by `tkinter` to draw a `polygon` on a `canvas`"""
        polygon_coordinates = []
        for node in self.outline_coordinates:
            polygon_coordinates.append(  int(round(  node.x,  0  ))  )
            polygon_coordinates.append(  int(round(  node.y,  0  ))  )
        return polygon_coordinates
class Star(Shape):
    def __init__(self, center_pos:loc.Pos, size_in_pixels=10, rotation_rad=0.0, depth_percentage=50):
        rotation_rad %= math.pi * 2 / 5 # Shape repeats every 72 degrees

        self.center_pos = center_pos
        self.size_in_pixels = size_in_pixels
        self.rotation_rad=rotation_rad
        self.depth_percentage=depth_percentage

        # store the outline in a list
        self.outline_coordinates = []

        outer_points = calculate_shape_arms_(center_pos=center_pos, traces=5, length_traces=size_in_pixels / 2, rotation=rotation_rad)
        inner_points = calculate_shape_arms_(center_pos=center_pos, traces=5, length_traces=size_in_pixels / 200 * depth_percentage,
                                         rotation=rotation_rad + (math.pi / float(5)))

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

        self.annotation=Annotation(4, image_size=img_size, coordinates=self.outline_coordinates)
class Square(Shape):
    def __init__(self, center_pos:loc.Pos, size_in_pixels=10, rotation_rad=0.0):
        rotation_rad %= math.pi * 2 / 4 # Shape repeats every 90 degrees

        self.center_pos = center_pos
        self.size_in_pixels = size_in_pixels
        self.rotation_rad=rotation_rad

        # store the outline in a list
        self.outline_coordinates = calculate_shape_arms_(center_pos=center_pos, traces=4, length_traces=size_in_pixels / 2, rotation=rotation_rad)

        self.annotation=Annotation(2, image_size=img_size, coordinates=self.outline_coordinates)
class SymmetricTriangle(Shape):
    def __init__(self, center_pos:loc.Pos, size_in_pixels=10, rotation_rad=0.0):
        rotation_rad %= math.pi * 2 / 3 # Shape repeats every 60 degrees

        self.center_pos = center_pos
        self.size_in_pixels = size_in_pixels
        self.rotation_rad=rotation_rad

        # store the outline in a list
        self.outline_coordinates = calculate_shape_arms_(center_pos=center_pos, traces=3, length_traces=size_in_pixels / 2, rotation=rotation_rad)

        self.annotation=Annotation(5, image_size=img_size, coordinates=self.outline_coordinates)
class Heart(Shape):
    def __init__(self, center_pos:loc.Pos, size_in_pixels=10, rotation_rad=0.0, depth_percentage=50):
        rotation_rad %= math.pi * 2 # Shape repeats every 360 degrees
        depth_percentage=min(95,max(40,depth_percentage)) # Limit depth percentage to 20-80

        self.center_pos = center_pos
        self.size_in_pixels = size_in_pixels
        self.rotation_rad=rotation_rad
        self.depth_percentage=depth_percentage

        radius = size_in_pixels / 2
        pi = math.pi

        # store the outline in a list
        shape_dict = {
            "point_1":      (3/2*pi,     radius),
            "under_arch_2": (65/36*pi,   radius*0.87),
            "right_3":      (1/9*pi,     radius*1.08),
            "top_right_4":  (1/4*pi,     radius*1.25),#1.41
            "top_5":        (31/90*pi,   radius*1.15),
            "top_center_6": (4/9*pi,     radius*0.95),
            "hole_7":       (1/2*pi,     size_in_pixels*depth_percentage/100) # use the point_pos as start_pos for this line
        }
        self.outline_coordinates = []

        # get location of the right side of the heart
        arm_rotation, arm_length = shape_dict["point_1"]
        point_pos = calculate_arm_point_(center_pos, arm_length, arm_rotation + rotation_rad)
        self.outline_coordinates.append(point_pos)
        self.outline_coordinates.append(point_pos)

        arm_rotation, arm_length = shape_dict["under_arch_2"]
        self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, arm_rotation + rotation_rad))
        arm_rotation, arm_length = shape_dict["right_3"]
        self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, arm_rotation + rotation_rad))
        arm_rotation, arm_length = shape_dict["top_right_4"]
        self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, arm_rotation + rotation_rad))
        arm_rotation, arm_length = shape_dict["top_5"]
        self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, arm_rotation + rotation_rad))
        arm_rotation, arm_length = shape_dict["top_center_6"]
        self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, arm_rotation + rotation_rad))

        arm_rotation, arm_length = shape_dict["hole_7"]
        hole_pos = calculate_arm_point_(point_pos, arm_length, arm_rotation + rotation_rad)
        self.outline_coordinates.append(hole_pos)

        # get location of the left side of the heart
        self.outline_coordinates.append(hole_pos)
        
        arm_rotation, arm_length = shape_dict["top_center_6"]
        self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, angle_mirror_(arm_rotation, mirror_vertical=True) + rotation_rad))
        arm_rotation, arm_length = shape_dict["top_5"]
        self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, angle_mirror_(arm_rotation, mirror_vertical=True) + rotation_rad))
        arm_rotation, arm_length = shape_dict["top_right_4"]
        self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, angle_mirror_(arm_rotation, mirror_vertical=True) + rotation_rad))
        arm_rotation, arm_length = shape_dict["right_3"]
        self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, angle_mirror_(arm_rotation, mirror_vertical=True) + rotation_rad))
        arm_rotation, arm_length = shape_dict["under_arch_2"]
        self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, angle_mirror_(arm_rotation, mirror_vertical=True) + rotation_rad))

        self.outline_coordinates.append(point_pos)
        self.outline_coordinates.append(point_pos)

        self.annotation=Annotation(3, image_size=img_size, coordinates=self.outline_coordinates)
class HalfCircle(Shape):
    def __init__(self, center_pos:loc.Pos, size_in_pixels=10, rotation_rad=0.0):
        rotation_rad %= math.pi * 2 # Shape repeats every 360 degrees

        self.center_pos = center_pos
        self.size_in_pixels = size_in_pixels
        self.rotation_rad=rotation_rad

        radius = size_in_pixels / 2
        pi = math.pi

        # store the outline in a list
        shape_dict = {
            "right_top":    (1/6*pi,    radius),
            "left_top":     (5/6*pi,    radius),
            "right_center": (0,         radius*0.75),
            "left_center":  (pi,        radius*0.75),
            "left_bottom":  (5/4*pi,    radius*0.5),
            "right_bottom": (7/4*pi,    radius*0.5)
        }
        self.outline_coordinates = []
        
        arm_rotation, arm_length = shape_dict["right_top"]
        self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, arm_rotation + rotation_rad))
        arm_rotation, arm_length = shape_dict["left_top"]
        self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, arm_rotation + rotation_rad))
        self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, arm_rotation + rotation_rad))
        arm_rotation, arm_length = shape_dict["left_center"]
        self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, arm_rotation + rotation_rad))
        # self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, arm_rotation + rotation_rad))
        arm_rotation, arm_length = shape_dict["left_bottom"]
        self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, arm_rotation + rotation_rad))
        arm_rotation, arm_length = shape_dict["right_bottom"]
        self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, arm_rotation + rotation_rad))
        arm_rotation, arm_length = shape_dict["right_center"]
        self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, arm_rotation + rotation_rad))
        # self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, arm_rotation + rotation_rad))
        arm_rotation, arm_length = shape_dict["right_top"]
        self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, arm_rotation + rotation_rad))
        self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, arm_rotation + rotation_rad))

        self.annotation=Annotation(1, image_size=img_size, coordinates=self.outline_coordinates)
class Circle(Shape):
    def __init__(self, center_pos:loc.Pos, size_in_pixels=10):

        self.center_pos = center_pos
        self.size_in_pixels = size_in_pixels

        radius = size_in_pixels / 2
        pi = math.pi

        # store the outline in a list
        shape_dict = {
            "right_top":    (1/4*pi,    math.sqrt( (radius**2) * 2)),
            "left_top":     (3/4*pi,    math.sqrt( (radius**2) * 2)),
            "left_bottom":  (5/4*pi,    math.sqrt( (radius**2) * 2)),
            "right_bottom": (7/4*pi,    math.sqrt( (radius**2) * 2))
        }
        self.outline_coordinates = []
        for dot in shape_dict:
            arm_rotation, arm_length = shape_dict[dot]
            self.outline_coordinates.append(calculate_arm_point_(center_pos, arm_length, arm_rotation))

        self.annotation=Annotation(0, image_size=img_size, coordinates=self.outline_coordinates)

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
    # if type(avoid_color) == type(str): TODO
    #     try:    colors.remove(str.lower(avoid_color))
    #     except: print(f'Told me to avoid color={avoid_color} in `get_random_tkinter_color_`, but that color does not exists')
    # elif type(avoid_color) == type(int): colors.remove(colors[avoid_color])
    return colors[ random.randint(0,  len(colors) - 1  ) ]

class ImageReceipt(Enum):
    MIX = 0
    ONLY_STAR = 1
    ONLY_SQUARE = 2
    ONLY_SYMMETRIC_TRIANGLE = 3
    ONLY_HEART = 4
    ONLY_HALF_CIRCLE = 5
    ONLY_CIRCLE = 6
class FolderReceipt:
    def __init__(self, path:str, amount_of_images:int, objects_per_image:int, image_receipt:ImageReceipt, img_size:loc.Size):
        self.amount_of_images=amount_of_images
        self.objects_per_image=objects_per_image
        self.image_receipt=image_receipt
        self.img_size=img_size
        self.name=f'{amount_of_images}_{objects_per_image}_{image_receipt.name.lower()}'
        self.path=os.path.join(path, self.name)
class FancyBar(ShadyBar):
    message = 'Total progress'
    suffix = '[%(index)d/%(max)d]  -  %(percent).1f%%  -  %(eta_td)s remaining  -  %(elapsed_td)s elapsed'
    # suffix = '[%(index)d/%(max)d]\t%(percent)d%\t[%(eta_td)s remaining]\t[%(elapsed_td)s remaining]'
    
def create_random_shape(canvas:tkinter.Canvas, img_size:loc.Size, forbidden_areas:list[Annotation], draw_shape_on_canvas:bool, star=False, square=False, symmetric_triangle=False, heart=False, half_circle=False, circle=False):#TODO
    if not ( star or square or symmetric_triangle or heart or half_circle or circle ):
        raise SyntaxError('No shape selected to create.')

    # Determine shape
    shapes = []
    if star:                shapes.append('star')
    if square:              shapes.append('square')
    if symmetric_triangle:  shapes.append('symmetric_triangle')
    if heart:               shapes.append('heart')
    if half_circle:         shapes.append('half_circle')
    if circle:              shapes.append('circle')
    shape_shape = shapes[random.randint(0, len(shapes)-1 )]
    
    valid_area = False
    patience = 1.0
    while(not valid_area and patience > 0.0):

        # Generate shape properties
        shape_size = max(25, int(round(  (random.randint(15,50)/100.0) * patience * img_size.min()  ))) # gets 15-50% the size of the image_size, shrinks every loop due to patience. 25 px is smallest size
        shape_center_pos = loc.Pos(x=random.randint(int(shape_size/2), img_size.x - int(shape_size/2)),
                                   y=random.randint(int(shape_size/2), img_size.y - int(shape_size/2)),
                                   force_int=True)
        shape_color = get_random_tkinter_color_(avoid_color='white')
        shape_rotation = random.random() * math.pi * 2

        # Generate Shape
        match shape_shape:
            case 'star': 
                shape = Star(shape_center_pos, size_in_pixels=shape_size, rotation_rad=shape_rotation,
                                depth_percentage=random.randint(20,70))
            case 'square':
                shape = Square(shape_center_pos, size_in_pixels=shape_size, rotation_rad=shape_rotation)
            case 'symmetric_triangle':
                shape = SymmetricTriangle(shape_center_pos, size_in_pixels=shape_size, rotation_rad=shape_rotation)
            case 'heart':
                shape = Heart(shape_center_pos, size_in_pixels=shape_size, rotation_rad=shape_rotation,
                              depth_percentage=random.randint(65,90))
            case 'half_circle':
                shape = HalfCircle(shape_center_pos, size_in_pixels=shape_size, rotation_rad=shape_rotation)
            case 'circle':
                shape = Circle(shape_center_pos, size_in_pixels=shape_size)
            case _:
                raise Warning('Out of range; in the count of shapes.')

        # Check if this shape collides with forbidden_areas, otherwise grab new shape
        valid_area = True
        for annotation in forbidden_areas:
            if shape.annotation.box.overlaps(annotation.box):
                valid_area = False
                patience -= 0.01
                break
    if not valid_area:
        raise RuntimeError('Tried my best to get a shape, but no dice.')
    
    # Draw it on the canvas and return the shape
    if isinstance(shape, Circle):
        canvas.create_oval(shape.annotation.box.pos.x, shape.annotation.box.pos.y, shape.annotation.box.pos.x + shape.annotation.box.size.x, shape.annotation.box.pos.y + shape.annotation.box.size.y,
                           outline=shape_color, width=1,
                           fill=shape_color)
        return shape
    
    canvas.create_polygon(shape.get_polygon_coordinates(),
                          outline=shape_color, width=1,
                          smooth=1 if isinstance(shape, Heart) or isinstance(shape, HalfCircle) else 0,
                          fill=shape_color)
    return shape
def create_random_image(image_code:int, objects:int, img_size:loc.Pos, path:str, image_receipt:ImageReceipt | None, verbose=False) -> None:
    # Setup environment
    root = tkinter.Tk()
    canvas_background_color = 'white' # BUG thinker and PIL background not the same
    canvas = tkinter.Canvas(root, bg=canvas_background_color, height=img_size.y, width=img_size.x, takefocus=0)
    annotation_info = []
    all_outline_coordinates = []

    # Generate shapes
    for i in range(0, objects):
        try:
            shape = create_random_shape(canvas=canvas,
                                        img_size=img_size,
                                        forbidden_areas=annotation_info,
                                        draw_shape_on_canvas=True,

                                        star=               image_receipt == ImageReceipt.MIX or image_receipt == ImageReceipt.ONLY_STAR,
                                        square=             image_receipt == ImageReceipt.MIX or image_receipt == ImageReceipt.ONLY_SQUARE,
                                        symmetric_triangle= image_receipt == ImageReceipt.MIX or image_receipt == ImageReceipt.ONLY_SYMMETRIC_TRIANGLE,
                                        heart=              image_receipt == ImageReceipt.MIX or image_receipt == ImageReceipt.ONLY_HEART,
                                        half_circle=        image_receipt == ImageReceipt.MIX or image_receipt == ImageReceipt.ONLY_HALF_CIRCLE,
                                        circle=             image_receipt == ImageReceipt.MIX or image_receipt == ImageReceipt.ONLY_CIRCLE

                                        )
        except: continue
        
        # Add the annotation to the list
        annotation_info.append(shape.annotation)
        all_outline_coordinates.append(shape.outline_coordinates)
    
    # Summit the data
    save_img(tkinter_canvas=canvas,
            path_filename=os.path.join(path, 'images', f'img ({image_code})'),
            as_png=True)
    save_annotation(annotation_info,
                    path_filename=os.path.join(path, 'annotations', f'img ({image_code})'))
    if not verbose:
        root.destroy()
        return
    
    # Mark all polygons
    for outline_coordinates in all_outline_coordinates:
        for coordinate in outline_coordinates:
            canvas.create_rectangle(coordinate.x-1,coordinate.y-1,coordinate.x+1,coordinate.y+1,outline='red',fill='blue',width=1) # draw dot on each coordinate

    for annotation in annotation_info:
        center_pos = loc.Pos(x= annotation.x * img_size.x,
                                y= annotation.y * img_size.y)
        size_shape = loc.Pos(x= annotation.width * img_size.x,
                                y= annotation.height * img_size.y)
        box_top_left = loc.Pos(x= center_pos.x - size_shape.x / 2,
                                y= center_pos.y - size_shape.y / 2,
                                force_int=True)
        box_bottom_right = loc.Pos(x= center_pos.x + size_shape.x / 2,
                                    y= center_pos.y + size_shape.y / 2,
                                    force_int=True)
        # Mark center
        # canvas.create_line(0,center_pos.y,img_size.x,center_pos.y, dash=(1,1), fill='gray')# horizontal
        # canvas.create_line(center_pos.x,0,center_pos.x,img_size.y, dash=(1,1), fill='gray')# vertical

        # Mark annotation
        canvas.create_rectangle(box_top_left.x,box_top_left.y,
                                box_bottom_right.x,box_bottom_right.y)
    root.title = f'{len(annotation_info)} of the {objects} that were requested'
    root.mainloop()
def create_from_folder_receipt(folder_receipt:FolderReceipt, verbose=False) -> None:
    for image_code in range(0, folder_receipt.amount_of_images):
        create_random_image(image_code=image_code,
                            objects=folder_receipt.objects_per_image,
                            img_size=folder_receipt.img_size,
                            path=folder_receipt.path,
                            image_receipt=folder_receipt.image_receipt,
                            verbose=verbose)
        
        # update `progress_bar` but there might not be one...
        try: progress_bar.next()
        except NameError: pass

def get_receipts_of_batch(amount:int, path:str, img_size:loc.Size)->list[FolderReceipt]:
    count = 0
    receipts = []

    for image_receipt in ImageReceipt:
        if image_receipt != ImageReceipt.MIX:
            receipts.append(FolderReceipt(path,
                                        amount_of_images= int(5*amount/100),
                                        objects_per_image= 1,
                                        image_receipt= image_receipt,
                                        img_size=img_size))
            count += int(5*amount/100)

        receipts.append(FolderReceipt(path,
                                      amount_of_images= int(4*amount/100),
                                      objects_per_image= 2,
                                      image_receipt= image_receipt,
                                      img_size=img_size))
        count += int(4*amount/100)
        
        receipts.append(FolderReceipt(path,
                                      amount_of_images= int(3*amount/100),
                                      objects_per_image= 5,
                                      image_receipt= image_receipt,
                                      img_size=img_size))
        count += int(3*amount/100)
        
        receipts.append(FolderReceipt(path,
                                      amount_of_images= int(2*amount/100),
                                      objects_per_image= 10,
                                      image_receipt= image_receipt,
                                      img_size=img_size))
        count += int(2*amount/100)
        
        receipts.append(FolderReceipt(path,
                                      amount_of_images= int(amount/100),
                                      objects_per_image= 20,
                                      image_receipt= image_receipt,
                                      img_size=img_size))
        count += int(amount/100)

    # remaining
    receipts.append(FolderReceipt(path,
                                  amount_of_images= int(amount-count),
                                  objects_per_image= 20,
                                  image_receipt= ImageReceipt.MIX,
                                  img_size=img_size))
    return receipts

if __name__ == '__main__':
    # Settings
    use_multithreading=True # True: Unleash all hell,   False: Slow but steady not being able to properly use your pc (with accurate time estimations)
    verbose=False # for debugging only

    # Batch settings
    train_size = 25000
    validation_size = int(train_size/80*20) # 20%
    
    img_sizes = [
        loc.Size(500,500),
        loc.Size(1000,1000),
        loc.Size(2000,2000)
    ]

    output_path = os.path.join(os.getcwd(), 'files', 'shape_generator')

    # Program
    import sorter
    for img_size in img_sizes:

        # Train 80%
        directory = os.path.join(output_path, f'{img_size.x}x{img_size.y}', 'train')
        receipts = get_receipts_of_batch(amount=    train_size,
                                         path=      directory,
                                         img_size=  img_size)
        total_img = train_size
        progress_bar = FancyBar(f'Generating [{img_size.x}x{img_size.y}] training\t', max=total_img)

        # Progress
        if use_multithreading:
            threads = []
            for receipt in receipts:
                thread = threading.Thread( target=create_from_folder_receipt, args=(receipt, verbose,))
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()
        else:
            for receipt in receipts:
                create_from_folder_receipt(receipt, verbose)
        progress_bar.finish()

        sorter.known_solutions.clear()
        sorter.known_solutions.append(sorter.KnownSolution(['img','.txt'],'img #.txt', start_iterator_at=1, absolute_directory=os.path.join(directory, 'annotations')))
        sorter.known_solutions.append(sorter.KnownSolution(['img','.png'],'img #.png', start_iterator_at=1, absolute_directory=os.path.join(directory, 'images')))
        sorter.sort(dir=directory,
                    mode=sorter.MoveModes.MOVE)

        # Validation 20%
        directory = os.path.join(output_path, f'{img_size.x}x{img_size.y}', 'validation')
        receipts = get_receipts_of_batch(amount=    validation_size,
                                         path=      directory,
                                         img_size=  img_size)
        total_img = validation_size
        progress_bar = FancyBar(f'Generating [{img_size.x}x{img_size.y}] validation\t', max=total_img)

        # Progress
        if use_multithreading:
            threads = []
            for receipt in receipts:
                thread = threading.Thread( target=create_from_folder_receipt, args=(receipt, verbose,))
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()
        else:
            for receipt in receipts:
                create_from_folder_receipt(receipt, verbose)
        progress_bar.finish()

        sorter.known_solutions.clear()
        sorter.known_solutions.append(sorter.KnownSolution(['img','.txt'],'img #.txt', start_iterator_at=1, absolute_directory=os.path.join(directory, 'annotations')))
        sorter.known_solutions.append(sorter.KnownSolution(['img','.png'],'img #.png', start_iterator_at=1, absolute_directory=os.path.join(directory, 'images')))
        sorter.sort(dir=directory,
                    mode=sorter.MoveModes.MOVE)
        
    # Merge everything into 1 big thingy
    # directory = output_path
    # sorter.known_solutions.clear()
    # sorter.known_solutions.append(sorter.KnownSolution(['img','.txt'],'img #.txt', start_iterator_at=1, absolute_directory=os.path.join(directory, 'annotations')))
    # sorter.known_solutions.append(sorter.KnownSolution(['img','.jpg'],'img #.jpg', start_iterator_at=1, absolute_directory=os.path.join(directory, 'images')))
    # sorter.sort(dir=directory,
    #             mode=sorter.MoveModes.MOVE_ZIP)
