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



# 品字

magick -size 2100x2960 xc:white \
-background none \
-compose over \
\( xfefm/001.jpg -resize 900x1400^ -set page +600+50 \) \
\( xfefm/pdf_img-000.jpg -resize 900x1400^ -set page +50+1500 \) \
\( xfefm/pdf_img-003.jpg -resize 900x1400^ -set page +1050+1500 \) \
-layers merge \
final_pinshape_3pics.jpg


# 倒品
magick -size 2100x2960 xc:white \
-background none \
-compose over \
\( bxyq/0000.jpg -resize 900x1400^ -set page +20+100 \) \
\( bxyq/0149.jpg -resize 900x1400^ -set page +1050+100 \) \
\( bxyq/0500.jpg -resize 900x1400^ -set page +550+1550 \) \
-layers merge \
final_pinshape_3pics.jpg