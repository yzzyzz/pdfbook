magick \
  \( "0011.jpg" -resize "1750x1238>" -background white -gravity center -extent 1750x1238 \) \
  \( -size 1750x4 xc:black \) \
  \( "0012.jpg" -resize "1750x1238>" -background white -gravity center -extent 1750x1238 \) \
  -append \
  -page "1750x2480" \
  -units PixelsPerInch \
  -density 300 \
  "merged_output.pdf"

open "merged_output.pdf"