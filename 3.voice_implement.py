#voice command implement kora hoise but slow

from tkinter import filedialog, PhotoImage, Listbox, Scale, Menu, Button, Label, Frame, Tk, END
import pygame
import os
import random
import threading
import time
import speech_recognition as sr
from mutagen.mp3 import MP3

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title('Melody')
        self.root.geometry("600x400")

        pygame.mixer.init()

        self.menubar = Menu(self.root)
        self.root.config(menu=self.menubar)

        self.songs = []
        self.current_song = ""
        self.paused = False
        self.shuffle = False
        self.repeat = False

        self.organise_menu = Menu(self.menubar, tearoff=False)
        self.organise_menu.add_command(label='Select Folder', command=self.load_music)
        self.menubar.add_cascade(label='Organise', menu=self.organise_menu)

        self.songlist = Listbox(self.root, bg="black", fg="white", width=100, height=15)
        self.songlist.pack()

        self.play_btn_image = PhotoImage(file='images/play.png')
        self.pause_btn_image = PhotoImage(file='images/pause.png')
        self.next_btn_image = PhotoImage(file='images/next.png')
        self.prev_btn_image = PhotoImage(file='images/previous.png')
        self.stop_btn_image = PhotoImage(file='images/stop.png')
        self.shuffle_btn_image = PhotoImage(file='images/shuffle.png')
        self.shuffle_btn_image_on = PhotoImage(file='images/shuffle_on.png')
        self.repeat_btn_image = PhotoImage(file='images/repeat.png')
        self.repeat_btn_image_on = PhotoImage(file='images/repeat_on.png')

        self.control_frame = Frame(self.root)
        self.control_frame.pack()

        self.play_btn = Button(self.control_frame, image=self.play_btn_image, borderwidth=0, command=self.play_music)
        self.pause_btn = Button(self.control_frame, image=self.pause_btn_image, borderwidth=0, command=self.pause_music)
        self.next_btn = Button(self.control_frame, image=self.next_btn_image, borderwidth=0, command=self.next_music)
        self.prev_btn = Button(self.control_frame, image=self.prev_btn_image, borderwidth=0, command=self.prev_music)
        self.stop_btn = Button(self.control_frame, image=self.stop_btn_image, borderwidth=0, command=self.stop_music)
        self.shuffle_btn = Button(self.control_frame, image=self.shuffle_btn_image, borderwidth=0, command=self.toggle_shuffle)
        self.repeat_btn = Button(self.control_frame, image=self.repeat_btn_image, borderwidth=0, command=self.toggle_repeat)
        self.push_to_talk_btn = Button(self.control_frame, text="Push to Talk", command=self.toggle_listening)

        self.play_btn.grid(row=0, column=1, padx=7, pady=10)
        self.pause_btn.grid(row=0, column=2, padx=7, pady=10)
        self.next_btn.grid(row=0, column=3, padx=7, pady=10)
        self.prev_btn.grid(row=0, column=0, padx=7, pady=10)
        self.stop_btn.grid(row=0, column=4, padx=7, pady=10)
        self.shuffle_btn.grid(row=0, column=5, padx=7, pady=10)
        self.repeat_btn.grid(row=0, column=6, padx=7, pady=10)
        self.push_to_talk_btn.grid(row=0, column=7, padx=7, pady=10)

        self.volume_slider = Scale(self.root, from_=0, to=1, resolution=0.1, orient="horizontal", command=self.set_volume)
        self.volume_slider.set(0.5)
        pygame.mixer.music.set_volume(0.5)
        self.volume_slider.pack()

        self.song_duration_label = Label(self.root, text="Duration: 00:00")
        self.song_duration_label.pack()
        self.elapsed_time_label = Label(self.root, text="Elapsed Time: 00:00")
        self.elapsed_time_label.pack()

        self.update_elapsed_time()

        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone(device_index=0)

        self.voice_commands = {
            "play": self.play_music,
            "pause": self.pause_music,
            "stop": self.stop_music,
            "next": self.next_music,
            "previous": self.prev_music,
            "shuffle": self.toggle_shuffle,
            "repeat": self.toggle_repeat
        }

        self.listening = False

    def load_music(self):
        self.directory = filedialog.askdirectory()
        self.songs.clear()
        self.songlist.delete(0, END)
        for song in os.listdir(self.directory):
            name, ext = os.path.splitext(song)
            if ext == '.mp3':
                self.songs.append(song)
        for song in self.songs:
            self.songlist.insert("end", song)
        self.songlist.selection_set(0)
        self.current_song = self.songs[self.songlist.curselection()[0]]

    def play_music(self):
        if not self.paused:
            pygame.mixer.music.load(os.path.join(self.directory, self.current_song))
            pygame.mixer.music.play()
        else:
            pygame.mixer.music.unpause()
            self.paused = False
        self.update_song_duration()

    def pause_music(self):
        pygame.mixer.music.pause()
        self.paused = True

    def stop_music(self):
        pygame.mixer.music.stop()
        self.paused = False

    def next_music(self):
        try:
            self.songlist.selection_clear(0, END)
            if self.shuffle:
                next_index = random.randint(0, len(self.songs) - 1)
            else:
                next_index = self.songs.index(self.current_song) + 1
            self.songlist.selection_set(next_index)
            self.current_song = self.songs[self.songlist.curselection()[0]]
            self.play_music()
        except IndexError:
            pass

    def prev_music(self):
        try:
            self.songlist.selection_clear(0, END)
            prev_index = self.songs.index(self.current_song) - 1
            self.songlist.selection_set(prev_index)
            self.current_song = self.songs[self.songlist.curselection()[0]]
            self.play_music()
        except IndexError:
            pass

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        self.update_shuffle_button()

    def toggle_repeat(self):
        self.repeat = not self.repeat
        self.update_repeat_button()

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(float(volume))

    def update_song_duration(self):
        try:
            song_path = os.path.join(self.directory, self.current_song)
            audio = MP3(song_path)
            song_length = audio.info.length
            minutes, seconds = divmod(song_length, 60)
            self.song_duration_label.config(text=f"Duration: {int(minutes):02}:{int(seconds):02}")
        except:
            self.song_duration_label.config(text="Duration: 00:00")

    def update_elapsed_time(self):
        if pygame.mixer.music.get_busy():
            elapsed_time = pygame.mixer.music.get_pos() / 1000
            minutes, seconds = divmod(elapsed_time, 60)
            self.elapsed_time_label.config(text=f"Elapsed Time: {int(minutes):02}:{int(seconds):02}")
        self.root.after(1000, self.update_elapsed_time)

    def update_shuffle_button(self):
        if self.shuffle:
            self.shuffle_btn.config(image=self.shuffle_btn_image_on)
        else:
            self.shuffle_btn.config(image=self.shuffle_btn_image)

    def update_repeat_button(self):
        if self.repeat:
            self.repeat_btn.config(image=self.repeat_btn_image_on)
        else:
            self.repeat_btn.config(image=self.repeat_btn_image)

    def toggle_listening(self):
        if not self.listening:
            self.listening = True
            self.push_to_talk_btn.config(text="Listening...")
            self.start_voice_command_thread()
        else:
            self.listening = False
            self.push_to_talk_btn.config(text="Push to Talk")

    def start_voice_command_thread(self):
        voice_thread = threading.Thread(target=self.listen_for_voice_commands)
        voice_thread.daemon = True
        voice_thread.start()

    def listen_for_voice_commands(self):
        while self.listening:
            with self.mic as source:
                audio = self.recognizer.listen(source)
            try:
                command = self.recognizer.recognize_google(audio).lower()
                print(f"Recognized command: {command}")  # Debug print statement
                if command in self.voice_commands:
                    self.voice_commands[command]()
                else:
                    print("Command not recognized")
            except sr.UnknownValueError:
                print("Could not understand audio")  # Debug print statement

if __name__ == "__main__":
    root = Tk()
    app = MusicPlayer(root)
    root.mainloop()
