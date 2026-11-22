# mux.sh clip voice out [delay_s] [maxdur]
c=$1; v=$2; o=$3; dl=${4:-0.3}
cd_=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $c)
vd=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $v)
T=$(python3 -c "print(max($cd_, $dl+$vd+0.3))")
P=$(python3 -c "print(max(0,$T-$cd_))")
ms=$(python3 -c "print(int($dl*1000))")
ffmpeg -loglevel error -y -i $c -i $v -filter_complex "[0:v]tpad=stop_mode=clone:stop_duration=$P[v];[0:a]volume=0.35,apad[a0];[1:a]adelay=$ms:all=1,volume=1.0,apad[a1];[a0][a1]amix=inputs=2:normalize=0[a]" -map '[v]' -map '[a]' -t $T -c:v libx264 -pix_fmt yuv420p -crf 20 -c:a aac -b:a 160k $o
echo $o $T
