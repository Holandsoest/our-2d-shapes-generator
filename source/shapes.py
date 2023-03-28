import common.location as loc
import tkinter
import math
import os

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


    from PIL import Image, ImageTk, EpsImagePlugin
    if as_eps:
        canvas.postscript(file = path_filename + '.eps')
        img = Image.open(path_filename + '.eps')
    else:
        import io
        postscript = canvas.postscript(colormode='color')
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


img_size = loc.Pos(x=200, y=200)
path = os.path.join(os.getcwd(), 'files', 'shape_generator', 'test_img')

root = tkinter.Tk()
canvas = tkinter.Canvas(root, bg="white", height=img_size.y, width=img_size.x)


star1 = Star(center_pos=loc.Pos(x=50, y=50),
             size_in_pixels=24,
             rotation_rad=0.0,
             depth_percentage=50)
star2 = Star(center_pos=loc.Pos(x=150, y=100),
             size_in_pixels=60,
             rotation_rad=1.0,
             depth_percentage=10)

canvas.create_polygon(star1.get_polygon_coordinates(),
                                        outline="blue", width=1,
                                        fill="gray")
# canvas.create_polygon(star2.get_polygon_coordinates(),
#                                         outline="blue", width=1,
#                                         fill="gray")


save_img(tkinter_canvas=canvas,
         path_filename=os.path.join(os.getcwd(), 'files', 'shape_generator'),
         as_jpg=True, as_bmp=True, as_gif=True, as_png=True, as_eps=True)