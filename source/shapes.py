import common.location as loc
import math
import os

output_directory = os.path.join(os.getcwd(), 'files')

def shoot(start_pos:loc.Pos, length_trace=1, rotation_rad=0.0) -> loc.Pos:
    return loc.Pos(
        x= start_pos.x + length_trace * math.cos(rotation_rad),
        y= start_pos.y + length_trace * (-math.sin(rotation_rad)) )
def firework_outwards(center_pos:loc.Pos, traces= 4, length_traces=10, rotation_rad=0):
    output = []

    trace_rad_spacing = math.pi * 2 / float(traces)

    for i in range(traces):
        output.append(shoot(
            start_pos=      center_pos,
            length_trace=   length_traces,
            rotation_rad=   rotation_rad + i * trace_rad_spacing
        ))

    return output

class Star:
    def __init__(self, pos:loc.Pos, size_in_pixels=10, rotation_rad=0.0, depth_percentage=50):
        self.pos = pos
        self.size_in_pixels = size_in_pixels
        self.rotation_rad=rotation_rad
        self.depth_percentage=depth_percentage
        self.folder_name = os.path.join(output_directory, 'star')

        # store the outline in a list
        self.outline_coordinates = []

        outer_points = firework_outwards(center_pos=pos, traces=5, length_traces=size_in_pixels / 2, rotation_rad=rotation_rad)
        inner_points = firework_outwards(center_pos=pos, traces=5, length_traces=size_in_pixels / 200 * depth_percentage,
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
    def get_outline(self) -> list:
        return self.outline_coordinates
    def draw_jpg(self) -> None:
        import tkinter
        import Image, ImageDraw
        
        root = tkinter.Tk()
        myCanvas = tkinter.Canvas(root, bg="white", height=200, width=200)

        polygon_coordinates = []
        for i in self.outline_coordinates:
            polygon_coordinates.append(  int(round(  i.x,  0  ))  )
            polygon_coordinates.append(  int(round(  i.y,  0  ))  )

        polygon = myCanvas.create_polygon([polygon_coordinates],
                                          outline="blue", width=1,
                                          fill="gray")

        # add to window and show
        myCanvas.pack()

        # memory only, not visible
        image1 = Image.new("RGB", (width, height), white)
        draw = ImageDraw.Draw(image1)

        # do the Tkinter canvas drawings (visible)
        cv.create_line([0, center, width, center], fill='green')

        # do the PIL image/draw (in memory) drawings
        draw.line([0, center, width, center], green)

        # PIL image can be saved as .png .jpg .gif or .bmp file (among others)
        filename = "my_drawing.jpg"
        image1.save(filename)

        root.mainloop() # For debugging only


star = Star(loc.Pos(50,50),
            size_in_pixels=10,
            rotation_rad=0.0,
            depth_percentage=50)
star.draw_jpg()