#!/usr/bin/env python

from Tkinter import *
from time import sleep
from random import randint
from algorithms import TDLearningAlgorithm
import Queue
import tkMessageBox
import sys
import shapes
import world
import threading

SCALE = 20
OFFSET = 3
MAXX = 10
MAXY = 12

NO_OF_LEVELS = 10

LEFT = "left"
RIGHT = "right"
DOWN = "down"

global tk_root
global controller
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
        keys = self.landed.keys()
        for k in keys:
            block = self.landed.pop(k)
            self.delete_block(block)
            del block

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

    def handle_move(self, direction):
        #if you can't move then you've hit something
        if not self.shape.move(direction):

            # if your heading down then the shape has 'landed'
            if direction == DOWN:
                self.score += self.board.check_for_complete_row(
                    self.shape.blocks
                )
                del self.shape
                self.shape = self.get_next_shape()

                # If the shape returned is None, then this indicates that
                # that the check before creating it failed and the
                # game is over!
                if self.shape is None:
                    self.score = 0
                    self.shape = self.get_next_shape()

                self.status_bar.set("Score: %-7d\t Level: %d " % (
                    self.score, self.level + 1)
                )

                # Signal that the shape has 'landed'
                return False
        return True

    def left_callback(self, event):
        if self.shape:
            self.shape.move(LEFT)
            #self.handle_move( LEFT )

    def right_callback(self, event):
        if self.shape:
            self.shape.move(RIGHT)
            #self.handle_move( RIGHT )

    def up_callback(self, event):
        if self.shape:
            # drop the tetrominoe to the bottom
            while self.handle_move(DOWN):
                pass

    def down_callback(self, event):
        if self.shape:
            self.shape.move(DOWN)
            #self.handle_move( DOWN )

    def a_callback(self, event):
        dataQ.put(10)
        self.board.clear()
        s = world.State()
        s = s.place_shape(world.OShape(), 0)
        s = s.place_shape(world.IShape(), 3)
        s = s.place_shape(world.OShape(), 0)
        s = s.place_shape(world.OShape(), 1)
        s = s.place_shape(world.OShape(), 8)
        s = s.place_shape(world.OShape(), 7)
        s = s.place_shape(world.ZShape(), 7)
        s = s.place_shape(world.SShape(), 7)
        s = s.place_shape(world.JShape(), 2)
        s = s.place_shape(world.LShape(), 1)
        s = s.place_shape(world.TShape(), 5)

        blocks = s.blocks
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

        #if self.shape:
        #    self.shape.rotate(clockwise=True)

    def s_callback(self, event):
        if self.shape:
            self.shape.rotate(clockwise=False)

    def p_callback(self, event):
        self.parent.after_cancel(self.after_id)
        tkMessageBox.askquestion(
            title="Paused!",
            message="Continue?",
            type=tkMessageBox.OK)
        self.after_id = self.parent.after(self.delay, self.move_my_shape)

    def setpos_callback(self, event):
        if self.shape:
            self.handle_move(LEFT)
            self.handle_move(LEFT)
            self.handle_move(LEFT)
            self.handle_move(LEFT)

            for idx in xrange(event):
                self.handle_move(RIGHT)

    def clear_callback(self, event):
        self.board.clear()
        self.shape = self.get_next_shape()

    def move_my_shape(self):
        if self.shape:
            self.handle_move(DOWN)
            self.after_id = self.parent.after(self.delay, self.move_my_shape)

    def get_next_shape(self):
        """
        Randomly select which tetrominoe will be used next.
        """
        the_shape = self.shapes[0]
        #the_shape = self.shapes[ randint(0,len(self.shapes)-1) ]
        return the_shape.check_and_create(self.board)

def update_state():
    try:
        item = dataQ.get(timeout=0.1)
        if item:
            print "item"
    except:
        pass
    tk_root.after(1000, update_state)


def run():
    algo = TDLearningAlgorithm()
    algo.run(100)


if __name__ == "__main__":
    tk_root = Tk()
    tk_root.title("tetris agent")
    controller = game_controller(tk_root)
    logic_thread = threading.Thread(target=run)
    logic_thread.start()
    tk_root.after(1000, update_state)
    tk_root.mainloop()
    logic_thread.join()
