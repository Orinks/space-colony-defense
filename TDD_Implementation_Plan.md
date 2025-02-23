TDD Implementation Plan for Space Colony Defense
==================================================

Overview
--------
We will develop the core game logic using a Test-Driven Development (TDD) approach. The plan is to write failing tests first (using pytest) that encapsulate the expectations from the Game_Concepts.md and then incrementally implement the minimal code necessary in order to pass those tests. We will refer to the pytest docs (in docs/pytest-docs) for guidance on assertion syntax, test discovery, and advanced test features.

Core Components to Cover
-------------------------
1. Turret Mechanics ✓
   - Movement: Ensure turret moves left/right, honoring screen boundaries. ✓
   - Shooting: Validate that shooting fires a projectile (or logs an action) and automatically targets the closest enemy. ✓
   - Audio cues: Optionally simulate sound triggers on movement or shooting (stub/mock these calls in tests).

2. Enemy Waves Generation ✓
   - Wave Composition: Create tests to verify that, for a given wave number (e.g., Wave 3, Wave 4, etc.), the correct mix of enemy types (Basic Invaders, Armored Ships, Swarmers, Bosses) is generated. ✓
   - Randomization: Simulate randomized aspects (like resource drops and enemy variations) by setting seeds or using mocks to ensure predictable test outcomes. ✓

3. Resource Management & Colony Health
   - Resource Drops: Test that destroying enemies correctly adds resources (energy, metal, food) to the player's count. ✓
   - Building and Upgrades: Verify that spending resources (e.g., repairing the colony or building a solar panel) results in the proper state change.
   - Health: Test both damage on colony and turret (with shield depletion) and resource-based repair actions.

4. Roguelike Structure and Game State
   - Permadeath: Write tests that simulate a colony health reaching zero and verify that the game resets or ends the run.
   - Progressive Difficulty: Test that each wave incrementally increases in difficulty (e.g., enemy speed, count, and special attacks). ✓
   - Meta-Progression: Ensure that victory actions (like "retreating" after a given wave) award the correct number of Tech Points and log information (Galactic Log).

Test Case Outline (Pseudocode Examples)
-----------------------------------------
1. Turret Tests (tests/test_turret.py)
   --------------------------------------------------
   # Pseudocode snippet:
   def test_turret_moves_left():
       # Arrange
       turret = Turret(initial_position=5)
       # Act
       turret.move_left()
       # Assert
       assert turret.position == 4

   def test_turret_shoots_at_nearest_enemy():
       # Arrange: initialize turret and multiple enemies
       turret = Turret(position=5)
       enemy1 = Enemy(position=3)
       enemy2 = Enemy(position=6)
       game_state = GameState(enemies=[enemy1, enemy2])
       # Act
       projectile = turret.shoot(game_state)
       # Assert (example check, ensure projectile has a target and correct direction)
       assert projectile.target in [enemy1, enemy2]

2. Enemy Wave Generation Tests (tests/test_enemy_wave.py)
   --------------------------------------------------
   def test_generate_wave_returns_expected_enemies():
       # Act
       wave = generate_wave(wave_number=3)
       # Assert: expect 10 Basic Invaders and 2 Armored Ships for wave 3 (per Game_Concepts.md example)
       basic_invaders = [enemy for enemy in wave if enemy.type == "Basic Invader"]
       armored_ships = [enemy for enemy in wave if enemy.type == "Armored Ship"]
       assert len(basic_invaders) == 10
       assert len(armored_ships) == 2

3. Resource Management Tests (tests/test_resources.py)
   --------------------------------------------------
   def test_resource_drop_on_enemy_defeat():
       # Arrange: enemy defeat simulation
       game_state = GameState(resources=Resources(energy=0, metal=0, food=0))
       enemy = Enemy(type="Basic Invader", resource_drop=ResourceDrop(energy=10))
       # Act: simulate enemy defeat
       game_state.collect_resource(enemy)
       # Assert
       assert game_state.resources.energy == 10

   def test_repair_colony_action():
       # Arrange: colony with damage and available metal resource
       colony = Colony(hp=80, max_hp=100)
       resources = Resources(metal=20)
       # Act: attempt repair action costing 20 metal to restore health
       repair_success = colony.repair(resources)
       # Assert: colony health is restored and metal is spent
       assert repair_success is True
       assert colony.hp == 100
       assert resources.metal == 0

4. Roguelike and Game State Tests (tests/test_game_state.py)
   --------------------------------------------------
   def test_game_loss_triggers_reset():
       # Arrange: game state with colony health condition at zero
       game_state = GameState(colony=Colony(hp=0))
       # Act: check for loss condition
       is_game_over = game_state.check_loss()
       # Assert
       assert is_game_over is True

   def test_tech_points_award_on_retreat():
       # Arrange: game state after surviving several waves
       game_state = GameState(wave=15)
       initial_tech_points = game_state.tech_points
       # Act: player chooses to retreat 
       game_state.retreat()
       # Assert: tech points have increased based on game performance
       assert game_state.tech_points > initial_tech_points

Test Environment and Execution
--------------------------------
• Place all tests under a dedicated "tests" directory.
• Use pytest for running tests. The project already references the pytest documentation in docs/pytest-docs.
• Run tests using the command:
    $ pytest
• Also run mypy and black to verify type correctness and code style:
    $ mypy cli && black --check cli

General TDD Workflow
--------------------
1. Write a test that defines a new function or improvement.
2. Run pytest; the new test should fail.
3. Write the minimal implementation in the appropriate module (e.g., in a new "game" module or as part of CLI commands) to pass the test.
4. Refactor code if needed while ensuring tests remain passing.
5. Repeat this cycle for each feature as outlined by the game design (Game_Concepts.md).

Additional Considerations
-------------------------
• For audio cues or haptic feedback, abstract the related functionality into separate service classes. Their behavior can be verified by mocks or stub functions in tests.
• If using randomness for enemy waves or resource drops, control randomness (seed or mock random number generators) to allow for predictable outcomes in tests.
• Consider writing integration tests that simulate a sequence of waves and management actions to verify the end-to-end flow of the game.

By following this plan, we ensure that game functionality evolves in a robust and testable manner using a TDD approach.
