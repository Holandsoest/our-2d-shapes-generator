import common.location as loc
import math



def shoot(start_pos:loc.Pos, length_trace=1, rotation_rad=0.0) -> loc.Pos:
    return loc.Pos(
        x= start_pos.x + length_trace * math.cos(rotation_rad),
        y= start_pos.y + length_trace * (-math.sin(rotation_rad))
                   )
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

        




