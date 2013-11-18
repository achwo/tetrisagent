#!/usr/bin/env python

from Tkinter import *
import Queue
import threading

from agent import TDLearningAgent
import time
import copy
import settings

BLOCK_SIZE_IN_PX = 40
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

GUI_REFRESH_IN_MS = 50
TOTAL_EPISODES = 1000
VISUALIZE_EPISODES_COUNT = 500
STEP_SLOWDOWN_IN_SEC = 0.3
EPISODE_SLOWDOWN_IN_SEC = 0

global tk_root
global controller
global agent
global dataQ
dataQ = Queue.Queue(maxsize=0)

direction_d = {"left": (-1, 0), "right": (1, 0), "down": (0, 1)}


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

    def check_for_complete_row(self, blocks):
        """
        Look for a complete row of blocks, from the bottom up until the top row
        or until an empty row is reached.
        """
        rows_deleted = 0

        # Add the blocks to those in the grid that have already 'landed'
        for block in blocks:
            self.landed[block.coord()] = block.id

        empty_row = 0

        # find the first empty row
        for y in xrange(self.board_height_in_blocks - 1, -1, -1):
            row_is_empty = True
            for x in xrange(self.board_width_in_blocks):
                if self.landed.get((x, y), None):
                    row_is_empty = False
                    break
            if row_is_empty:
                empty_row = y
                break

        # Now scan up and until a complete row is found.
        y = self.board_height_in_blocks - 1
        while y > empty_row:

            complete_row = True
            for x in xrange(self.board_width_in_blocks):
                if self.landed.get((x, y), None) is None:
                    complete_row = False
                    break

            if complete_row:
                rows_deleted += 1

                # delete the completed row
                for x in xrange(self.board_width_in_blocks):
                    block = self.landed.pop((x, y))
                    self.delete_block(block)
                    del block

                # move all the rows above it down
                for ay in xrange(y - 1, empty_row, -1):
                    for x in xrange(self.board_width_in_blocks):
                        block = self.landed.get((x, ay), None)
                        if block:
                            block = self.landed.pop((x, ay))
                            dx, dy = direction_d[DOWN]

                            self.move_block(block, direction_d[DOWN])
                            self.landed[(x + dx, ay + dy)] = block

                # move the empty row down index down too
                empty_row += 1
                # y stays same as row above has moved down.

            else:
                y -= 1

        # self.output() # non-gui diagnostic

        # return the score, calculated by the number of rows deleted.
        return (100 * rows_deleted) * rows_deleted

    def output(self):
        for y in xrange(self.board_height_in_blocks):
            line = []
            for x in xrange(self.board_width_in_blocks):
                if self.landed.get((x, y), None):
                    line.append("X")
                else:
                    line.append(".")
            print "".join(line)

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

    def move_block(self, id, coord):
        """
        Move the block, identified by 'id', by x and y. Note this is a
        relative movement, e.g. move 10, 10 means move 10 pixels right and
        10 pixels down NOT move to position 10,10. 
        """
        x, y = coord
        self.canvas.move(
            id, x * self.block_size_in_px, y * self.block_size_in_px)

    def delete_block(self, id):
        """
        Delete the identified block
        """
        self.canvas.delete(id)

    def check_block(self, (x, y)):
        """
        Check if the x, y coordinate can have a block placed there.
        That is; if there is a 'landed' block there or it is outside the
        board boundary, then return False, otherwise return true.
        """
        if x < 0 or x >= self.board_width_in_blocks or y < 0 or y >= self.board_height_in_blocks:
            return False
        elif self.landed.has_key((x, y)):
            return False
        else:
            return True


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
        self.delay = 1    # ms

        global avg_label
        global max_label
        global it_label
        global q_label

        max_label = Label(tk_root, text=MAX_BLOCKS_LABEL.format(0))
        max_label.grid(row=2, column=1, sticky=W)
        avg_label = Label(tk_root, text=AVG_BLOCKS_LABEL.format(0))
        avg_label.grid(row=1, column=1, sticky=W)
        it_label = Label(tk_root, text=ITERATIONS_LABEL.format(0))
        it_label.grid(row=3, column=1, sticky=W)
        q_label = Label(tk_root, text=Q_OR_NOT_LABEL.format('-'))
        q_label.grid(row=4, column=1, sticky=W)

        quitButton = Button(parent, text="Quit",
                            command=parent.quit)
        quitButton.grid(row=5, column=2, sticky=E)

        self.board = Board(
            parent,
            block_size_in_px=BLOCK_SIZE_IN_PX,
            board_width_in_blocks=BOARD_WIDTH_IN_BLOCKS,
            board_height_in_blocks=BOARD_HEIGHT_IN_BLOCKS,
            offset=OFFSET_TO_WINDOW_BORDER_IN_PX
        )
        self.parent.bind("a", self.a_callback)

    def a_callback(self, event):
        pass

    def update_board(self, blocks):
        self.board.clear()

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

        for r in range(len(blocks)):
            for c in range(len(blocks[r])):
                self.board.add_block((r, c), get_color(blocks[r][c]))

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

    def run(self, episodes):
        for i in range(0, episodes):
            if self.stop_event.is_set():
                break
            self._episode()
            self.iterations += 1
            self._update_gui()

    def _episode(self):
        self.blocks_last_iteration = 0
        super(TDLearningAgentSlow, self)._episode()
        self.blocks_per_iteration.append(self.blocks_last_iteration)
        if EPISODE_SLOWDOWN_IN_SEC > 0:
            time.sleep(EPISODE_SLOWDOWN_IN_SEC)

    def _step(self):
        super(TDLearningAgentSlow, self)._step()
        self.blocks_last_iteration += 1
        self._update_gui()
        if STEP_SLOWDOWN_IN_SEC > 0:
            time.sleep(STEP_SLOWDOWN_IN_SEC)

    def _update_gui(self):
        # if self.iterations % VISUALIZE_EPISODES_COUNT == 0:
        blockcopy = copy.deepcopy(self.environment.blocks)
        self.dataQ.put(blockcopy)


def refresh_gui():
    try:
        blocks = dataQ.get(timeout=0.1)
        if blocks:
            controller.update_board(blocks)
    except:
        pass

    # if agent.iterations % 100 == 0:
    if agent.iterations > 0:
        avg = reduce(lambda x, y: x + y, agent.blocks_per_iteration) / len(
            agent.blocks_per_iteration)
        maximum = max(agent.blocks_per_iteration)

        max_label["text"] = MAX_BLOCKS_LABEL.format(maximum)
        avg_label["text"] = AVG_BLOCKS_LABEL.format(avg)
        it_label["text"] = ITERATIONS_LABEL.format(agent.iterations)

    q_label["text"] = Q_OR_NOT_LABEL.format(agent.action_from_q)

    # controller.update_board(environment)
    tk_root.after(GUI_REFRESH_IN_MS, refresh_gui)


def run(stop_event):
    global agent
    agent = TDLearningAgentSlow()
    agent.dataQ = dataQ
    agent.stop_event = stop_event
    agent.run(TOTAL_EPISODES)


if __name__ == "__main__":
    tk_root = Tk()
    tk_root.title("tetris agent")
    tk_root.minsize(450, 250)
    tk_root.geometry("750x500")
    controller = game_controller(tk_root)
    logic_stop_event = threading.Event()
    logic_thread = threading.Thread(target=run,
                                    args=(logic_stop_event,))
    logic_thread.start()
    tk_root.after(GUI_REFRESH_IN_MS, refresh_gui)
    tk_root.mainloop()
    logic_stop_event.set()
    logic_thread.join()
