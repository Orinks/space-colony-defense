![](https://www.pygame.org/docs/_static/pygame_tiny.png)
##### pygame documentation
Pygame Home || Help Contents || Reference Index
**Most useful stuff** : Color | display | draw | event | font | image | key | locals | mixer | mouse | Rect | Surface | time | music | pygame
**Advanced stuff** : cursors | joystick | mask | sprite | transform | BufferProxy | freetype | gfxdraw | midi | PixelArray | pixelcopy | sndarray | surfarray | math
**Other** : camera | controller | examples | fastevent | scrap | tests | touch | version
`pygame._sdl2.touch`
    
pygame module to work with touch input
pygame._sdl2.touch.get_num_devices | — | get the number of touch devices  
---|---|---  
pygame._sdl2.touch.get_device | — | get the a touch device id for a given index  
pygame._sdl2.touch.get_num_fingers | — | the number of active fingers for a given touch device  
pygame._sdl2.touch.get_finger | — | get information about an active finger  
New in pygame 2: This module requires SDL2.
pygame._sdl2.touch.get_num_devices()¶
    
get the number of touch devices
get_num_devices() -> int
Return the number of available touch devices.
pygame._sdl2.touch.get_device()¶
    
get the a touch device id for a given index
get_device(index) -> touchid
Parameters
    
**index** (_int_) -- This number is at least 0 and less than the `number of devices`.
Return an integer id associated with the given `index`.
pygame._sdl2.touch.get_num_fingers()¶
    
the number of active fingers for a given touch device
get_num_fingers(touchid) -> int
Return the number of fingers active for the touch device whose id is touchid.
pygame._sdl2.touch.get_finger()¶
    
get information about an active finger
get_finger(touchid, index) -> int
Parameters
    
  * **touchid** (_int_) -- The touch device id.
  * **index** (_int_) -- The index of the finger to return information about, between 0 and the `number of active fingers`.


Return a dict for the finger `index` active on `touchid`. The dict contains these keys:
```
id     the id of the finger (an integer).
x     the normalized x position of the finger, between 0 and 1.
y     the normalized y position of the finger, between 0 and 1.
pressure  the amount of pressure applied by the finger, between 0 and 1.

```

Edit on GitHub
### Navigation
  * index
  * modules |
  * next |
  * previous |
  * pygame v2.6.0 documentation »
  * `pygame._sdl2.touch`


© Copyright 2000-2023, pygame developers. 
