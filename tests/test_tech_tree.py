import unittest
from unittest.mock import MagicMock, patch
import pytest
from typing import Dict, List, Optional

# Import the modules we're testing
from cli.game.tech_tree import TechCategory, TechUpgrade, PlayerTechTree, TECH_UPGRADES


class TestTechUpgrade(unittest.TestCase):
    """Test the TechUpgrade class functionality"""
    
    def test_init(self):
        """Test that TechUpgrade initializes with correct values"""
        tech = TechUpgrade(
            id="test_tech",
            name="Test Tech",
            description="A test technology",
            category=TechCategory.DEFENSE,
            cost=10,
            max_level=3,
            prerequisites=["prereq1", "prereq2"]
        )
        
        self.assertEqual(tech.id, "test_tech")
        self.assertEqual(tech.name, "Test Tech")
        self.assertEqual(tech.description, "A test technology")
        self.assertEqual(tech.category, TechCategory.DEFENSE)
        self.assertEqual(tech.base_cost, 10)
        self.assertEqual(tech.level, 0)
        self.assertEqual(tech.max_level, 3)
        self.assertEqual(tech.prerequisites, ["prereq1", "prereq2"])
    
    def test_get_cost(self):
        """Test that cost calculation works correctly for different levels"""
        tech = TechUpgrade(
            id="test_tech",
            name="Test Tech",
            description="A test technology",
            category=TechCategory.DEFENSE,
            cost=10
        )
        
        # Cost for level 0 -> 1 should be base_cost * 1
        self.assertEqual(tech.get_cost(0), 10)
        
        # Cost for level 1 -> 2 should be base_cost * 2
        self.assertEqual(tech.get_cost(1), 20)
        
        # Cost for level 2 -> 3 should be base_cost * 3
        self.assertEqual(tech.get_cost(2), 30)
    
    def test_can_purchase_with_sufficient_points(self):
        """Test that can_purchase returns True when player has enough points"""
        tech = TechUpgrade(
            id="test_tech",
            name="Test Tech",
            description="A test technology",
            category=TechCategory.DEFENSE,
            cost=10
        )
        
        # Player has 15 points, tech costs 10
        self.assertTrue(tech.can_purchase({}, 15))
    
    def test_can_purchase_with_insufficient_points(self):
        """Test that can_purchase returns False when player doesn't have enough points"""
        tech = TechUpgrade(
            id="test_tech",
            name="Test Tech",
            description="A test technology",
            category=TechCategory.DEFENSE,
            cost=10
        )
        
        # Player has 5 points, tech costs 10
        self.assertFalse(tech.can_purchase({}, 5))
    
    def test_can_purchase_with_prerequisites_met(self):
        """Test that can_purchase returns True when prerequisites are met"""
        tech = TechUpgrade(
            id="test_tech",
            name="Test Tech",
            description="A test technology",
            category=TechCategory.DEFENSE,
            cost=10,
            prerequisites=["prereq1", "prereq2"]
        )
        
        # Player has all prerequisites
        owned_techs = {"prereq1": 1, "prereq2": 2}
        self.assertTrue(tech.can_purchase(owned_techs, 15))
    
    def test_can_purchase_with_prerequisites_not_met(self):
        """Test that can_purchase returns False when prerequisites are not met"""
        tech = TechUpgrade(
            id="test_tech",
            name="Test Tech",
            description="A test technology",
            category=TechCategory.DEFENSE,
            cost=10,
            prerequisites=["prereq1", "prereq2"]
        )
        
        # Player is missing prereq2
        owned_techs = {"prereq1": 1}
        self.assertFalse(tech.can_purchase(owned_techs, 15))
    
    def test_can_purchase_at_max_level(self):
        """Test that can_purchase returns False when tech is at max level"""
        tech = TechUpgrade(
            id="test_tech",
            name="Test Tech",
            description="A test technology",
            category=TechCategory.DEFENSE,
            cost=10,
            level=3,
            max_level=3
        )
        
        # Tech is already at max level
        self.assertFalse(tech.can_purchase({}, 100))


class TestPlayerTechTree(unittest.TestCase):
    """Test the PlayerTechTree class functionality"""
    
    def test_init(self):
        """Test that PlayerTechTree initializes with correct values"""
        tech_tree = PlayerTechTree()
        
        # Should have all techs from TECH_UPGRADES
        self.assertEqual(len(tech_tree.techs), len(TECH_UPGRADES))
        
        # Should have no owned techs initially
        self.assertEqual(len(tech_tree.owned_techs), 0)
        
        # Should have 0 available points initially
        self.assertEqual(tech_tree.available_points, 0)
    
    def test_purchase_tech_success(self):
        """Test that purchasing a tech works when conditions are met"""
        tech_tree = PlayerTechTree()
        available_points = 20
        
        # Purchase a tech with no prerequisites
        result = tech_tree.purchase_tech("resource_storage", available_points)
        
        self.assertTrue(result)
        self.assertEqual(tech_tree.owned_techs["resource_storage"], 1)
        self.assertEqual(tech_tree.techs["resource_storage"].level, 1)
    
    def test_purchase_tech_failure_insufficient_points(self):
        """Test that purchasing a tech fails when player doesn't have enough points"""
        tech_tree = PlayerTechTree()
        available_points = 2  # Not enough for any tech
        
        # Try to purchase a tech
        result = tech_tree.purchase_tech("resource_storage", available_points)
        
        self.assertFalse(result)
        self.assertEqual(len(tech_tree.owned_techs), 0)
    
    def test_purchase_tech_failure_prerequisites_not_met(self):
        """Test that purchasing a tech fails when prerequisites are not met"""
        tech_tree = PlayerTechTree()
        available_points = 100  # Plenty of points
        
        # Try to purchase a tech with prerequisites
        result = tech_tree.purchase_tech("advanced_shields", available_points)
        
        self.assertFalse(result)
        self.assertEqual(len(tech_tree.owned_techs), 0)
    
    def test_get_available_techs(self):
        """Test that get_available_techs returns correct techs"""
        tech_tree = PlayerTechTree()
        available_points = 10  # Enough for some techs
        
        # Initially, only techs with no prerequisites and cost <= 10 should be available
        available_techs = tech_tree.get_available_techs(available_points)
        
        # Should include resource_storage (cost 5) and rapid_fire (cost 10)
        self.assertIn("resource_storage", available_techs)
        self.assertIn("rapid_fire", available_techs)
        
        # Should not include advanced_shields (has prerequisite) or wave_skip (cost 30)
        self.assertNotIn("advanced_shields", available_techs)
        self.assertNotIn("wave_skip", available_techs)
    
    def test_apply_tech_effects(self):
        """Test that tech effects are correctly applied to game state"""
        tech_tree = PlayerTechTree()
        
        # Mock game state
        game_state = MagicMock()
        game_state.colony = MagicMock()
        game_state.colony.max_hp = 100
        game_state.colony.hp = 100
        game_state.resources = MagicMock()
        game_state.resources.energy = 50
        game_state.resources.metal = 30
        game_state.resources.food = 20
        game_state.wave = 1
        
        # Add some owned techs
        tech_tree.owned_techs = {
            "reinforced_colony": 2,  # Level 2
            "resource_storage": 1,   # Level 1
            "wave_skip": 1           # Level 1
        }
        
        # Update tech levels to match owned_techs
        for tech_id, level in tech_tree.owned_techs.items():
            tech_tree.techs[tech_id].level = level
        
        # Apply tech effects
        tech_tree.apply_tech_effects(game_state)
        
        # Check reinforced_colony effect (2 * 25 = 50 bonus HP)
        self.assertEqual(game_state.colony.max_hp, 150)
        self.assertEqual(game_state.colony.hp, 150)
        
        # Check resource_storage effect (1 * 20 = 20 bonus resources)
        self.assertEqual(game_state.resources.energy, 70)
        self.assertEqual(game_state.resources.metal, 50)
        self.assertEqual(game_state.resources.food, 30)  # food gets half the bonus
        
        # Check wave_skip effect (start at wave 1)
        self.assertEqual(game_state.wave, 1)  # Should remain 1 since max(1, 1) = 1


if __name__ == "__main__":
    unittest.main()
import unittest
from unittest.mock import MagicMock, patch
import pytest
from typing import Dict, List, Optional

# Import the modules we'll be testing
# These imports will be uncommented as we implement the actual modules
# from cli.game.tech_tree import TechCategory, TechUpgrade, PlayerTechTree, TECH_UPGRADES


class TestTechUpgrade(unittest.TestCase):
    """Test the TechUpgrade class functionality"""
    
    def test_init(self):
        """Test that TechUpgrade initializes with correct values"""
        # This test will be implemented when we create the TechUpgrade class
        pass
    
    def test_get_cost(self):
        """Test that cost calculation works correctly for different levels"""
        # This test will be implemented when we create the TechUpgrade class
        pass
    
    def test_can_purchase_with_sufficient_points(self):
        """Test that can_purchase returns True when player has enough points"""
        # This test will be implemented when we create the TechUpgrade class
        pass
    
    def test_can_purchase_with_insufficient_points(self):
        """Test that can_purchase returns False when player doesn't have enough points"""
        # This test will be implemented when we create the TechUpgrade class
        pass
    
    def test_can_purchase_with_prerequisites_met(self):
        """Test that can_purchase returns True when prerequisites are met"""
        # This test will be implemented when we create the TechUpgrade class
        pass
    
    def test_can_purchase_with_prerequisites_not_met(self):
        """Test that can_purchase returns False when prerequisites are not met"""
        # This test will be implemented when we create the TechUpgrade class
        pass
    
    def test_can_purchase_at_max_level(self):
        """Test that can_purchase returns False when tech is at max level"""
        # This test will be implemented when we create the TechUpgrade class
        pass


class TestPlayerTechTree(unittest.TestCase):
    """Test the PlayerTechTree class functionality"""
    
    def test_init(self):
        """Test that PlayerTechTree initializes with correct values"""
        # This test will be implemented when we create the PlayerTechTree class
        pass
    
    def test_purchase_tech_success(self):
        """Test that purchasing a tech works when conditions are met"""
        # This test will be implemented when we create the PlayerTechTree class
        pass
    
    def test_purchase_tech_failure(self):
        """Test that purchasing a tech fails when conditions are not met"""
        # This test will be implemented when we create the PlayerTechTree class
        pass
    
    def test_get_available_techs(self):
        """Test that get_available_techs returns correct techs"""
        # This test will be implemented when we create the PlayerTechTree class
        pass
    
    def test_apply_tech_effects(self):
        """Test that tech effects are correctly applied to game state"""
        # This test will be implemented when we create the PlayerTechTree class
        pass


if __name__ == "__main__":
    unittest.main()
