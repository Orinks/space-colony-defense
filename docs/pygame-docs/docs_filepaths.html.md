![](https://www.pygame.org/docs/_static/pygame_tiny.png)
##### pygame documentation
Pygame Home || Help Contents || Reference Index
**Most useful stuff** : Color | display | draw | event | font | image | key | locals | mixer | mouse | Rect | Surface | time | music | pygame
**Advanced stuff** : cursors | joystick | mask | sprite | transform | BufferProxy | freetype | gfxdraw | midi | PixelArray | pixelcopy | sndarray | surfarray | math
**Other** : camera | controller | examples | fastevent | scrap | tests | touch | version
A pygame function or method which takes a file path argument will accept either a Unicode or a byte (8-bit or ASCII character) string. Unicode strings are translated to Python's default filesystem encoding, as returned by sys.getfilesystemencoding(). A Unicode code point above U+FFFF (`\uFFFF`) can be coded directly with a 32-bit escape sequences (`\Uxxxxxxxx`), even for Python interpreters built with an UCS-2 (16-bit character) Unicode type. Byte strings are passed to the operating system unchanged.
Null characters (`\x00`) are not permitted in the path, raising an exception. An exception is also raised if an Unicode file path cannot be encoded. How UTF-16 surrogate codes are handled is Python-interpreter-dependent. Use UTF-32 code points and 32-bit escape sequences instead. The exception types are function-dependent.
Edit on GitHub
### Navigation
  * index
  * modules |
  * next |
  * previous |
  * pygame v2.6.0 documentation »
  * File Path Function Arguments


© Copyright 2000-2023, pygame developers. 
