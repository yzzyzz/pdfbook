magick \
  \( "0010.jpg" -resize 2480x1754\> -background white -gravity center -extent 2480x1754 \) \
  \( "0011.jpg" -resize 2480x1754\> -background white -gravity center -extent 2480x1754 \) \
  +append \
  -units PixelsPerInch -density 300x300 \
  "merged_output.pdf"
