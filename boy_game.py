from pico2d import *
from transitions import Machine
import time
import math


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
        # RUN 전용 애니메이션 스프라이트 시트
        self.run_image = load_image('run_animation.png')
        # idle, sleep, 그리고 run 상태를 정의하고 전이를 설정합니다.
        states = ['idle', 'sleep', 'run']
        transitions = [
            {'trigger': 'sleep', 'source': 'idle', 'dest': 'sleep'},
            {'trigger': 'wake', 'source': 'sleep', 'dest': 'idle'},
            {'trigger': 'run', 'source': ['idle', 'sleep'], 'dest': 'run'},
            {'trigger': 'stop', 'source': 'run', 'dest': 'idle'}
        ]
        # 움직임을 위한 속도 변수 초기화
        self.speed = 5  # 이동 속도 (픽셀 per 프레임)
        self.facing = 1  # 1: 오른쪽, -1: 왼쪽
        self.machine = Machine(model=self, states=states, initial='idle', transitions=transitions, auto_transitions=False)
        # idle 상태 진입 시 타이머 초기화
        self.idle_start_time = time.time()
        self.sleep_tick = 0
    def on_enter_idle(self):
        # idle 상태에 들어갈 때 타이머를 재시작하고 속도 초기화
        self.idle_start_time = time.time()
        self.vx = 0

    def update(self):
        # 상태에 따라 프레임 업데이트와 전환을 수행
        if self.state == 'idle':
            # idle: 정상 속도 애니메이션, 5초 후 sleep 전이
            self.frame = (self.frame + 1) % 8
            if (time.time() - self.idle_start_time) > 5:
                self.sleep()
        elif self.state == 'sleep':
            # sleep: 슬로우 애니메이션 (5번 업데이트마다 프레임 증가)
            self.sleep_tick += 1
            if self.sleep_tick % 5 == 0:
                self.frame = (self.frame + 1) % 8
            # 바닥에 붙어 있으므로 y는 그대로, 이동 없음

        elif self.state == 'run':
            # run: 프레임 업데이트 및 이동
            self.frame = (self.frame + 1) % 8
            self.x += self.vx
            # 화면 경계 클램프
            canvas_w = get_canvas_width()
            if self.x < 0:
                self.x = 0
            elif self.x > canvas_w:
                self.x = canvas_w

    def draw(self):
        # idle와 sleep 은 같은 스프라이트 시트이며, 시트를 4등분(4행)하고 가장 위 행을 사용
        idle_frame_width = self.image.w // 8          # 가정: 한 행에 8 프레임
        idle_frame_height = self.image.h // 4          # 4행 중 하나의 높이 (top row)
        run_frame_width = self.run_image.w // 8
        run_frame_height = self.run_image.h            # run 이미지가 단일 행이라고 가정

        # top row (가장 위) 의 y offset (clip_y) 계산 (pico2d 는 하단 기준)
        idle_y_offset = self.image.h - idle_frame_height

        if self.state == 'idle':
            flip = 'h' if self.facing == -1 else ''
            self.image.clip_composite_draw(
                self.frame * idle_frame_width,
                idle_y_offset,
                idle_frame_width, idle_frame_height,
                0, flip,
                self.x, self.y,
                idle_frame_width, idle_frame_height)
        elif self.state == 'run':
            flip = 'h' if self.facing == -1 else ''
            # run 이미지가 단일 행이라 y 오프셋은 0 사용
            self.run_image.clip_composite_draw(
                self.frame * run_frame_width,
                0,
                run_frame_width, run_frame_height,
                0, flip,
                self.x, self.y,
                run_frame_width, run_frame_height)
        elif self.state == 'sleep':
            flip = 'h' if self.facing == -1 else ''
            self.image.clip_composite_draw(
                self.frame * idle_frame_width,
                idle_y_offset,
                idle_frame_width, idle_frame_height,
                math.radians(90), flip,
                self.x, self.y - 25,
                idle_frame_width, idle_frame_height)



def handle_events():
    global running

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_SPACE:
                boy.wake()
            elif event.key == SDLK_ESCAPE:
                running = False
            elif event.key == SDLK_LEFT:
                boy.facing = -1
                boy.vx = -boy.speed
                if boy.state != 'run':
                    boy.run()
            elif event.key == SDLK_RIGHT:
                boy.facing = 1
                boy.vx = boy.speed
                if boy.state != 'run':
                    boy.run()
        elif event.type == SDL_KEYUP:
            if (event.key == SDLK_LEFT or event.key == SDLK_RIGHT) and boy.state == 'run':
                boy.vx = 0
                boy.stop()


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
