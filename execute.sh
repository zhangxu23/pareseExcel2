. /etc/profile

downloadstr="python3 downloadexcel.py $1"
#echo $downloadstr
/bin/cp  file/ tempfile/ -rf
rm -rf file/*
rm  -rf  unzipfile/*
result=`eval $downloadstr`
#echo $result
if [ $result = '下载成功' ]
then
    #echo $result
    python3 unrarfile.py 
    python3 parseExcel.py >a.log
    echo 'true'
else
    echo 'file download failed'
fi

