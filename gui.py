#!/usr/bin/env python

from Tkinter import *
import Queue
import threading
import tkFileDialog
import time
import copy

from agent import TDLearningAgent
import settings
import util


FIELD_ROWSPAN = 20
BLOCK_SIZE_IN_PX = 30
OFFSET_TO_WINDOW_BORDER_IN_PX = 3
BOARD_WIDTH_IN_BLOCKS = settings.FIELD_WIDTH
BOARD_WIDTH_IN_PX = BOARD_WIDTH_IN_BLOCKS * BLOCK_SIZE_IN_PX
BOARD_HEIGHT_IN_BLOCKS = settings.FIELD_HEIGHT
BOARD_HEIGHT_IN_PX = BOARD_HEIGHT_IN_BLOCKS * BLOCK_SIZE_IN_PX

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
SAVE_BUTTON_TEXT = "Save Q"
LOAD_BUTTON_TEXT = "Load Q"
Q_FILENAME = "q"

GUI_REFRESH_IN_MS = 50
TOTAL_EPISODES = 5000
VISUALIZE_EPISODES_COUNT = 500
STEP_SLOWDOWN_IN_SEC = 0.3
EPISODE_SLOWDOWN_IN_SEC = 0

global controller
global layout
global agent
global dataQ
dataQ = Queue.Queue(maxsize=0)


class Board(Frame):
    """
    The board represents the tetris playing area. A grid of x by y blocks.
    """

    def __init__(self, parent):
        Frame.__init__(self, parent)

        # blocks are indexed by there coordinates e.g. (4,5), these are
        self.landed = {}
        self.parent = parent
        self.offset = OFFSET_TO_WINDOW_BORDER_IN_PX

        self.canvas = Canvas(parent,
                             height=BOARD_HEIGHT_IN_PX + self.offset,
                             width=BOARD_WIDTH_IN_PX + self.offset)
        # self.canvas.pack()
        self.canvas.grid(row=1, column=0, rowspan=FIELD_ROWSPAN)

    def clear(self):
        self.canvas.delete(ALL)
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

        self.options = {'filetypes': [('all files, ', '.*')],
                        'initialfile': 'q', 'parent': tk_root,
                        'title': "Choose a File"}

        self.board = Board(parent)
        self.parent.bind("<Escape>", self.quit_callback)

    def fast_forward_callback(self):
        if not agent.fast_forward:
            agent.fast_forward_total = int(layout.fastForwardInput.get())
            agent.fast_forward_count = agent.fast_forward_total
            agent.fast_forward = True

    def save_callback(self):
        filename = tkFileDialog.asksaveasfilename(**self.options)

        if filename:
            util.save_to_json_file(agent.Q, filename)

    def load_callback(self):
        filename = tkFileDialog.askopenfilename(**self.options)

        if filename:
            agent.Q = util.read_from_json_file(filename)

    def pause_callback(self):
        if is_game_paused():
            layout.pauseBtn['text'] = PAUSE_BUTTON_TEXT
            resume_game()
        else:
            layout.pauseBtn['text'] = RESUME_BUTTON_TEXT
            pause_game()

    def quit_callback(self):
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

    def clear_callback(self):
        self.board.clear()


class Layout(object):
    def __init__(self, parent, controller):
        self.controller = controller
        self.parent = parent
        self.init_components()
        self.init_grid()
        self.make_visible(self.assemble_grid())

    def init_components(self):
        self.avgLabel = Label(self.parent, text=AVG_BLOCKS_LABEL.format(0))
        self.maxLabel = Label(self.parent, text=MAX_BLOCKS_LABEL.format(0))
        self.itLabel = Label(self.parent, text=ITERATIONS_LABEL.format(0))
        self.qLabel = Label(self.parent, text=Q_OR_NOT_LABEL.format('-'))

        self.pauseBtn = Button(self.parent, text=PAUSE_BUTTON_TEXT,
                               command=self.controller.pause_callback)

        self.fastForwardInput = Entry(self.parent, width=5)
        self.fastForwardInput.insert(0, "50")

        self.fastForwardBtn = Button(self.parent,
                                     text=FAST_FORWARD_BUTTON_TEXT,
                                     command=self.controller.fast_forward_callback)

        self.saveBtn = Button(self.parent, text=SAVE_BUTTON_TEXT,
                              command=self.controller.save_callback)

        self.loadBtn = Button(self.parent, text=LOAD_BUTTON_TEXT,
                              command=self.controller.load_callback)

        self.quitBtn = Button(self.parent, text=QUIT_BUTTON_TEXT,
                              command=self.controller.quit_callback)

    def init_grid(self):
        w_and_colspan_3 = dict(sticky=W, columnspan=3)

        self.rows_from_top = [
            [(self.avgLabel, w_and_colspan_3)],
            [(self.maxLabel, w_and_colspan_3)],
            [(self.itLabel, w_and_colspan_3)],
            [(self.qLabel, w_and_colspan_3)],
            # add row from top here
        ]

        e = {'sticky': E}
        w = {'sticky': W}

        self.rows_from_bottom = [
            [(self.pauseBtn, e), (self.fastForwardInput, e),
             (self.fastForwardBtn, w)],
            [(self.saveBtn, e), (self.loadBtn, e), None, (self.quitBtn, w)]
        ]

    def assemble_grid(self):
        """
        In the grid list sublists are rows and columns are sublist elements
        If you want to add an element, just put it in the row and column
        you want.
        """

        rows_from_top = self.rows_from_top
        rows_from_bottom = self.rows_from_bottom

        empty_lines = FIELD_ROWSPAN - len(rows_from_top) - len(rows_from_bottom)

        grid = []

        grid.extend(rows_from_top)
        grid.extend(empty_lines * [[]])
        grid.extend(rows_from_bottom)

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
                        grid[row][col][0].grid(column=col + 1, row=row + 1)
                    else:
                        grid[row][col][0].grid(column=col + 1, row=row + 1,
                                               **grid[row][col][1])


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

        layout.maxLabel["text"] = MAX_BLOCKS_LABEL.format(maximum)
        layout.avgLabel["text"] = AVG_BLOCKS_LABEL.format(avg)
        layout.itLabel["text"] = ITERATIONS_LABEL.format(
            agent.iterations)

    layout.qLabel["text"] = Q_OR_NOT_LABEL.format(agent.action_from_q)
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
    height = BOARD_HEIGHT_IN_PX + OFFSET_TO_WINDOW_BORDER_IN_PX * 2
    tk_root.minsize(450, height)
    controller = Controller(tk_root)
    layout = Layout(tk_root, controller)

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
