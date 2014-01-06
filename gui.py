#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Tkinter import *
import Queue
import inspect
import threading
import tkFileDialog
import tkMessageBox
import copy

import matplotlib
from environment import LShape, TShape, IShape, ZShape, SShape, OShape, JShape
import features
import reward_features

matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from agent import Agent
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
FEATURES_BUTTON_TEXT = 'State Features auswaehlen'

GUI_REFRESH_IN_MS = 200
TOTAL_EPISODES = 500000
NUM_EPISODES_IN_AVG_CALC = 50

global controller
global agent
global dataQ
dataQ = Queue.Queue(maxsize=0)


class BoardFrame(Frame):
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


class ControlFrame(Frame):
    def __init__(self, parent, controller):
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
                                     command=self.controller.ff_callback)
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
        self.featuresButton = Button(self, text=FEATURES_BUTTON_TEXT,
                                     command=self.controller.features_callback)

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
            [(emptyLabel, None)],

            [(self.shapesButton, w_and_colspan_3)],
            [(self.rewardsButton, w_and_colspan_3)],
            [(self.featuresButton, w_and_colspan_3)],
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


class MainController(object):
    def __init__(self, parent):
        self.parent = parent
        self.score = 0
        self.level = 0
        self.delay = 1

        self.options = {'filetypes': [('all files, ', '.*')],
                        'initialfile': 'q', 'parent': tk_root,
                        'title': "Choose a File"}

        self.board = BoardFrame(parent)
        self.board.clear()

        self.panel = ControlFrame(parent, self)
        self.panel.grid(row=0, column=1, sticky=N + W)

        self.plot_controller = PlotController(parent)

        self.parent.protocol("WM_DELETE_WINDOW", self.quit_callback)
        self.parent.bind("<Escape>", self.quit_callback)
        self.parent.bind("<Control-f>", self.ff_callback)
        self.parent.bind("<Control-space>", self.pause_callback)

        self._load_config()

    def _load_config(self):
        config = util.load_json(util.CONFIG_FILENAME)

        if config:
            a = self.panel.alphaInput
            g = self.panel.gammaInput
            e = self.panel.epsilonInput
            f = self.panel.fastForwardInput

            try:
                a.delete(0, END)
                a.insert(0, config['alpha'])
                g.delete(0, END)
                g.insert(0, config['gamma'])
                e.delete(0, END)
                e.insert(0, config['epsilon'])
                f.delete(0, END)
                f.insert(0, config['fastforward_count'])
            except:
                print 'Error reading config file'

    def is_game_paused(self):
        return not agent.resume_event.is_set()

    def _update_input_state(self):
        if self.is_game_paused():
            self.set_gui_state_pause()
        else:
            self.set_gui_state_resume()

    def refresh_gui(self):
        agent_state = self._get_agent_state()
        self._update_input_state()
        if agent_state:
            self.board.update(agent_state['blocks'])
            self._update_labels(agent_state)
            self.plot_controller.update(agent_state)

        agent.wait_for_update_event.set()
        self.parent.after(GUI_REFRESH_IN_MS, self.refresh_gui)

    def _get_agent_state(self):
        blocks = None
        try:
            blocks = dataQ.get(timeout=0.1)
        except:
            pass

        if blocks:
            steps_per_episode = copy.deepcopy(agent.steps_per_episode)
            return {
                'steps_per_episode': steps_per_episode,
                'episode_count': len(steps_per_episode),
                'blocks': blocks,
                'step_count': agent.step_count,
                'q_value': agent.action_from_q
            }

    def _update_labels(self, agent_state):
        self.panel.blocksLabel["text"] = PLACED_BLOCKS_LABEL.format(
            agent_state['step_count'])

        episode_count = agent_state['episode_count']
        self.panel.qLabel["text"] = Q_OR_NOT_LABEL.format(
            agent_state['q_value'])
        if episode_count > 0:
            maximum = max(agent_state['steps_per_episode'])
            self.panel.maxLabel["text"] = MAX_BLOCKS_LABEL.format(maximum)

            steps_per_episode = agent_state['steps_per_episode']
            latest_episodes = steps_per_episode[-NUM_EPISODES_IN_AVG_CALC:]
            avg = (reduce(lambda x, y: x + y, latest_episodes) /
                   len(latest_episodes))
            self.panel.avgLabel["text"] = AVG_BLOCKS_LABEL.format(avg)
            self.panel.iterationsLabel["text"] = ITERATIONS_LABEL.format(
                episode_count)

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

    def ff_callback(self, event=None):
        if not agent.fast_forward:
            self.board.clear()
            agent.fast_forward_total = int(
                self.panel.fastForwardInput.get())
            agent.fast_forward_count = agent.fast_forward_total
            agent.fast_forward = True
            if self.is_game_paused():
                self.pause_callback()

    def save_callback(self):
        util.save_q_table(agent.Q)
        util.save_statistics(agent.steps_per_episode)
        tkMessageBox.showinfo('Gratulation!', 'Die Q-Tabelle wurde erfolgreich gespeichert')

    def load_callback(self):
        agent.Q = util.load_q_table()
        stats = util.load_json(util.STATISTICS_FILENAME)
        agent.steps_per_episode = stats['steps_per_episode']
        agent.push_state()
        tkMessageBox.showinfo('Heureka!', 'Die Q-Tabelle wurde erfolgreich geladen')

    def quit_callback(self, event=None):
        agent.stop_event.set()
        util.save_gui_config(controller)
        self._resume_agent()
        agent.wait_for_update_event.set()
        self.parent.quit()
        self.parent.destroy()

    def clear_callback(self, event):
        self.board.clear()

    def pause_callback(self, event=None):
        if self.is_game_paused():
            self._resume_agent()
            self.set_gui_state_resume()
        else:
            self._pause_agent()
            self.set_gui_state_pause()

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
        RewardsController()

    def features_callback(self):
        StateFeatureController()
        #if hasattr(self, 'features_dialog'):
        #    self.features_dialog.destroy()
        #self.features_dialog = StateFeatureDialog()


class PlotController(object):
    def __init__(self, parent):
        f = Figure(figsize=(14, 5), dpi=50)
        self.subplot = f.add_subplot(111)

        self.plot_line, = self.subplot.plot([], [])
        self.subplot.set_xlabel('episode')
        self.subplot.set_ylabel('blocks')
        self.maxline = self.subplot.axhline(y=-1, color='red', linestyle='--')

        # a tk.DrawingArea
        self.plot_canvas = FigureCanvasTkAgg(f, master=parent)
        self.plot_canvas.show()

    def update(self, agent_state):
        if not agent.fast_forward:
            steps_per_episode = agent_state['steps_per_episode']
            episode_count = len(steps_per_episode)
            if episode_count == 0:
                return

            x = range(episode_count)
            y = steps_per_episode
            self.plot_line.set_data(x, y)
            ax = self.plot_canvas.figure.axes[0]
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
            self.maxline.set_ydata(max_y)
            self.plot_canvas.draw()


class MeasuredAgent(Agent):
    """
    Special class for GUI representation with measurements and event handling
    """

    def __init__(self):
        super(MeasuredAgent, self).__init__()
        self.step_count = 0
        self.steps_per_episode = []
        self.fast_forward = False
        self.fast_forward_total = 0
        self.fast_forward_count = 0

    def push_state(self):
        self._push_state()

    def _wait_for_update(self):
        if self.resume_event.is_set() and not self.stop_event.is_set():
            self._push_state()
            self.wait_for_update_event.clear()
            self.wait_for_update_event.wait()

    def run(self, episodes):
        for i in range(0, episodes):
            if self.stop_event.is_set():
                break
            self._episode()
            #self._wait_for_update()

    def _episode(self):
        if self._is_fast_forward_finished():
            self.stop_fast_forward()
            self.resume_event.clear()

        self.step_count = 0
        super(MeasuredAgent, self)._episode()
        self.steps_per_episode.append(self.step_count)
        if self.fast_forward:
            self.fast_forward_count -= 1

    def _step(self):
        self.resume_event.wait()

        if self.stop_event.is_set():
            return
        super(MeasuredAgent, self)._step()
        self.step_count += 1
        if not self.fast_forward:
            self._wait_for_update()

    def stop_fast_forward(self):
        self.fast_forward = False
        self.fast_forward_count = self.fast_forward_total
        self._wait_for_update()

    def _is_fast_forward_finished(self):
        return (self.fast_forward and self.fast_forward_count <= 0)

    def _is_game_over(self):
        if self.stop_event.is_set():
            return True
        return super(MeasuredAgent, self)._is_game_over()

    def _push_state(self):
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


class RewardsController(object):
    def __init__(self):
        self.init_rewards()
        self.rewards_settings = {}
        self.dialog = RewardsDialog(self)

    def destroy():
        self.dialog.destroy()

    def init_rewards(self):
        self.avail_rewards = inspect.getmembers(reward_features,
                            lambda member: inspect.isfunction(
                            member) and member.__module__ == 'reward_features')
        self.active_rewards = agent.environment.rewards

    def on_ok(self):
        rewards = {}

        for reward, settings in self.rewards_settings.iteritems():
            if settings[0].get() != 0 and settings[1].get() != '':
                rewards[reward] = float(settings[1].get())

        agent.environment.rewards = rewards
        self.dialog.destroy()


class RewardsDialog(Toplevel):
    def __init__(self, controller, **kw):
        Toplevel.__init__(self, **kw)

        Button(self, text="Ok", command=controller.on_ok).grid(column=4, row=20)

        r, c = 0, 0

        for reward in controller.avail_rewards:
            active = BooleanVar()
            Checkbutton(self, text=reward[0], variable=active).grid(column=c, row=r)
            textfield = Entry(self, width=5)
            textfield.grid(column=c + 1, row=r)

            if reward[1] in controller.active_rewards:
                active.set(True)
                textfield.insert(0, controller.active_rewards[reward[1]])

            controller.rewards_settings[reward[1]] = [active, textfield]

            c += 2
            if c > 4:
                c = 0
                r += 1


class StateFeatureController():
    def __init__(self):
        self.feature_settings = {}

        self.avail_features = inspect.getmembers(features,
                                lambda member: inspect.isfunction(
                                member) and member.__module__ == 'features')
        self.active_features = agent.features

        self.dialog = StateFeatureDialog(self)

    def on_ok(self):
        features = []

        for feature, setting in self.feature_settings.iteritems():
            if setting.get() != 0:
                features.append(feature)

        agent.features = features
        self.dialog.destroy()


class StateFeatureDialog(Toplevel):
    def __init__(self, controller, **kw):
        Toplevel.__init__(self, **kw)

        Button(self, text="Ok", command=controller.on_ok).grid(column=4, row=20)

        r, c = 0, 0

        for reward in controller.avail_features:
            active = BooleanVar()
            Checkbutton(self, text=reward[0], variable=active).grid(column=c,
                                                                    row=r)

            if reward[1] in controller.active_features:
                active.set(True)

            controller.feature_settings[reward[1]] = active

            # these are for 3 features per line
            c += 2
            if c > 4:
                c = 0
                r += 1


def start_agent(stop_event, resume_event, wait_for_update_event):
    global agent
    agent = MeasuredAgent()
    agent.dataQ = dataQ
    agent.stop_event = stop_event
    agent.resume_event = resume_event
    agent.wait_for_update_event = wait_for_update_event
    agent.run(TOTAL_EPISODES)


if __name__ == "__main__":
    tk_root = Tk()
    tk_root.title("tetris agent")
    height = BOARD_HEIGHT_IN_PX + OFFSET_TO_WINDOW_BORDER_IN_PX * 2
    tk_root.minsize(450, height)
    controller = MainController(tk_root)
    logic_stop_event = threading.Event()
    logic_resume_event = threading.Event()
    logic_wait_for_update_event = threading.Event()
    logic_thread = threading.Thread(target=start_agent,
                                    args=(logic_stop_event,
                                          logic_resume_event,
                                          logic_wait_for_update_event,))
    logic_thread.start()
    tk_root.after(GUI_REFRESH_IN_MS, controller.refresh_gui)
    tk_root.mainloop()
    logic_stop_event.set()
    logic_thread.join()
