
rm -r tmpdata
rm -r dst
mkdir tmpdata
fn=$1
mkdir dst
unzip $fn -d tmpdata
dst_index=0
cat tmpdata/vol.opf | grep 'html' | while read line
do
    echo $line
    # 补齐4位数字 
    dst_index=$((dst_index+1))
    name_index=$(printf "%04d" $dst_index)
    src_html=$(echo $line | awk -F '"' '{print $4}')
    src_pic=$(cat tmpdata/$src_html | grep 'img' | awk -F '"' '{print $2}' | sed 's/\.\.//g')
    echo "tmpdata"$src_pic $name_index
    suffix=$(echo $src_pic | awk -F '.' '{print $2}')
    cp tmpdata/$src_pic dst/$name_index.$suffix
done
open dst
