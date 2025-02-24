Pygame Integration Plan for Space Colony Defense

Overview:
------------
This document describes how to integrate Pygame into the existing Space Colony Defense codebase to implement the main game loop and rendering. The plan leverages the existing game logic (turret, enemy waves, management, resources, etc.) and adds Pygame functionality for graphics, event handling, and audio playback using its mixer.

Key Steps:

1. Create a Pygame-Based Game Loop
   • Create a new module (cli/game/game_loop.py).
   • Initialize Pygame (display window, clock, and mixer for audio).
   • Write a main loop that:
       - Processes Pygame events (e.g., KEYDOWN for left/right movement, shooting, and triggering management actions).
       - Updates game state (e.g., turret movements, enemy wave updates, collisions).
       - Renders current game objects (turret, enemies, colony/resource status) to the screen using Pygame drawing routines.
       - Calls pygame.display.flip() each frame.
   • Example pseudocode snippet:
       -----------------------------------------
       import pygame
       from cli.game.game_state import GameState, Resources, Colony
       from cli.game.turret import Turret
       from cli.game.enemy_wave import generate_wave

       def main():
           pygame.init()
           screen = pygame.display.set_mode((800, 600))
           clock = pygame.time.Clock()

           # Initialize game state and objects
           colony = Colony(hp=100, max_hp=100)
           resources = Resources(energy=50, metal=50, food=20)
           game_state = GameState(colony=colony, resources=resources)
           turret = Turret(initial_position=400, audio_service=game_state.audio)
           enemies = generate_wave(wave_number=1)

           running = True
           while running:
               for event in pygame.event.get():
                   if event.type == pygame.QUIT:
                       running = False
                   elif event.type == pygame.KEYDOWN:
                       if event.key == pygame.K_LEFT:
                           turret.move_left()
                       elif event.key == pygame.K_RIGHT:
                           turret.move_right()
                       elif event.key == pygame.K_SPACE:
                           proj = turret.shoot(enemies)
                           # (Maintain list of projectiles for rendering and collision.)
                       elif event.key == pygame.K_m:
                           # Trigger management phase (can pause the game and show management menu)
                           pass

               # Update enemy positions and other game state details as needed
               # (e.g., moving enemy waves, collision detection, resource collection)

               # Rendering: clear screen, draw turret, enemies, resource status, etc.
               screen.fill((0, 0, 0))
               # Draw turret (e.g., as a rectangle)
               # Draw enemies (e.g., as circles)
               # Overlay text for colony HP and resource levels using pygame.font
               pygame.display.flip()
               clock.tick(60)

           pygame.quit()

       if __name__ == "__main__":
           main()
       -----------------------------------------

2. Integrate Existing Game Logic
   • In game_loop.py, import and instantiate GameState, Turret, and enemy wave generation.
   • Use the existing audio service interface and, if required, create a PygameAudioService wrapper that uses pygame.mixer to play sound clips corresponding to SoundEffect enumerations.
   • Ensure that actions (e.g., turret move, shoot, resource updates) trigger the proper audio feedback as already implemented.

3. Map Keyboard Inputs to Game Actions
   • In the game loop event handling, map:
       - Left/right arrow keys to turret.move_left() and turret.move_right().
       - The space bar to turret.shoot(enemies).
       - A key (e.g., "M") to trigger the management phase interaction.
   • The management phase can be implemented as a paused state (or overlay) using the existing management module and its audio-integrated interface.

4. Render and Update Game State
   • Implement basic rendering for game objects:
       - Use pygame.draw.rect() for the turret.
       - Use pygame.draw.circle() for enemies.
       - Use pygame.font to render text (e.g., current resources, colony health).
   • Update positions and check for collisions each frame.
   • Maintain a consistent frame rate using pygame.Clock.

5. Audio Integration via Pygame
   • Modify (or wrap) the current AudioService or create a new PygameAudioService that:
       - Initializes pygame.mixer.
       - Maps each SoundEffect to an audio file (e.g., "turret_move.wav", "resource_change.wav", etc.).
       - In play_sound() and play_narration(), call pygame.mixer.Sound.play() instead of the no-op stubs.
   • Ensure that audio feedback remains accessible and is triggered together with visual updates.

Integration Overrides:
--------------------------
• Modify cli/__main__.py to call game_loop.main() so that starting the game runs the pygame-based loop.
• Keep the existing CLI logic intact for testing but redirect actual game runs through Pygame.
• Use monkeypatching in tests if necessary to simulate Pygame key events during automated testing.

This plan outlines the precise steps and pseudocode needed to introduce Pygame for rendering and interactivity, ensuring that the game's core logic (already integrated with accessibility via audio cues) will drive real-time visual gameplay.

End of Plan.
