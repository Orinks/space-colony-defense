import pygame
from typing import Optional, Tuple, List, Callable, Dict, Any
from enum import Enum, auto

class ObjectType(Enum):
    """Types of game objects"""
    BUTTON = auto()
    TURRET = auto()
    ENEMY = auto()
    PROJECTILE = auto()
    BUILDING = auto()
    RESOURCE = auto()
    TEXT = auto()
    BACKGROUND = auto()


class GameObject:
    """Base class for all game objects"""
    
    def __init__(
        self, 
        x: int, 
        y: int, 
        width: int, 
        height: int, 
        object_type: ObjectType
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = object_type
        self.visible = True
        self.active = True
    
    def update(self, dt: float) -> None:
        """Update the object state"""
        pass
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the object to the screen"""
        pass
    
    def contains_point(self, point_x: int, point_y: int) -> bool:
        """Check if the object contains the given point"""
        return (self.x <= point_x <= self.x + self.width and 
                self.y <= point_y <= self.y + self.height)


class Button(GameObject):
    """Interactive button"""
    
    def __init__(
        self, 
        x: int, 
        y: int, 
        width: int, 
        height: int, 
        text: str,
        on_click: Callable[[], None],
        bg_color: Tuple[int, int, int] = (100, 100, 100),
        hover_color: Tuple[int, int, int] = (150, 150, 150),
        text_color: Tuple[int, int, int] = (255, 255, 255),
        font_size: int = 24
    ):
        super().__init__(x, y, width, height, ObjectType.BUTTON)
        self.text = text
        self.on_click = on_click
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False
        self.clicked = False
        self.font = pygame.font.Font(None, font_size)
        
    def update(self, dt: float) -> None:
        """Update button state based on mouse position"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.hovered = self.contains_point(mouse_x, mouse_y)
        
        # Handle click
        if self.hovered and pygame.mouse.get_pressed()[0] and not self.clicked:
            self.clicked = True
            self.on_click()
        elif not pygame.mouse.get_pressed()[0]:
            self.clicked = False
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the button"""
        # Draw button background
        color = self.hover_color if self.hovered else self.bg_color
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        
        # Draw button border
        border_color = (200, 200, 200)
        pygame.draw.rect(screen, border_color, (self.x, self.y, self.width, self.height), 2)
        
        # Draw button text - note: no keyword arguments
        text_surface = self.font.render(self.text, 1, self.text_color)
        text_rect = text_surface.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
        screen.blit(text_surface, text_rect)


class TurretObject(GameObject):
    """Visual representation of the turret"""
    
    def __init__(self, x: int, y: int, width: int, height: int, turret_data: Any):
        super().__init__(x, y, width, height, ObjectType.TURRET)
        self.turret_data = turret_data
        self.color = (0, 255, 0)  # Green turret
        
    def update(self, dt: float) -> None:
        """Update based on turret data"""
        # Update position based on turret_data
        # In a real implementation, we would map the turret's game position to screen coordinates
        pass
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the turret"""
        # Draw the turret base
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Draw the turret cannon
        pygame.draw.rect(
            screen, 
            (0, 200, 0),  # Darker green for cannon
            (self.x + self.width//2 - 5, self.y - 20, 10, 20)
        )


class EnemyObject(GameObject):
    """Visual representation of an enemy"""
    
    def __init__(self, x: int, y: int, width: int, height: int, enemy_data: Any):
        super().__init__(x, y, width, height, ObjectType.ENEMY)
        self.enemy_data = enemy_data
        self.color = (255, 0, 0)  # Red for enemies
        
    def update(self, dt: float) -> None:
        """Update based on enemy data"""
        # Update position based on enemy_data
        # In a real implementation, we would map the enemy's game position to screen coordinates
        pass
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the enemy"""
        # Draw different shapes based on enemy type
        if hasattr(self.enemy_data, 'type'):
            if self.enemy_data.type.name == "SWARMER":
                pygame.draw.circle(screen, self.color, (self.x + self.width//2, self.y + self.height//2), self.width//2)
            elif self.enemy_data.type.name == "DESTROYER":
                pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            elif self.enemy_data.type.name == "ARMORED_SHIP":
                pygame.draw.polygon(screen, self.color, [
                    (self.x + self.width//2, self.y),  # top
                    (self.x + self.width, self.y + self.height),  # bottom right
                    (self.x, self.y + self.height)  # bottom left
                ])
            else:
                # Default enemy shape
                pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        else:
            # Default enemy shape
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))


class ProjectileObject(GameObject):
    """Visual representation of a projectile"""
    
    def __init__(self, x: int, y: int, projectile_data: Any):
        super().__init__(x, y, 6, 6, ObjectType.PROJECTILE)
        self.projectile_data = projectile_data
        self.color = (255, 255, 0)  # Yellow for projectiles
        
    def update(self, dt: float) -> None:
        """Update based on projectile data"""
        # Update position based on projectile_data
        # In a real implementation, we would map the projectile's game position to screen coordinates
        pass
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the projectile"""
        pygame.draw.circle(screen, self.color, (self.x, self.y), 3)


class BuildingObject(GameObject):
    """Visual representation of a building"""
    
    def __init__(self, x: int, y: int, width: int, height: int, building_data: Any):
        super().__init__(x, y, width, height, ObjectType.BUILDING)
        self.building_data = building_data
        self.color = (0, 0, 255)  # Blue for buildings
        
    def update(self, dt: float) -> None:
        """Update based on building data"""
        pass
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the building"""
        # Draw building with different colors based on type
        if hasattr(self.building_data, 'type'):
            if self.building_data.type.name == "SOLAR_PANEL":
                color = (100, 100, 255)  # Light blue
            elif self.building_data.type.name == "HYDROPONIC_FARM":
                color = (0, 255, 0)  # Green
            elif self.building_data.type.name == "SCRAP_FORGE":
                color = (150, 75, 0)  # Brown
            elif self.building_data.type.name == "SHIELD_GENERATOR":
                color = (255, 0, 255)  # Purple
            elif self.building_data.type.name == "RESEARCH_LAB":
                color = (255, 255, 255)  # White
            else:
                color = self.color
        else:
            color = self.color
        
        # Draw the building
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        
        # Draw building level indicator
        if hasattr(self.building_data, 'level'):
            level = self.building_data.level.value
            for i in range(level):
                pygame.draw.rect(
                    screen, 
                    (255, 255, 0),  # Yellow indicators
                    (self.x + 5 + i*10, self.y + self.height - 10, 5, 5)
                )


class TextObject(GameObject):
    """Text display object"""
    
    def __init__(
        self, 
        x: int, 
        y: int, 
        text: str,
        color: Tuple[int, int, int] = (255, 255, 255),
        font_size: int = 24,
        centered: bool = False
    ):
        # Set initial width and height to 0, will be updated when text is set
        super().__init__(x, y, 0, 0, ObjectType.TEXT)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, font_size)
        self.centered = centered
        self._update_text_surface()
        
    def _update_text_surface(self) -> None:
        """Update the text surface"""
        # No keyword arguments for font.render()
        self.text_surface = self.font.render(self.text, 1, self.color)
        self.width = self.text_surface.get_width()
        self.height = self.text_surface.get_height()
        
    def set_text(self, text: str) -> None:
        """Set the text content"""
        self.text = text
        self._update_text_surface()
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the text"""
        if self.centered:
            text_rect = self.text_surface.get_rect(center=(self.x, self.y))
            screen.blit(self.text_surface, text_rect)
        else:
            screen.blit(self.text_surface, (self.x, self.y))


class GameObjectManager:
    """Manages all game objects"""
    
    def __init__(self):
        self.objects: List[GameObject] = []
        
    def add_object(self, obj: GameObject) -> None:
        """Add an object to the manager"""
        self.objects.append(obj)
    
    def remove_object(self, obj: GameObject) -> None:
        """Remove an object from the manager"""
        if obj in self.objects:
            self.objects.remove(obj)
    
    def remove_object_by_type(self, object_type: ObjectType) -> None:
        """Remove all objects of a specific type"""
        self.objects = [obj for obj in self.objects if obj.type != object_type]
    
    def clear(self) -> None:
        """Remove all objects"""
        self.objects.clear()
    
    def get_objects_by_type(self, object_type: ObjectType) -> List[GameObject]:
        """Get all objects of a specific type"""
        return [obj for obj in self.objects if obj.type == object_type]
    
    def update(self, dt: float) -> None:
        """Update all objects"""
        for obj in self.objects:
            if obj.active:
                obj.update(dt)
    
    def render(self, screen: pygame.Surface) -> None:
        """Render all objects"""
        # Sort objects by type to ensure proper rendering order
        sorted_objects = sorted(self.objects, key=lambda obj: obj.type.value)
        
        for obj in sorted_objects:
            if obj.visible:
                obj.render(screen)
