#!/usr/bin/env python

from Tkinter import *
import Queue
import threading

from agent import TDLearningAgentSlow
import shapes
import environment

SCALE = 30

import shapes
import environment


SCALE = 20
OFFSET = 3
MAXX = 10
MAXY = 12

LEFT = "left"
RIGHT = "right"
DOWN = "down"

REFRESH_IN_MS = 100

global environment
global tk_root
global controller
global dataQ
dataQ = Queue.Queue(maxsize=0)

direction_d = {"left": (-1, 0), "right": (1, 0), "down": (0, 1)}


class status_bar(Frame):
    """
    Status bar to display the score and level
    """

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.label = Label(self, bd=1, relief=SUNKEN, anchor=W)
        self.label.pack(fill=X)

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(test="")
        self.label.update_idletasks()


class Board(Frame):
    """
    The board represents the tetris playing area. A grid of x by y blocks.
    """

    def __init__(self, parent, scale=20, max_x=10, max_y=20, offset=3):
        """
        Init and config the tetris board, default configuration:
        Scale (block size in pixels) = 20
        max X (in blocks) = 10
        max Y (in blocks) = 20
        offset (in pixels) = 3
        """
        Frame.__init__(self, parent)

        # blocks are indexed by there corrdinates e.g. (4,5), these are
        self.landed = {}
        self.parent = parent
        self.scale = scale
        self.max_x = max_x
        self.max_y = max_y
        self.offset = offset

        self.canvas = Canvas(parent,
                             height=(max_y * scale) + offset,
                             width=(max_x * scale) + offset)
        self.canvas.pack()

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
        for y in xrange(self.max_y - 1, -1, -1):
            row_is_empty = True
            for x in xrange(self.max_x):
                if self.landed.get((x, y), None):
                    row_is_empty = False
                    break;
            if row_is_empty:
                empty_row = y
                break

        # Now scan up and until a complete row is found. 
        y = self.max_y - 1
        while y > empty_row:

            complete_row = True
            for x in xrange(self.max_x):
                if self.landed.get((x, y), None) is None:
                    complete_row = False
                    break;

            if complete_row:
                rows_deleted += 1

                #delete the completed row
                for x in xrange(self.max_x):
                    block = self.landed.pop((x, y))
                    self.delete_block(block)
                    del block


                # move all the rows above it down
                for ay in xrange(y - 1, empty_row, -1):
                    for x in xrange(self.max_x):
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

        #self.output() # non-gui diagnostic

        # return the score, calculated by the number of rows deleted.        
        return (100 * rows_deleted) * rows_deleted

    def output(self):
        for y in xrange(self.max_y):
            line = []
            for x in xrange(self.max_x):
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
        rx = (x * self.scale) + self.offset
        ry = (y * self.scale) + self.offset

        return self.canvas.create_rectangle(
            rx, ry, rx + self.scale, ry + self.scale, fill=colour
        )

    def move_block(self, id, coord):
        """
        Move the block, identified by 'id', by x and y. Note this is a
        relative movement, e.g. move 10, 10 means move 10 pixels right and
        10 pixels down NOT move to position 10,10. 
        """
        x, y = coord
        self.canvas.move(id, x * self.scale, y * self.scale)

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
        if x < 0 or x >= self.max_x or y < 0 or y >= self.max_y:
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

        #lookup table
        self.shapes = [shapes.SquareShape,
                       shapes.TShape,
                       shapes.LShape,
                       shapes.ReverseLShape,
                       shapes.ZShape,
                       shapes.SShape,
                       shapes.IShape]

        self.status_bar = status_bar(parent)
        self.status_bar.pack(side=TOP, fill=X)
        #print "Status bar width",self.status_bar.cget("width")

        self.status_bar.set("Score: %-7d\t Level: %d " % (
            self.score, self.level + 1)
        )

        quitButton = Button(parent, text="Quit",
            command=parent.quit)
        quitButton.place(x=0, y=0)

        self.board = Board(
            parent,
            scale=SCALE,
            max_x=MAXX,
            max_y=MAXY,
            offset=OFFSET
        )

        self.board.pack(side=BOTTOM)

        self.parent.bind("a", self.a_callback)

    def a_callback(self, event):
        print self.board.landed
        self.board.clear()

    def update_board(self, state):
        self.board.clear()
        blocks = state.blocks
        for r in range(len(blocks)):
            for c in range(len(blocks[r])):
                if blocks[r][c] is "o":
                    self.board.add_block((r, c), "yellow")
                if blocks[r][c] is "i":
                    self.board.add_block((r, c), "cyan")
                if blocks[r][c] is "z":
                    self.board.add_block((r, c), "red")
                if blocks[r][c] is "s":
                    self.board.add_block((r, c), "green")
                if blocks[r][c] is "j":
                    self.board.add_block((r, c), "blue")
                if blocks[r][c] is "l":
                    self.board.add_block((r, c), "orange")
                if blocks[r][c] is "t":
                    self.board.add_block((r, c), "magenta")


    def clear_callback(self, event):
        self.board.clear()


def update_state():
    while True:
        try:
            item = dataQ.get(timeout=0.1)
        except:
            break
    controller.update_board(environment)
    tk_root.after(REFRESH_IN_MS, update_state)


def run(stop_event):
    global environment
    agent = TDLearningAgentSlow()
    agent.dataQ = dataQ
    environment = agent.environment
    agent.stop_event = stop_event
    agent.run(REFRESH_IN_MS)


if __name__ == "__main__":
    tk_root = Tk()
    tk_root.title("tetris agent")
    controller = game_controller(tk_root)
    logic_stop_event = threading.Event()
    logic_thread = threading.Thread(target=run, args=(logic_stop_event,))
    logic_thread.start()
    tk_root.after(REFRESH_IN_MS, update_state)
    tk_root.mainloop()
    logic_stop_event.set()
    logic_thread.join()
