__description__ = \
"""
Drive a set of LED matrix panels.
"""
__author__ = "Michael J. Harms"
__date__ = "2017-01-01"

import numpy as np

class Panel:
    """
    Hold the basic properties of an LED panel.
    """
    
    def __init__(self,x_size=32,y_size=32):
        """
        Initialize an instance of Panel.
        """

        self._shape = (x_size,y_size)
        self._offset = (0,0)
        self._chain_offset = 0 
        self._transform_function = None

    @property
    def shape(self):
        """
        The dimensions of the panel.
        """

        return self._shape

    @property
    def offset(self):
        """
        The offset of the panel pixels (from top-left of display).
        """

        return self._offset

    @offset.setter
    def offset(self,offset):
       
        if len(offset) != 2:
            err = "Offset must have 2 dimensions.\n"
            raise ValueError(err)

        self._offset = tuple(offset)

    @property
    def chain_offset(self):
        """
        The offset of the panel pixels in the chain (left to right).
        """
        return self._chain_offset

    @chain_offset.setter
    def chain_offset(self,chain_offset):

        if type(chain_offset) != int:
            err = "Chain offset must be an integer.\n"
            raise ValueError(err)

        self._chain_offset = chain_offset

    def _r90(self,m):
        """
        Rotate by 90 degrees.
        """

        return np.rot90(m,1)

    def _r180(self,m):
        """
        Rotate by 180 degrees.
        """
        return np.rot90(m,2)

    def _r270(self,m):
        """
        Rotate by 270 degrees.
        """
        return np.rot90(m,3)

    def set_transform_function(self,transform_key):
        """
        Define the function to transform the function. Transform key should be
        0 (no rotation), 90 (90 degree rot), 180, or 270.
        """

        options = {  0:None,
                    90:self._r90 ,
                   180:self._r180,
                   270:self._r270}

        self._transform_function = options[transform_key]

    def transform(self,some_matrix):
        """
        Transform matrix appropriately.
        """
       
        if self._transform_function == None:
            return some_matrix

        return self._transform_function(some_matrix) 
        
       
class Display:
    """
    A collection of Panel instances arranged according to "layout" in space and
    according to "chain" electronically.  Each panel can also have a specified
    rotation (0,90,180,270).  After initializing the Panel, passing an RGB
    (or RGBA) matrix to the "draw" method will then plot the image on the LED
    panels.
    """

    def __init__(self,layout,chain,rotation=(),backend="rgbmatrix"):
        """
        
        layout: a 2D array (or 2D list) of Panel instaces indicating their
                arrangement in space.
        chain:  a 1D array that has all Panel instances in layout indicating
                how the panels are actually wired together as a chain.
        rotation: a 1D array indicating the rotation to apply to each panel.
        backend: how to plot.  rgbmatrix will use the rgbmatrix library to 
                 draw on LED panels.  matplotlib will use matplotlib to plot
                 on a graph. 
        """
       
        self._layout = np.array(layout)
        self._chain = np.array(chain)

        # -------------- Do a bunch of sanity checks --------------------
        if len(self._layout.shape) != 2:
            err = "Layout must be a 2D array!\n"
            raise ValueError(err)

        if len(self._chain.shape) != 1:
            err = "Chain must be a 1D array!\n"
            raise ValueError(err)

        chain_dict = dict([(c,0) for c in self._chain])
        if len(chain_dict.keys()) != self._chain.shape[0]:
            err = "Chain entries must be unique!\n"
            raise ValueError(err) 

        for i in range(self._layout.shape[0]):
            for j in range(self._layout.shape[1]):
                try:
                    chain_dict.pop(self._layout[i,j])
                except KeyError:
                    err = "Chain must contain all entries in layout!\n"
                    raise ValueError(err)
      
        if len(chain_dict) != 0:
            err = "Layout must have all entries in chain!\n"
            raise ValueError(err)

        if len(rotation) != 0 and len(rotation) != len(self._chain):
            err = "Rotations must be specified for no panels or all panels.\n"
            raise ValueError(err)


        x_dims = []
        y_dims = []
        for s in self._chain:
            x_dims.append(s.shape[0])
            y_dims.append(s.shape[1])
   
        if len(np.unique(x_dims)) != 1 or len(np.unique(y_dims)) != 1:
            err = "Sub panels must all have the same dimensions.\n"
            raise ValueError(err)

        # -------------- End sanity checks --------------------

        # Record size of each subpanel
        self._subpanel_x_size = self._chain[0].shape[0]
        self._subpanel_y_size = self._chain[0].shape[1]
    
        # Figure out the total size of the panel 
        self._total_x_size = sum([p.shape[0] for p in self._layout[:,0]])
        self._total_y_size = sum([p.shape[1] for p in self._layout[0,:]])

        # Figure out offsets for the coordinates of each panel, mapping them to 
        # the global coordinates. This uses the top-left corner as the origin. 
        x_offset = 0
        y_offset = 0
        for i in range(self._layout.shape[0]):
            for j in range(self._layout.shape[1]):
                self._layout[i,j].offset = [x_offset,y_offset]
                y_offset += self._subpanel_y_size
            y_offset = 0
            x_offset += self._subpanel_x_size

        # Figure out where to place each panel in the chain
        chain_offset = 0 
        for i, s in enumerate(self._chain):
            s.chain_offset = chain_offset
            chain_offset += s.shape[0]

            if len(rotation) != 0:
                s.set_transform_function(rotation[i])

        self._chain_matrix = np.zeros((self._subpanel_y_size,
                                       len(self._chain)*self._subpanel_x_size,
                                       3),dtype=np.int)

        # Deal with graphical backend
        if backend == "rgbmatrix":
            self._backend = RgbmatrixBackend(self._subpanel_y_size,
                                             len(self._chain),1)
        elif backend == "matplotlib":
            self._backend = MatplotlibBackend()
        else:
            err = "backend {} not recognized.\n".format(backend)
            raise ValueError(err)


    def draw(self,image):
        """
        Take a matrix of RGB values and draw them using the chosen backend.  
        Use the specified layout, chain, and rotation to plot each chunk of
        of the image on the appropriate panel with the appropriate orientation.
        """

        # Make sure the image has the correct dimensions
        if image.shape[0] != self._total_x_size or image.shape[1] != self._total_y_size:
            local_shape = (self._total_x_size,self._total_y_size)
            err = "Image dimensions ({}) do not match panel dimensions ({})\n".format(image.shape,
                                                                                      local_shape)
            raise ValueError(err)

        # Make sure the image has RGB channels 
        if image.shape[2] < 3:
            err = "Image must have at least RGB channels\n"
            raise ValueError(err)

        # Map the matrix into the chain 
        for i, s in enumerate(self._chain):

            chain_x_0 = 0
            chain_x_1 = self._subpanel_y_size
            chain_y_0 = s.chain_offset
            chain_y_1 = s.chain_offset + self._subpanel_x_size

            image_x_0 = s.offset[0]
            image_x_1 = s.offset[0] + self._subpanel_x_size

            image_y_0 = s.offset[1]
            image_y_1 = s.offset[1] + self._subpanel_y_size

            # Map and rotate
            self._chain_matrix[chain_x_0:chain_x_1,
                               chain_y_0:chain_y_1,:3] = \
                               s.transform(image[image_x_0:image_x_1,
                                               image_y_0:image_y_1,:3])

        # Draw the image.
        self._backend.draw(self._chain_matrix)
  

class Backend:
    """
    Dummy Backend that, when subclassed allows plotting of matrices.
    """   
 
    def __init__(self):
        pass

    def draw(self,matrix):
        pass

class MatplotlibBackend(Backend):

    def __init__(self):

        from matplotlib import pyplot as plt
        self._plt = plt 
        
    def draw(self,matrix):
    
        self._plt.imshow(matrix,interpolation="nearest")
        self._plt.show()

class RgbmatrixBackend(Backend):
    
    def __init__(self,rows,chain_length,num_parallel=1,pwmbits=11,brightness=40,corr_luminance=True):
        """
        Initialize rgbmatrix.
        """
    
        from PIL import Image
        self._img = Image
        
        from rgbmatrix import RGBMatrix
    
        self._rows = int(rows)
        self._chain_length = int(chain_length)
        self._num_parallel = int(num_parallel)

        self._pwmbits = int(round(pwmbits,0))
        if self._pwmbits < 0 or self._pwmbits < 11:
            err = "pwmbits must be integer between 0 and 11.\n"
            raise ValueError(err)

        self._brightness = int(round(brightness,0))
        if self._brightness < 0 or self._brightness > 100:
            err = "Brightness must be integer between 0 and 100.\n"
            raise ValueError(err)

        self._corr_luminance = bool(corr_luminance)
       
        self._matrix = RGBMatrix(self._rows,self._chain_length,self._num_parallel)
        self._matrix.pwmBits = self._pwmbits
        self._matrix.brightness = self._brightness
        self._matrix.luminanceCorrect = self._corr_luminance

        self._canvas = self._matrix.CreateFrameCanvas()

    def draw(self,matrix):
        """
        Draw the graphic on the panels.
        """

        # Create a PIL image from the matrix 
        img = self._img.fromarray(np.uint8(matrix))

        # Draw it.
        self._canvas.SetImage(img,0,0)
        self._canvas = self._matrix.SwapOnVSync(self._canvas)
  
 
