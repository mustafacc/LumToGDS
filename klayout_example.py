import klayout.db as db

ly = db.Layout()

# sets the database unit to 1 nm
ly.dbu = 0.001

# adds a single top cell
top_cell = ly.create_cell("SAMPLE")

# creates a new layer (layer number 1, datatype 0)
layer1 = ly.layer(1, 0)

pattern = """
.#...#.#......###..#...#..###..#...#.#####
.#..#..#.....#...#.#...#.#...#.#...#...#..
.#.#...#.....#...#.#...#.#...#.#...#...#..
.##....#.....#####..#.# .#...#.#...#...#..
.#.#...#.....#...#...#. .#...#.#...#...#..
.#..#..#.....#...#...#. .#...#.#...#...#..
.#...#.#####.#...#...#. ..###...###....#..
"""

# produces pixels from the bitmap as 0.5x0.5 µm
# boxes on a 1x1 µm grid:
y = 8.0
for line in pattern.split("\n"):

  x = 0.0
  for bit in line:

    if bit == "#":
      # creates a rectangle for the "on" pixel
      rect = db.DBox(0, 0, 0.5, 0.5).moved(x, y)
      top_cell.shapes(layer1).insert(rect)

    x += 1.0

  y -= 1.0

# adds an envelope box on layer 2/0
layer2 = ly.layer(2, 0)
envelope = top_cell.dbbox().enlarged(1.0, 1.0)
top_cell.shapes(layer2).insert(envelope)
  
# writes the layout to GDS
ly.write("basic.gds")
