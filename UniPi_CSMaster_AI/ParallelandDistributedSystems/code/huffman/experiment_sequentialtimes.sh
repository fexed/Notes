make seq 1> /dev/null
sum=0
for i in {1..10}
do
    tmp=$(./huffman_seq longfile)
    sum=$(($sum + $tmp))
    #echo $tmp
done
sum=$(($sum/10))
echo $sum