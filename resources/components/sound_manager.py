import vlc
from .audio_scripts import get_audio_metadata
from ursina import Entity

class SoundManager(Entity):
    def __init__(self):
        super().__init__()
        self.current_song_name: str = None
        self.current_song: vlc.MediaPlayer = vlc.MediaPlayer()
        self.current_song_title: str | None = None
        self.current_song_artist: str | None = None
        self.current_volume: int = self.current_song.audio_get_volume()

    def playsong(self, newSong, sname):
        self.current_song_name = sname
        
        if nm := get_audio_metadata(newSong):
            self.current_song_title = nm["title"]
            self.current_song_artist = nm["artist"]
        else:
            self.current_song_title = sname
            self.current_song_artist = sname

        if self.current_song.get_state() == vlc.State.Playing or self.current_song.get_state() == vlc.State.Paused:
            self.current_song.stop()

        self.current_song = vlc.MediaPlayer(newSong)
        self.current_song.play()
        
        if self.current_song_title == None:
            self.current_song_title = sname

        print(self.current_song_title)
        

    def stop(self):
        self.current_song.stop()
    
    def input(self, event) -> None:
        self.current_volume = self.current_song.audio_get_volume()

        if event == "up arrow":
            print("Volume UP")
            if self.current_volume < 100:
                self.current_song.audio_set_volume(self.current_volume + 2)

                if self.current_volume > 100:
                    self.current_song.audio_set_volume(100)
                
            

        elif event == "down arrow":
            print("Volume Down")
            if self.current_volume >= 1:
                self.current_song.audio_set_volume(self.current_volume - 1)
        