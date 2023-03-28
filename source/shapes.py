import common.location as loc
import tkinter
import math
import os

object_names_array=["circle, half circle, square, heart, star, triangle"]

def shoot_(start_pos:loc.Pos, length_trace=1, rotation_rad=0.0) -> loc.Pos:
    return loc.Pos(
        x= start_pos.x + length_trace * math.cos(rotation_rad),
        y= start_pos.y + length_trace * (-math.sin(rotation_rad)) )
def firework_outwards_(center_pos:loc.Pos, traces= 4, length_traces=10, rotation_rad=0):
    output = []

    trace_rad_spacing = math.pi * 2 / float(traces)

    for i in range(traces):
        output.append(shoot_(
            start_pos=      center_pos,
            length_trace=   length_traces,
            rotation_rad=   rotation_rad + i * trace_rad_spacing
        ))

    return output
class Star:
    def __init__(self, center_pos:loc.Pos, size_in_pixels=10, rotation_rad=0.0, depth_percentage=50):
        self.center_pos = center_pos
        self.size_in_pixels = size_in_pixels
        self.rotation_rad=rotation_rad
        self.depth_percentage=depth_percentage

        # store the outline in a list
        self.outline_coordinates = []

        outer_points = firework_outwards_(center_pos=center_pos, traces=5, length_traces=size_in_pixels / 2, rotation_rad=rotation_rad)
        inner_points = firework_outwards_(center_pos=center_pos, traces=5, length_traces=size_in_pixels / 200 * depth_percentage,
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
    def get_outline_coordinates(self):
        return self.outline_coordinates
    def get_annotation(self, img_size:loc.Pos) -> str:
        class_id = '4'

        x = float(self.center_pos.x)/float(img_size.x)

        y = float(self.center_pos.y)/float(img_size.y)

        min_x = self.outline_coordinates[0].x
        max_x = self.outline_coordinates[0].x
        for pos in self.outline_coordinates:
            min_x = min(min_x, pos.x)
            max_x = max(max_x, pos.x)
        dx = max_x - min_x
        width = float(dx)/float(img_size.x)

        min_y = self.outline_coordinates[0].y
        max_y = self.outline_coordinates[0].y
        for pos in self.outline_coordinates:
            min_y = min(min_y, pos.y)
            max_y = max(max_y, pos.y)
        dy = max_y - min_y
        height = float(dy)/float(img_size.y)

        return f'{class_id} {x} {y} {width} {height}'

    def get_polygon_coordinates(self):
        """Returns a list of coordinates that can be used by `tkinter` to draw a `polygon` on a `canvas`"""
        polygon_coordinates = []
        for node in self.outline_coordinates:
            polygon_coordinates.append(  int(round(  node.x,  0  ))  )
            polygon_coordinates.append(  int(round(  node.y,  0  ))  )
        return polygon_coordinates

def save_img(tkinter_canvas:tkinter.Canvas, path_filename:str, as_png=False, as_jpg=False, as_gif=False, as_bmp=False, as_eps=False) -> None:
    if not ( as_png or as_jpg or as_gif or as_bmp or as_eps ):
        print('WARNING: Could not save as no file format was given.')
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
    # 3. This took me hours :'(
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

def get_random_tkinter_color_() -> str:
    return 'blue' # TODO
def create_random_image(image_code:int, max_objects:int, img_size:loc.Pos, path:str) -> None:
    import random

    # Setup environment
    root = tkinter.Tk()
    canvas = tkinter.Canvas(root, bg="white", height=img_size.y, width=img_size.x)
    annotation_info = []

    # Variables
    shapes = random.randint(1,max_objects)

    # Generate shapes
    for i in range(1, shapes):

        # Get parameters
        shape_size = int(random.randint(10, int(img_size.min() / 1.5)))
        shape_pos = loc.Pos(x=random.randint(int(shape_size/2), img_size.x - int(shape_size/2)),
                            y=random.randint(int(shape_size/2), img_size.y - int(shape_size/2)),
                            force_int=True)
        shape_color = get_random_tkinter_color_()

        # Choose shape
        match random.randint(0,0):
            case 0: 
                shape = Star(center_pos=shape_pos,
                             size_in_pixels=shape_size,
                             rotation_rad=random.random() * math.pi * 2 / 5,
                             depth_percentage=random.randint(20,70))
            case _:
                raise Warning('Out of range; in the count of shapes.')

        #TODO check for overlap -> return BAD

        annotation_info.append(shape.get_annotation(img_size=img_size))
        canvas.create_polygon(shape.get_polygon_coordinates(),
                              outline=shape_color, width=1,
                              fill=shape_color)
    
    # Summit the data
    save_img(tkinter_canvas=canvas,
            path_filename=os.path.join(path, 'images', f'img ({image_code})'),
            as_jpg=True)
    save_annotation(annotation_info,
                    path_filename=os.path.join(path, 'annotations', f'img ({image_code})'))
def create_random_batch(size_batch:int, img_size:loc.Pos, image_code_start=1, batch_nr=0) -> None:
    if batch_nr == 0:
        path = os.path.join(os.getcwd(), 'files', 'shape_generator')
    else:
        path = os.path.join(os.getcwd(), 'files', 'shape_generator', f'batch {batch_nr}')
    
    for image_code in range(image_code_start, image_code_start + size_batch):
        create_random_image(image_code=image_code,
                            max_objects=5,                                      ###########
                            img_size=img_size,
                            path=path)


if __name__ == '__main__':

    img_size = loc.Pos(x=200, y=200)
    create_random_batch(size_batch=10, img_size=img_size)
