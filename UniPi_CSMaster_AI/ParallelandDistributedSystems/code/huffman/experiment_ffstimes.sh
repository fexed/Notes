echo "FastFlow implementation"
for nw in {1..200}
do
    make fastflow NW=$nw 1> /dev/null
    sum=0
    for i in {1..10}
    do
        tmp=$(./huffman_fastflow longfile)
        sum=$(($sum + $tmp))
        #echo $tmp
    done
    sum=$(($sum/10))
    echo "$nw -> $sum usec"
    echo "$nw;$sum" >> data_fastflow
done