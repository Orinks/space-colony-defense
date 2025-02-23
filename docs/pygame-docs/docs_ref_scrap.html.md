![](https://www.pygame.org/docs/_static/pygame_tiny.png)
##### pygame documentation
Pygame Home || Help Contents || Reference Index
**Most useful stuff** : Color | display | draw | event | font | image | key | locals | mixer | mouse | Rect | Surface | time | music | pygame
**Advanced stuff** : cursors | joystick | mask | sprite | transform | BufferProxy | freetype | gfxdraw | midi | PixelArray | pixelcopy | sndarray | surfarray | math
**Other** : camera | controller | examples | fastevent | scrap | tests | touch | version
`pygame.scrap`
    
pygame module for clipboard support.
pygame.scrap.init | — | Initializes the scrap module.  
---|---|---  
pygame.scrap.get_init | — | Returns True if the scrap module is currently initialized.  
pygame.scrap.get | — | Gets the data for the specified type from the clipboard.  
pygame.scrap.get_types | — | Gets a list of the available clipboard types.  
pygame.scrap.put | — | Places data into the clipboard.  
pygame.scrap.contains | — | Checks whether data for a given type is available in the clipboard.  
pygame.scrap.lost | — | Indicates if the clipboard ownership has been lost by the pygame application.  
pygame.scrap.set_mode | — | Sets the clipboard access mode.  
**EXPERIMENTAL!** : This API may change or disappear in later pygame releases. If you use this, your code may break with the next pygame release.
The scrap module is for transferring data to/from the clipboard. This allows for cutting and pasting data between pygame and other applications. Some basic data (MIME) types are defined and registered:
```
 pygame     string
constant    value    description
--------------------------------------------------
SCRAP_TEXT  "text/plain"  plain text
SCRAP_BMP  "image/bmp"   BMP encoded image data
SCRAP_PBM  "image/pbm"   PBM encoded image data
SCRAP_PPM  "image/ppm"   PPM encoded image data

```

`pygame.SCRAP_PPM`, `pygame.SCRAP_PBM` and `pygame.SCRAP_BMP` are suitable for surface buffers to be shared with other applications. `pygame.SCRAP_TEXT` is an alias for the plain text clipboard type.
Depending on the platform, additional types are automatically registered when data is placed into the clipboard to guarantee a consistent sharing behaviour with other applications. The following listed types can be used as strings to be passed to the respective `pygame.scrap`pygame module for clipboard support. module functions.
For **Windows** platforms, these additional types are supported automatically and resolve to their internal definitions:
```
"text/plain;charset=utf-8"  UTF-8 encoded text
"audio/wav"         WAV encoded audio
"image/tiff"         TIFF encoded image data

```

For **X11** platforms, these additional types are supported automatically and resolve to their internal definitions:
```
"text/plain;charset=utf-8"  UTF-8 encoded text
"UTF8_STRING"        UTF-8 encoded text
"COMPOUND_TEXT"       COMPOUND text

```

User defined types can be used, but the data might not be accessible by other applications unless they know what data type to look for. Example: Data placed into the clipboard by `pygame.scrap.put("my_data_type", byte_data)` can only be accessed by applications which query the clipboard for the `"my_data_type"` data type.
For an example of how the scrap module works refer to the examples page (`pygame.examples.scrap_clipboard.main()`access the clipboard) or the code directly in GitHub (pygame/examples/scrap_clipboard.py).
New in pygame 1.8.
Note
The scrap module is currently only supported for Windows, X11 and Mac OS X. On Mac OS X only text works at the moment - other types may be supported in future releases.
pygame.scrap.init()¶
    
Initializes the scrap module.
init() -> None
Initialize the scrap module.
Raises
    
**pygame.error** standard pygame exception -- if unable to initialize scrap module
Note
The scrap module requires `pygame.display.set_mode()`Initialize a window or screen for display be called before being initialized.
pygame.scrap.get_init()¶
    
Returns True if the scrap module is currently initialized.
get_init() -> bool
Gets the scrap module's initialization state.
Returns
    
`True` if the `pygame.scrap`pygame module for clipboard support. module is currently initialized, `False` otherwise
Return type
    
bool
New in pygame 1.9.5.
pygame.scrap.get()¶
    
Gets the data for the specified type from the clipboard.
get(type) -> bytes | None
Retrieves the data for the specified type from the clipboard. The data is returned as a byte string and might need further processing (such as decoding to Unicode).
Parameters
    
**type** (_string_) -- data type to retrieve from the clipboard
Returns
    
data (bytes object) for the given type identifier or `None` if no data for the given type is available
Return type
    
bytes | None
```
text = pygame.scrap.get(pygame.SCRAP_TEXT)
if text:
  print("There is text in the clipboard.")
else:
  print("There does not seem to be text in the clipboard.")

```

pygame.scrap.get_types()¶
    
Gets a list of the available clipboard types.
get_types() -> list
Gets a list of data type string identifiers for the data currently available on the clipboard. Each identifier can be used in the `pygame.scrap.get()`Gets the data for the specified type from the clipboard. method to get the clipboard content of the specific type.
Returns
    
list of strings of the available clipboard data types, if there is no data in the clipboard an empty list is returned
Return type
    
list
```
for t in pygame.scrap.get_types():
  if "text" in t:
    # There is some content with the word "text" in its type string.
    print(pygame.scrap.get(t))

```

pygame.scrap.put()¶
    
Places data into the clipboard.
put(type, data) -> None
Places data for a given clipboard type into the clipboard. The data must be a string buffer. The type is a string identifying the type of data to be placed into the clipboard. This can be one of the predefined `pygame.SCRAP_PBM`, `pygame.SCRAP_PPM`, `pygame.SCRAP_BMP` or `pygame.SCRAP_TEXT` values or a user defined string identifier.
Parameters
    
  * **type** (_string_) -- type identifier of the data to be placed into the clipboard
  * **data** (_bytes_) -- data to be place into the clipboard, a bytes object


Raises
    
**pygame.error** standard pygame exception -- if unable to put the data into the clipboard
```
with open("example.bmp", "rb") as fp:
  pygame.scrap.put(pygame.SCRAP_BMP, fp.read())
# The image data is now on the clipboard for other applications to access
# it.
pygame.scrap.put(pygame.SCRAP_TEXT, b"A text to copy")
pygame.scrap.put("Plain text", b"Data for user defined type 'Plain text'")

```

pygame.scrap.contains()¶
    
Checks whether data for a given type is available in the clipboard.
contains(type) -> bool
Checks whether data for the given type is currently available in the clipboard.
Parameters
    
**type** (_string_) -- data type to check availability of
Returns
    
`True` if data for the passed type is available in the clipboard, `False` otherwise
Return type
    
bool
```
if pygame.scrap.contains(pygame.SCRAP_TEXT):
  print("There is text in the clipboard.")
if pygame.scrap.contains("own_data_type"):
  print("There is stuff in the clipboard.")

```

pygame.scrap.lost()¶
    
Indicates if the clipboard ownership has been lost by the pygame application.
lost() -> bool
Indicates if the clipboard ownership has been lost by the pygame application.
Returns
    
`True`, if the clipboard ownership has been lost by the pygame application, `False` if the pygame application still owns the clipboard
Return type
    
bool
```
if pygame.scrap.lost():
  print("The clipboard is in use by another application.")

```

pygame.scrap.set_mode()¶
    
Sets the clipboard access mode.
set_mode(mode) -> None
Sets the access mode for the clipboard. This is only of interest for X11 environments where clipboard modes `pygame.SCRAP_SELECTION` (for mouse selections) and `pygame.SCRAP_CLIPBOARD` (for the clipboard) are available. Setting the mode to `pygame.SCRAP_SELECTION` in other environments will not change the mode from `pygame.SCRAP_CLIPBOARD`.
Parameters
    
**mode** -- access mode, supported values are `pygame.SCRAP_CLIPBOARD` and `pygame.SCRAP_SELECTION` (`pygame.SCRAP_SELECTION` only has an effect when used on X11 platforms)
Raises
    
**ValueError** -- if the `mode` parameter is not `pygame.SCRAP_CLIPBOARD` or `pygame.SCRAP_SELECTION`
Edit on GitHub
### Navigation
  * index
  * modules |
  * next |
  * previous |
  * pygame v2.6.0 documentation »
  * `pygame.scrap`


© Copyright 2000-2023, pygame developers. 
