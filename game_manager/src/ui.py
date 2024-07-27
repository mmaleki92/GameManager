import copy
from typing import Tuple
import pygame
import pygame_gui
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_label import UILabel


class AppStateManager:
    def __init__(self):
        self.states = {}
        self.active_state = None

    def register_state(self, state):
        if state.name not in self.states:
            self.states[state.name] = state

    def run(self, event):
        if self.active_state is not None:
            self.active_state.run(event)

            if self.active_state.time_to_transition:
                self.active_state.time_to_transition = False
                new_state_name = self.active_state.target_state_name
                self.active_state.end()
                outgoing_data_copy = copy.deepcopy(self.active_state.outgoing_transition_data)
                self.active_state = self.states[new_state_name]
                self.active_state.incoming_transition_data = outgoing_data_copy
                self.active_state.start()

            if self.active_state.time_to_quit_app:
                return False

        return True

    def set_initial_state(self, name):
        if name in self.states:
            self.active_state = self.states[name]
            self.active_state.start()

class BaseAppState:
    def __init__(self, name, target_state_name, state_manager):
        self.name = name
        self.target_state_name = target_state_name
        self.outgoing_transition_data = {}
        self.incoming_transition_data = {}
        self.state_manager = state_manager
        self.time_to_transition = False
        self.time_to_quit_app = False

        self.state_manager.register_state(self)

    def set_target_state_name(self, target_name):
        self.target_state_name = target_name

    def trigger_transition(self):
        self.time_to_transition = True

    def start(self):
        pass

    def end(self):
        pass

    def run(self, event):
        pass

class UI(BaseAppState):
    def __init__(self, screen):
        state_manager = AppStateManager()

        super().__init__('creator_ui', 'select_level', state_manager)

        self.elements = {}
        self.bind_dict = {}
        screen_size = screen.get_size()
        
        self.ui_manager = pygame_gui.UIManager(screen_size, "data/ui_theme.json")
        self.ui_manager.preload_fonts([{'name': 'fira_code', 'point_size': 10, 'style': 'bold'},
                                {'name': 'fira_code', 'point_size': 10, 'style': 'regular'},
                                {'name': 'fira_code', 'point_size': 14, 'style': 'bold'}])

        state_manager.set_initial_state('creator_ui')

    def add_button(self, name: str, position: Tuple, size: Tuple, text: str, hover_text: str):
        button = UIButton(pygame.Rect(position, size), text, self.ui_manager, tool_tip_text=hover_text)
        self.elements[name] = button

    def bind_function(self, name: str, function):
        if isinstance(self.bind_dict.get(name), list): 
                self.bind_dict[name].append(function)
        else:
            self.bind_dict[name] = [function]

    def unbind_function(self, name: str, function):
        function_list = self.bind_dict.get(name)

        if function_list:
            if function in function_list:
                function_list.remove(function)

    def end(self):
        for e in self.elements:
            e.kill()

    def run(self, event):
        self.ui_manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for name, function in self.elements.items():
                if event.ui_element == function:
                    for fun in self.bind_dict[name]: 
                        fun()
                    