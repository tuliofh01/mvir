#!python3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter, tkinter.filedialog
import _thread , os
import time
import win32api
import pyaudio, pydub
import wave, numpy
import matplotlib, pylab
import matplotlib.animation


class Player:

    def __init__(self, plot_bg = '#101010', line_fg = 'white',
                 line_width = 1.5, chunk_size = 256):
        matplotlib.use('TkAgg')
        #CONFIG VARIABLES
        self.plot_bg = plot_bg
        self.line_fg = line_fg
        self.line_width = line_width
        self.chunk_size = chunk_size
        #CONTROL VARIABLES
        self.frame, self.song = 0,0
        self.pause, self.switch = False, False
        #PLAYER CALL
        self.player()

    def player(self):
        self.wf = wave.open(self.player_stack(self.song)[1], 'rb')
        p = pyaudio.PyAudio()
        self.stream = p.open(format=p.get_format_from_width(self.wf.getsampwidth()),
                             channels=self.wf.getnchannels(),
                             rate=self.wf.getframerate(),
                             output=True)
        data = self.wf.readframes(self.chunk_size)
        self.song_length = self.wf.getnframes() / self.chunk_size
        while True:
            try:
                print(self.song_length, self.frame)
                self.frame += 1
                self.stream.write(data)
                data = self.wf.readframes(self.chunk_size)
                self.data_array = numpy.fromstring(data, dtype=numpy.int16)
                if self.frame == 1:
                    try:
                        _thread.start_new_thread(self.tk_widget, ())
                    except:
                        print(666)
                elif self.frame == int(self.song_length) or self.switch:
                    if self.song != self.player_stack()[0] - 1:
                        self.song += 1
                        self.frame = 0
                    else:
                        self.song = 0
                        self.frame = 0
                    self.wf = wave.open(self.player_stack(self.song)[1], 'rb')
                    self.stream = p.open(format=p.get_format_from_width(self.wf.getsampwidth()),
                             channels=self.wf.getnchannels(),
                             rate=self.wf.getframerate(),
                             output=True)
                    self.switch = False
                self.song_length = self.wf.getnframes() / self.chunk_size
            except Exception as ex:
                print(' '.join(['Error:', ex]))
                

    def tk_widget(self):
        root = tkinter.Tk()
        root.overrideredirect(True)
        # 1280x1024 resolution
        root.geometry('+%s+%s' % (str(int(win32api.GetSystemMetrics(0)/2 + 160)), str(int(win32api.GetSystemMetrics(1)/2+291))))
        root.wm_attributes("-transparentcolor", "linen")
        fig = matplotlib.pyplot.figure(figsize=(6, 2), facecolor='linen')
        ax1 = fig.add_subplot(1, 1, 1)
        button_frame_bottom = tkinter.Frame(bg='#323232', bd=0)
        button_frame_bottom.pack(side='bottom', fill='both', expand=True)

        def animate(i):
            ax1.clear()
            ax1.axis([0, len(self.data_array), -(10 ** 5) / 4, (10 ** 5) / 3])
            cur_axes = pylab.gca()
            cur_axes.axes.get_xaxis().set_visible(False)
            cur_axes.axes.get_yaxis().set_visible(False)
            cur_axes.spines['top'].set_visible(False)
            cur_axes.spines['right'].set_visible(False)
            cur_axes.spines['bottom'].set_visible(False)
            cur_axes.spines['left'].set_visible(False)
            ax1.set_axis_bgcolor(self.plot_bg)
            ax1.plot(self.data_array, linewidth=self.line_width, c=self.line_fg)

        def switch_song():
            self.switch = True
            _thread.start_new_thread(self.tk_widget, ())
            root.destroy()
            
        def pause():
            if self.pause:
                self.pause = False
                self.wf = wave.open(self.player_stack(self.song)[1], 'rb')
                p = pyaudio.PyAudio()
                self.stream = p.open(format=p.get_format_from_width(self.wf.getsampwidth()),
                        channels=self.wf.getnchannels(),
                        rate=self.wf.getframerate(),
                        output=True)
            else:self.pause = True
            self.frame = 0
            def p1():
                while self.pause:self.wf = wave.open('void.wav', 'rb')
            _thread.start_new(p1, ())

        def StartMove(event):
            self.x = event.x
            self.y = event.y

        def StopMove(event):
            self.x = None
            self.y = None

        def OnMotion(event):
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = root.winfo_x() + deltax
            y = root.winfo_y() + deltay
            root.geometry("+%s+%s" % (x, y))

        canvas = FigureCanvasTkAgg(fig, root)
        canvas.get_tk_widget().pack()
        ani = matplotlib.animation.FuncAnimation(fig, animate, interval=1)
        drag_button = tkinter.Button(root, bg='#626262', bd=0, height=19)
        drag_arrow = tkinter.PhotoImage(file='drag_arrow.gif')
        drag_button.config(image=drag_arrow, command=pause)

        def drag_bind():
            drag_button.bind("<ButtonPress-1>", StartMove)
            drag_button.bind("<ButtonRelease-1>", StopMove)
            drag_button.bind("<B1-Motion>", OnMotion)

        _thread.start_new_thread(drag_bind, ())
        drag_button.pack(in_=button_frame_bottom, side='right')
        play_button = tkinter.Button(root, bg='#626262', bd=0, height=19)
        play_arrow = tkinter.PhotoImage(file='play_arrow.gif')
        play_button.config(image=play_arrow, command=pause)
        play_button.pack(in_=button_frame_bottom, side='left')
        forward_button = tkinter.Button(root, bg='#626262', bd=0, height=19)
        forward_arrow = tkinter.PhotoImage(file='forward_arrow.gif')
        forward_button.config(image=forward_arrow, command=switch_song)
        forward_button.pack(in_=button_frame_bottom, side='left')
        frame_str = tkinter.StringVar()
        frame_rate_label = tkinter.Label(root, textvariable=frame_str, bg='#323232', bd=0, fg='white')

        def frame_rate_update():
            while True:
                frame_comp = list()
                frame_comp.append(self.frame)
                time.sleep(1)
                frame_comp.append(self.frame)
                fps_rate = (frame_comp[1] - frame_comp[0])
                frame_str.set('| FPS : %s | -- | SONG: %s |' % (str(fps_rate), self.player_stack(self.song)[1][:-4]))
                del frame_comp

        _thread.start_new_thread(frame_rate_update, ())
        frame_rate_label.pack(in_=button_frame_bottom, side='left')
        root.update()
        root.mainloop()

    def list_songs(self):
        #pydub.AudioSegment.ffmpeg = "C:\\ffmpeg\\bin"
        file_list = os.listdir(os.getcwd())
        music_list = list()
        for i in range(len(file_list)):
            if file_list[i][-3:] == 'mp3':
                song = pydub.AudioSegment.from_mp3(file_list[i])
                song.export(file_list[i][:-3] + 'wav', format='wav')
                music_list.append(file_list[i][:-3] + 'wav')
            elif file_list[i][-3:] == 'wav':
                music_list.append(file_list[i])
        del music_list[music_list.index('void.wav')]
        return music_list

    def player_stack(self, song=0):
        music_list = self.list_songs()
        return len(music_list), music_list[song]


if __name__ == '__main__':
    print('Please, copy all your songs to the default folder (%s) ' % os.getcwd())
    art = '''
             d8888  d8b                              888     888 
            d8P888  88P                              888     888 
           d8P 888  8P                               888     888 
 .d8888b  d8P  888  "   .d8888b        88888b.d88b.  Y88b   d88P 
d88P"    d88   888      88K            888 "888 "88b  Y88b d88P  
888      8888888888     "Y8888b.       888  888  888   Y88o88P   
Y88b.          888           X88       888  888  888    Y888P    
 "Y8888P       888       88888P'       888  888  888     Y8P     
                                                                 
                                                                  v1.2
    LIFE IS HELL!
    Welcome "%s"!
    Wanna change the default configurations?
        ''' % win32api.GetUserName()
    print(art)
    o1 = input('(Y/N):')
    if o1 in ['y', 'Y', 'Yes', 'yes', 'YES']:
        bg_color_list = ('red', 'blue', 'green', 'cyan', 'magenta', 'yellow', 'black', 'white')
        line_color_list = ('red', 'blue', 'green', 'cyan', 'magenta', 'yellow', 'black', 'white')
        line_width_list = (0.5, 1, 1.5, 2)
        chunk_size_list = (128, 256, 512, 640, 1024, 1280, 2194)
        for i in bg_color_list: print(i.upper(), end= ' - ')
        custom_plot_bg = input('Set BACKGROUND color:').lower()
        for i in line_color_list: print(i.upper(), end= ' - ')
        custom_line_fg = input('Set LINE color:').lower()
        for i in line_width_list: print(i, end= ' - ')
        custom_line_width = float(input('Set LINE width:'))
        for i in chunk_size_list: print(i, end= ' - ')
        print('The default value is 256')
        custom_chunk_size = int(input('Set CHUNK size:'))
        Player(plot_bg = custom_plot_bg, line_fg = custom_line_fg,
                    line_width = custom_line_width, chunk_size = custom_chunk_size)
    else:
        Player()
