from gridlab.entity import Entity

DESCRIPTION_TEMPLATE_MAP = {
    Entity.PLAYER: 'You are at ({pos.x}, {pos.y})',
    Entity.GOAL: 'A goal is at ({pos.x}, {pos.y})',
    Entity.KEY: 'A key is at ({pos.x}, {pos.y})',
    Entity.TIMER_RESET: 'A timer reset is at ({pos.x}, {pos.y})',
    Entity.ENEMY: 'A enemy is at ({pos.x}, {pos.y})',
    Entity.WALL: 'A wall is at ({pos.x}, {pos.y})',
    Entity.BLOCK: 'A block is at ({pos.x}, {pos.y})',
    Entity.DOOR: 'A door is at ({pos.x}, {pos.y})',
    Entity.SPIKE: 'A spike is at ({pos.x}, {pos.y})',
    Entity.GOAL_REACHED: 'The player reached the goal at ({pos.x}, {pos.y})',
    Entity.PLAYER_DIED: 'The player died at ({pos.x}, {pos.y})',
}
