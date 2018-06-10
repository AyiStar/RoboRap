from PyQt5 import QtWidgets, QtGui, QtCore, Qt
from main import RoboRap
import os, sys
import functools
import wave
#import pyaudio
from pydub import AudioSegment
from pydub.playback import play
import threading

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):

        super().__init__()
        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)
        self.setWindowTitle('RoboRap')
        self.show()



class MainWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.roborap = RoboRap()
        self.record_flag = True

        self.status_bar = QtWidgets.QLabel('Welcome!')
        self.status_bar.setAlignment(Qt.Qt.AlignCenter)
        self.bpm_hint = QtWidgets.QLabel('Select BPM')
        self.bpm_hint.setAlignment(Qt.Qt.AlignCenter)
        self.bpm_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.bpm_slider.setRange(240, 480)
        self.bpm_slider.setTickInterval(10)
        self.bpm_slider.setSingleStep(1)
        self.lyrics_input = QtWidgets.QPlainTextEdit()
        self.record_button = QtWidgets.QPushButton('Record')
        self.finish_button = QtWidgets.QPushButton('Finish')
        self.rap_button = QtWidgets.QPushButton('Rap it!')

        self.record_button.clicked.connect(self.on_record_button)
        self.finish_button.clicked.connect(self.on_finish_button)
        self.rap_button.clicked.connect(self.on_rap_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.status_bar)
        layout.addWidget(self.record_button)
        layout.addWidget(self.finish_button)
        layout.addWidget(self.lyrics_input)
        layout.addWidget(self.bpm_hint)
        layout.addWidget(self.bpm_slider)
        layout.addWidget(self.rap_button)
        self.setLayout(layout)



    def on_record_button(self):
        t = threading.Thread(target=self.record_thread)
        t.start()


    def record_thread(self):

        pa=pyaudio.PyAudio()
        stream=pa.open(format = pyaudio.paInt16,channels=1, rate=16000,input=True, frames_per_buffer=8000)
        data=[]
        self.record_flag = True

        # Record
        while True:
            string_audio_data = stream.read(8000)
            data.append(string_audio_data)
            if self.record_flag == False:
                break

        # Save wav file
        wf=wave.open('tmp.wav','wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"".join(data))
        wf.close()
        stream.close()

        # Translate the content
        record_audio = None
        with open('tmp.wav', 'rb') as fp:
            record_audio = fp.read()
        result = self.client.asr(record_audio, 'wav', 16000, {
            'dev_pid': '1537',
            })
        content = result.get('result')[0].replace('，', '\n')
        print(type(content))
        self.lyrics_input.setPlainText(content)


    def on_finish_button(self):
        self.record_flag = False

    def on_rap_button(self):
        t = threading.Thread(target=self.rap_thread)
        t.start()


    def rap_thread(self):
        content = self.lyrics_input.toPlainText().split('\n')
        bpm = self.bpm_slider.value()
        self.roborap.setBPM(bpm)
        print(bpm)
        total_num = len(content)
        rap_sounds = []
        self.status_bar.setText('Rappify: {0}%'.format(0))
        for i, sentence in enumerate(content):
            rap_sounds.append(self.roborap.get_rap(sentence))
            self.status_bar.setText('Rappify: {0}%'.format(100*(i+1)/total_num))
        rap = functools.reduce(lambda x, y: x+y, rap_sounds)
        self.status_bar.setText('Rap done!')
        play(rap)




def main():
    app = QtWidgets.QApplication(sys.argv)
    main_GUI = MainWindow()
    main_GUI.show()
    sys.exit(app.exec_())

def test():
    roborap = RoboRap()
    content = ['一人我饮酒醉', '醉把佳人成双对']
    total_num = len(content)
    rap_sounds = []
    print(content)
    for i, sentence in enumerate(content):
        # self.status_bar.setText('Rappify: {0}%'.format(100*i/total_num))
        print('Rappify: {0}%'.format(100*i/total_num))
        rap_sounds.append(roborap.get_rap(sentence))
    rap = functools.reduce(lambda x, y: x+y, rap_sounds)
    play(rap)



if __name__ == '__main__':
    main()