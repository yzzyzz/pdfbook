magick \
  \( "0011.jpg" -resize "1754x1240>" -background white -gravity center -extent 1754x1240 \) \
  \( "0012.jpg" -resize "1754x1240>" -background white -gravity center -extent 1754x1240 \) \
  -append \
  -page "1754x2480" \
  -units PixelsPerInch \
  -density 300 \
  "merged_output.pdf"
open "merged_output.pdf"