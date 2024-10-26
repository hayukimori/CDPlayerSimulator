import vlc
from pathlib import Path, PosixPath
from tinytag import TinyTag
from ursina import Entity

def get_audio_metadata(file_path) -> dict | None:
    try:
        tag = TinyTag.get(file_path)
        metadata = {
            'title': tag.title,
            'artist': tag.artist,
            'duration': tag.duration
        }
        return metadata
    
    except Exception as e:
        print("Error extracting metadata")
        return None

class DiscManager(Entity):
    def __init__(self, disc_audio1: PosixPath) -> None:
        super().__init__()
        self.bool_var = False

        self.player :vlc.MediaPlayer = vlc.MediaPlayer(disc_audio1)
        self.em = self.player.event_manager()
        self.em.event_attach(vlc.EventType.MediaPlayerEndReached, self.onEnd)

        self.player.play()
    
    def onEnd(self, event) -> None:
        if event.type == vlc.EventType.MediaPlayerEndReached:
            self.bool_var = True

    def back(self):
        self.player.set_media(self.player.get_media())
        self.player.play()
    
    def update(self):
        if self.bool_var:
            self.back()
            self.bool_var = False


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
            if self.current_volume < 100:
                self.current_song.audio_set_volume(self.current_volume + 2)

                if self.current_volume > 100:
                    self.current_song.audio_set_volume(100)
                
        elif event == "down arrow":
            if self.current_volume >= 1:
                self.current_song.audio_set_volume(self.current_volume - 1)
        