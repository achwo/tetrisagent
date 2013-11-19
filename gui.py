#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Tkinter import *
import Queue
import threading

from agent import TDLearningAgent
import time
import copy
import settings

BLOCK_SIZE_IN_PX = 30
OFFSET_TO_WINDOW_BORDER_IN_PX = 3
BOARD_WIDTH_IN_BLOCKS = settings.FIELD_WIDTH
BOARD_HEIGHT_IN_BLOCKS = settings.FIELD_HEIGHT

LEFT = "left"
RIGHT = "right"
DOWN = "down"

MAX_BLOCKS_LABEL = "Maximale Anzahl von Bloecken: {0}"
AVG_BLOCKS_LABEL = "Platzierte Bloecke im Durchschnitt: {0}"
ITERATIONS_LABEL = "Anzahl der Durchläufe: {0}"
Q_OR_NOT_LABEL = "Action aus Q: {0}"
PAUSE_BUTTON_TEXT = "Pause"
RESUME_BUTTON_TEXT = "Resume"
QUIT_BUTTON_TEXT = "Quit"
FAST_FORWARD_BUTTON_TEXT = ">>"

GUI_REFRESH_IN_MS = 50
TOTAL_EPISODES = 5000
VISUALIZE_EPISODES_COUNT = 500
STEP_SLOWDOWN_IN_SEC = 0.3
EPISODE_SLOWDOWN_IN_SEC = 0

global controller
global agent
global dataQ
dataQ = Queue.Queue(maxsize=0)


class Board(Frame):

    """
    The board represents the tetris playing area. A grid of x by y blocks.
    """

    def __init__(self, parent, block_size_in_px=20, board_width_in_blocks=10,
                 board_height_in_blocks=20, offset=3):
        Frame.__init__(self, parent)

        # blocks are indexed by there corrdinates e.g. (4,5), these are
        self.landed = {}
        self.parent = parent
        self.block_size_in_px = BLOCK_SIZE_IN_PX
        self.board_width_in_blocks = BOARD_WIDTH_IN_BLOCKS
        self.board_height_in_blocks = BOARD_HEIGHT_IN_BLOCKS
        self.offset = OFFSET_TO_WINDOW_BORDER_IN_PX

        self.canvas = Canvas(parent,
                             height=(
                                 self.board_height_in_blocks * self.block_size_in_px) + self.offset,
                             width=(self.board_width_in_blocks * self.block_size_in_px) + self.offset)
        # self.canvas.pack()
        self.canvas.grid(row=0, column=0)

    def clear(self):
        self.canvas.delete(ALL)
        x_left = self.offset
        y_up = self.offset
        y_bottom = self.board_height_in_blocks * self.block_size_in_px + self.offset
        x_right = self.board_width_in_blocks * self.block_size_in_px + self.offset
        vanish_zone_height = 2 * self.block_size_in_px + self.offset

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
        if colour == None:
            return
            
        rx = (x * self.block_size_in_px) + self.offset
        ry = (y * self.block_size_in_px) + self.offset

        return self.canvas.create_rectangle(
            rx, ry, rx + self.block_size_in_px, ry + self.block_size_in_px,
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


class Controller(object):

    """
    Main game loop and receives GUI callback events for keypresses etc...
    """

    def __init__(self, parent):
        """
        Intialise the game...
        """
        self.parent = parent
        self.score = 0
        self.level = 0
        self.delay = 1

        self.board = Board(
            parent,
            block_size_in_px=BLOCK_SIZE_IN_PX,
            board_width_in_blocks=BOARD_WIDTH_IN_BLOCKS,
            board_height_in_blocks=BOARD_HEIGHT_IN_BLOCKS,
            offset=OFFSET_TO_WINDOW_BORDER_IN_PX
        )

        control_frame = Frame(parent)
        control_frame.grid(row=0, column=1, sticky=N + W)

        self.avgLabel = Label(control_frame, text=AVG_BLOCKS_LABEL.format(0))
        self.avgLabel.grid(row=1, column=1, sticky=W, columnspan=3)
        self.maxLabel = Label(control_frame, text=MAX_BLOCKS_LABEL.format(0))
        self.maxLabel.grid(row=2, column=1, sticky=W, columnspan=3)
        self.iterationsLabel = Label(control_frame, text=ITERATIONS_LABEL.format(0))
        self.iterationsLabel.grid(row=3, column=1, sticky=W, columnspan=3)
        self.qLabel = Label(control_frame, text=Q_OR_NOT_LABEL.format('-'))
        self.qLabel.grid(row=4, column=1, sticky=W, columnspan=3)

        input_width = 5

        Label(control_frame, text='Fast Forward count: ').grid(row=5, column=1, sticky=E)
        self.fastForwardInput = Entry(control_frame, width=input_width)
        self.fastForwardInput.insert(0, "50")
        self.fastForwardInput.grid(row=5, column=2)

        Label(control_frame, text='alpha: ').grid(row=6, column=1, sticky=E)
        self.alphaInput = Entry(control_frame, width=input_width)
        self.alphaInput.insert(0, "0.9")
        self.alphaInput.grid(row=6, column=2)

        Label(control_frame, text='gamma: ').grid(row=7, column=1, sticky=E)
        self.gammaInput = Entry(control_frame, width=input_width)
        self.gammaInput.insert(0, "0.8")
        self.gammaInput.grid(row=7, column=2)

        Label(control_frame, text='epsilon: ').grid(row=8, column=1, sticky=E)
        self.epsilonInput = Entry(control_frame, width=input_width)
        self.epsilonInput.insert(0, "0.3")
        self.epsilonInput.grid(row=8, column=2)

        self.pauseButton = Button(control_frame, text=PAUSE_BUTTON_TEXT,
                                     command=self.pause_callback)
        self.pauseButton.grid(row=9, column=1, sticky=E)

        self.fastForwardButton = Button(control_frame, text=FAST_FORWARD_BUTTON_TEXT,
                                   command=self.fast_forward_callback)
        self.fastForwardButton.grid(row=9, column=2, sticky=E)

        self.quitButton = Button(control_frame, text=QUIT_BUTTON_TEXT,
                            command=self.quit_callback)
        self.quitButton.grid(row=9, column=3, sticky=E)

        self.parent.bind("<Escape>", self.quit_callback)

        self._set_agent_inputs_state(DISABLED)

    def _set_agent_inputs_state(self, state):
        self.alphaInput['state'] = state
        self.gammaInput['state'] = state
        self.epsilonInput['state'] = state

    def _set_agent_learning_vars(self):
        alpha = float(self.alphaInput.get())
        gamma = float(self.gammaInput.get())
        epsilon = float(self.epsilonInput.get())
        agent.alpha = alpha
        agent.gamma = gamma
        agent.epsilon = epsilon

    def fast_forward_callback(self):
        if not agent.fast_forward:
            agent.fast_forward_total = int(self.fastForwardInput.get())
            agent.fast_forward_count = agent.fast_forward_total
            agent.fast_forward = True

    def pause_callback(self):
        if is_game_paused():
            self.pauseButton['text'] = PAUSE_BUTTON_TEXT
            self._set_agent_inputs_state(DISABLED)
            self._set_agent_learning_vars()
            resume_game()
        else:
            self.pauseButton['text'] = RESUME_BUTTON_TEXT
            self._set_agent_inputs_state(NORMAL)
            pause_game()

    def quit_callback(self, event=None):
        agent.resume_event.set()
        self.parent.quit()

    def clear_callback(self, event):
        self.board.clear()


class TDLearningAgentSlow(TDLearningAgent):

    """
    Special class for GUI representation with slower calculation speed
    """

    def __init__(self):
        super(TDLearningAgentSlow, self).__init__()
        self.blocks_last_iteration = 0
        self.blocks_per_iteration = []
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
            self.fast_forward = False
            self.fast_forward_count = self.fast_forward_total
        self.blocks_last_iteration = 0
        super(TDLearningAgentSlow, self)._episode()
        self.blocks_per_iteration.append(self.blocks_last_iteration)
        if self.fast_forward:
            self.fast_forward_count -= 1
        if EPISODE_SLOWDOWN_IN_SEC > 0 and not self.fast_forward:
            time.sleep(EPISODE_SLOWDOWN_IN_SEC)

    def _is_fast_forward_finished(self):
        return self.fast_forward and self.fast_forward_count <= 0

    def _step(self):
        self.resume_event.wait()
        super(TDLearningAgentSlow, self)._step()
        self.blocks_last_iteration += 1

        self._update_gui()
        if STEP_SLOWDOWN_IN_SEC > 0 and not self.fast_forward:
            time.sleep(STEP_SLOWDOWN_IN_SEC)

    def _is_game_over(self):
        if self.stop_event.is_set():
            return True
        return super(TDLearningAgentSlow, self)._is_game_over()

    def _update_gui(self):
        if not self.fast_forward:
            blockcopy = copy.deepcopy(self.environment.blocks)
            self.dataQ.put(blockcopy)


def is_game_paused():
    return not agent.resume_event.is_set()


def pause_game():
    agent.resume_event.clear()


def resume_game():
    agent.resume_event.set()


def refresh_gui():
    try:
        blocks = dataQ.get(timeout=0.1)
        if blocks:
            controller.board.update(blocks)
    except:
        pass

    if agent.iterations > 0:
        avg = reduce(lambda x, y: x + y, agent.blocks_per_iteration) / len(
            agent.blocks_per_iteration)
        maximum = max(agent.blocks_per_iteration)

        controller.maxLabel["text"] = MAX_BLOCKS_LABEL.format(maximum)
        controller.avgLabel["text"] = AVG_BLOCKS_LABEL.format(avg)
        controller.iterationsLabel["text"] = ITERATIONS_LABEL.format(agent.iterations)

    controller.qLabel["text"] = Q_OR_NOT_LABEL.format(agent.action_from_q)
    controller.parent.after(GUI_REFRESH_IN_MS, refresh_gui)


def run(stop_event, resume_event):
    global agent
    agent = TDLearningAgentSlow()
    agent.dataQ = dataQ
    agent.stop_event = stop_event
    agent.resume_event = resume_event
    agent.resume_event.set()
    agent.run(TOTAL_EPISODES)


if __name__ == "__main__":
    tk_root = Tk()
    tk_root.title("tetris agent")
    height = BOARD_HEIGHT_IN_BLOCKS * BLOCK_SIZE_IN_PX + OFFSET_TO_WINDOW_BORDER_IN_PX * 2
    tk_root.minsize(450, height)
    controller = Controller(tk_root)
    logic_stop_event = threading.Event()
    logic_resume_event = threading.Event()
    logic_thread = threading.Thread(target=run, 
                                    args=(logic_stop_event, logic_resume_event))
    logic_thread.start()
    tk_root.after(GUI_REFRESH_IN_MS, refresh_gui)
    tk_root.mainloop()
    logic_stop_event.set()
    logic_thread.join()
