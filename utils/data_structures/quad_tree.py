# External
import pygame

class QuadTree:
    def __init__(self, rect: pygame.rect.FRect, capacity=4) -> None:
        self.rect = rect
        self.capacity = capacity

        self.subdivided = False
        self.elements = list()
        self.children = list()

    def insert(self, point: tuple[float, float], value: any) -> bool:
        if not self.rect.collidepoint(point):
            return False
        
        if len(self.elements) < self.capacity:
            self.elements.append([point, value])
            return True
        
        if not self.subdivided:
            self.subdivide()

        for child in self.children:
            child.insert(point, value)
    
    def subdivide(self) -> None:
        self.subdivided = True

        child_width = self.rect.width / 2
        child_height = self.rect.height / 2

        self.children = [
            QuadTree(rect=pygame.rect.FRect(self.rect.x, self.rect.y, child_width, child_height), capacity=self.capacity),
            QuadTree(rect=pygame.rect.FRect(self.rect.x, self.rect.y + child_height, child_width, child_height), capacity=self.capacity),
            QuadTree(rect=pygame.rect.FRect(self.rect.x + child_width, self.rect.y, child_width, child_height), capacity=self.capacity),
            QuadTree(rect=pygame.rect.FRect(self.rect.x + child_width, self.rect.y + child_height, child_width, child_height), capacity=self.capacity)
        ]

    def query_range(self, rect: pygame.rect.FRect) -> list:
        if not self.rect.colliderect(rect):
            return list()
        
        results = list()
        for element in self.elements:
            if rect.collidepoint(element[0]):
                results.append(element[1])

        if not self.subdivided:
            return results

        for child in self.children:
            results.extend(child.query_range(rect))

        return results