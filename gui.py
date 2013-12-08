#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Tkinter import *
import Queue
import inspect
import threading
import tkFileDialog
import time
import copy

import matplotlib
from environment import LShape, TShape, IShape, ZShape, SShape, OShape, JShape
import reward_features

matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from agent import TDLearningAgent
import settings
import util


FIELD_ROWSPAN = 10
BLOCK_SIZE_IN_PX = 30
OFFSET_TO_WINDOW_BORDER_IN_PX = 5
BOARD_WIDTH_IN_BLOCKS = settings.FIELD_WIDTH
BOARD_WIDTH_IN_PX = BOARD_WIDTH_IN_BLOCKS * BLOCK_SIZE_IN_PX
BOARD_HEIGHT_IN_BLOCKS = settings.FIELD_HEIGHT
BOARD_HEIGHT_IN_PX = BOARD_HEIGHT_IN_BLOCKS * BLOCK_SIZE_IN_PX

LEFT = "left"
RIGHT = "right"
DOWN = "down"

MAX_BLOCKS_LABEL = "Maximale Anzahl von Bloecken: {0}"
AVG_BLOCKS_LABEL = "Platzierte Bloecke im Durchschnitt: {0}"
ITERATIONS_LABEL = "Anzahl der Durchläufe: {0}"
Q_OR_NOT_LABEL = "Action aus Q: {0}"
PLACED_BLOCKS_LABEL = 'Platzierte Blöcke: {0}'
PAUSE_BUTTON_TEXT = "Pause"
RESUME_BUTTON_TEXT = "Play"
QUIT_BUTTON_TEXT = "Quit"
FAST_FORWARD_BUTTON_TEXT = ">>"
SAVE_BUTTON_TEXT = "Save Q"
LOAD_BUTTON_TEXT = "Load Q"
Q_FILENAME = "q"
SHAPES_BUTTON_TEXT = 'Shapes auswaehlen'
REWARDS_BUTTON_TEXT = 'Rewards auswaehlen'

GUI_REFRESH_IN_MS = 50
TOTAL_EPISODES = 5000
STEP_SLOWDOWN_IN_SEC = 0.3
EPISODE_SLOWDOWN_IN_SEC = 0
NUM_EPISODES_IN_AVG_CALC = 50

global controller
global agent
global dataQ
dataQ = Queue.Queue(maxsize=0)


class Board(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.landed = {}
        self.parent = parent
        self.offset = OFFSET_TO_WINDOW_BORDER_IN_PX

        self.canvas = Canvas(parent,
                             height=BOARD_HEIGHT_IN_PX + self.offset,
                             width=BOARD_WIDTH_IN_PX + self.offset)

        self.canvas.grid(row=0, column=0)

    def clear(self):
        self.canvas.delete(ALL)
        self.draw_border()

    def draw_border(self):
        x_left = self.offset
        y_up = self.offset
        y_bottom = BOARD_HEIGHT_IN_PX + self.offset
        x_right = BOARD_WIDTH_IN_PX + self.offset
        vanish_zone_height = 2 * BLOCK_SIZE_IN_PX + self.offset

        self.canvas.create_line(x_left, y_up, x_left, y_bottom)
        self.canvas.create_line(x_right, y_up, x_right, y_bottom)
        self.canvas.create_line(x_left, y_bottom, x_right, y_bottom)
        self.canvas.create_line(x_left, y_up, x_right, y_up)
        self.canvas.create_line(x_left, vanish_zone_height,
                                x_right, vanish_zone_height,
                                fill="red", dash=(4, 2))

    def add_block(self, (x, y), colour):
        """
        Create a block by drawing it on the canvas, return
        it's ID to the caller.
        """
        if colour is None:
            return

        rx = (x * BLOCK_SIZE_IN_PX) + self.offset
        ry = (y * BLOCK_SIZE_IN_PX) + self.offset

        return self.canvas.create_rectangle(
            rx, ry, rx + BLOCK_SIZE_IN_PX, ry + BLOCK_SIZE_IN_PX,
            fill=colour
        )

    def update(self, blocks):
        def get_color(x):
            return {
                'o': 'yellow',
                'i': 'cyan',
                'z': 'red',
                's': 'green',
                'j': 'blue',
                'l': 'orange',
                't': 'magenta',
            }.get(x)

        self.clear()
        for r in range(len(blocks)):
            for c in range(len(blocks[r])):
                color = get_color(blocks[r][c])
                self.add_block((r, c), color)


class ControlPanel(Frame):
    def __init__(self, parent, controller):
        #super(ControlPanel, self).__init__(parent)
        Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.init_components()
        grid = self.init_grid()
        self.make_visible(grid)

    def init_components(self):
        self.blocksLabel = Label(self, text=PLACED_BLOCKS_LABEL.format(0))
        self.avgLabel = Label(self, text=AVG_BLOCKS_LABEL.format(0))
        self.maxLabel = Label(self, text=MAX_BLOCKS_LABEL.format(0))
        self.iterationsLabel = Label(self, text=ITERATIONS_LABEL.format(0))
        self.qLabel = Label(self, text=Q_OR_NOT_LABEL.format('-'))

        self.pauseBtn = Button(self, text=RESUME_BUTTON_TEXT,
                               command=self.controller.pause_callback)
        self.fastForwardInput = Entry(self, width=5)
        self.fastForwardInput.insert(0, "50")
        self.fastForwardBtn = Button(self,
                                     text=FAST_FORWARD_BUTTON_TEXT,
                                     command=self.controller.fast_forward_callback)
        self.saveBtn = Button(self, text=SAVE_BUTTON_TEXT,
                              command=self.controller.save_callback)
        self.loadBtn = Button(self, text=LOAD_BUTTON_TEXT,
                              command=self.controller.load_callback)
        self.quitBtn = Button(self, text=QUIT_BUTTON_TEXT,
                              command=self.controller.quit_callback)

        self.shapesButton = Button(self, text=SHAPES_BUTTON_TEXT,
                                   command=self.controller.shapes_callback)
        self.rewardsButton = Button(self, text=REWARDS_BUTTON_TEXT,
                                    command=self.controller.rewards_callback)

        input_width = 5

        self.fastForwardLabel = Label(self, text='Fast Forward count: ')
        self.fastForwardInput = Entry(self, width=input_width)
        self.fastForwardInput.insert(0, "50")

        self.alphaLabel = Label(self, text='alpha: ')
        self.alphaInput = Entry(self, width=input_width)
        self.alphaInput.insert(0, "0.9")

        self.gammaLabel = Label(self, text='gamma: ')
        self.gammaInput = Entry(self, width=input_width)
        self.gammaInput.insert(0, "0.8")

        self.epsilonLabel = Label(self, text='epsilon: ')
        self.epsilonInput = Entry(self, width=input_width)
        self.epsilonInput.insert(0, "0.3")

        f = Figure(figsize=(7, 5), dpi=50)
        self.subplot = f.add_subplot(111)

        self.line_x = []
        self.line_y = []
        self.plot_line, = self.subplot.plot(self.line_x, self.line_y)
        self.subplot.set_xlabel('episode')
        self.subplot.set_ylabel('blocks')
        self.maxline = self.subplot.axhline(y=-1, color='red', linestyle='--')

        # a tk.DrawingArea
        self.plot_canvas = FigureCanvasTkAgg(f, master=self)
        self.plot_canvas.show()

    def init_grid(self):
        w_and_colspan_3 = dict(sticky=W, columnspan=3)

        e = {'sticky': E}
        w = {'sticky': W}

        emptyLabel = Label(self)

        grid = [
            [(self.blocksLabel, w_and_colspan_3)],
            [(self.avgLabel, w_and_colspan_3)],
            [(self.maxLabel, w_and_colspan_3)],
            [(self.iterationsLabel, w_and_colspan_3)],
            [(self.qLabel, w_and_colspan_3)],
            [(self.plot_canvas.get_tk_widget(), e), ],
            [(emptyLabel, None)],

            [(self.shapesButton, w_and_colspan_3)],
            [(self.rewardsButton, w_and_colspan_3)],
            [(self.alphaLabel, e), (self.alphaInput, w)],
            [(self.gammaLabel, e), (self.gammaInput, w)],
            [(self.epsilonLabel, e), (self.epsilonInput, w)],
            [(self.fastForwardLabel, e), (self.fastForwardInput, w)],
            [(self.pauseBtn, e),
             (self.fastForwardBtn, w)],
            [(self.saveBtn, e), (self.loadBtn, e), None, (self.quitBtn, w)]
        ]

        emptyLabel['height'] = FIELD_ROWSPAN - len(grid)

        return grid

    def make_visible(self, grid):
        """
        Puts every item in grid to the position in the list.
        Since list is 0-based and in the canvas we only use positions > 0,
        list index is added by 1 each time.
        """

        for row in range(len(grid)):
            for col in range(len(grid[row])):
                if grid[row][col] is not None:
                    if grid[row][col][1] is None:
                        grid[row][col][0].grid(column=col, row=row + 1)
                    else:
                        grid[row][col][0].grid(column=col, row=row + 1,
                                               **grid[row][col][1])


class Controller(object):
    def __init__(self, parent):
        self.parent = parent
        self.score = 0
        self.level = 0
        self.delay = 1

        self.options = {'filetypes': [('all files, ', '.*')],
                        'initialfile': 'q', 'parent': tk_root,
                        'title': "Choose a File"}

        self.board = Board(parent)
        self.board.clear()

        self.panel = ControlPanel(parent, self)
        self.panel.grid(row=0, column=1, sticky=N + W)

        self.parent.bind("<Escape>", self.quit_callback)
        self.parent.bind("<Control-f>", self.fast_forward_callback)
        self.parent.bind("<Control-space>", self.pause_callback)

        self._load_config()

    def _load_config(self):
        config = util.load_gui_config(self)

        if config:
            a = self.panel.alphaInput
            g = self.panel.gammaInput
            e = self.panel.epsilonInput

            a.delete(0, END)
            a.insert(0, config['alpha'])
            g.delete(0, END)
            g.insert(0, config['gamma'])
            e.delete(0, END)
            e.insert(0, config['epsilon'])

    def _set_agent_inputs_state(self, state):
        self.panel.alphaInput['state'] = state
        self.panel.gammaInput['state'] = state
        self.panel.epsilonInput['state'] = state

    def _set_agent_learning_vars(self):
        alpha = float(self.panel.alphaInput.get())
        gamma = float(self.panel.gammaInput.get())
        epsilon = float(self.panel.epsilonInput.get())
        agent.alpha = alpha
        agent.gamma = gamma
        agent.epsilon = epsilon

    def fast_forward_callback(self, event=None):
        if not agent.fast_forward:
            self.board.clear()
            agent.fast_forward_total = int(
                self.panel.fastForwardInput.get())
            agent.fast_forward_count = agent.fast_forward_total
            agent.fast_forward = True
            if is_game_paused():
                self.pause_callback()

    def save_callback(self):
        filename = tkFileDialog.asksaveasfilename(**self.options)

        if filename:
            util.save_to_file(agent.Q, filename)

    def load_callback(self):
        filename = tkFileDialog.askopenfilename(**self.options)

        if filename:
            agent.Q = util.read_from_file(filename)

    def quit_callback(self, event=None):
        util.save_gui_config(controller)
        self._resume_agent()
        self.parent.quit()
        self.parent.destroy()

    def clear_callback(self, event):
        self.board.clear()

    def pause_callback(self, event=None):
        if is_game_paused():
            self.set_gui_state_resume()
            self._resume_agent()
        else:
            self.set_gui_state_pause()
            self._pause_agent()

    def set_gui_state_resume(self):
        self.panel.pauseBtn['text'] = PAUSE_BUTTON_TEXT
        self._set_agent_inputs_state(DISABLED)
        self._set_agent_learning_vars()

    def set_gui_state_pause(self):
        self.panel.pauseBtn['text'] = RESUME_BUTTON_TEXT
        self._set_agent_inputs_state(NORMAL)
        agent.stop_fast_forward()

    def _pause_agent(self):
        agent.resume_event.clear()

    def _resume_agent(self):
        agent.resume_event.set()

    def shapes_callback(self):
        if hasattr(self, 'shapes_dialog'):
            self.shapes_dialog.destroy()
        self.shapes_dialog = ShapesDialog()

    def rewards_callback(self):
        if hasattr(self, 'rewards_dialog'):
            self.rewards_dialog.destroy()
        self.rewards_dialog = RewardsDialog()


class TDLearningAgentSlow(TDLearningAgent):
    """
    Special class for GUI representation with slower calculation speed
    """

    def __init__(self):
        super(TDLearningAgentSlow, self).__init__()
        self.step_count = 0
        self.steps_per_episode = []
        self.fast_forward = False
        self.fast_forward_total = 0
        self.fast_forward_count = 0

    def run(self, episodes):
        for i in range(0, episodes):
            if self.stop_event.is_set():
                break
            self._episode()
            self.iterations += 1
            self._update_gui()

    def _episode(self):
        if self._is_fast_forward_finished():
            self.stop_fast_forward()
            self.resume_event.clear()

        self.step_count = 0
        super(TDLearningAgentSlow, self)._episode()
        self.steps_per_episode.append(self.step_count)
        if self.fast_forward:
            self.fast_forward_count -= 1
        if EPISODE_SLOWDOWN_IN_SEC > 0 and not self.fast_forward:
            time.sleep(EPISODE_SLOWDOWN_IN_SEC)

    def _step(self):
        self.resume_event.wait()
        super(TDLearningAgentSlow, self)._step()
        self.step_count += 1

        self._update_gui()
        if STEP_SLOWDOWN_IN_SEC > 0 and not self.fast_forward:
            time.sleep(STEP_SLOWDOWN_IN_SEC)

    def stop_fast_forward(self):
        self.fast_forward = False
        self.fast_forward_count = self.fast_forward_total
        self._update_gui()

    def _is_fast_forward_finished(self):
        return (self.fast_forward and self.fast_forward_count <= 0)

    def _is_game_over(self):
        if self.stop_event.is_set():
            return True
        return super(TDLearningAgentSlow, self)._is_game_over()

    def _update_gui(self):
        if not self.fast_forward:
            blockcopy = copy.deepcopy(self.environment.field.blocks)
            self.dataQ.put(blockcopy)


class ShapesDialog(Toplevel):
    def __init__(self, **kw):
        Toplevel.__init__(self, **kw)

        self.init_shapes(agent.environment.possible_shapes)

        Checkbutton(self, text='L', variable=self.shapes[LShape]).grid(column=0, row=1)
        Checkbutton(self, text='J', variable=self.shapes[JShape]).grid(column=1, row=1)
        Checkbutton(self, text='O', variable=self.shapes[OShape]).grid(column=2, row=1)
        Checkbutton(self, text='S', variable=self.shapes[SShape]).grid(column=3, row=1)
        Checkbutton(self, text='Z', variable=self.shapes[ZShape]).grid(column=0, row=2)
        Checkbutton(self, text='I', variable=self.shapes[IShape]).grid(column=1, row=2)
        Checkbutton(self, text='T', variable=self.shapes[TShape]).grid(column=2, row=2)

        Button(self, text="Ok", command=self.on_ok).grid(column=3, row=3)

    def on_ok(self):
        shapes = []
        for shape, value in self.shapes.iteritems():
            if value.get() != 0:
                shapes.append(shape)

        agent.environment.possible_shapes = shapes
        self.destroy()

    def init_shapes(self, possible_shapes):

        self.shapes = {LShape: BooleanVar(), JShape: BooleanVar(),
                       OShape: BooleanVar(), SShape: BooleanVar(),
                       ZShape: BooleanVar(), IShape: BooleanVar(),
                       TShape: BooleanVar()}

        for shape in possible_shapes:
            self.shapes[shape] = BooleanVar(value=True)


class RewardsDialog(Toplevel):
    def __init__(self, **kw):
        Toplevel.__init__(self, **kw)

        self.init_rewards()

        Button(self, text="Ok", command=self.on_ok).grid(column=4, row=20)

    def init_rewards(self):
        avail_rewards = inspect.getmembers(reward_features, inspect.isfunction)
        active_rewards = agent.environment.rewards
        self.rewards_settings = {}

        r, c = 0, 0

        for reward in avail_rewards:
            active = BooleanVar()
            Checkbutton(self, text=reward[0], variable=active).grid(column=c, row=r)
            textfield = Entry(self, width=5)
            textfield.grid(column=c+1, row=r)

            if reward[1] in active_rewards:
                active.set(True)
                textfield.insert(0, active_rewards[reward[1]])

            self.rewards_settings[reward[1]] = [active, textfield]

            c += 2
            if c > 4:
                c = 0
                r += 1

    def on_ok(self):

        rewards = {}

        for reward, settings in self.rewards_settings.iteritems():
            if settings[0].get() != 0 and settings[1].get() != '':
                rewards[reward] = int(settings[1].get())

        agent.environment.rewards = rewards
        self.destroy()


def is_game_paused():
    return not agent.resume_event.is_set()


def update_input_state():
    if is_game_paused():
        controller.set_gui_state_pause()
    else:
        controller.set_gui_state_resume()


def update_block_canvas():
    try:
        blocks = dataQ.get(timeout=0.1)
        if blocks:
            controller.board.update(blocks)
    except:
        pass


def update_labels():
    episodes = agent.steps_per_episode[-NUM_EPISODES_IN_AVG_CALC:]
    avg = reduce(lambda x, y: x + y, episodes) / len(episodes)
    maximum = max(agent.steps_per_episode)

    controller.panel.blocksLabel["text"] = PLACED_BLOCKS_LABEL.format(
        agent.step_count)
    controller.panel.maxLabel["text"] = MAX_BLOCKS_LABEL.format(maximum)
    controller.panel.avgLabel["text"] = AVG_BLOCKS_LABEL.format(avg)
    controller.panel.iterationsLabel["text"] = ITERATIONS_LABEL.format(
        agent.iterations)


def update_plot():
    if not agent.fast_forward:
        x = range(len(agent.steps_per_episode))
        y = agent.steps_per_episode
        controller.panel.plot_line.set_data(x, y)
        ax = controller.panel.plot_canvas.figure.axes[0]
        XSCALE = 100
        YSCALE = 35
        if len(x) > XSCALE:
            ax.set_xlim(0, len(x))
        else:
            ax.set_xlim(0, XSCALE)

        max_y = max(y)
        if max_y > YSCALE:
            ax.set_ylim(0, max_y)
        else:
            ax.set_ylim(0, YSCALE)
        controller.panel.maxline.set_ydata(max_y)
        controller.panel.plot_canvas.draw()


def refresh_gui():
    update_input_state()
    update_block_canvas()

    if agent.iterations > 0:
        update_labels()
        update_plot()

    controller.panel.qLabel["text"] = Q_OR_NOT_LABEL.format(
        agent.action_from_q)
    controller.parent.after(GUI_REFRESH_IN_MS, refresh_gui)


def run(stop_event, resume_event):
    global agent
    agent = TDLearningAgentSlow()
    agent.dataQ = dataQ
    agent.stop_event = stop_event
    agent.resume_event = resume_event
    agent.run(TOTAL_EPISODES)


if __name__ == "__main__":
    tk_root = Tk()
    tk_root.title("tetris agent")
    height = BOARD_HEIGHT_IN_PX + OFFSET_TO_WINDOW_BORDER_IN_PX * 2
    tk_root.minsize(450, height)
    controller = Controller(tk_root)
    logic_stop_event = threading.Event()
    logic_resume_event = threading.Event()
    logic_thread = threading.Thread(target=run,
                                    args=(logic_stop_event,
                                          logic_resume_event))
    logic_thread.start()
    tk_root.after(GUI_REFRESH_IN_MS, refresh_gui)
    tk_root.mainloop()
    logic_stop_event.set()
    logic_thread.join()
