# -*- coding: utf-8 -*-

from appuifw import app, Canvas, query
from graphics import Image
from e32 import ao_sleep
from random import randrange as rnd, choice
from os import mkdir
from os.path import exists
from ConfigParser import ConfigParser
import sys



def generate():
  return [[choice(spawn_list) for y in xrange(map_h)] for x in xrange(map_w)]

def is_empty():
  for x in map:
    for y in x:
      if y:
        return False
  return True

def append(x, y):
  global boms
  map[x][y] += 1
  if map[x][y] == 5:
    map[x][y] = 0
    boms += 1
    for a, b in ((0, -1), (0, 1), (-1, 0), (1, 0)):
      bulets.append(
        [x*cell_width+cell_center+a, y*cell_width+cell_center+b, speed*a, speed*b])

def new_game(next=False):
  global map, bulets, turns, level, pause
  map = generate()
  bulets, pause = [], False
  if next:
    level += 1
    turns += 1
  else:
    level, turns = 1, 10

def save_config():
  if not exists(path):
    mkdir(path)
  file = open(path+"config.ini", "w")
  cfg = ConfigParser()
  cfg.add_section("main")
  cfg.set("main", "map_size", map_size_set)
  cfg.set("main", "spawn", spawn_set)
  cfg.write(file)
  file.close()

def load_config(apply=True):
  global map_size_set, spawn_set
  if exists(path+"config.ini"):
    cfg = ConfigParser()
    cfg.read(path+"config.ini")
    map_size_set = eval(cfg.get("main", "map_size"))
    spawn_set = eval(cfg.get("main","spawn"))
    if apply:
      apply_config(False)

def apply_config(save=True):
  global left, top, right, bottom, map_w, map_h, cell_width, cell_center, r, spawn_list
  map_w, map_h = map_size_set
  cell_width = 360//map_w
  cell_center = cell_width//2
  r = cell_width//8
  top = (500-map_h*cell_width)//2
  left = (360-map_w*cell_width)//2
  right = left+map_w*cell_width
  bottom = top+map_h*cell_width
  spawn_list = []
  for k in spawn_set:
    spawn_list += [k]*spawn_set[k]
  new_game()
  if save:
    save_config()

def find_config():
  if exists(path+"config.ini"):
    load_config()

def save_game(slot=1):
  if not exists(path):
    mkdir(path)
  file = open(path+"%i.save"%slot, "w")
  cfg = ConfigParser()
  cfg.add_section("config")
  cfg.add_section("save")
  cfg.set("config", "map_size", map_size_set)
  cfg.set("config", "spawn", spawn_set)
  cfg.set("save", "map", map)
  cfg.set("save", "level", level)
  cfg.set("save", "turns", turns)
  cfg.write(file)
  file.close()

def load_game(slot=1):
  global map_size_set, spawn_set, map, level, turns
  if exists(path+"%i.save"%slot):
    cfg = ConfigParser()
    cfg.read(path+"%i.save"%slot)
    map_size_set = eval(cfg.get("config", "map_size"))
    spawn_set = eval(cfg.get("config","spawn"))
    apply_config(False)
    map = eval(cfg.get("save", "map"))
    level = cfg.getint("save", "level")
    turns = cfg.getint("save", "turns")

def get_saves():
  slots = [None]*5
  cfg = ConfigParser()
  for n in range(1, 6):
    if exists(path+"%i.save"%n):
      cfg.read(path+"%i.save"%n)
      l = cfg.getint("save", "level")
      t = cfg.getint("save", "turns")
      slots[n-1] = (l, t)
  return slots

def query_slot(f):
  global window_query_slot
  slots = get_saves()
  buttons = []
  for n in range(5):
    rect = (40, 70+n*45, 240, 110+n*45)
    text = ru("пусто")
    if slots[n]:
      text = ru("%i lvl %i turns"%slots[n])
    buttons.append(
        (rect, lambda a=n: f(a+1) or hide_win(), text))
  window_query_slot[4] = [window_query_slot[4][0]]+buttons
  for b in window_query_slot[4]:
    draw_button(b[0], b[2], window_query_slot[2])
  show_win(window_query_slot)

def open_settings():
  global screen
  screen = settings_img
  hide_win()
  draw()
  draw_settings()

def back():
  global screen
  screen = game_img

def pause_f():
  global pause
  if bulets:
    pause = not pause

def show_win(win):
  global window
  hide_win()
  draw()
  window = win
  screen.blit(window[2], target=window[0], mask=window[3])

def hide_win():
  global window
  window = None

def quit():
  global run
  run = False

def edit_spawn(n, plus):
  global spawn_set
  if plus is None:
    return spawn_set[n]
  if plus and spawn_set[n] < 5:
    spawn_set[n] += 1
  elif not plus and spawn_set[n] > 0:
    spawn_set[n] -= 1

def edit_map_size(n, plus):
  global map_size_set
  k = 360.0/500.0
  if plus is None:
    return map_size_set[n]
  if plus:
    if n == 0 and map_size_set[n] < 20:
      map_size_set[n] += 1
    elif float(map_size_set[0])/float(map_size_set[1]+1) > k:
      map_size_set[1] += 1
  elif not plus and map_size_set[n] > 1:
    map_size_set[n] -= 1
    if n == 0 and float(map_size_set[0])/float(map_size_set[1]) <= 0.75:
        map_size_set[1] = int(map_size_set[0]/k)

def ramka(coords, d, clr, clr2, img):
  x, y, x2, y2 = coords
  r = d/2
  img.ellipse((x, y, x+d, y+d), clr2, clr, 2)
  img.ellipse((x2-d, y, x2, y+d), clr2, clr, 2)
  img.ellipse((x, y2-d, x+d, y2), clr2, clr, 2)
  img.ellipse((x2-d, y2-d, x2, y2), clr2, clr, 2)
  img.rectangle((x, y+r, x2, y2-r), clr, clr)
  img.rectangle((x+r, y, x2-r, y2), clr, clr)
  img.line((x+r, y, x2-r, y), clr2, 0, 2)
  img.line((x+r, y2-1, x2-r, y2-1), clr2, 0, 2)
  img.line((x, y+r, x, y2-r), clr2, 0, 2)
  img.line((x2-1, y+r, x2-1, y2-r), clr2, 0, 2)

def draw_button(coords, text, img, clr1=0xff00, clr2=0, textclr=0xff0000):
  ramka(coords, 20, clr1, clr2, img)
  draw_label(coords, text, img, textclr)

def draw_label(coords, text, img, color=0):
  x1, y1, x2, y2 = coords
  for font in ("title", "normal", "dense", "annotation"):
    size = img.measure_text(text, font)
    w, h = size[1], -size[0][1]
    if w >= x2-x1-5:
      continue
    x = x1+(x2-x1-w)//2
    y = y1+(y2-y1+h)//2
    img.text((x, y), text, color, font)
    break

def init_img():
  for b in buttons:
    draw_button(b[0], b[2], game_img)
  for b in buttons_settings:
    draw_button(b[0], b[2], settings_img)
  for b in buttons_settings_v:
    x1, y1, s, w, h = b[0]
    draw_button((x1, y1, x1+w, y1+h), u"-", settings_img)
    draw_button((x1+s+w, y1, x1+s+w*2, y1+h), u"+", settings_img)
  draw_button((0, 5, 360, 45), ru("настройки генератора"), settings_img, 0xffffff, 0xffffff, 0)
  draw_button((0, 60, 360, 50), ru("вероятность спавна"), settings_img, 0xffffff, 0xffffff, 0)
  for x, y, r in ((30, 80, 0), (150, 80, 7), (270, 80, 15), (60, 210, 22), (240, 210, 28)):
    settings_img.rectangle((x, y, x+60, y+60), 0, width=2)
    settings_img.ellipse((x+30-r, y+30-r, x+30+r, y+30+r), 0, 0xff00)
  draw_button((0, 340, 360, 380), ru("размер карты"), settings_img, 0xffffff, 0xffffff, 0)
  
  for w in (window_win, window_lose, window_query_exit,
                  window_query_slot, menu):
    w.insert(2, Image.new(w[1]))
    w.insert(3, Image.new(w[1], "1"))
    ramka((5, 5)+(w[1][0]-5, w[1][1]-5), 100, 0xff0000, 0, w[2])
    ramka((15, 15)+(w[1][0]-15, w[1][1]-15), 100, 0xffffff, 0, w[2])
    w[3].clear(0)
    ramka((5, 5)+(w[1][0]-5, w[1][1]-5), 100, 0xffffff, 0xffffff, w[3])
    for b in w[4]:
      draw_button(b[0], b[2], w[2])
    for l in w[5]:
      draw_label(l[0], l[1], w[2], l[2])

def event(e):
  global turns, window
  if e["type"] == 258:
    px, py = e["pos"]
    if window:
      px, py = px-window[0][0], py-window[0][1]
      for b in window[4]:
        x1, y1, x2, y2 = b[0]
        if x1<=px<=x2 and y1<=py<=y2:
          b[1]()
    elif screen == game_img:
      if left < px < right and top < py < bottom and not bulets:
        turns -= 1
        append((px-left)//cell_width, (py-top)//cell_width)
      else:
        for b in buttons:
          x1, y1, x2, y2 = b[0]
          if x1<=px<=x2 and y1<=py<=y2:
            b[1]()
    elif screen == settings_img:
      for b in buttons_settings:
        x1, y1, x2, y2 = b[0]
        if x1<=px<=x2 and y1<=py<=y2:
          b[1]()
      for b in buttons_settings_v:
        x1, y1, s, w, h = b[0]
        if x1<= px <=x1+w and y1<= py <=y1+h:
          b[1](False)
        elif x1+w+s<=px<=x1+w*2+s and y1<=py<=y1+h:
          b[1](True)
      draw_settings()

def draw():
  game_img.rectangle((0, 0, 360, 500), 0xffffff, 0xffffff)
  for x in xrange(map_w):
    for y in xrange(map_h):
      game_img.rectangle((x*cell_width+left, y*cell_width+top, (x+1)*cell_width+left, (y+1)*cell_width+top), 0)
      m = map[x][y]*r
      if m:
        cx, cy = (x+0.5)*cell_width+left, (y+0.5)*cell_width+top
        game_img.ellipse((cx-m, cy-m, cx+m, cy+m), 0, 0xff00)
  for b in bulets:
    game_img.ellipse((b[0]-3+left, b[1]-3+top, b[0]+3+left, b[1]+3+top), 0xff0000, 0xff00)
  game_img.rectangle((0, bottom, 200, 640), 0xffffff, 0xffffff)
  for x, y, l in labels:
    game_img.text((x, y), l%globals(), 0xff, "title")
  redraw()

def draw_settings():
  for b in buttons_settings_v:
    x1, y1, s, w, h = b[0]
    draw_button((x1+w+2, y1, x1+w+s-2, y1+h), ru(b[1](None)), settings_img, 0xffffff, 0xffffff, 0)
  redraw()

def main():
  global turns, boms, bulets, window
  while run:
    if window or pause or screen == settings_img:
      redraw()
      ao_sleep(0.02)
      continue
    for b in bulets:
      b[0] += b[2]
      b[1] += b[3]
      if b[0] <= 0 or b[0] >= map_w*cell_width or b[1] <= 0 or b[1] >= map_h*cell_width:
        try:
          bulets.remove(b)
        except:
          pass
      elif (cell_center-speed < b[0]%cell_width < cell_center+speed) and (
              cell_center-speed < b[1]%cell_width < cell_center+speed):
        x, y = b[0]//cell_width, b[1]//cell_width
        if map[x][y]:
          append(x, y)
          try:
            bulets.remove(b)
          except:
            pass
    if not bulets:
      if boms:
        turns += boms//3
        boms = 0
      if not turns:
        show_win(window_lose)
    if is_empty():
      show_win(window_win)
    if not  window:
      draw()
    ao_sleep(0.02)



redraw = lambda x=0: c.blit(screen)
game_img = Image.new((360, 640))
settings_img = Image.new((360, 640))
screen, window = game_img, None
c = Canvas(redraw, event)
app.directional_pad = False
app.screen = "full"
app.body = c

global map_w, map_h, cell_width, cell_center, r, left, top, right, bottom, map, spawn_list
ru = lambda x: str(x).decode("utf-8")
path = "e:\\python\\bubbles\\"
run, pause = True, False
bulets, turns, boms = [], 10, 0
speed, level = 6, 1
map_size_set = [6, 6]
spawn_set = {0:2, 1:2, 2:2, 3:2, 4:1}
sys.stderr = open(path+"out.txt", "w")


buttons_win = [
    ((65, 190, 215, 240), lambda a=0: (new_game(True) or hide_win()), ru("дальше"))]
labels_win = [
    ((0, 0, 280, 140), ru("выиграл !"), 0),
    ((0, 100, 280, 180), ru("красава"), 0)]
window_win = [(40, 100), (280, 280), buttons_win, labels_win]

buttons_lose = [
    ((65, 145, 215, 185), lambda a=0: (new_game() or hide_win()), ru("заново")),
    ((65, 190, 215, 230), lambda a=0: query_slot(load_game), ru("загрузить"))]
labels_lose = [
    ((0, 0, 280, 100), ru("проиграл :("), 0),
    ((0, 50, 280, 140), ru("ещё раз ?"), 0)]
window_lose = [(40, 100), (280, 280), buttons_lose, labels_lose]

buttons_query_exit = [
    ((30, 110, 130, 150), quit, ru("да")),
    ((150, 110, 250, 150), hide_win, ru("нет"))]
labels_query_exit = [
    ((0, 0, 280, 100), ru("выйти ? :("), 0)]
window_query_exit = [(40, 150), (280, 200), buttons_query_exit, labels_query_exit]

buttons_query_slot = [
    ((80, 330, 200, 370), hide_win, ru("отмена"))]
labels_query_slot = [
    ((0, 0, 280, 70), ru("выбери слот"), 0)]
window_query_slot = [(40, 40), (280, 400), buttons_query_slot, labels_query_slot]

buttons_menu = [
    ((70, 90, 230, 130), lambda a=0: (new_game() or hide_win()), ru("переиграть")),
    ((70, 135, 230, 175), open_settings, ru("настройки")),
    ((70, 180, 230, 220), lambda a=0: query_slot(save_game), ru("сохранить")),
    ((70, 225, 230, 265), lambda a=0: query_slot(load_game), ru("загрузить")),
    ((70, 270, 230, 315), hide_win, ru("назад"))]
labels_menu = [
    ((0, 0, 300, 100), ru("меню"), 0)]
menu = [(30, 50), (300, 380), buttons_menu, labels_menu]

buttons = [
    ((235, 595, 355, 635), lambda a=0: show_win(window_query_exit), ru("выйти")),
    ((235, 550, 355, 590), pause_f, ru("пауза")),
    ((235, 505, 355, 545), lambda a=0: show_win(menu), ru("меню"))]
    
buttons_settings = [
    ((30, 595, 150, 635), (lambda a=0: apply_config() or back()), ru("принять")),
    ((210, 595, 330, 635), back, ru("назад"))]

buttons_settings_v = [
    ((15, 160, 30, 30, 30), lambda a: edit_spawn(0, a)),
    ((135, 160, 30, 30, 30), lambda a: edit_spawn(1, a)),
    ((255, 160, 30, 30, 30), lambda a: edit_spawn(2, a)),
    ((45, 290, 30, 30, 30), lambda a: edit_spawn(3, a)),
    ((225, 290, 30, 30, 30), lambda a: edit_spawn(4, a)),
    ((30, 385, 40, 40, 40), lambda a: edit_map_size(0, a)),
    ((210, 385, 40, 40, 40), lambda a: edit_map_size(1, a))]

labels = [
    (10, 525, ru("уровень: %(level)i")),
    (10, 570, ru("ходы: %(turns)i")),
    (10, 610, ru("лопнуло: %(boms)i"))]

init_img()
apply_config(False)
find_config()
main()