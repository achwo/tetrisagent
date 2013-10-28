direction_d = {"left": (-1, 0), "right": (1, 0), "down": (0, 1)}

LEFT = "left"
RIGHT = "right"
DOWN = "down"


class Block(object):

    def __init__(self, id, (x, y)):
        self.id = id
        self.x = x
        self.y = y

    def coord(self):
        return (self.x, self.y)


class Shape(object):

    """
    Shapeis the  Base class for the game pieces e.g. square, T, S, Z, L,
    reverse L and I. Shapes are constructed of blocks.
    """
    @classmethod
    def check_and_create(cls, board, coords, colour):
        """
        Check if the blocks that make the Shape can be placed in empty coords
        before creating and returning the Shape instance. Otherwise, return
        None.
        """
        # for coord in coords:
        #    if not board.check_block( coord ):
        #        return None

        return cls(board, coords, colour)

    def __init__(self, board, coords, colour):
        """
        Initialise theShapebase.
        """
        self.board = board
        self.blocks = []

        for coord in coords:
            block = Block(self.board.add_block(coord, colour), coord)

            self.blocks.append(block)

    def move(self, direction):
        """
        Move the blocks in the direction indicated by adding (dx, dy) to the
        current block coordinates
        """
        d_x, d_y = direction_d[direction]

        for block in self.blocks:

            x = block.x + d_x
            y = block.y + d_y

            if not self.board.check_block((x, y)):
                return False

        for block in self.blocks:

            x = block.x + d_x
            y = block.y + d_y

            self.board.move_block(block.id, (d_x, d_y))

            block.x = x
            block.y = y

        return True

    def rotate(self, clockwise=True):
        """
        Rotate the blocks around the 'middle' block, 90-degrees. The
        middle block is always the index 0 block in the list of blocks
        that make up a Shape.
        """
        # TO DO: Refactor for DRY
        middle = self.blocks[0]
        rel = []
        for block in self.blocks:
            rel.append((block.x - middle.x, block.y - middle.y))

        # to rotate 90-degrees (x,y) = (-y, x)
        # First check that the there are no collisions or out of bounds moves.
        for idx in xrange(len(self.blocks)):
            rel_x, rel_y = rel[idx]
            if clockwise:
                x = middle.x + rel_y
                y = middle.y - rel_x
            else:
                x = middle.x - rel_y
                y = middle.y + rel_x

            if not self.board.check_block((x, y)):
                return False

        for idx in xrange(len(self.blocks)):
            rel_x, rel_y = rel[idx]
            if clockwise:
                x = middle.x + rel_y
                y = middle.y - rel_x
            else:
                x = middle.x - rel_y
                y = middle.y + rel_x

            diff_x = x - self.blocks[idx].x
            diff_y = y - self.blocks[idx].y

            self.board.move_block(self.blocks[idx].id, (diff_x, diff_y))

            self.blocks[idx].x = x
            self.blocks[idx].y = y

        return True


class ShapeLimitedRotate(Shape):

    """
    This is a base class for the Shapes like the S, Z and I that don't fully
    rotate (which would result in theShapemoving *up* one block on a 180).
    Instead they toggle between 90 degrees clockwise and then back 90 degrees
    anti-clockwise.
    """
    def __init__(self, board, coords, colour):
        self.clockwise = True
        super(ShapeLimitedRotate, self).__init__(board, coords, colour)

    def rotate(self, clockwise=True):
        """
        Clockwise, is used to indicate if theShapeshould rotate clockwise
        or back again anti-clockwise. It is toggled.
        """
        super(ShapeLimitedRotate, self).rotate(clockwise=self.clockwise)
        if self.clockwise:
            self.clockwise = False
        else:
            self.clockwise = True


class SquareShape(Shape):

    @classmethod
    def check_and_create(cls, board):
        coords = [(4, 0), (5, 0), (4, 1), (5, 1)]
        return super(SquareShape, cls).check_and_create(board, coords, "red")

    def rotate(self, clockwise=True):
        """
        Override the rotate method for the squareShapeto do exactly nothing!
        """
        pass


class TShape(Shape):

    @classmethod
    def check_and_create(cls, board):
        coords = [(4, 0), (3, 0), (5, 0), (4, 1)]
        return super(TShape, cls).check_and_create(board, coords, "yellow")


class LShape(Shape):

    @classmethod
    def check_and_create(cls, board):
        coords = [(4, 0), (3, 0), (5, 0), (3, 1)]
        return super(LShape, cls).check_and_create(board, coords, "orange")


class ReverseLShape(Shape):

    @classmethod
    def check_and_create(cls, board):
        coords = [(5, 0), (4, 0), (6, 0), (6, 1)]
        return super(ReverseLShape, cls).check_and_create(
            board, coords, "green")


class ZShape(ShapeLimitedRotate):

    @classmethod
    def check_and_create(cls, board):
        coords = [(5, 0), (4, 0), (5, 1), (6, 1)]
        return super(ZShape, cls).check_and_create(board, coords, "purple")


class SShape(ShapeLimitedRotate):

    @classmethod
    def check_and_create(cls, board):
        coords = [(5, 1), (4, 1), (5, 0), (6, 0)]
        return super(SShape, cls).check_and_create(board, coords, "magenta")


class IShape(ShapeLimitedRotate):

    @classmethod
    def check_and_create(cls, board):
        coords = [(4, 0), (3, 0), (5, 0), (6, 0)]
        return super(IShape, cls).check_and_create(board, coords, "blue")
