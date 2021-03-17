from tkintertable import TableCanvas, TableModel
from tkinter import *
import csv


class MyTableModel(TableModel):

    def __init__(self, filename):
        with open(filename) as the_file:
            self.skip_metadata(the_file)
            reader = csv.reader(the_file, delimiter=';')
            self.data_rows = [row for row in reader]
            column_count = len(self.data_rows[0])
            super().__init__(columns=column_count)
            self.columntypes = {str(col): 'text' for col in range(column_count)}

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

        #are we drawing a filtered subset of the recs?
        if self.filtered == True and self.model.filteredrecs != None:
            self.rows = len(self.model.filteredrecs)
            self.delete('colrect')

        self.rowrange = range(0,self.rows)
        self.configure(scrollregion=(0,0, self.tablewidth+self.x_start,
                self.rowheight*self.rows+10))

        x1, y1, x2, y2 = self.getVisibleRegion()
        startvisiblerow, endvisiblerow = self.getVisibleRows(y1, y2)
        self.visiblerows = range(startvisiblerow, endvisiblerow)
        startvisiblecol, endvisiblecol = self.getVisibleCols(x1, x2)
        self.visiblecols = range(startvisiblecol, endvisiblecol)

        if self.cols == 0 or self.rows == 0:
            self.delete('entry')
            self.delete('rowrect')
            self.delete('currentrect')
            self.delete('gridline','text')
            self.tablerowheader.redraw()
            return

        #self.drawGrid(startvisiblerow, endvisiblerow)
        align = self.align
        self.delete('fillrect')
        self.drawData(model, align)

        #self.drawSelectedCol()
        self.tablecolheader.redraw()
        self.tablerowheader.redraw(align=self.align, showkeys=self.showkeynamesinheader)
        #self.setSelectedRow(self.currentrow)
        self.drawSelectedRow()
        self.drawSelectedRect(self.currentrow, self.currentcol)
        #print self.multiplerowlist

        if len(self.multiplerowlist)>1:
            self.tablerowheader.drawSelectedRows(self.multiplerowlist)
            self.drawMultipleRows(self.multiplerowlist)
            self.drawMultipleCells()

    def drawData(self, model, align):
        bgcolor = model.getColorAt(0, 0, 'bg')
        fgcolor = model.getColorAt(0, 0, 'fg')
        for row in self.visiblerows:
            for col in self.visiblecols:
                text = model.getValueAt(row,col)
                self.drawText(row, col, text, fgcolor, align)
                if bgcolor is not None:
                    self.drawRect(row,col, color=bgcolor)


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
