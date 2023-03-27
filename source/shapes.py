import common.location as loc
import math



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
    def __init__(self, pos:loc.Pos, size_in_pixels=10, rotation_rad=0, depth_percentage=50):
        self.pos = pos
        self.size_in_pixels = size_in_pixels
        self.rotation_rad=rotation_rad
        self.depth_percentage=depth_percentage

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
    def get_outline(self) -> list(loc.Pos):
        return self.outline_coordinates
    def draw_jpg(self) -> None:
        import tkinter
        root = tkinter.Tk()
        myCanvas = tkinter.Canvas(root, bg="white", height=200, width=200)

        polygon = myCanvas.create_polygon(self.outline_coordinates, )

        # add to window and show
        myCanvas.pack()
        root.mainloop()
        import time
        time.sleep(60)


