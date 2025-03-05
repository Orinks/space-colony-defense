from typing import List, Optional, Tuple, Any
from cli.game.turret import Turret, Projectile
from cli.game.game_state import GameState, Resources, Colony
from cli.game.enemy_wave import generate_wave, EnemyType, Enemy
from cli.game.audio_service import AudioService, SoundEffect
from cli.game.menu_system import MenuSystem
from cli.game.save_system import save_game, load_game, auto_save, list_save_files, get_save_info
from cli.game.config import save_config, load_config


class GameLoop:
    def __init__(self, audio_service: Optional[AudioService] = None) -> None:
        """Initialize the game loop with all required components"""
        self.audio = audio_service or AudioService()
        self.game_running = False
        self.in_main_menu = True
        
        # Initialize menu system first to load configuration
        self.menu = MenuSystem(None, self.audio)  # Temporarily pass None for game_state
        
        # Now reset the game with the loaded configuration
        self.reset_game()

    def reset_game(self) -> None:
        """Reset the game to its initial state"""
        # Initialize colony and resources
        colony = Colony(hp=100, max_hp=100)
        resources = Resources(energy=50, metal=30, food=20)

        # Create game state
        self.game_state = GameState(
            colony=colony, resources=resources, wave=1, tech_points=0, audio=self.audio
        )

        # Create turret
        self.turret = Turret(
            initial_position=5, screen_width=10, audio_service=self.audio
        )

        # Initialize other game components
        self.enemies: List[Enemy] = []
        self.projectiles: List[Projectile] = []
        
        # Update menu system with the new game state
        if hasattr(self, 'menu'):
            # Preserve the existing menu (and its configuration) if it exists
            self.menu.game_state = self.game_state
        else:
            # Create a new menu system if it doesn't exist yet
            self.menu = MenuSystem(self.game_state, self.audio)
            
        self.is_game_over = False
        self.is_wave_complete = False
        self.is_management_phase = False

        # Show main menu first
        self.menu.show_main_menu()

    def start_game(self) -> None:
        """Start a new game"""
        self.game_running = True
        self.in_main_menu = False
        self.audio.play_narration("New game started. Prepare for Wave 1!")
        self.start_wave()

    def load_saved_game(self, save_path: str) -> bool:
        """Load a game from a save file"""
        loaded_game_state = load_game(save_path)
        if loaded_game_state:
            # Update game state
            self.game_state = loaded_game_state
            self.game_state.audio = self.audio  # Ensure audio service is set
            
            # Update menu with loaded game state
            self.menu.game_state = self.game_state
            
            # Set game running
            self.game_running = True
            self.in_main_menu = False
            self.is_game_over = False
            self.is_wave_complete = False
            self.is_management_phase = True  # Start in management phase
            
            # Announce successful load
            self.audio.play_sound(SoundEffect.ACTION_SUCCESS)
            self.audio.play_narration(f"Game loaded. You are at wave {self.game_state.wave}.")
            self.menu.query_status()
            
            return True
        else:
            # Announce failed load
            self.audio.play_sound(SoundEffect.ACTION_FAIL)
            self.audio.play_narration("Failed to load game.")
            return False

    def start_wave(self) -> None:
        """Start a new wave of enemies"""
        self.enemies = generate_wave(self.game_state.wave)
        self.is_wave_complete = False
        self.is_management_phase = False
        self.audio.play_narration(
            f"Wave {self.game_state.wave} incoming. {len(self.enemies)} enemies detected."
        )

    def update(self) -> None:
        """Update game state for one frame"""
        if self.in_main_menu:
            # Main menu handling is done through input handling
            return

        if not self.game_running:
            return

        if self.is_game_over:
            return

        if self.is_management_phase:
            # Management phase logic handled by menu system
            return

        if self.is_wave_complete:
            self.start_management_phase()
            return

        # Update projectiles
        self.update_projectiles()

        # Update enemies
        self.update_enemies()

        # Check for wave completion
        if len(self.enemies) == 0 and not self.is_wave_complete:
            self.is_wave_complete = True
            self.audio.play_sound(SoundEffect.ACTION_SUCCESS)
            self.audio.play_narration(f"Wave {self.game_state.wave} complete!")
            self.start_management_phase()  # Immediately start management phase

        # Check for game over
        if self.game_state.check_loss():
            self.game_over()

    def update_projectiles(self) -> None:
        """Update all projectiles and check for collisions"""
        active_projectiles: List[Projectile] = []

        for projectile in self.projectiles:
            # In a real game, we'd update projectile position here
            # For now, just check if it has a target
            if projectile.target:
                # Check if the target is still in enemies list
                # We need to use a different approach since we can't directly compare different Enemy types
                target_found = False
                for enemy in self.enemies[:]:
                    # Compare by position/x coordinate instead of direct object comparison
                    if (
                        hasattr(projectile.target, "position")
                        and hasattr(enemy, "x")
                        and projectile.target.position == enemy.x
                    ):
                        # Remove enemy
                        self.enemies.remove(enemy)
                        # Play hit sound
                        self.audio.play_sound(SoundEffect.ENEMY_HIT)
                        # Collect resources from enemy
                        self.game_state.collect_resource(enemy)
                        target_found = True
                        break
                    elif (
                        hasattr(projectile.target, "x")
                        and hasattr(enemy, "x")
                        and projectile.target.x == enemy.x
                    ):
                        # Remove enemy
                        self.enemies.remove(enemy)
                        # Play hit sound
                        self.audio.play_sound(SoundEffect.ENEMY_HIT)
                        # Collect resources from enemy
                        self.game_state.collect_resource(enemy)
                        target_found = True
                        break

                if not target_found:
                    # Keep projectile if target wasn't found (might have been removed already)
                    active_projectiles.append(projectile)
            else:
                # Keep untargeted projectiles alive for visual effect
                active_projectiles.append(projectile)

        self.projectiles = active_projectiles

    def update_enemies(self) -> None:
        """Update enemy positions and check for collisions with turret or base"""
        for enemy in self.enemies[:]:  # Use a copy for safe iteration
            # In a real game, we'd update enemy position here
            # For this simplified version, we'll just simulate random enemy attacks

            # Randomly some enemies might "attack" the turret
            # In a real implementation, this would be position-based
            if enemy.type == EnemyType.ARMORED_SHIP:
                # Apply shield protection if available
                damage = 10
                if self.game_state.shield_strength > 0:
                    absorbed = min(damage, self.game_state.shield_strength)
                    damage -= absorbed
                    self.game_state.shield_strength -= absorbed
                    self.audio.play_narration(f"Shield absorbed {absorbed} damage")
                
                if damage > 0:
                    self.turret.take_damage(damage)

            # If enemy reaches bottom, damage colony
            # In a real implementation, we'd check y position
            if enemy.type == EnemyType.SWARMER:
                # Apply shield protection if available
                damage = 5
                if self.game_state.shield_strength > 0:
                    absorbed = min(damage, self.game_state.shield_strength)
                    damage -= absorbed
                    self.game_state.shield_strength -= absorbed
                    self.audio.play_narration(f"Shield absorbed {absorbed} damage")
                
                if damage > 0:
                    self.game_state.colony.hp -= damage
                    self.audio.play_sound(SoundEffect.ACTION_FAIL)
                    self.audio.play_narration(
                        f"Colony damaged! Health: {self.game_state.colony.hp}"
                    )
                
                self.enemies.remove(enemy)

    def start_management_phase(self) -> None:
        """Start the management phase between waves"""
        self.is_management_phase = True
        
        # Generate resources from buildings
        self.game_state.produce_from_buildings()
        
        # Autosave the game after each wave
        auto_save(self.game_state)
        
        self.audio.play_narration(
            "Management phase. Review your status and prepare for the next wave."
        )
        self.menu.query_status()

    def end_management_phase(self) -> None:
        """End the management phase and start the next wave"""
        self.is_management_phase = False
        self.game_state.wave += 1  # Increment wave number
        self.start_wave()

    def handle_input(self, action: str) -> bool:
        """
        Handle player input
        Returns: True if the game should continue, False if it should exit
        """
        if action == "pause_speech":
            self.audio.pause_speech()
            return True
        elif action == "resume_speech":
            self.audio.resume_speech()
            return True
        elif action == "stop_speech":
            self.audio.stop_speech()
            return True
        elif action == "save_game":
            if self.game_running and not self.is_game_over:
                if save_game(self.game_state):
                    self.audio.play_sound(SoundEffect.ACTION_SUCCESS)
                    self.audio.play_narration("Game saved successfully.")
                else:
                    self.audio.play_sound(SoundEffect.ACTION_FAIL)
                    self.audio.play_narration("Failed to save game.")
            return True
        
        if self.in_main_menu:
            # Main menu input handling
            if action == "up":
                self.menu.navigate_up()
            elif action == "down":
                self.menu.navigate_down()
            elif action == "select":
                result = self.menu.select_current_option()
                if result == "new_game":
                    self.start_game()
                elif result == "load_game":
                    # Show load game menu
                    self.menu.show_load_game_menu()
                elif result == "exit":
                    # Save configuration before exiting
                    self.save_configuration()
                    return False
            elif action.startswith("load_slot_"):
                # Handle load game selection
                try:
                    slot_index = int(action.split("_")[-1])
                    save_files = list_save_files()
                    if 0 <= slot_index < len(save_files):
                        self.load_saved_game(save_files[slot_index])
                except (ValueError, IndexError):
                    self.audio.play_sound(SoundEffect.ACTION_FAIL)
                    self.audio.play_narration("Invalid save slot.")
            return True

        if self.is_game_over:
            if action == "restart":
                self.reset_game()
                self.start_game()
            elif action == "menu":
                self.reset_game()  # This also shows the main menu
            return True

        if self.is_management_phase:
            if action == "end_management":
                self.end_management_phase()
            elif action == "repair":
                self.menu.select_current_option()  # Assuming menu is on repair option
            elif action == "status":
                self.menu.query_status()
            elif action == "up":
                self.menu.navigate_up()
            elif action == "down":
                self.menu.navigate_down()
            elif action == "select":
                self.menu.select_current_option()
            elif action == "build":
                self.menu._show_build_menu()
            elif action == "upgrade":
                self.menu._show_upgrade_options()
            elif action == "skip_wave" and self.game_state.wave_skip_available > 0:
                if self.game_state.skip_waves():
                    self.end_management_phase()
            elif action == "menu":
                self.in_main_menu = True
                self.game_running = False
                self.menu.show_main_menu()
            return True

        # Combat phase controls
        if action == "left":
            self.turret.move_left()
        elif action == "right":
            self.turret.move_right()
        elif action == "shoot":
            projectile = self.turret.shoot(self.enemies)
            self.projectiles.append(projectile)
        elif action == "missile":
            if self.game_state.fire_missile():
                # Clear all enemies on screen (simplified implementation)
                self.enemies.clear()
                self.audio.play_sound(SoundEffect.ACTION_SUCCESS)
                self.audio.play_narration("Missile destroyed all enemies!")
        elif action == "status":
            self.menu.query_status()
        elif action == "menu":
            self.in_main_menu = True
            self.game_running = False
            self.menu.show_main_menu()

        return True  # Continue running

    def game_over(self) -> None:
        """Handle game over state"""
        self.is_game_over = True
        self.audio.play_sound(SoundEffect.ACTION_FAIL)
        self.audio.play_narration(
            f"Game Over! Your colony was destroyed on wave {self.game_state.wave}. You earned {self.game_state.tech_points} tech points."
        )
        
    def save_configuration(self) -> None:
        """Save all configuration settings before exiting"""
        try:
            # Get current configuration
            config = load_config()
            
            # Update audio settings from audio service
            if hasattr(self.audio, 'enable_sounds'):
                config["audio"]["enable_sounds"] = self.audio.enable_sounds
            if hasattr(self.audio, 'enable_narration'):
                config["audio"]["enable_narration"] = self.audio.enable_narration
                
            # Update speech mode from menu system
            if hasattr(self.menu, 'use_running_screen_reader'):
                config["audio"]["use_running_screen_reader"] = self.menu.use_running_screen_reader
                
            # Update difficulty from menu system
            if hasattr(self.menu, 'difficulty_level'):
                config["game"]["difficulty"] = self.menu.difficulty_level
                
            # Save updated configuration
            save_config(config)
            print("Configuration saved on exit")
        except Exception as e:
            print(f"Error saving configuration on exit: {e}")
