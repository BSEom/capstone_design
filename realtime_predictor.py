#-*-coding:utf-8-*-
#!/usr/bin/python
#
# Run sound classifier in realtime.
#
from common import *

import os
import sys
import time
import array
import numpy as np
import queue
from collections import deque
import argparse
import pymysql

parser = argparse.ArgumentParser(description='Run sound classifier')
parser.add_argument('--input', '-i', default='0', type=int,
                    help='Audio input device index. Set -1 to list devices')
parser.add_argument('--input-file', '-f', default='', type=str,
                    help='If set, predict this audio file.')
#parser.add_argument('--save_file', default='recorded.wav', type=str,
#                    help='File to save samples captured while running.')
parser.add_argument('--model-pb-graph', '-pb', default='', type=str,
                    help='Feed model you want to run, or conf.runtime_weight_file will be used.')
args = parser.parse_args()

result_label=[]
result_percent=[0]
final_result=''

def most_frequent(result_label):
    global final_result
    final_result= max(result_label, key=result_label.count)
    if final_result!='baby': #최다 결과가 아기가 아님
        if max(result_percent)>=0.6: #아기 정확도 최대치가 0.6 이상
            final_result='baby' #결과=baby
    #print(conf.labels[result_label])

# # Capture & pridiction jobs
raw_frames = queue.Queue(maxsize=100)
def callback(in_data, frame_count, time_info, status):
    wave = array.array('h', in_data)
    raw_frames.put(wave, True)
    return (None, pyaudio.paContinue)

def on_predicted(ensembled_pred):
    result = np.argmax(ensembled_pred)
    result_label.append(conf.labels[result])
    if conf.labels[result]=='baby': #결과가 아기일 때
        result_percent.append(ensembled_pred[result]) #정확도를 리스트에 저장
    most_frequent(result_label)
    print(conf.labels[result], ensembled_pred[result])

raw_audio_buffer = []
pred_queue = deque(maxlen=conf.pred_ensembles)
def main_process(model, on_predicted):
    # Pool audio data
    global raw_audio_buffer
    while not raw_frames.empty():
        raw_audio_buffer.extend(raw_frames.get())
        if len(raw_audio_buffer) >= conf.mels_convert_samples: break
    if len(raw_audio_buffer) < conf.mels_convert_samples: return
    # Convert to log mel-spectrogram
    audio_to_convert = np.array(raw_audio_buffer[:conf.mels_convert_samples]) / 32767
    raw_audio_buffer = raw_audio_buffer[conf.mels_onestep_samples:]
    mels = audio_to_melspectrogram(conf, audio_to_convert)
    # Predict, ensemble
    X = []
    for i in range(conf.rt_process_count):
        cur = int(i * conf.dims[1] / conf.rt_oversamples)
        X.append(mels[:, cur:cur+conf.dims[1], np.newaxis])
    X = np.array(X)
    samplewise_normalize_audio_X(X)
    raw_preds = model.predict(X)
    for raw_pred in raw_preds:
        pred_queue.append(raw_pred)
        ensembled_pred = geometric_mean_preds(np.array([pred for pred in pred_queue]))
        on_predicted(ensembled_pred)

# # Main controller
def process_file(model, filename, on_predicted=on_predicted):
    # Feed audio data as if it was recorded in realtime
    audio = read_audio(conf, filename, trim_long_data=False) * 32767
    while len(audio) > conf.rt_chunk_samples:
        raw_frames.put(audio[:conf.rt_chunk_samples])
        audio = audio[conf.rt_chunk_samples:]
        main_process(model, on_predicted)

def my_exit(model):
    model.close()
    exit(0)

def get_model(graph_file):
    model_node = {
        'alexnet': ['import/conv2d_1_input',
                    'import/batch_normalization_1/keras_learning_phase',
                    'import/output0'],
        'mobilenetv2': ['import/input_1',
                        'import/bn_Conv1/keras_learning_phase',
                        'import/output0']
    }

    return KerasTFGraph(
        conf.runtime_model_file if graph_file == '' else graph_file,
        input_name=model_node[conf.model][0],
        keras_learning_phase_name=model_node[conf.model][1],
        output_name=model_node[conf.model][2])

def run_predictor():
    #model = get_model(args.model_pb_graph)
    model=get_model('(ex4)jw_a.pb')
    # file mode
    if args.input_file == '': #(원래는!=조건)
        
        count = 1;
        
        try:
    #DB Connection 생성
            conn = pymysql.connect(host='localhost', user='root', password='1234', db='wavdb', charset='utf8') 
            cursor = conn.cursor() 
        
        except:
            print("non_connect")
        
        
        while True:
            filename = '/workspace/gpu_server/uploads/'+str(count)+'_demo.wav'
            
            if os.path.isfile(filename):
                flag_3 = time.time()
                print(count)
                process_file(model, filename) #인자가 없을 때 자동으로 이 파일 사용
                print(final_result)
                
                query = "INSERT INTO classification (file_name, class) VALUE ('"+str(count)+"_demo.wav', '"+final_result+"')"
                cursor.execute(query)
                conn.commit() 
                count = count + 1
                print('분류 시간: ', time.time()-flag_3)
                result_label.clear()
                result_percent.clear()  # 분류 정확도 리스트
                result_percent.append(0)
                
            else:
        	    print("there is no file"+filename)
        	    time.sleep(0.05)
               #time.sleep(0.05)
        my_exit(model)
    # device list display mode
    if args.input < 0:
        print_pyaudio_devices()
        my_exit(model)
    # normal: realtime mode
    
    # main loop
    my_exit(model)

if __name__ == '__main__':
    run_predictor()
