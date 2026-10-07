# SPDX-License-Identifier: MIT
"""Find quiet source chunk edges for local Whisper; never export audio slices."""
import argparse,json,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--runtime',required=True);p.add_argument('--input',required=True);p.add_argument('--output',required=True);a=p.parse_args()
sys.path.insert(0,a.runtime)
import imageio_ffmpeg,numpy as np
raw=subprocess.check_output([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',a.input,'-f','f32le','-ac','1','-ar','16000','pipe:1'])
y=np.frombuffer(raw,dtype='<f4');step=160
rms=20*np.log10(np.maximum(np.sqrt(np.mean(y[:len(y)//step*step].reshape(-1,step)**2,axis=1)),1e-9))
dur=len(y)/16000;start=0;result=[]
while start<dur:
 if dur-start<=29.9:end=dur
 else:
  low=int((start+22)*100);high=min(len(rms),int((start+29.5)*100))
  j=min(range(low,high),key=lambda i:float(np.mean(rms[max(0,i-5):i+6])))
  end=j/100
 result.append({'role':'Reciter source window '+str(len(result)+1),'start':start,'end':end})
 start=end
Path(a.output).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('Planned',len(result),'quiet-edge analysis windows; source duration',dur)
