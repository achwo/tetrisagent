#!/usr/bin/env python

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
ITERATIONS_LABEL = "Anzahl der Durchlaeufe: {0}"
Q_OR_NOT_LABEL = "Action aus Q: {0}"
PAUSE_BUTTON_TEXT = "Pause"
RESUME_BUTTON_TEXT = "Resume"
QUIT_BUTTON_TEXT = "Quit"
FAST_FORWARD_BUTTON_TEXT = "Fast Forward"

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
        self.canvas.grid(row=1, column=0, rowspan=5)

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


class game_controller(object):

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

        self.fastForwardInput = Entry(parent)
        self.fastForwardInput.insert(0, "50")
        self.fastForwardInput.grid(row=1, column=2)


        self.maxLabel = Label(parent, text=MAX_BLOCKS_LABEL.format(0))
        self.maxLabel.grid(row=2, column=1, sticky=W)
        self.avgLabel = Label(parent, text=AVG_BLOCKS_LABEL.format(0))
        self.avgLabel.grid(row=1, column=1, sticky=W)
        self.iterationsLabel = Label(parent, text=ITERATIONS_LABEL.format(0))
        self.iterationsLabel.grid(row=3, column=1, sticky=W)
        self.qLabel = Label(parent, text=Q_OR_NOT_LABEL.format('-'))
        self.qLabel.grid(row=4, column=1, sticky=W)

        self.fastForwardButton = Button(parent, text=FAST_FORWARD_BUTTON_TEXT,
                                   command=self.fast_forward_callback)
        self.fastForwardButton.grid(row=5, column=2, sticky=E)

        self.pauseButton = Button(parent, text=PAUSE_BUTTON_TEXT,
                                     command=self.pause_callback)
        self.pauseButton.grid(row=5, column=1, sticky=E)

        self.quitButton = Button(parent, text=QUIT_BUTTON_TEXT,
                            command=self.quit_callback)
        self.quitButton.grid(row=5, column=3, sticky=E)

        self.board = Board(
            parent,
            block_size_in_px=BLOCK_SIZE_IN_PX,
            board_width_in_blocks=BOARD_WIDTH_IN_BLOCKS,
            board_height_in_blocks=BOARD_HEIGHT_IN_BLOCKS,
            offset=OFFSET_TO_WINDOW_BORDER_IN_PX
        )
        self.parent.bind("<Escape>", self.quit_callback)

    def fast_forward_callback(self):
        if not agent.fast_forward:
            agent.fast_forward_total = int(controller.fastForwardInput.get())
            agent.fast_forward_count = agent.fast_forward_total
            agent.fast_forward = True

    def pause_callback(self):
        if is_game_paused():
            self.pauseButton['text'] = PAUSE_BUTTON_TEXT
            resume_game()
        else:
            self.pauseButton['text'] = RESUME_BUTTON_TEXT
            pause_game()

    def quit_callback(self, event=None):
        agent.resume_event.set()
        self.parent.quit()

    def update_board(self, blocks):
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
                
        self.board.clear()
        for r in range(len(blocks)):
            for c in range(len(blocks[r])):
                color = get_color(blocks[r][c])
                self.board.add_block((r, c), color)

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
            controller.update_board(blocks)
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
    controller = game_controller(tk_root)
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
