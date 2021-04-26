# arguments
Num=$1
Prefix=$2 # template_batch6

# generate tex files
python main.py --pageNum $Num --prefix $Prefix

# generate pdf files
for ((it=0; it<Num; it++))
do
    pdflatex -interaction=nonstopmode $Prefix$it.tex
done

# convert to image
for ((it=0; it<Num; it++))
do
    echo $it
    convert -density 300 $Prefix$it.pdf -filter lagrange -distort resize 33% -background white -alpha remove -quality 100 $Prefix$it.jpg
done

# visualize
# python generate_xml.py -I "$Prefix"*.jpg # --visualize
