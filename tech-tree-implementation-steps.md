# Tech Tree Implementation Plan

## Step 1: Save/Load Functionality for Tech Tree

### Extend Save System
First, add tech tree save/load functions to `cli/game/save_system.py`:

```python
def save_tech_tree(tech_tree: PlayerTechTree, save_path: Optional[str] = None) -> bool:
    """Save tech tree to file"""
    try:
        # Generate save path if not provided
        if save_path is None:
            save_dir = get_save_directory()
            save_path = os.path.join(save_dir, "tech_tree.json")
        
        # Convert tech tree to serializable dictionary
        save_data = {
            "owned_techs": tech_tree.owned_techs,
            "available_points": tech_tree.available_points
        }
        
        # Write to file
        with open(save_path, "w") as f:
            json.dump(save_data, f, indent=2)
            
        print(f"Tech tree saved to {save_path}")
        return True
        
    except Exception as e:
        print(f"Error saving tech tree: {e}")
        return False

def load_tech_tree(save_path: Optional[str] = None) -> Optional[PlayerTechTree]:
    """Load tech tree from file"""
    try:
        # Generate save path if not provided
        if save_path is None:
            save_dir = get_save_directory()
            save_path = os.path.join(save_dir, "tech_tree.json")
        
        # Check if file exists
        if not os.path.exists(save_path):
            print(f"Tech tree file not found: {save_path}")
            return PlayerTechTree()  # Return a new tech tree
        
        # Read save data
        with open(save_path, "r") as f:
            save_data = json.load(f)
        
        # Create tech tree
        tech_tree = PlayerTechTree()
        tech_tree.owned_techs = save_data.get("owned_techs", {})
        tech_tree.available_points = save_data.get("available_points", 0)
        
        # Update tech levels based on owned_techs
        for tech_id, level in tech_tree.owned_techs.items():
            if tech_id in tech_tree.techs:
                tech_tree.techs[tech_id].level = level
        
        print(f"Tech tree loaded from {save_path}")
        return tech_tree
        
    except Exception as e:
        print(f"Error loading tech tree: {e}")
        return PlayerTechTree()  # Return a new tech tree on error
```

### Tests for Save/Load Functionality
Add tests in `tests/test_save_system.py`:

```python
def test_save_load_tech_tree(tmp_path):
    """Test saving and loading tech tree"""
    from cli.game.tech_tree import PlayerTechTree
    from cli.game.save_system import save_tech_tree, load_tech_tree
    
    # Create a tech tree with some purchased techs
    tech_tree = PlayerTechTree()
    tech_tree.available_points = 50
    tech_tree.purchase_tech("reinforced_colony", 50)
    tech_tree.purchase_tech("resource_storage", 50)
    
    # Save tech tree to a temporary file
    save_path = os.path.join(tmp_path, "test_tech_tree.json")
    success = save_tech_tree(tech_tree, save_path)
    
    # Assert save was successful
    assert success is True
    assert os.path.exists(save_path)
    
    # Load tech tree from the temporary file
    loaded_tech_tree = load_tech_tree(save_path)
    
    # Assert loaded tech tree matches the original
    assert loaded_tech_tree is not None
    assert loaded_tech_tree.available_points == 50
    assert "reinforced_colony" in loaded_tech_tree.owned_techs
    assert "resource_storage" in loaded_tech_tree.owned_techs
    assert loaded_tech_tree.techs["reinforced_colony"].level == 1
    assert loaded_tech_tree.techs["resource_storage"].level == 1
```

## Step 2: Integrate Tech Tree with Game Loop

### Update GameLoop Class
Modify `cli/game/game_loop.py` to integrate the tech tree:

```python
def __init__(self, audio_service: Optional[AudioService] = None) -> None:
    """Initialize the game loop with all required components"""
    self.audio = audio_service or AudioService()
    self.game_running = False
    self.in_main_menu = True
    
    # Initialize menu system
    self.menu = MenuSystem(None, self.audio)
    
    # Load tech tree
    from cli.game.tech_tree import PlayerTechTree
    from cli.game.save_system import load_tech_tree
    self.tech_tree = load_tech_tree() or PlayerTechTree()
    
    # Reset the game with the loaded configuration
    self.reset_game()
```

```python
def reset_game(self) -> None:
    # Existing reset_game code...
    
    # Apply tech tree effects to the new game state
    if hasattr(self, 'tech_tree'):
        self.tech_tree.apply_tech_effects(self.game_state)
```

```python
def game_over(self) -> None:
    # Existing game_over code...
    
    # Add earned tech points to the persistent tech tree
    if hasattr(self, 'tech_tree'):
        self.tech_tree.available_points += self.game_state.tech_points
        from cli.game.save_system import save_tech_tree
        save_tech_tree(self.tech_tree)
        
        # Announce total tech points
        self.audio.play_narration(
            f"You now have {self.tech_tree.available_points} total tech points available."
        )
```

### Tests for Game Loop Integration
Add to `tests/test_game_loop.py`:

```python
def test_game_loop_loads_tech_tree():
    """Test that the game loop loads the tech tree on initialization"""
    # Arrange
    from cli.game.tech_tree import PlayerTechTree
    
    # Mock the load_tech_tree function to return a specific tech tree
    mock_tech_tree = PlayerTechTree()
    mock_tech_tree.available_points = 42
    
    with patch('cli.game.game_loop.load_tech_tree', return_value=mock_tech_tree):
        # Act
        game = GameLoop()
        
        # Assert
        assert hasattr(game, 'tech_tree')
        assert game.tech_tree.available_points == 42

def test_game_over_saves_tech_points():
    """Test that game over adds tech points to the tech tree"""
    # Arrange
    audio = MockAudioService()
    game = GameLoop(audio_service=audio)
    game.tech_tree.available_points = 10
    game.game_state.tech_points = 15
    
    with patch('cli.game.game_loop.save_tech_tree') as mock_save:
        # Act
        game.game_over()
        
        # Assert
        assert game.tech_tree.available_points == 25  # 10 + 15
        mock_save.assert_called_once_with(game.tech_tree)
```

## Step 3: Create Tech Tree Menu Interface

### Add to MenuSystem
Update `cli/game/menu_system.py` to add the tech tree menu:

```python
class TechTreeOption(Enum):
    DEFENSE = auto()
    WEAPONS = auto()
    ECONOMY = auto() 
    SPECIAL = auto()
    BACK = auto()
```

```python
def show_tech_tree_menu(self) -> None:
    """Show the tech tree menu"""
    self.current_menu = "tech_tree"
    self.current_index = 0
    self.tech_tree_options = list(TechTreeOption)
    
    # Load tech tree
    from cli.game.save_system import load_tech_tree
    self.tech_tree = load_tech_tree()
    
    self.audio.play_narration(f"Tech Tree. You have {self.tech_tree.available_points} tech points available.")
    self._announce_current_option()
```

```python
def _handle_tech_tree_selection(self) -> Optional[str]:
    """Handle selection in the tech tree menu"""
    option = self.tech_tree_options[self.current_index]
    
    if option == TechTreeOption.BACK:
        self.audio.play_sound(SoundEffect.MENU_NAV)
        self.audio.play_narration("Returning to main menu")
        self.current_menu = "main"
        self.current_index = 0
        return None
        
    # Show category-specific tech upgrades
    category_map = {
        TechTreeOption.DEFENSE: TechCategory.DEFENSE,
        TechTreeOption.WEAPONS: TechCategory.WEAPONS,
        TechTreeOption.ECONOMY: TechCategory.ECONOMY,
        TechTreeOption.SPECIAL: TechCategory.SPECIAL,
    }
    
    if option in category_map:
        self._show_category_techs(category_map[option])
        
    return None
```

```python
def _show_category_techs(self, category: TechCategory) -> None:
    """Show techs in a specific category"""
    self.current_menu = "tech_category"
    self.current_index = 0
    
    # Filter techs by category
    self.category_techs = [
        tech for tech_id, tech in self.tech_tree.techs.items()
        if tech.category == category
    ]
    
    # Add a "Back" option
    self.category_techs.append(None)  # None represents "Back"
    
    self.audio.play_narration(f"{category.name} technologies")
    self._announce_current_tech_option()
```

### Update Select Method
Update the `select_current_option` method in `MenuSystem` to handle tech tree menus:

```python
def select_current_option(self) -> Optional[str]:
    if self.current_menu == "main":
        return self._handle_main_menu_selection()
    elif self.current_menu == "options":
        return self._handle_options_menu_selection()
    elif self.current_menu == "build":
        return self._handle_build_menu_selection()
    elif self.current_menu == "load_game":
        return self._handle_load_game_selection()
    elif self.current_menu == "tech_tree":
        return self._handle_tech_tree_selection()
    elif self.current_menu == "tech_category":
        self._handle_tech_category_selection()
        return None
    else:  # game menu
        self._handle_game_menu_selection()
        return None
```

### Update Main Menu Options
Add the Tech Tree option to the main menu:

```python
class MainMenuOption(Enum):
    NEW_GAME = auto()
    LOAD_GAME = auto()
    TECH_TREE = auto()  # Add this option
    OPTIONS = auto()
    EXIT = auto()
```

Update `_handle_main_menu_selection`:

```python
def _handle_main_menu_selection(self) -> Optional[str]:
    # Existing code...
    elif option == MainMenuOption.TECH_TREE:
        self.audio.play_sound(SoundEffect.MENU_NAV)
        self.audio.play_narration("Tech Tree")
        self.show_tech_tree_menu()
        return None
    # Existing code...
```

### Tests for Tech Tree Menu
Add tests in `tests/test_menu_system.py`:

```python
def test_tech_tree_menu():
    """Test that the tech tree menu displays correctly"""
    # Arrange
    audio = MockAudioService()
    game_state = GameState(
        colony=Colony(hp=100, max_hp=100),
        resources=Resources(energy=50, metal=30, food=20),
        audio=audio
    )
    menu = MenuSystem(game_state, audio)
    menu.show_main_menu()
    
    # Navigate to TECH_TREE option
    while menu.main_menu_options[menu.current_index] != MainMenuOption.TECH_TREE:
        menu.navigate_down()
    
    # Act
    with patch('cli.game.menu_system.load_tech_tree') as mock_load:
        mock_tech_tree = MagicMock()
        mock_tech_tree.available_points = 42
        mock_load.return_value = mock_tech_tree
        
        menu.select_current_option()
    
    # Assert
    assert menu.current_menu == "tech_tree"
    assert any("Tech Tree" in narration for narration in audio.narrations)
    assert any("42 tech points" in narration for narration in audio.narrations)
```

## Step 4: Add Tech Point Acquisition During Gameplay

### Update GameState Class
Modify `cli/game/game_state.py` to add tech point acquisition:

```python
def complete_wave(self) -> None:
    """Award tech points for completing a wave"""
    # More points for higher waves
    points_earned = max(1, self.wave // 3)
    self.tech_points += points_earned
    self.audio.play_narration(f"Wave {self.wave} complete. Gained {points_earned} tech points.")
```

```python
def defeat_boss(self) -> None:
    """Award tech points for defeating boss waves (every 5 waves)"""
    if self.wave % 5 == 0:
        boss_points = self.wave // 2
        self.tech_points += boss_points
        self.audio.play_narration(f"Boss defeated! Gained {boss_points} tech points.")
```

```python
def retreat(self) -> None:
    """Award tech points when player chooses to retreat, but only if they've made progress"""
    # Only award points if player has defeated at least 50% of the wave's enemies
    if self.enemies_defeated_in_current_wave >= self.total_enemies_in_wave // 2:
        points_earned = self.wave // 2
        self.tech_points += points_earned
        self.audio.play_narration(f"Strategic retreat successful. Gained {points_earned} tech points.")
    else:
        self.audio.play_narration("Retreat completed. No tech points earned - not enough enemies defeated.")
```

### Update Game Loop
Modify the wave completion handler in `cli/game/game_loop.py`:

```python
def update(self) -> None:
    # Existing code...
    
    # Check for wave completion
    if len(self.enemies) == 0 and not self.is_wave_complete:
        self.is_wave_complete = True
        self.audio.play_sound(SoundEffect.ACTION_SUCCESS)
        
        # Award tech points for completing the wave
        self.game_state.complete_wave()
        
        # Check if it was a boss wave (every 5 waves)
        if self.game_state.wave % 5 == 0:
            self.game_state.defeat_boss()
            
        self.start_management_phase()  # Start management phase
```

```python
def handle_input(self, action: str) -> bool:
    # Existing code...
    
    # Handle retreat action
    if action == "retreat" and not self.is_wave_complete:
        # Set values for calculation
        self.game_state.total_enemies_in_wave = len(self.initial_enemies)
        self.game_state.enemies_defeated_in_current_wave = self.initial_enemies_count - len(self.enemies)
        
        # Process retreat
        self.game_state.retreat()
        self.is_wave_complete = True
        self.start_management_phase()
        return True
    
    # Existing code...
```

### Update GameState Initialization
Add tracking properties to `GameState` class:

```python
def __init__(self, ...):
    # Existing init code...
    
    # For retreat calculations
    self.total_enemies_in_wave = 0
    self.enemies_defeated_in_current_wave = 0
```

### Tests for Tech Point Acquisition
Add tests to `tests/test_game_state.py`:

```python
def test_tech_points_awarded_for_wave_completion():
    """Test that completing a wave awards tech points"""
    # Arrange
    colony = Colony(hp=100, max_hp=100)
    game_state = GameState(
        colony=colony,
        resources=Resources(energy=50, metal=30, food=20),
        wave=5,
        tech_points=10
    )
    
    # Act
    game_state.complete_wave()
    
    # Assert
    assert game_state.tech_points > 10  # Should have earned some points
    
def test_boss_wave_awards_extra_tech_points():
    """Test that boss waves award extra tech points"""
    # Arrange
    colony = Colony(hp=100, max_hp=100)
    game_state = GameState(
        colony=colony,
        resources=Resources(energy=50, metal=30, food=20),
        wave=5,  # Boss wave
        tech_points=10
    )
    
    # Act
    game_state.defeat_boss()
    
    # Assert
    assert game_state.tech_points > 10  # Should have earned some points
    
def test_successful_retreat_awards_tech_points():
    """Test that retreating after defeating enough enemies awards tech points"""
    # Arrange
    colony = Colony(hp=100, max_hp=100)
    game_state = GameState(
        colony=colony,
        resources=Resources(energy=50, metal=30, food=20),
        wave=4,
        tech_points=10
    )
    game_state.total_enemies_in_wave = 10
    game_state.enemies_defeated_in_current_wave = 6  # 60% defeated
    
    # Act
    game_state.retreat()
    
    # Assert
    assert game_state.tech_points > 10  # Should have earned some points
    
def test_early_retreat_awards_no_tech_points():
    """Test that retreating early awards no tech points"""
    # Arrange
    colony = Colony(hp=100, max_hp=100)
    game_state = GameState(
        colony=colony,
        resources=Resources(energy=50, metal=30, food=20),
        wave=4,
        tech_points=10
    )
    game_state.total_enemies_in_wave = 10
    game_state.enemies_defeated_in_current_wave = 3  # Only 30% defeated
    
    # Act
    game_state.retreat()
    
    # Assert
    assert game_state.tech_points == 10  # Should not have earned points
```
