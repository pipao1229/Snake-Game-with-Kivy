from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.button import Button
from kivy.uix.label import Label
from random import randint

# Main Snake game logic
class SnakeGame(Widget):
    def __init__(self, update_score_callback, game_over_callback, **kwargs):
        super().__init__(**kwargs)
        self.grid_size = 20  # Size of each grid cell
        # Center the snake's initial position on the grid
        start_x = (Window.width // self.grid_size // 2) * self.grid_size
        start_y = (Window.height // self.grid_size // 2) * self.grid_size
        self.snake_pos = [(start_x, start_y)]  # Initial position of the snake
        self.food_pos = [0, 0]  # Initial position of the food
        self.score = 0  # Initial score
        self.direction = Vector(0, 0)  # Snake's movement direction
        self.speed = self.grid_size  # Speed of the snake (aligned with grid size)
        self.update_score_callback = update_score_callback  # Callback to update score
        self.game_over_callback = game_over_callback  # Callback for game over
        self.game_active = True  # Status to control game activity

        self.setup_keyboard()  # Setup keyboard input
        self.spawn_food()  # Generate the first food item
        Clock.schedule_interval(self.move_snake, 1.0 / 10.0)  # Schedule snake movement
        self.bind(size=self._update_canvas)
        self.bind(pos=self._update_canvas)
        Clock.schedule_once(self._update_canvas, 0)

    # Setup keyboard controls
    def setup_keyboard(self):
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)

    # Update the game canvas (drawing elements)
    def _update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Background
            Color(0.1, 0.1, 0.1)
            Rectangle(pos=self.pos, size=self.size)
            
            # Draw snake head
            Color(0, 1, 0)
            Rectangle(pos=self.snake_pos[0], size=(self.grid_size, self.grid_size))
            
            # Snake eyes
            Color(0, 0, 0)
            head_x, head_y = self.snake_pos[0]
            Ellipse(pos=(head_x + self.grid_size / 7, head_y + self.grid_size / 1.5), 
                    size=(self.grid_size / 4, self.grid_size / 4))
            Ellipse(pos=(head_x + self.grid_size / 1.6, head_y + self.grid_size / 1.5), 
                    size=(self.grid_size / 4, self.grid_size / 4))
            
            # Snake body
            Color(0, 0.8, 0)
            for pos in self.snake_pos[1:]:
                Rectangle(pos=pos, size=(self.grid_size, self.grid_size))
            
            # Food
            Color(1, 0, 0)
            Rectangle(pos=self.food_pos, size=(self.grid_size, self.grid_size))

    # Spawn food at a random position aligned with the grid
    def spawn_food(self):
        max_x = (Window.width - self.grid_size) // self.grid_size
        max_y = (Window.height - self.grid_size) // self.grid_size
        
        # Generate random food position aligned with the grid
        x = randint(0, max_x) * self.grid_size
        y = randint(0, max_y) * self.grid_size
        
        # Ensure food does not spawn on the snake
        while (x, y) in self.snake_pos:
            x = randint(0, max_x) * self.grid_size
            y = randint(0, max_y) * self.grid_size
            
        self.food_pos = [x, y]

    # Move the snake based on current direction and check for collisions
    def move_snake(self, dt):
        if not self.game_active or self.direction == Vector(0, 0):
            return

        x, y = self.snake_pos[0]
        new_x = x + self.direction[0] * self.speed
        new_y = y + self.direction[1] * self.speed

        # Check if the snake hits the boundaries of the window
        if (new_x < 0 or new_x > Window.width - 15 or 
            new_y < 0 or new_y > Window.height - 15):
            self.game_over()
            return False
        
        # Check if the snake collides with itself
        if (new_x, new_y) in self.snake_pos[1:]:
            self.game_over()
            return False

        self.snake_pos.insert(0, (new_x, new_y))  # Add new position to the head
        
        # Check if the snake eats the food
        if (new_x == self.food_pos[0] and new_y == self.food_pos[1]):
            self.score += 1
            self.update_score_callback(self.score)
            self.spawn_food()  # Generate new food
        else:
            self.snake_pos.pop()  # Remove tail if no food eaten

        self._update_canvas()

    # Handle game over scenario
    def game_over(self):
        self.game_active = False
        self.direction = Vector(0, 0)
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard = None
        self.game_over_callback()

    # Handle closing the keyboard
    def _on_keyboard_closed(self):
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard = None

    # Handle keyboard input for controlling the snake's direction
    def _on_key_down(self, keyboard, keycode, text, modifiers):
        if not self.game_active:
            return
        
        if keycode[1] == 'up' and self.direction != Vector(0, -1):
            self.direction = Vector(0, 1)
        elif keycode[1] == 'down' and self.direction != Vector(0, 1):
            self.direction = Vector(0, -1)
        elif keycode[1] == 'left' and self.direction != Vector(1, 0):
            self.direction = Vector(-1, 0)
        elif keycode[1] == 'right' and self.direction != Vector(-1, 0):
            self.direction = Vector(1, 0)

    # Reset the game state
    def reset(self):
        start_x = (Window.width // self.grid_size // 2) * self.grid_size
        start_y = (Window.height // self.grid_size // 2) * self.grid_size
        self.snake_pos = [(start_x, start_y)]
        self.score = 0
        self.direction = Vector(0, 0)
        self.game_active = True
        
        self.spawn_food()
        
        if not self._keyboard:
            self.setup_keyboard()
        
        Clock.unschedule(self.move_snake)
        Clock.schedule_interval(self.move_snake, 1.0 / 10.0)
        
        self._update_canvas()

# UI for the Snake game app
class SnakeAppUI(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.snake_game = SnakeGame(self.update_score, self.show_game_over)
        self.add_widget(self.snake_game)
        self.score_label = Label(
            text='Score: 0',
            size_hint=(None, None),
            size=(200, 40),
            pos_hint={'x': 0.02, 'top': 0.98},
            color=(1, 1, 1, 1)
        )
        self.add_widget(self.score_label)
        self.restart_button = Button(
            text='Play Again',
            size_hint=(None, None),
            size=(120, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            on_press=self.restart_game,
            opacity=0  # Hidden until game over
        )
        self.add_widget(self.restart_button)

    # Update the score display
    def update_score(self, score):
        self.score_label.text = f'Score: {score}'

    # Show game over UI
    def show_game_over(self):
        self.restart_button.opacity = 1

    # Restart the game
    def restart_game(self, instance):
        self.restart_button.opacity = 0
        self.snake_game.reset()
        self.update_score(0)

# Main application class
class SnakeApp(App):
    def build(self):
        return SnakeAppUI()

if __name__ == '__main__':
    SnakeApp().run()
