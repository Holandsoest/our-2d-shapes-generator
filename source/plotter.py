"""## BUG:
- The output filesize is not correct. The ques right now is that this is because `.EPS` does some optimization upon first rastirisation before it enters `Pillow`. Very sad. Much cry :'("""
import common.location as loc
import shapes
from enum import Enum # Keep enums UPPER_CASE according to https://docs.python.org/3/howto/enum.html  
from progress.bar import ShadyBar
from PIL import Image, ImageTk
import threading
import tkinter
import random
import shutil
import time
import math
import os


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

def get_random_tkinter_color_(avoid_colors:list[str]|str|None) -> str:
    colors = ["black", "red", "green", "blue", "cyan", "yellow", "magenta", "white"]
    if isinstance(avoid_colors, list):
        for avoid_color in avoid_colors:
            try:    colors.remove(str.lower(avoid_color))
            except: pass
    elif isinstance(avoid_colors, str):
        try:    colors.remove(str.lower(avoid_colors))
        except: pass
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
    
def create_random_shape(canvas:tkinter.Canvas, img_size:loc.Size, forbidden_areas:list[shapes.Annotation], star=False, square=False, symmetric_triangle=False, heart=False, half_circle=False, circle=False) -> shapes.Heart|shapes.Circle|shapes.HalfCircle|shapes.Square|shapes.Star|shapes.SymmetricTriangle:
    if not ( star or square or symmetric_triangle or heart or half_circle or circle ):
        raise SyntaxError('No shape selected to create.')

    # Determine shape
    possible_shapes = []
    if star:                possible_shapes.append('star')
    if square:              possible_shapes.append('square')
    if symmetric_triangle:  possible_shapes.append('symmetric_triangle')
    if heart:               possible_shapes.append('heart')
    if half_circle:         possible_shapes.append('half_circle')
    if circle:              possible_shapes.append('circle')
    chosen_shape = possible_shapes[random.randint(0, len(possible_shapes)-1 )]
    
    valid_area = False
    patience = 1.0
    while(not valid_area and patience > 0.0):

        # Generate shape properties
        shape_size = max(25, int(round(  (random.randint(15,50)/100.0) * patience * img_size.min()  ))) # gets 15-50% the size of the image_size, shrinks every loop due to patience. 25 px is smallest size
        shape_center_pos = loc.Pos(x=random.randint(int(shape_size/2), img_size.x - int(shape_size/2)),
                                   y=random.randint(int(shape_size/2), img_size.y - int(shape_size/2)),
                                   force_int=True)
        shape_rotation = random.random() * math.pi * 2

        # Generate Shape
        match chosen_shape:
            case 'star': 
                shape = shapes.Star(img_size, shape_center_pos, size_in_pixels=shape_size, rotation_rad=shape_rotation,
                                depth_percentage=random.randint(20,70))
            case 'square':
                shape = shapes.Square(img_size, shape_center_pos, size_in_pixels=shape_size, rotation_rad=shape_rotation)
            case 'symmetric_triangle':
                shape = shapes.SymmetricTriangle(img_size, shape_center_pos, size_in_pixels=shape_size, rotation_rad=shape_rotation)
            case 'heart':
                shape = shapes.Heart(img_size, shape_center_pos, size_in_pixels=shape_size, rotation_rad=shape_rotation,
                              depth_percentage=random.randint(65,90))
            case 'half_circle':
                shape = shapes.HalfCircle(img_size, shape_center_pos, size_in_pixels=shape_size, rotation_rad=shape_rotation)
            case 'circle':
                shape = shapes.Circle(img_size, shape_center_pos, size_in_pixels=shape_size)
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
    
    return shape
def create_random_image(image_code:int, objects:int, image_size:loc.Size, path:str, image_receipt:ImageReceipt | None, background_image=None, verbose=False) -> None:
    # Setup environment
    window = tkinter.Tk()
    canvas = tkinter.Canvas(window, bg='white', height=image_size.y, width=image_size.x, takefocus=False, state=tkinter.DISABLED)
    if isinstance(background_image, Image.Image):
        tk_background = ImageTk.PhotoImage(background_image)
        canvas.create_image(0,0, anchor=tkinter.NW, image=tk_background)
    list_of_shapes = []
    annotation_info = []
    all_outline_coordinates = []

    # Generate shapes
    for i in range(0, objects):
        try:
            shape = create_random_shape(canvas=canvas,
                                        img_size=image_size,
                                        forbidden_areas=annotation_info,

                                        star=               image_receipt == ImageReceipt.MIX or image_receipt == ImageReceipt.ONLY_STAR,
                                        square=             image_receipt == ImageReceipt.MIX or image_receipt == ImageReceipt.ONLY_SQUARE,
                                        symmetric_triangle= image_receipt == ImageReceipt.MIX or image_receipt == ImageReceipt.ONLY_SYMMETRIC_TRIANGLE,
                                        heart=              image_receipt == ImageReceipt.MIX or image_receipt == ImageReceipt.ONLY_HEART,
                                        half_circle=        image_receipt == ImageReceipt.MIX or image_receipt == ImageReceipt.ONLY_HALF_CIRCLE,
                                        circle=             image_receipt == ImageReceipt.MIX or image_receipt == ImageReceipt.ONLY_CIRCLE
                                        )
        except: continue
        
        # Add the annotation to the list
        list_of_shapes.append(shape)
        annotation_info.append(shape.annotation)
        all_outline_coordinates.append(shape.outline_coordinates)
    
    # Draw the shapes
    depth_shadow_px = random.randint(0, int(image_size.min()/50))
    sun_rotation_rad = math.pi * 2 * random.random()
    for shape in list_of_shapes:
        shape.draw_shadow(canvas,
                          depth_shadow_px,
                          sun_rotation_rad)
    for shape in list_of_shapes:
        fill_color = get_random_tkinter_color_(avoid_colors='white')
        avoid_colors = ["red", "green", "blue", "cyan", "yellow", "magenta"]
        try:    avoid_colors.remove(fill_color)
        except: pass
        outline_color = get_random_tkinter_color_(avoid_colors)
        shape.draw_shape(tkinter_canvas=canvas,
                         outline_color=outline_color,
                         fill_color=fill_color,
                         width_outline=1,
                         location_offset=loc.Pos())
    # Summit the data
    save_img(tkinter_canvas=canvas,
             path_filename=os.path.join(path, 'images', f'img ({image_code})'),
             as_png=True)
    save_annotation(annotation_info,
                    path_filename=os.path.join(path, 'annotations', f'img ({image_code})'))
    if not verbose:
        window.destroy()
        return
    
    # Mark all polygons
    for outline_coordinates in all_outline_coordinates:
        for coordinate in outline_coordinates:
            canvas.create_rectangle(coordinate.x-1,coordinate.y-1,coordinate.x+1,coordinate.y+1,outline='red',fill='blue',width=1) # draw dot on each coordinate

    for annotation in annotation_info:
        center_pos = loc.Pos(x= annotation.x * image_size.x,
                             y= annotation.y * image_size.y)
        size_shape = loc.Pos(x= annotation.width * image_size.x,
                             y= annotation.height * image_size.y)
        box_top_left = loc.Pos(x= center_pos.x - size_shape.x / 2,
                               y= center_pos.y - size_shape.y / 2,
                               force_int=True)
        box_bottom_right = loc.Pos(x= center_pos.x + size_shape.x / 2,
                                   y= center_pos.y + size_shape.y / 2,
                                   force_int=True)
        
        # Mark annotation
        canvas.create_rectangle(box_top_left.x,box_top_left.y,
                                box_bottom_right.x,box_bottom_right.y)
    window.title = f'{len(annotation_info)} of the {objects} that were requested'
    window.mainloop()
def create_from_folder_receipt(folder_receipt:FolderReceipt, verbose=False) -> None:
    # Prepare the background of the image, what is for each the same
    background_image_location = os.path.join(os.getcwd(),'file','background.bmp')
    if os.path.exists(background_image_location):
        background_image = Image.open(background_image_location, mode='r')
        background_image = background_image.resize((folder_receipt.img_size.x, folder_receipt.img_size.y), Image.Resampling.NEAREST)

    # Generate all images from the receipt
    for image_code in range(0, folder_receipt.amount_of_images):
        create_random_image(image_code=image_code,
                            objects=folder_receipt.objects_per_image,
                            image_size=folder_receipt.img_size,
                            path=folder_receipt.path,
                            image_receipt=folder_receipt.image_receipt,
                            verbose=verbose,
                            background_image=background_image) 
        
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
    use_multithreading=False # True: Unleash all hell,   False: Slow but steady not being able to properly use your pc (with accurate time estimations)
    verbose=False # for debugging only

    # Batch settings
    train_size = 20#250000
    validation_size = int(train_size/80*20) # 20%
    
    img_sizes = [
        loc.Size(500,500),
        # loc.Size(1000,1000),
        # loc.Size(2000,2000)
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
        
        # Create `.zip`
        directory = os.path.join(output_path,f'{img_size.x}x{img_size.y}')
        filename = f'{time.localtime().tm_year}-{str(time.localtime().tm_mon).zfill(2)}-{str(time.localtime().tm_mday).zfill(2)}_{img_size.x}x{img_size.y}_T{train_size}+V{validation_size}_{str(time.localtime().tm_hour).zfill(2)}{str(time.localtime().tm_min).zfill(2)}{str(time.localtime().tm_sec).zfill(2)}'
        progress_bar = FancyBar(f'Creating {filename}.zip\t', max=1)
        progress_bar.start()
        shutil.make_archive(filename,'zip', directory)
        progress_bar.next()
        progress_bar.finish()

        # Remove original folder
        progress_bar = FancyBar(f'Removing originals\t', max=sorter.count_items_in_folder(directory)[0])
        progress_bar.start()
        sorter.remove_files(directory, progress_bar)
        progress_bar.finish()
