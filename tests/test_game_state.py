from cli.game.game_state import GameState, Resources, Colony

def test_game_loss_triggers_reset():
    # Arrange
    colony = Colony(hp=0, max_hp=100)
    game_state = GameState(
        colony=colony,
        resources=Resources(energy=0, metal=0, food=0),
        wave=1,
        tech_points=0
    )
    # Act & Assert
    assert game_state.check_loss() is True

def test_tech_points_award_on_retreat():
    # Arrange
    colony = Colony(hp=100, max_hp=100)
    game_state = GameState(
        colony=colony,
        resources=Resources(energy=0, metal=0, food=0),
        wave=15,
        tech_points=5
    )
    initial_tech_points = game_state.tech_points
    # Act
    game_state.retreat()
    # Assert
    assert game_state.tech_points > initial_tech_points
