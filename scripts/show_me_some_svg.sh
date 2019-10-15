#!/bin/bash


echo "Generating G(5, 3, 2)..."
./gen_gnrs.py 5 3 2 > g532.dot
echo "Converting it to SVG..."
dot -Tsvg g532.dot -o g532.svg
echo "Done! Open g532.svg and enjoy"
