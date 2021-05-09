from tkintertable import TableCanvas, TableModel
from tkinter import *
import csv


class MyTableModel(TableModel):

    def __init__(self, filename):
        with open(filename) as the_file:
            self.data_rows = self.read_data(the_file)
            column_count = len(self.data_rows[0])
            super(MyTableModel, self).__init__(columns=column_count)
            self.columntypes = {str(col): 'text' for col in range(column_count)}

    def read_data(self, the_file):
        self.skip_metadata(the_file)
        reader = csv.reader(the_file, delimiter=';')
        result = [row for row in reader]
        self.make_equal_length(result)
        self.fill_in_column_headers(result)
        return result

    @staticmethod
    def fill_in_column_headers(rows):
        number_of_header_rows = 3
        for row in rows[:number_of_header_rows]:
            header_to_replicate = ""
            for col_index, column_header in enumerate(row):
                if column_header and column_header != header_to_replicate:
                    header_to_replicate = column_header
                if not column_header:
                    row[col_index] = header_to_replicate

    @staticmethod
    def make_equal_length(rows):
        max_length = max([len(row) for row in rows])
        for row in rows:
            row += [''] * (max_length - len(row))

    @staticmethod
    def skip_metadata(the_file):
        line = next(the_file)
        while 'START OF COLLECTION' not in line:
            line = next(the_file)

    def getColumnName(self, colIndex):
        return str(colIndex)

    def getColCells(self, colIndex):
        return [row[colIndex] for row in self.data_rows]

    def getRowCount(self):
        return len(self.data_rows)

    def getRecordAtRow(self, rowIndex):
        return self.data_rows[rowIndex]

    def getCellRecord(self, rowIndex, columnIndex):
        return self.data_rows[rowIndex][columnIndex]


class MyTableCanvas(TableCanvas):

    def redrawVisible(self, event=None, callback=None):
        """Redraw the visible portion of the canvas"""

        model = self.model
        self.rows = self.model.getRowCount()
        self.cols = self.model.getColumnCount()

        self.tablewidth = (self.cellwidth) * self.cols
        self.configure(bg=self.cellbackgr)
        self.setColPositions()

        # are we drawing a filtered subset of the recs?
        if self.filtered is True and self.model.filteredrecs is not None:
            self.rows = len(self.model.filteredrecs)
            self.delete('colrect')

        self.rowrange = range(0, self.rows)
        self.configure(scrollregion=(0, 0, self.tablewidth + self.x_start,
                                     self.rowheight * self.rows + 10))

        x1, y1, x2, y2 = self.getVisibleRegion()
        startvisiblerow, endvisiblerow = self.getVisibleRows(y1, y2)
        self.visiblerows = range(startvisiblerow, endvisiblerow)
        startvisiblecol, endvisiblecol = self.getVisibleCols(x1, x2)
        self.visiblecols = range(startvisiblecol, endvisiblecol)

        if self.cols == 0 or self.rows == 0:
            self.delete('entry')
            self.delete('rowrect')
            self.delete('currentrect')
            self.delete('gridline', 'text')
            self.tablerowheader.redraw()
            return

        # self.drawGrid(startvisiblerow, endvisiblerow)
        align = self.align
        self.delete('fillrect')
        self.drawData(model, align)

        # self.drawSelectedCol()
        self.tablecolheader.redraw()
        self.tablerowheader.redraw(align=self.align, showkeys=self.showkeynamesinheader)
        # self.setSelectedRow(self.currentrow)
        self.drawSelectedRow()
        self.drawSelectedRect(self.currentrow, self.currentcol)
        # print self.multiplerowlist

        if len(self.multiplerowlist) > 1:
            self.tablerowheader.drawSelectedRows(self.multiplerowlist)
            self.drawMultipleRows(self.multiplerowlist)
            self.drawMultipleCells()

    def drawData(self, model, align):
        bgcolor = model.getColorAt(0, 0, 'bg')
        fgcolor = model.getColorAt(0, 0, 'fg')
        for row in self.visiblerows:
            for col in self.visiblecols:
                text = model.getValueAt(row, col)
                self.drawText(row, col, text, fgcolor, align)
                if bgcolor is not None:
                    self.drawRect(row, col, color=bgcolor)

    def drawCellEntry(self, row, col, text=None):
        pass

    def adjustColumnWidths(self):
        """Optimally adjust col widths to accomodate the longest entry
            in each column - usually only called  on first redraw"""

        try:
            fontsize = self.thefont[1]
        except:
            fontsize = self.fontsize
        scale = 8.5 * float(fontsize)/12
        for col in range(self.cols):
            colname = self.model.getColumnName(col)
            if colname in self.model.columnwidths:
                w = self.model.columnwidths[colname]
            else:
                w = self.cellwidth
            # Increase maxlen by a factor of 1.5 (obtained by trial and error)
            # to account for the wider, uppercase names in some column headers
            maxlen = self.model.getlongestEntry(col) * 1.5
            size = maxlen * scale
            if size < w:
                continue
            self.model.columnwidths[colname] = size + float(fontsize)/12*6
        return

    def handle_arrow_keys(self, event):
        super(MyTableCanvas, self).handle_arrow_keys(event)
        cell_rect = Rectangle(self.getCellCoords(self.currentrow, self.currentcol))
        moved_x = self.pan_to_reveal(cell_rect)
        moved_y = self.scroll_to_reveal(cell_rect)
        if moved_x or moved_y:
            self.redrawVisible()

    def scroll_to_reveal(self, target_rect):
        viewport_rect = self.get_visible_rectangle()
        move_to_y = None
        if target_rect.top < viewport_rect.top:
            move_to_y = target_rect.top
        elif target_rect.bottom > viewport_rect.bottom:
            move_to_y = target_rect.bottom - (viewport_rect.height - target_rect.height)
        if move_to_y:
            move_to_y /= self.rowheight * self.rows
            self.yview('moveto', move_to_y)
            self.tablerowheader.yview('moveto', move_to_y)
        return move_to_y

    def pan_to_reveal(self, target_rect):
        viewport_rect = self.get_visible_rectangle()
        move_to_x = None
        if target_rect.left < viewport_rect.left:
            move_to_x = target_rect.left
        elif target_rect.right > viewport_rect.right:
            move_to_x = target_rect.right - (viewport_rect.width - target_rect.width)
        if move_to_x:
            move_to_x /= self.tablewidth
            self.xview('moveto', move_to_x)
            self.tablecolheader.xview('moveto', move_to_x)
        return move_to_x

    def get_visible_rectangle(self):
        return Rectangle(self.getVisibleRegion())


class Rectangle:

    def __init__(self, bounds):
        self.left = bounds[0]
        self.top = bounds[1]
        self.right = bounds[2]
        self.bottom = bounds[3]

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.bottom - self.top


class Viewer(Frame):

    def __init__(self, parent=None):
        self.parent = parent
        Frame.__init__(self)
        self.main = self.master
        self.main.geometry('800x500+200+100')
        self.main.title(sys.argv[1])
        f = Frame(self.main)
        f.pack(fill=BOTH, expand=1)
        table = MyTableCanvas(f, model=MyTableModel(sys.argv[1]))
        table.show()


app = Viewer()
app.mainloop()
