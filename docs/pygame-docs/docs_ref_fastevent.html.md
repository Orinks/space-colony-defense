![](https://www.pygame.org/docs/_static/pygame_tiny.png)
##### pygame documentation
Pygame Home || Help Contents || Reference Index
**Most useful stuff** : Color | display | draw | event | font | image | key | locals | mixer | mouse | Rect | Surface | time | music | pygame
**Advanced stuff** : cursors | joystick | mask | sprite | transform | BufferProxy | freetype | gfxdraw | midi | PixelArray | pixelcopy | sndarray | surfarray | math
**Other** : camera | controller | examples | fastevent | scrap | tests | touch | version
`pygame.fastevent`
    
pygame module for interacting with events and queues
pygame.fastevent.init | — | initialize pygame.fastevent  
---|---|---  
pygame.fastevent.get_init | — | returns True if the fastevent module is currently initialized  
pygame.fastevent.pump | — | internally process pygame event handlers  
pygame.fastevent.wait | — | wait for an event  
pygame.fastevent.poll | — | get an available event  
pygame.fastevent.get | — | get all events from the queue  
pygame.fastevent.post | — | place an event on the queue  
IMPORTANT NOTE: THIS MODULE IS DEPRECATED IN PYGAME 2.2
In older pygame versions before pygame 2, `pygame.event`pygame module for interacting with events and queues was not well suited for posting events from different threads. This module served as a replacement (with less features) for multithreaded use. Now, the usage of this module is highly discouraged in favour of use of the main `pygame.event`pygame module for interacting with events and queues module. This module will be removed in a future pygame version.
Below, the legacy docs of the module is provided
pygame.fastevent.init()¶
    
initialize pygame.fastevent
init() -> None
Initialize the pygame.fastevent module.
pygame.fastevent.get_init()¶
    
returns True if the fastevent module is currently initialized
get_init() -> bool
Returns True if the pygame.fastevent module is currently initialized.
pygame.fastevent.pump()¶
    
internally process pygame event handlers
pump() -> None
For each frame of your game, you will need to make some sort of call to the event queue. This ensures your program can internally interact with the rest of the operating system.
This function is not necessary if your program is consistently processing events on the queue through the other `pygame.fastevent`pygame module for interacting with events and queues functions.
There are important things that must be dealt with internally in the event queue. The main window may need to be repainted or respond to the system. If you fail to make a call to the event queue for too long, the system may decide your program has locked up.
pygame.fastevent.wait()¶
    
wait for an event
wait() -> Event
Returns the current event on the queue. If there are no messages waiting on the queue, this will not return until one is available. Sometimes it is important to use this wait to get events from the queue, it will allow your application to idle when the user isn't doing anything with it.
pygame.fastevent.poll()¶
    
get an available event
poll() -> Event
Returns next event on queue. If there is no event waiting on the queue, this will return an event with type NOEVENT.
pygame.fastevent.get()¶
    
get all events from the queue
get() -> list of Events
This will get all the messages and remove them from the queue.
pygame.fastevent.post()¶
    
place an event on the queue
post(Event) -> None
This will post your own event objects onto the event queue. You can post any event type you want, but some care must be taken. For example, if you post a MOUSEBUTTONDOWN event to the queue, it is likely any code receiving the event will expect the standard MOUSEBUTTONDOWN attributes to be available, like 'pos' and 'button'.
Because pygame.fastevent.post() may have to wait for the queue to empty, you can get into a dead lock if you try to append an event on to a full queue from the thread that processes events. For that reason I do not recommend using this function in the main thread of an SDL program.
Edit on GitHub
### Navigation
  * index
  * modules |
  * next |
  * previous |
  * pygame v2.6.0 documentation »
  * `pygame.fastevent`


© Copyright 2000-2023, pygame developers. 
