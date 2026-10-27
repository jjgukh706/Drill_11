from pico2d import *
from transitions import Machine
import random


# Game object class here

class Grass:
    def __init__(self):
        self.image = load_image('grass.png')

    def draw(self):
        self.image.draw(400, 30)

    def update(self):
        pass

class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.image = load_image('animation_sheet.png')
        # idle 상태만 가지고, 프레임을 반복 재생합니다.
        self.machine = Machine(model=self, states=['idle'], initial='idle', auto_transitions=False)

    def update(self):
        # 프레임을 0~7 사이에서 순환시켜 애니메이션을 재생합니다.
        self.frame = (self.frame + 1) % 8

    def draw(self):
        # 현재 프레임에 해당하는 이미지 영역을 그립니다.
        # Idle 애니메이션은 스프라이트 시트의 가장 위쪽 행에 있습니다.
        # pico2d 이미지 객체는 .h (전체 높이)와 .w (전체 너비)를 가지고 있습니다.
        frame_width = 100
        frame_height = 100
        # 가장 위쪽 행의 하단 좌표는 전체 높이 - 프레임 높이 입니다.
        top_row_bottom = self.image.h - frame_height
        self.image.clip_draw(self.frame * frame_width, top_row_bottom,
                             frame_width, frame_height,
                             self.x, self.y)


def handle_events():
    global running

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False


def reset_world():
    global world
    global boy

    world = []

    grass = Grass()
    world.append(grass)

    boy = Boy()
    world.append(boy)



def update_world():
    for o in world:
        o.update()
    pass


def render_world():
    clear_canvas()
    for o in world:
        o.draw()
    update_canvas()


running = True

open_canvas()
reset_world()
# game loop
while running:
    handle_events()
    update_world()
    render_world()
    delay(0.01)
# finalization code
close_canvas()
