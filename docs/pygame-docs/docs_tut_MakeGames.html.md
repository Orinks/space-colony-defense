![](https://www.pygame.org/docs/_static/pygame_tiny.png)
##### pygame documentation
Pygame Home || Help Contents || Reference Index
**Most useful stuff** : Color | display | draw | event | font | image | key | locals | mixer | mouse | Rect | Surface | time | music | pygame
**Advanced stuff** : cursors | joystick | mask | sprite | transform | BufferProxy | freetype | gfxdraw | midi | PixelArray | pixelcopy | sndarray | surfarray | math
**Other** : camera | controller | examples | fastevent | scrap | tests | touch | version
## Making Games With Pygame¶
### Table of Contents¶
1. Introduction
> 1.1. A note on coding styles
2. Revision: Pygame fundamentals
> 2.1. The basic pygame game
> 2.2. Basic pygame objects
> 2.3. Blitting
> 2.4. The event loop
> 2.5. Ta-da!
3. Kicking things off
> 3.1. The first lines, and loading modules
> 3.2. Resource handling functions
4. Game object classes
> 4.1. A simple ball class
>> 4.1.1. Diversion 1: Sprites
>> 4.1.2. Diversion 2: Vector physics
5. User-controllable objects
> 5.1. A simple bat class
>> 5.1.1. Diversion 3: Pygame events
6. Putting it all together
> 6.1. Let the ball hit sides
> 6.2. Let the ball hit bats
> 6.3. The Finished product
### 1. Introduction¶
First of all, I will assume you have read the Line By Line Chimp tutorial, which introduces the basics of Python and pygame. Give it a read before reading this tutorial, as I won't bother repeating what that tutorial says (or at least not in as much detail). This tutorial is aimed at those who understand how to make a ridiculously simple little "game", and who would like to make a relatively simple game like Pong. It introduces you to some concepts of game design, some simple mathematics to work out ball physics, and some ways to keep your game easy to maintain and expand.
All the code in this tutorial works toward implementing TomPong, a game I've written. By the end of the tutorial, you should not only have a firmer grasp of pygame, but you should also understand how TomPong works, and how to make your own version.
Now, for a brief recap of the basics of pygame. A common method of organising the code for a game is to divide it into the following six sections:
>   * **Load modules** which are required in the game. Standard stuff, except that you should remember to import the pygame local names as well as the pygame module itself
>   * **Resource handling classes** ; define some classes to handle your most basic resources, which will be loading images and sounds, as well as connecting and disconnecting to and from networks, loading save game files, and any other resources you might have.
>   * **Game object classes** ; define the classes for your game object. In the pong example, these will be one for the player's bat (which you can initialise multiple times, one for each player in the game), and one for the ball (which can again have multiple instances). If you're going to have a nice in-game menu, it's also a good idea to make a menu class.
>   * **Any other game functions** ; define other necessary functions, such as scoreboards, menu handling, etc. Any code that you could put into the main game logic, but that would make understanding said logic harder, should be put into its own function. So as plotting a scoreboard isn't game logic, it should be moved into a function.
>   * **Initialise the game** , including the pygame objects themselves, the background, the game objects (initialising instances of the classes) and any other little bits of code you might want to add in.
>   * **The main loop** , into which you put any input handling (i.e. watching for users hitting keys/mouse buttons), the code for updating the game objects, and finally for updating the screen.
> 

Every game you make will have some or all of those sections, possibly with more of your own. For the purposes of this tutorial, I will write about how TomPong is laid out, and the ideas I write about can be transferred to almost any kind of game you might make. I will also assume that you want to keep all of the code in a single file, but if you're making a reasonably large game, it's often a good idea to source certain sections into module files. Putting the game object classes into a file called `objects.py`, for example, can help you keep game logic separate from game objects. If you have a lot of resource handling code, it can also be handy to put that into `resources.py`. You can then `from objects,resources import *` to import all of the classes and functions.
### 1.1. A note on coding styles¶
The first thing to remember when approaching any programming project is to decide on a coding style, and stay consistent. Python solves a lot of the problems because of its strict interpretation of whitespace and indentation, but you can still choose the size of your indentations, whether you put each module import on a new line, how you comment code, etc. You'll see how I do all of this in the code examples; you needn't use my style, but whatever style you adopt, use it all the way through the program code. Also try to document all of your classes, and comment on any bits of code that seem obscure, though don't start commenting the obvious. I've seen plenty of people do the following:
```
player1.score += scoreup    # Add scoreup to player1 score

```

The worst code is poorly laid out, with seemingly random changes in style, and poor documentation. Poor code is not only annoying for other people, but it also makes it difficult for you to maintain.
Edit on GitHub
### Navigation
  * index
  * modules |
  * next |
  * previous |
  * pygame v2.6.0 documentation »
  * Making Games With Pygame


© Copyright 2000-2023, pygame developers. 
