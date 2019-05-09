# -*- coding: utf-8 -*-

import os, sys , pygame
from random import randrange, choice
from pygame.locals import *



def generate():
  return [[choice(spawn_list) for y in xrange(map_h)] for x in xrange(map_w)]

def is_empty():
  for x in surf:
    for y in x:
      if y:
        return False
  return True

def append(x, y):
  global boms
  surf[x][y] += 1
  if surf[x][y] == 5:
    surf[x][y] = 0
    boms += 1
    for a, b in ((0, -1), (0, 1), (-1, 0), (1, 0)):
      bulets.append(
        [x*cell + cell//2 + a*speed, y*cell + cell//2 + b*speed, speed*a, speed*b])

def new_game(next=False):
  global surf, bulets, turns, level, pause, boms
  surf = generate()
  bulets, pause, boms = [], False, 0
  if next:
    level += 1
    turns += 1
  else:
    level, turns = 1, 10

def save_config():
  if not exists(path):
    mkdir(path)
  file = open("config.ini", "w")
  cfg = ConfigParser()
  cfg.add_section("main")
  cfg.set("main", "map_size", map_size_set)
  cfg.set("main", "spawn", spawn_set)
  cfg.write(file)
  file.close()

def load_config(apply=True):
  global map_size_set, spawn_set
  if exists("config.ini"):
    cfg = ConfigParser()
    cfg.read(path+"config.ini")
    map_size_set = eval(cfg.get("main", "map_size"))
    spawn_set = eval(cfg.get("main","spawn"))
    if apply:
      apply_config(False)

def apply_config(save=True):
  global right, bottom, map_w, map_h, cell, r, spawn_list
  map_w, map_h = map_size_set
  cell = (win_h-top*2)//map_h
  r = (cell-4)//8
  right = left+map_w*cell
  bottom = top+map_h*cell
  spawn_list = []
  for k in spawn_set:
    spawn_list += [k]*spawn_set[k]
  new_game()
  if save:
    save_config()

def find_config():
  if exists("config.ini"):
    load_config()

def pause_f():
  global pause
  pause = not pause

def ramka(img, w, h, r, clr1, clr2=0, pos=(0,0), lw=2):
  new = False
  x, y = pos
  if not img:
    bg = clr1[0]//2, clr1[1]//2, clr1[2]//2
    img = pygame.Surface((w, h))
    img.fill(bg)
    new = True
  for cx, cy in ((x+r, y+r), (x+w-r, y+r), (x+w-r, y+h-r), (x+r, y+h-r)):
    pygame.draw.circle(img, clr1, (int(cx), int(cy)), r)
    pygame.draw.circle(img, clr2, (int(cx), int(cy)), r, lw)
  pygame.draw.rect(img, clr1, (x, y+r, w, h-2*r))
  pygame.draw.rect(img, clr1, (x+r, y, w-2*r, h))
  for p1, p2 in ([(x, y+r), (x, y+h-r)], [(x+r, y), (x+w-r, y)],
                 [(x+w-2, y+r), (x+w-2, y+h-r)], [(x+r, y+h-2), (x+w-r, y+h-2)]):
    pygame.draw.line(img, clr2, p1, p2, lw)
  if new:
    img.set_colorkey(bg)
    return img.convert_alpha()

def create_button(rect, text, func):
  img = ramka(None, rect[2], rect[3], 10, (0,255,0))
  text = font.render(text, True, (0,0,0,255))
  trect = text.get_rect()
  trect.center = rect[2]/2, rect[3]/2
  img.blit(text, trect)
  return [pygame.Rect(rect), img, func]

def draw():
  window.fill((255,255,255))
  for x in range(map_w):
    for y in range(map_h):
      px, py = x*cell+left, y*cell+top
      pygame.draw.rect(window, 0, (px, py, cell, cell), 2)
      m = surf[x][y]
      if m:
        pygame.draw.circle(window, (0,255,0), (px+cell//2, py+cell//2), m*r)
        pygame.draw.circle(window, 0, (px+cell//2, py+cell//2), m*r, 1)
  for b in bulets:
    pygame.draw.circle(window, (255,0,0), (b[0]+left, b[1]+top), 4)
  for btn in buttons:
    window.blit(btn[1], btn[0])
  for l in labels:
    text = font.render(l[1]%globals(), True, (0,0,0,255))
    trect = text.get_rect()
    trect.topleft = l[0]
    window.blit(text, trect)
  pygame.display.update()

def event_callback():
  global turns
  for event in pygame.event.get():
    if event.type == QUIT:
      runing = False
    elif event.type == KEYDOWN:
      if event.key == K_ESCAPE:
        runing = False
    elif event.type ==  MOUSEBUTTONUP:
      px, py = event.pos
      if left < px < right and top < py < bottom and not bulets:
        turns -= 1
        append((px-left)//cell, (py-top)//cell)
      for rect, bi, f in buttons:
        if rect.collidepoint(event.pos):
          f()

def main():
  global turns, boms
  while 1:
    event_callback()
    if not pause:
      for b in bulets:
        b[0] += b[2]
        b[1] += b[3]
        if b[0] < speed or b[0] > right-top-speed \
         or b[1] < speed or b[1] > bottom-left-speed:
          bulets.remove(b)
        elif (cell//2-speed < b[0]%cell < cell//2+speed) and (
              cell//2-speed < b[1]%cell < cell//2+speed):
          x, y = b[0]//cell, b[1]//cell
          if surf[x][y]:
            append(x, y)
            bulets.remove(b)
      if not bulets:
        turns += boms//3
        boms = 0
        if not turns:
          new_game()
      if is_empty():
        turns += boms//3
        new_game(True)
    draw()
    clock.tick(60)



global map_w, map_h, cell, r, left, top, right, bottom, surf, spawn_list, bulets, pause, level, turns, boms
sys.stderr = sys.stdout = open('out.txt', 'w')
os.environ['SDL_VIDEO_CENTERED'] = "1"
ru = lambda x: str(x).decode('utf-8')

win_w, win_h = 0, 0
pygame.init()
window = pygame.display.set_mode((win_w, win_h), FULLSCREEN)
win_w, win_h = window.get_size()
pygame.display.set_caption('bubbles')
clock = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf', 30)

top, left = 20, 20
speed = 6
map_size_set = [6, 6]
spawn_set = {0:2, 1:2, 2:2, 3:2, 4:1}
apply_config(False)

buttons = [
    create_button((win_w-250, win_h-300, 200, 50), ru('переиграть'), new_game),
    create_button((win_w-250, win_h-240, 200, 50), ru('пауза'), pause_f)
]
labels = [
   ((right+50, win_h-300), ru("уровень: %(level)i")),
   ((right+50, win_h-240), ru("ходы: %(turns)i")),
   ((right+50, win_h-180), ru("лопнуло: %(boms)i"))]

main()