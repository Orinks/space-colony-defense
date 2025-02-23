from typing import List
import pytest
from cli.game.enemy_wave import (
    generate_wave,
    Enemy,
    EnemyType,
    ResourceType,
    ResourceDrop
)

def test_generate_wave_returns_expected_enemies():
    # Act
    wave = generate_wave(wave_number=3)
    
    # Assert: expect 10 Basic Invaders and 2 Armored Ships for wave 3
    basic_invaders = [enemy for enemy in wave if enemy.type == EnemyType.BASIC_INVADER]
    armored_ships = [enemy for enemy in wave if enemy.type == EnemyType.ARMORED_SHIP]
    
    assert len(basic_invaders) == 10
    assert len(armored_ships) == 2

def test_wave_enemies_start_at_top():
    # Act
    wave = generate_wave(wave_number=1)
    
    # Assert all enemies start at y=0 (top of screen)
    assert all(enemy.y == 0 for enemy in wave)
    # Assert enemies are spread across x-axis
    x_positions = [enemy.x for enemy in wave]
    assert len(set(x_positions)) == len(wave)  # All x positions should be unique

def test_wave_1_has_basic_invaders_only():
    wave = generate_wave(wave_number=1)
    assert len(wave) == 5
    assert all(enemy.type == EnemyType.BASIC_INVADER for enemy in wave)

def test_wave_5_introduces_swarmers():
    wave = generate_wave(wave_number=5)
    
    basic_invaders = [e for e in wave if e.type == EnemyType.BASIC_INVADER]
    swarmers = [e for e in wave if e.type == EnemyType.SWARMER]
    
    assert len(basic_invaders) >= 8
    assert len(swarmers) >= 3  # Introduce some swarmers in wave 5

def test_wave_10_has_all_enemy_types():
    wave = generate_wave(wave_number=10)
    
    enemy_types = {enemy.type for enemy in wave}
    assert enemy_types == {
        EnemyType.BASIC_INVADER,
        EnemyType.ARMORED_SHIP,
        EnemyType.SWARMER
    }

def test_basic_invader_drops_energy():
    enemy = Enemy(type=EnemyType.BASIC_INVADER, x=0)
    resource = enemy.get_resource_drop()
    assert resource is not None
    assert resource.type == ResourceType.ENERGY
    assert resource.amount == 10

def test_armored_ship_drops_metal():
    enemy = Enemy(type=EnemyType.ARMORED_SHIP, x=0)
    resource = enemy.get_resource_drop()
    assert resource is not None
    assert resource.type == ResourceType.METAL
    assert resource.amount == 15

def test_swarmer_drops_food():
    enemy = Enemy(type=EnemyType.SWARMER, x=0)
    resource = enemy.get_resource_drop()
    assert resource is not None
    assert resource.type == ResourceType.FOOD
    assert resource.amount == 5

def test_custom_resource_drop_overrides_default():
    custom_drop = ResourceDrop(ResourceType.ENERGY, 50)
    enemy = Enemy(type=EnemyType.ARMORED_SHIP, x=0, resource_drop=custom_drop)
    resource = enemy.get_resource_drop()
    assert resource == custom_drop

def test_later_waves_have_more_enemies():
    wave1 = generate_wave(wave_number=1)
    wave15 = generate_wave(wave_number=15)
    assert len(wave15) > len(wave1)

def test_later_waves_have_stronger_enemies():
    wave1 = generate_wave(wave_number=1)
    wave20 = generate_wave(wave_number=20)
    
    # Wave 1 should only have basic invaders
    assert all(e.type == EnemyType.BASIC_INVADER for e in wave1)
    
    # Wave 20 should have some armored ships or swarmers
    stronger_enemies = [e for e in wave20 if e.type != EnemyType.BASIC_INVADER]
    assert len(stronger_enemies) > 0

def test_wave_difficulty_scales():
    wave5 = generate_wave(wave_number=5)
    wave15 = generate_wave(wave_number=15)
    wave25 = generate_wave(wave_number=25)
    
    # Each wave should be larger than the last
    assert len(wave25) > len(wave15) > len(wave5)
